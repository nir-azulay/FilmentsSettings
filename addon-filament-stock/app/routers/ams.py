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
# The ha-bambulab integration exposes per-tray sensors like
#   sensor.h2s_<serial>_ams_<ams_idx>_tray_<tray_idx>
# (ams_idx is 1-based per unit; tray_idx is 1-4) and an "external spool" sensor
#   sensor.h2s_<serial>_external_spool   (sometimes _vt_tray, depending on
#   integration version)
# We match both shapes and synthesise a stable (ams_idx, tray_idx) tuple.
_AMS_TRAY_RE = re.compile(
    r"^sensor\.(?P<printer>.+?)_ams_(?P<ams>\d+)_tray_(?P<tray>\d+)$"
)
_EXTERNAL_TRAY_RE = re.compile(
    r"^sensor\.(?P<printer>.+?)_(?:external_spool|vt_tray|external_tray)$"
)

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
    ams_match = _AMS_TRAY_RE.match(entity_id)
    ext_match = _EXTERNAL_TRAY_RE.match(entity_id) if not ams_match else None
    if not ams_match and not ext_match:
        return None

    attrs = entity.get("attributes") or {}
    state = entity.get("state")
    loaded = _is_loaded(state)

    if ams_match:
        printer = ams_match.group("printer")
        ams_idx: int | None = int(ams_match.group("ams"))
        tray_idx = int(ams_match.group("tray"))
        location_label = f"AMS {ams_idx} · Slot {tray_idx}"
        kind = "ams"
    else:
        assert ext_match is not None
        printer = ext_match.group("printer")
        ams_idx = None
        tray_idx = 0  # external spool has no slot index; use 0 for stable sort
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
