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
from ..ha_client import HAClientError, get_all_states, render_template
from ..models import ColorStock, Filament
from .assignments import get_current_assignments_map

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
    r"_(?P<ams>\d+)_tray_(?P<tray>\d+)"
    # HA appends "_2", "_3", ... when two devices try to claim the same
    # entity_id slug. ha-bambulab does this for AMS 2 Pro #2's trays
    # because both AMS 2 Pros' tray entities want to be named
    # ..._ams_1_tray_<n>. Capture the suffix so we can use it as a
    # secondary AMS-instance discriminator below.
    r"(?:_(?P<dupe>\d+))?$"
)
# Last-resort matcher: anything that mentions "_tray_<n>" and lives on a sensor
# whose attributes look like a Bambu tray (we test that in _parse_tray).
_FALLBACK_TRAY_RE = re.compile(
    r"^sensor\.(?P<printer>.+?)_tray_(?P<tray>\d+)(?:_(?P<dupe>\d+))?$"
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

    # HA appends "_2", "_3", ... when two entities want the same entity_id
    # slug. ha-bambulab does this for the second AMS 2 Pro's trays because
    # both AMS 2 Pros' trays naturally land at .._ams_1_tray_<n>. The dupe
    # number is the strongest signal we have for "this tray belongs to AMS
    # unit #N of this model" -- HA assigns _2 to the second device, _3 to
    # the third, and so on. Treat dupe=None as instance 1.
    def _instance_from(match: re.Match[str] | None) -> int:
        if match is None:
            return 1
        try:
            dupe = match.groupdict().get("dupe")
        except IndexError:
            dupe = None
        return int(dupe) + 1 if dupe else 1

    instance_idx: int = 1

    if ams_match:
        printer = ams_match.group("printer")
        variant = ams_match.group("variant")  # "ams" | "ams_pro" | "ams2pro" | ...
        ams_idx: int | None = int(ams_match.group("ams"))
        tray_idx = int(ams_match.group("tray"))
        instance_idx = _instance_from(ams_match)
        # Pretty-print the variant slug for the UI. "AMS" gets the
        # `AMS <idx>` form (the index is the unit number), the named
        # variants get `AMS 2 Pro #<idx>` to make the index visually
        # distinct from the model name. We use `instance_idx` (HA's _2 / _3
        # suffix) when it's > 1, otherwise the entity_id's ams_idx -- but
        # _renumber_ams_units() later overwrites this with a clean
        # 1..N sequence anyway, so this is just a fallback label.
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
            unit_suffix = f" #{instance_idx}" if instance_idx > 1 else f" #{ams_idx}"
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
        instance_idx = _instance_from(fallback_match)
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

    # HA's `friendly_name` attribute is the gold-standard label for these
    # entities -- ha-bambulab sets it to e.g. "AMS 2 Pro #1 Tray 1", which
    # already contains the correct hardware-model name AND the per-printer
    # unit index. When present, derive a clean "AMS 2 Pro #1 · Slot 1" label
    # straight from it instead of cobbling one together from the entity_id.
    friendly_name = attrs.get("friendly_name")
    if isinstance(friendly_name, str) and friendly_name:
        derived = _label_from_friendly_name(friendly_name, kind)
        if derived:
            location_label = derived

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
        # HA's _2/_3/... entity-id duplicate suffix. We use this to tell two
        # AMS units of the same model apart -- ha-bambulab's AMS 2 Pro #2
        # claims the same _ams_1_tray_<n> slug as AMS 2 Pro #1, and HA
        # disambiguates by appending _2 to the tray entity_ids.
        "instance_idx": instance_idx,
        "friendly_name": (attrs.get("friendly_name") if isinstance(attrs.get("friendly_name"), str) else None),
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


# ── Device-registry lookup via /api/template ─────────────────────────────────
# HA's plain /api/states response does not expose device metadata. The
# easiest way to get model/manufacturer/name without pulling in a WebSocket
# client is to render a Jinja2 template that loops over the entities we
# want and emits a small JSON map. Keys are entity_ids; values are
# {"name": ..., "model": ..., "manufacturer": ..., "via_device_id": ...}.
#
# We restrict the template's loop to a small list of entity_ids (the ones we
# already classified as Bambu trays) so it stays cheap even on installs with
# thousands of entities.


def _entity_ids_jinja_list(entity_ids: list[str]) -> str:
    """Render a Python list of strings as a Jinja2 list literal -- e.g.
    ['sensor.a', 'sensor.b']. Used to inject the list into the template
    body. Safe because we already validated entity_ids match our matcher
    regexes (so no quotes / newlines / control chars)."""
    inner = ", ".join(f"'{eid}'" for eid in entity_ids)
    return f"[{inner}]"


def _build_device_info_template(entity_ids: list[str]) -> str:
    eids = _entity_ids_jinja_list(entity_ids)
    # device_attr() returns None for entities without an associated device,
    # so wrap each call in iif() to keep the JSON valid. We render JSON by
    # hand because Jinja's `tojson` filter is not consistently available
    # across HA template contexts.
    return (
        "{% set out = namespace(parts=[]) %}"
        "{% for eid in " + eids + " %}"
        "{% set did = device_id(eid) %}"
        "{% set name = device_attr(did, 'name_by_user') or device_attr(did, 'name') %}"
        "{% set model = device_attr(did, 'model') %}"
        "{% set manuf = device_attr(did, 'manufacturer') %}"
        "{% set via   = device_attr(did, 'via_device_id') %}"
        "{% set vname = device_attr(via, 'name_by_user') or device_attr(via, 'name') %}"
        "{% set part %}"
        '"{{ eid }}": {'
        '"device_id": {{ (did or "")|tojson }}, '
        '"name": {{ (name or "")|tojson }}, '
        '"model": {{ (model or "")|tojson }}, '
        '"manufacturer": {{ (manuf or "")|tojson }}, '
        '"via_device_id": {{ (via or "")|tojson }}, '
        '"via_name": {{ (vname or "")|tojson }}'
        "}"
        "{% endset %}"
        "{% set out.parts = out.parts + [part] %}"
        "{% endfor %}"
        "{ {{ out.parts | join(', ') }} }"
    )


async def _fetch_device_info(entity_ids: list[str]) -> dict[str, dict[str, str]]:
    """Render a template that joins each entity to its device-registry row
    and returns ``{entity_id: {name, model, manufacturer, via_name, ...}}``.

    Empty / None values are returned as empty strings to keep callers simple.
    Returns an empty dict on any rendering or parsing failure -- this is a
    nice-to-have lookup; the rest of the AMS view stays functional without it.
    """
    if not entity_ids:
        return {}
    try:
        body = await render_template(_build_device_info_template(entity_ids))
    except HAClientError as exc:
        _log.warning("device-info template render failed: %s", exc)
        return {}
    body = (body or "").strip()
    if not body:
        return {}
    import json as _json
    try:
        parsed = _json.loads(body)
    except _json.JSONDecodeError as exc:
        _log.warning("device-info template returned non-JSON: %s (body=%r)", exc, body[:200])
        return {}
    if not isinstance(parsed, dict):
        return {}
    return parsed


# ── Bambu hardware-model normalisation ───────────────────────────────────────

# Map raw `device_attr(..., 'model')` strings from ha-bambulab to a pretty
# label. Lower-cased substring match -- ha-bambulab has used different
# strings across releases ("AMS 2 PRO", "AMS-2-Pro", etc.).
_MODEL_LABEL_PATTERNS: tuple[tuple[str, str], ...] = (
    ("ams 2 pro", "AMS 2 Pro"),
    ("ams2 pro", "AMS 2 Pro"),
    ("ams-2-pro", "AMS 2 Pro"),
    ("ams2pro", "AMS 2 Pro"),
    ("ams ht", "AMS HT"),
    ("ams-ht", "AMS HT"),
    ("ams ht1", "AMS HT"),
    ("ams hub", "AMS HUB"),
    ("ams-hub", "AMS HUB"),
    ("ams lite", "AMS Lite"),
    ("ams-lite", "AMS Lite"),
    # The generic "AMS" or "AMS1" comes last so it doesn't shadow the
    # specific variants above.
    ("ams", "AMS"),
)


def _pretty_model(raw_model: str | None) -> str | None:
    if not raw_model:
        return None
    s = raw_model.strip().lower()
    if not s:
        return None
    for needle, label in _MODEL_LABEL_PATTERNS:
        if needle in s:
            return label
    return raw_model.strip()


# ── friendly_name extraction ────────────────────────────────────────────────
# ha-bambulab sets `friendly_name` on each tray sensor to something like
# "AMS 2 Pro #1 Tray 1" / "AMS HT #2 Tray 1" / "AMS 1 Tray 3". That string
# already contains the model name, the per-printer unit index, AND the
# slot number -- everything we want in the location_label.

_FRIENDLY_TRAY_RE = re.compile(
    r"^(?P<unit>.+?)\s+Tray\s+(?P<slot>\d+)\s*$",
    re.IGNORECASE,
)

_FRIENDLY_MODEL_RE = re.compile(
    r"^(?P<model>"
    r"AMS\s*2\s*Pro|AMS\s*Pro|AMS\s*HT|AMS\s*Lite|AMS\s*HUB|AMS"
    r")\b",
    re.IGNORECASE,
)


def _label_from_friendly_name(friendly: str, kind: str) -> str | None:
    """Convert a HA friendly_name like "AMS 2 Pro #1 Tray 1" into our
    "AMS 2 Pro #1 · Slot 1" format. Returns None when the friendly_name
    doesn't look like a tray name (so callers keep their fallback)."""
    if not friendly or kind != "ams":
        return None
    m = _FRIENDLY_TRAY_RE.match(friendly.strip())
    if not m:
        return None
    return f"{m.group('unit').strip()} · Slot {int(m.group('slot'))}"


def _model_from_friendly_name(friendly: str | None) -> str | None:
    """Pull just the hardware model out of a friendly_name like
    "AMS 2 Pro #1 Tray 1". Returns "AMS 2 Pro" / "AMS HT" / "AMS" / etc.,
    or None if the string doesn't start with a recognised model."""
    if not friendly:
        return None
    m = _FRIENDLY_MODEL_RE.match(friendly.strip())
    if not m:
        return None
    # Re-normalise spacing/case via _pretty_model so "AMS 2 PRO" and
    # "AMS  2  Pro" both end up as "AMS 2 Pro".
    return _pretty_model(m.group("model"))


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

    # Enrich with device-registry info (hardware model, printer device name,
    # etc.) so the UI can say "AMS 2 Pro #1" instead of "AMS 128". Best-effort:
    # _fetch_device_info silently returns {} on any failure so the rest of the
    # panel keeps working.
    device_info = await _fetch_device_info([t["entity_id"] for t in trays])
    _enrich_with_device_info(trays, device_info)

    # Now that we know the real hardware groups, normalise the ams_idx within
    # each (printer_label, model) bucket so users see "AMS 2 Pro #1" / "#2"
    # instead of "AMS 128" / "AMS 129".
    _renumber_ams_units(trays)

    # Drop nonsense `remain_pct` values that ha-bambulab uses to mean
    # "unknown" (typically -1, occasionally 255 on older firmware).
    for t in trays:
        rp = t.get("remain_pct")
        if rp is None or rp < 0 or rp > 100:
            t["remain_pct"] = None

    # Annotate each tray with its current "I loaded this from my stock"
    # assignment, if any. One query for all trays via the helper -- O(1)
    # extra DB cost regardless of the number of trays. Added in 0.6.0.
    assignment_map = get_current_assignments_map(db)
    for t in trays:
        t["assignment"] = assignment_map.get(t["entity_id"])

    # Stable ordering: external spool last, otherwise (printer, ams, tray).
    trays.sort(
        key=lambda t: (
            t["kind"] != "ams",
            t.get("printer_label") or t.get("printer") or "",
            t.get("model_label") or "",
            t.get("ams_idx") if t.get("ams_idx") is not None else 99,
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


# ── Enrichment helpers ───────────────────────────────────────────────────────


def _enrich_with_device_info(
    trays: list[dict[str, Any]], device_info: dict[str, dict[str, str]]
) -> None:
    """Annotate each tray with `device_name`, `model_label`, `printer_label`.

    `printer_label` is the friendly name of the AMS device's *parent*
    (`via_device`) -- which on ha-bambulab is the printer itself. That gives
    us "H2S" or "H2S 3D Printer" instead of "h2s_<hex serial>_externalspool".
    """
    for t in trays:
        info = device_info.get(t["entity_id"]) or {}
        raw_model = info.get("model") or ""
        device_name = info.get("name") or ""
        via_name = info.get("via_name") or ""

        # Resolve the model label, in priority order:
        #   1. friendly_name (e.g. "AMS 2 Pro #1 Tray 1" -> "AMS 2 Pro")
        #   2. device-registry model field
        #   3. AMS entity-id variant slug we parsed earlier
        friendly_model = _model_from_friendly_name(t.get("friendly_name"))
        registry_model = _pretty_model(raw_model)
        if t["kind"] == "external":
            t["model_label"] = "External spool"
        else:
            t["model_label"] = friendly_model or registry_model or "AMS"

        t["device_name"] = device_name
        # Prefer the parent (printer) name from the device registry. Fall
        # back to the entity's own device name minus any "AMS" / "external"
        # suffix, then to the raw printer slug we already extracted from
        # the entity_id.
        printer_label = (
            via_name
            or _strip_ams_suffix(device_name)
            or _slug_to_label(t.get("printer") or "")
        )
        t["printer_label"] = printer_label or "Printer"

        # External spools get their definitive label here -- AMS trays are
        # finalised by _renumber_ams_units() below since the # suffix
        # depends on whether there's more than one of this model on the
        # printer.
        if t["kind"] == "external":
            t["unit_label"] = "External spool"
            t["location_label"] = "External spool"


def _renumber_ams_units(trays: list[dict[str, Any]]) -> None:
    """Replace ha-bambulab's internal AMS device identifiers with stable
    1-based sequence numbers per (printer, model). Two physical AMS units
    of the same model are distinguished by `(ams_idx, instance_idx)` --
    ha-bambulab uses HA's entity-id `_2`/`_3` suffix on the second / third
    duplicate, so a single classic AMS produces `(1, 1)`, two AMS 2 Pros
    produce `(1, 1)` and `(1, 2)`, and two AMS HTs produce `(128, 1)` and
    `(129, 1)`.

    External spools are skipped.

    Mutates each AMS tray's `ams_idx`, `unit_label`, and `location_label`
    in-place.
    """
    # Group AMS trays by (printer_label, model_label).
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for t in trays:
        if t["kind"] != "ams":
            continue
        key = (t.get("printer_label") or "", t.get("model_label") or "AMS")
        groups.setdefault(key, []).append(t)

    for (printer_label, model_label), members in groups.items():
        # Discover the distinct (ams_idx, instance_idx) pairs within this
        # bucket and assign each a 1-based sequence number, sorted by the
        # composite key. Two AMS 2 Pros with `ams_idx=1` will appear as
        # (1, 1) and (1, 2) and get sequence numbers 1 and 2.
        unit_keys = sorted(
            {
                (t.get("ams_idx") or 0, t.get("instance_idx") or 1)
                for t in members
            }
        )
        seq_map = {pair: pos + 1 for pos, pair in enumerate(unit_keys)}
        multi_unit = len(unit_keys) > 1

        for t in members:
            pair = (t.get("ams_idx") or 0, t.get("instance_idx") or 1)
            seq = seq_map[pair]
            t["ams_idx"] = seq  # overwrite raw idx with display index
            if model_label == "AMS":
                # Classic AMS: "AMS 1 · Slot 3".
                t["unit_label"] = f"AMS {seq}"
            elif multi_unit:
                # Named variant with more than one of the same model on this
                # printer: "AMS 2 Pro #1".
                t["unit_label"] = f"{model_label} #{seq}"
            else:
                # Lone unit of its model: no #N suffix needed.
                t["unit_label"] = model_label
            t["location_label"] = f"{t['unit_label']} · Slot {t['tray_idx']}"


# ── Printer-name normalisation helpers ───────────────────────────────────────

_AMS_SUFFIX_RE = re.compile(
    r"\s*(?:"
    r"externalspool|external_spool|external|external_tray|external_filament"
    r"|vt_tray|virtual_tray|virtual_spool"
    r"|ams\s*\d*|ams\s*pro|ams\s*ht|ams\s*lite|ams\s*hub|ams\s*2\s*pro"
    r")\s*$",
    re.IGNORECASE,
)


def _strip_ams_suffix(name: str) -> str:
    """Trim trailing AMS / external-spool words from a device name.

    "H2S 0938BC5C2200107 ExternalSpool"  -> "H2S 0938BC5C2200107"
    "H2S 0938BC5C2200107 AMS 1"          -> "H2S 0938BC5C2200107"
    "H2S 0938BC5C2200107 AMS 2 Pro #1"   -> "H2S 0938BC5C2200107"
    """
    if not name:
        return ""
    stripped = name.strip()
    # Strip up to 2 trailing AMS/external tokens (e.g. "AMS 2 Pro" then "#1").
    for _ in range(3):
        new = _AMS_SUFFIX_RE.sub("", stripped).rstrip(" -·#")
        if new == stripped:
            break
        stripped = new
    return stripped


def _slug_to_label(slug: str) -> str:
    """Make a snake_case slug human-friendly:
    "h2s_0938bc5c2200107_externalspool" -> "H2S 0938bc5c2200107"
    """
    if not slug:
        return ""
    label = slug.replace("_", " ").strip()
    label = _AMS_SUFFIX_RE.sub("", label).rstrip(" -·#")
    # Title-case the first token if it's a short printer prefix like "h2s",
    # "p1p", "x1c", etc. (mix of letters and digits, <=5 chars). Leave long
    # hex serial-number tokens alone.
    parts = label.split()
    if parts and len(parts[0]) <= 5 and any(c.isalpha() for c in parts[0]):
        parts[0] = parts[0].upper()
    return " ".join(parts)


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
