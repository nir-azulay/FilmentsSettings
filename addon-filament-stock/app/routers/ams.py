"""AMS (Automatic Material System) view endpoints.

Surfaces the currently-loaded filament in every Bambu AMS tray reported by
the `greghesp/ha-bambulab` HACS integration, and cross-references each tray
with the local Filament + ColorStock rows so the UI can render

  "AMS 1 / Slot 3: SUNLU PETG HS Black at 73% -- matches 2 spools in stock"

at a glance.

Read-only -- nothing here mutates HA state or the local DB.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..ha_client import HAClientError, get_all_states
from ..models import ColorStock, Filament

router = APIRouter(tags=["ams"])
_log = logging.getLogger("filament_stock.ams")

# ── Tray entity-id matching ──────────────────────────────────────────────────
# The ha-bambulab integration uses different entity-id schemes depending on
# the AMS hardware model:
#
#   Classic AMS (the original 4-bay):
#     sensor.<printer>_ams_<ams_idx>_tray_<tray_idx>
#
#   AMS 2 Pro / AMS HT / AMS Lite:
#     sensor.<printer>_ams_pro_<ams_idx>_tray_<tray_idx>
#     sensor.<printer>_ams2pro_<ams_idx>_tray_<tray_idx>
#     sensor.<printer>_ams_ht_<ams_idx>_tray_<tray_idx>
#     sensor.<printer>_ams_lite_<ams_idx>_tray_<tray_idx>
#     (variant slug between `_ams` and `_<ams_idx>_tray_` depends on the
#     ha-bambulab release; the version-agnostic match is "contains _tray_<n>
#     somewhere and exposes Bambu tray attributes" -- see _FALLBACK_TRAY_RE.)
#
#   External spool / virtual tray:
#     sensor.<printer>_external_spool        (newer)
#     sensor.<printer>_vt_tray               (older)
#     sensor.<printer>_external_tray         (some forks)
#
# We try the structured matches first so we extract a clean (printer, ams_idx,
# tray_idx) tuple; if those miss we fall back to entity_id-keyword + Bambu
# attribute sniffing, so future hardware models work without a code change.
_AMS_TRAY_RE = re.compile(
    r"^sensor\.(?P<printer>.+?)"
    r"_(?P<variant>ams(?:_pro|2pro|_ht|_lite|_hub)?)"
    r"_(?P<ams>\d+)_tray_(?P<tray>\d+)$"
)
# Last-resort matcher: anything that mentions "_tray_<n>" and lives on a sensor
# whose attributes look like a Bambu tray (we test that in _parse_tray).
_FALLBACK_TRAY_RE = re.compile(
    r"^sensor\.(?P<printer>.+?)_tray_(?P<tray>\d+)$"
)
# External spool entity-id schemes seen across ha-bambulab versions and
# forks. We also fall back to an attribute-sniffing match below
# (see _looks_like_external_spool) so that future names work without code
# changes.
_EXTERNAL_TRAY_RE = re.compile(
    r"^sensor\.(?P<printer>.+?)_(?:"
    r"external_spool|external_spool_tray|external_tray"
    r"|ext_spool|ext_tray"
    r"|vt_tray|virtual_tray|virtual_spool"
    r"|x1_external|external"
    r")$"
)

# Heuristic for "this is an external-spool sensor we missed with the regex
# above" -- entity_id mentions external/vt/spool somewhere and the sensor
# carries Bambu tray attributes.
_EXTERNAL_KEYWORD_RE = re.compile(r"(?:external|vt_tray|virtual)")

# Attribute keys ha-bambulab puts on tray sensors. Presence of any one of
# these is what tells us a "_tray_<n>" sensor really belongs to Bambu (and
# not, say, some random custom integration that happens to use the same word).
_BAMBU_TRAY_ATTRS = (
    "filament_id",
    "tray_info_idx",
    "tray_uuid",
    "tray_type",
    "tray_sub_brands",
    "tray_color",
)


def _looks_like_bambu_tray(attrs: dict[str, Any]) -> bool:
    return any(k in attrs for k in _BAMBU_TRAY_ATTRS)

# State values that mean "nothing loaded" rather than a real filament name.
_EMPTY_STATES = {"empty", "unknown", "unavailable", "none", ""}


def _norm_hex(raw: Any) -> str | None:
    """Normalise Bambu's color attribute to #RRGGBB (drop alpha channel)."""
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if not s.startswith("#"):
        s = "#" + s
    # #RRGGBB, #RRGGBBAA, or even a bare RRGGBB. Always keep the leading 7 chars.
    s = s[:7].upper()
    if not re.fullmatch(r"#[0-9A-F]{6}", s):
        return None
    return s


def _coerce_int(raw: Any) -> int | None:
    try:
        if raw is None or raw == "":
            return None
        return int(float(raw))
    except (TypeError, ValueError):
        return None


def _is_loaded(state: str | None) -> bool:
    if state is None:
        return False
    return state.strip().lower() not in _EMPTY_STATES


def _parse_tray(entity: dict[str, Any]) -> dict[str, Any] | None:
    """Convert one HA state dict into our tray shape, or None if it isn't a
    Bambu AMS tray entity at all."""
    entity_id = entity.get("entity_id", "")
    attrs = entity.get("attributes") or {}
    state = entity.get("state")

    ams_match = _AMS_TRAY_RE.match(entity_id)
    ext_match = _EXTERNAL_TRAY_RE.match(entity_id) if not ams_match else None
    fallback_match = (
        _FALLBACK_TRAY_RE.match(entity_id)
        if not ams_match and not ext_match and _looks_like_bambu_tray(attrs)
        else None
    )
    # Attribute-based fallback for the external spool. We get here when the
    # printer's external-spool sensor lives at a name we haven't seen yet
    # (e.g. "_x1_spool", "_h2s_external_filament", whatever). We rely on the
    # entity_id mentioning external/vt/virtual AND the sensor exposing the
    # Bambu tray attribute set.
    external_fallback = (
        not ams_match
        and not ext_match
        and not fallback_match
        and entity_id.startswith("sensor.")
        and _EXTERNAL_KEYWORD_RE.search(entity_id) is not None
        and _looks_like_bambu_tray(attrs)
    )
    if not ams_match and not ext_match and not fallback_match and not external_fallback:
        return None

    loaded = _is_loaded(state)

    if ams_match:
        printer = ams_match.group("printer")
        variant = ams_match.group("variant")  # "ams" | "ams_pro" | "ams2pro" | ...
        ams_idx: int | None = int(ams_match.group("ams"))
        tray_idx = int(ams_match.group("tray"))
        # Pretty-print the variant slug for the UI. "AMS" gets the
        # `AMS <idx>` form (the index is the unit number), the named
        # variants get `AMS 2 Pro #<idx>` to make the index visually
        # distinct from the model name.
        if variant == "ams":
            variant_label = "AMS"
            unit_suffix = f" {ams_idx}"
        else:
            variant_label = {
                "ams_pro": "AMS 2 Pro",
                "ams2pro": "AMS 2 Pro",
                "ams_ht": "AMS HT",
                "ams_lite": "AMS Lite",
                "ams_hub": "AMS HUB",
            }.get(variant, "AMS")
            unit_suffix = f" #{ams_idx}"
        location_label = f"{variant_label}{unit_suffix} · Slot {tray_idx}"
        kind = "ams"
    elif fallback_match:
        # We have a "_tray_<n>" sensor with Bambu attributes but its entity_id
        # doesn't match any known _ams_<n>_ scheme. Best we can do is treat the
        # whole prefix as the printer/AMS identifier and surface the raw
        # entity_id so the user can tell us if our regex still misses
        # something on their hardware.
        printer = fallback_match.group("printer")
        ams_idx = None
        tray_idx = int(fallback_match.group("tray"))
        # Try to lift an AMS index out of the entity_id, e.g.
        # "h2s_xxx_ams_pro_2_tray_3" -> 2. Best-effort only.
        m = re.search(r"_(?:ams|ams_pro|ams2pro|ams_ht|ams_lite|ams_hub)_(\d+)_", entity_id)
        if m:
            ams_idx = int(m.group(1))
        location_label = (
            f"AMS {ams_idx} · Slot {tray_idx}" if ams_idx is not None
            else f"Tray {tray_idx}"
        )
        kind = "ams"
    elif ext_match:
        printer = ext_match.group("printer")
        ams_idx = None
        tray_idx = 0  # external spool has no slot index; use 0 for stable sort
        location_label = "External spool"
        kind = "external"
    else:
        # external_fallback: sensor.<printer>_<...something external...>
        # We can't extract a clean printer name, so we lift the longest
        # plausible prefix (everything between "sensor." and the first
        # external/vt/virtual keyword).
        body = entity_id[len("sensor."):]
        m = _EXTERNAL_KEYWORD_RE.search(body)
        printer = body[: m.start()].rstrip("_") if m else body
        ams_idx = None
        tray_idx = 0
        location_label = "External spool"
        kind = "external"

    # ha-bambulab uses a mix of attribute names across versions, so we try the
    # likely ones in order and fall back to None.
    filament_id = (
        attrs.get("filament_id")
        or attrs.get("tray_info_idx")
        or attrs.get("tray_uuid")
    )
    color_hex = _norm_hex(attrs.get("color") or attrs.get("tray_color"))
    material = (
        attrs.get("tray_type")
        or attrs.get("filament_type")
        or attrs.get("type")
    )
    name = (
        attrs.get("tray_sub_brands")
        or attrs.get("filament_name")
        or attrs.get("name")
        or (state if loaded else None)
    )
    remain = _coerce_int(attrs.get("remain"))

    return {
        "entity_id": entity_id,
        "printer": printer,
        "kind": kind,
        "ams_idx": ams_idx,
        "tray_idx": tray_idx,
        "location_label": location_label,
        "loaded": loaded,
        "raw_state": state,
        "filament_id": str(filament_id) if filament_id else None,
        "color_hex": color_hex,
        "material": str(material) if material else None,
        "name": str(name) if name else None,
        "remain_pct": remain,
        # Echoing last_updated lets the UI render an "as of …" timestamp.
        "last_updated": entity.get("last_updated") or entity.get("last_changed"),
    }


# ── Stock cross-reference ────────────────────────────────────────────────────


def _match_color(
    filament: Filament | None, tray_color_hex: str | None
) -> ColorStock | None:
    """Pick the best-fitting ColorStock row for the tray.

    Priority:
      1. Exact (case-insensitive) hex match on a color we have in stock.
      2. If the filament has exactly one color row, use it (covers single-color
         filaments where Bambu reports a slightly different shade).
      3. Otherwise nothing -- the UI shows "not tracked".
    """
    if filament is None or not filament.colors:
        return None
    if tray_color_hex:
        target = tray_color_hex.upper()
        for c in filament.colors:
            ch = (c.color_hex or "").upper()[:7]
            if ch == target:
                return c
    if len(filament.colors) == 1:
        return filament.colors[0]
    return None


def _stock_summary_for(tray: dict[str, Any], db: Session) -> dict[str, Any]:
    """Look up local stock that corresponds to this tray's filament_id."""
    if not tray["loaded"] or not tray["filament_id"]:
        return {"matched": False, "reason": "tray_empty" if not tray["loaded"] else "no_filament_id"}

    filament = (
        db.query(Filament).filter(Filament.filament_id == tray["filament_id"]).first()
    )
    if filament is None:
        return {
            "matched": False,
            "reason": "filament_id_not_in_stock",
            "filament_id": tray["filament_id"],
        }

    color = _match_color(filament, tray["color_hex"])
    base = {
        "matched": True,
        "filament_db_id": filament.id,
        "brand": filament.brand,
        "material": filament.material,
        "filament_type": filament.filament_type,
        "filament_total_available": filament.current_stock,
    }
    if color is None:
        base.update(
            {
                "color_matched": False,
                "color_reason": "color_hex_not_in_stock",
                "filament_color_count": len(filament.colors),
            }
        )
        return base

    base.update(
        {
            "color_matched": True,
            "color_stock_id": color.id,
            "color_name": color.color_name,
            "color_hex": color.color_hex,
            "available_spool": color.available_spool,
            "available_refill": color.available_refill,
            "available_total": color.available_total,
            "status": color.status,
        }
    )
    return base


# ── Routes ───────────────────────────────────────────────────────────────────


@router.get("/ams/trays")
async def get_ams_trays(db: Session = Depends(get_db)):
    """Return one entry per Bambu AMS tray (and external spool) currently
    visible to Home Assistant, with the matching local stock row attached.

    Response shape::

        {
          "available": true,
          "trays": [
            {
              "entity_id": "...", "printer": "...", "ams_idx": 1, "tray_idx": 3,
              "location_label": "AMS 1 · Slot 3",
              "loaded": true, "filament_id": "P759ffa0",
              "color_hex": "#1A1A1A", "material": "PETG",
              "name": "SUNLU PETG High Speed", "remain_pct": 73,
              "last_updated": "...",
              "stock": { "matched": true, "color_matched": true, ... }
            },
            ...
          ]
        }

    On failure to reach HA::

        { "available": false, "error": "..." , "trays": [] }
    """
    try:
        states = await get_all_states()
    except HAClientError as exc:
        _log.warning("AMS view unavailable: %s", exc)
        # 200 with available=false so the UI can show a friendly empty state
        # instead of a 500-error toast. Real HTTP errors only for bugs.
        return {"available": False, "error": str(exc), "trays": []}

    trays: list[dict[str, Any]] = []
    for st in states:
        tray = _parse_tray(st)
        if tray is None:
            continue
        tray["stock"] = _stock_summary_for(tray, db)
        trays.append(tray)

    # Stable ordering: external spool last, otherwise (printer, ams, tray).
    trays.sort(
        key=lambda t: (
            t["kind"] != "ams",
            t.get("printer") or "",
            t.get("ams_idx") or 99,
            t.get("tray_idx") or 0,
        )
    )

    if not trays:
        raise HTTPException(
            status_code=404,
            detail=(
                "No Bambu AMS tray sensors found in Home Assistant. Install the"
                " 'greghesp/ha-bambulab' HACS integration and add your printer,"
                " then the entities sensor.<printer>_ams_<n>_tray_<n> will"
                " appear here."
            ),
        )

    return {"available": True, "trays": trays}


@router.get("/ams/debug")
async def debug_ams_candidates():
    """Diagnostic endpoint: return every sensor whose entity_id mentions
    'ams' or 'tray', tagged with how (or whether) our matcher recognised it.

    Use this when an AMS hardware variant doesn't show up on the main panel
    so we can extend the regex / attribute list. Read-only; safe to call any
    time.

    Response shape::

        {
          "ok": true,
          "matched_count": 4,
          "unmatched_count": 1,
          "candidates": [
            {
              "entity_id": "sensor.h2s_xxx_ams_pro_2_tray_3",
              "state": "Bambu PLA Matte",
              "attribute_keys": ["filament_id", "tray_type", ...],
              "matched_by": "ams_regex"  // or "fallback_regex" / "external_regex" / null
            },
            ...
          ]
        }
    """
    try:
        states = await get_all_states()
    except HAClientError as exc:
        _log.warning("AMS debug unavailable: %s", exc)
        return {"ok": False, "error": str(exc), "candidates": []}

    out: list[dict[str, Any]] = []
    matched_count = 0
    unmatched_count = 0
    for st in states:
        entity_id = st.get("entity_id", "")
        if not entity_id.startswith("sensor."):
            continue
        if "ams" not in entity_id and "tray" not in entity_id and "spool" not in entity_id:
            continue
        attrs = st.get("attributes") or {}
        matched_by: str | None = None
        if _AMS_TRAY_RE.match(entity_id):
            matched_by = "ams_regex"
        elif _EXTERNAL_TRAY_RE.match(entity_id):
            matched_by = "external_regex"
        elif _FALLBACK_TRAY_RE.match(entity_id) and _looks_like_bambu_tray(attrs):
            matched_by = "tray_attr_fallback"
        elif _EXTERNAL_KEYWORD_RE.search(entity_id) and _looks_like_bambu_tray(attrs):
            matched_by = "external_attr_fallback"
        if matched_by:
            matched_count += 1
        else:
            unmatched_count += 1
        out.append(
            {
                "entity_id": entity_id,
                "state": st.get("state"),
                "attribute_keys": sorted(attrs.keys()),
                # A small subset of attribute values that are useful for
                # disambiguation -- never include the whole attribute blob
                # since some entities carry large arrays.
                "useful_attrs": {
                    k: attrs.get(k)
                    for k in (
                        "filament_id",
                        "tray_info_idx",
                        "tray_type",
                        "tray_sub_brands",
                        "color",
                        "tray_color",
                        "remain",
                    )
                    if k in attrs
                },
                "matched_by": matched_by,
            }
        )

    out.sort(key=lambda e: (e["matched_by"] is None, e["entity_id"]))
    return {
        "ok": True,
        "matched_count": matched_count,
        "unmatched_count": unmatched_count,
        "candidates": out,
    }
