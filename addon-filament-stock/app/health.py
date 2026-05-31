"""Doctor / setup-checklist for the Filament Stock add-on.

Aggregates a handful of best-effort health checks so the frontend can
render a single "is everything OK?" card. The endpoint is cheap enough
to call on every page load: at most one ``GET /api/states`` against HA
Core, plus a lightweight ``GET /api/services`` and ``GET /api/`` ping.

Each check returns a dict with this shape::

    {
        "id": "ha_bambulab_installed",
        "name": "ha-bambulab integration",
        "ok": False,
        "severity": "error" | "warn",
        "message": "Short human-readable result.",
        "hint": "What the user should do to fix it." | None,
        "detail": { ... arbitrary debug info ... } | None,
    }

The full report is::

    {
        "ok": bool,           # True iff *every* check is ok=True
        "severity": "ok" | "warn" | "error",  # worst-case severity
        "checks": [ ... ordered list of check dicts ... ],
        "summary": "1 issue needs attention." | "All systems go.",
    }

Implementation rules:

* No check ever raises -- a check is allowed to *fail* (ok=False) but the
  function must always return a result dict. This keeps the doctor
  endpoint from collapsing the whole UI when one upstream API hiccups.
* Network calls are budgeted: any check that needs HA Core uses the
  ``ha_client`` helpers, which already wrap httpx with a small timeout.
* We share the ``GET /api/states`` payload across multiple checks rather
  than refetching it per-check.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from sqlalchemy import text

from . import ha_client
from .addon_options import get_options
from .database import DATABASE_URL, SessionLocal
from .routers.ams import (
    _AMS_TRAY_RE,
    _EXTERNAL_KEYWORD_RE,
    _EXTERNAL_TRAY_RE,
    _FALLBACK_TRAY_RE,
    _looks_like_bambu_tray,
)

_log = logging.getLogger("filament_stock.health")

# A subset of entity_id prefixes that the ha-bambulab integration owns.
# We use it for the "is the integration installed?" check, which fires
# even when no AMS trays are detected (e.g. user wired up the printer
# but not an AMS).
_BAMBULAB_ENTITY_PREFIXES = (
    "sensor.",
    "binary_sensor.",
    "button.",
    "switch.",
    "light.",
)
_BAMBULAB_FRIENDLY_HINTS = (
    "bambu",
    "p1s", "p1p", "x1c", "x1e", "a1",  # printer model substrings
    "h2s", "h2d",
)


def _is_bambulab_entity(state: dict[str, Any]) -> bool:
    """Heuristic: does this state look like it came from ha-bambulab?

    We can't query the device registry directly here (the doctor must
    not require an additional template render), so we look at the
    entity_id prefix + friendly_name for known Bambu vocabulary. False
    positives are fine -- this only feeds the "integration installed"
    flag, not anything that triggers a write.
    """
    entity_id = state.get("entity_id") or ""
    if not entity_id.startswith(_BAMBULAB_ENTITY_PREFIXES):
        return False
    # Strong signal: any of our AMS / external tray regexes matches.
    if _AMS_TRAY_RE.match(entity_id) or _EXTERNAL_TRAY_RE.match(entity_id):
        return True
    if _FALLBACK_TRAY_RE.match(entity_id) and _looks_like_bambu_tray(
        state.get("attributes") or {}
    ):
        return True
    # Weak signal: entity_id or friendly_name mentions a Bambu term.
    haystacks = [entity_id.lower()]
    attrs = state.get("attributes") or {}
    fn = attrs.get("friendly_name")
    if isinstance(fn, str):
        haystacks.append(fn.lower())
    return any(hint in h for h in haystacks for hint in _BAMBULAB_FRIENDLY_HINTS)


def _printers_from_entities(states: list[dict[str, Any]]) -> set[str]:
    """Return the set of distinct printer slugs visible in AMS / external
    tray entity_ids. The slug is whatever ha-bambulab put between
    ``sensor.`` and the first ``_ams_`` / ``_external_`` segment.
    """
    printers: set[str] = set()
    for state in states:
        entity_id = state.get("entity_id") or ""
        ams = _AMS_TRAY_RE.match(entity_id)
        if ams:
            printers.add(ams.group("printer"))
            continue
        ext = _EXTERNAL_TRAY_RE.match(entity_id)
        if ext:
            printers.add(ext.group("printer"))
    return printers


def _count_tray_entities(states: list[dict[str, Any]]) -> int:
    """Count entities that look like AMS or external-spool trays."""
    count = 0
    for state in states:
        entity_id = state.get("entity_id") or ""
        attrs = state.get("attributes") or {}
        if _AMS_TRAY_RE.match(entity_id):
            count += 1
            continue
        if _EXTERNAL_TRAY_RE.match(entity_id):
            count += 1
            continue
        if _FALLBACK_TRAY_RE.match(entity_id) and _looks_like_bambu_tray(attrs):
            count += 1
            continue
        if _EXTERNAL_KEYWORD_RE.search(entity_id) and _looks_like_bambu_tray(attrs):
            count += 1
    return count


# ── individual checks ──────────────────────────────────────────────────────


def _check_supervisor_token() -> dict[str, Any]:
    ok = bool(os.environ.get("SUPERVISOR_TOKEN"))
    return {
        "id": "supervisor_token",
        "name": "Supervisor token",
        "ok": ok,
        "severity": "ok" if ok else "error",
        "message": (
            "Supervisor injected a token for the add-on."
            if ok
            else "SUPERVISOR_TOKEN env var is missing."
        ),
        "hint": (
            None
            if ok
            else "Make sure config.yaml has 'homeassistant_api: true' and"
            " restart the add-on. The token is injected at startup."
        ),
        "detail": None,
    }


async def _check_ha_core_reachable() -> dict[str, Any]:
    ok = await ha_client.ping_core()
    return {
        "id": "ha_core_reachable",
        "name": "Home Assistant Core API",
        "ok": ok,
        "severity": "ok" if ok else "error",
        "message": (
            "Home Assistant Core API responded on /api/."
            if ok
            else "Could not reach http://supervisor/core/api/."
        ),
        "hint": (
            None
            if ok
            else "Check the Supervisor logs -- Home Assistant Core may be"
            " restarting or unreachable from inside the add-on container."
        ),
        "detail": None,
    }


def _check_database_writable() -> dict[str, Any]:
    """Open a session and run a trivial read/write. We don't INSERT into
    a user-facing table -- a SELECT 1 + an unrelated PRAGMA write proves
    the DB file is reachable and the engine handles writes."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1")).scalar()
            # `user_version` is a free 32-bit slot meant for app-level
            # schema versioning; writing the same value back is a no-op
            # and safe even if another version of the app uses it later.
            current = db.execute(text("PRAGMA user_version")).scalar()
            db.execute(text(f"PRAGMA user_version = {int(current or 0)}"))
            db.commit()
        return {
            "id": "database_writable",
            "name": "SQLite database",
            "ok": True,
            "severity": "ok",
            "message": f"Database is reachable: {DATABASE_URL}",
            "hint": None,
            "detail": None,
        }
    except Exception as exc:  # pragma: no cover - defensive
        _log.exception("database_writable check failed")
        return {
            "id": "database_writable",
            "name": "SQLite database",
            "ok": False,
            "severity": "error",
            "message": f"Could not write to the database: {exc!r}",
            "hint": (
                "Check that /config is writable from the container. If you"
                " just restored from a snapshot, restart the add-on once."
            ),
            "detail": None,
        }


def _check_ha_bambulab_installed(states: list[dict[str, Any]]) -> dict[str, Any]:
    bambulab_entities = [s for s in states if _is_bambulab_entity(s)]
    ok = len(bambulab_entities) > 0
    return {
        "id": "ha_bambulab_installed",
        "name": "ha-bambulab integration",
        "ok": ok,
        "severity": "ok" if ok else "error",
        "message": (
            f"Found {len(bambulab_entities)} entities that look like"
            " they came from ha-bambulab."
            if ok
            else "No Bambu-looking entities found in Home Assistant."
        ),
        "hint": (
            None
            if ok
            else "Install the 'Bambu Lab' integration via HACS"
            " (greghesp/ha-bambulab) and add at least one printer."
        ),
        "detail": None,
    }


def _check_bambu_printers_found(states: list[dict[str, Any]]) -> dict[str, Any]:
    printers = _printers_from_entities(states)
    ok = len(printers) >= 1
    return {
        "id": "bambu_printers_found",
        "name": "Bambu printers detected",
        "ok": ok,
        "severity": "ok" if ok else "warn",
        "message": (
            f"Detected {len(printers)} printer(s): {', '.join(sorted(printers))}."
            if ok
            else "No Bambu printers detected in the entity registry."
        ),
        "hint": (
            None
            if ok
            else "Open Settings -> Devices -> Bambu Lab and add your"
            " printer. The add-on watches for tray entities that"
            " appear once the printer is configured."
        ),
        "detail": {"printers": sorted(printers)},
    }


def _check_ams_entities_found(states: list[dict[str, Any]]) -> dict[str, Any]:
    tray_count = _count_tray_entities(states)
    ok = tray_count >= 1
    return {
        "id": "ams_entities_found",
        "name": "AMS / external spool trays",
        "ok": ok,
        "severity": "ok" if ok else "warn",
        "message": (
            f"Detected {tray_count} tray entit{'y' if tray_count == 1 else 'ies'}."
            if ok
            else "No AMS trays or external spool entities found."
        ),
        "hint": (
            None
            if ok
            else "If you have an AMS unit, make sure it's powered on and"
            " connected to the printer. Without trays the AMS Status"
            " panel will be empty, but the rest of the add-on still"
            " works for tracking stock."
        ),
        "detail": {"tray_count": tray_count},
    }


async def _check_bambu_set_filament_service() -> dict[str, Any]:
    """Check whether ``bambu_lab.set_filament`` is registered in HA.

    ha-bambulab only registers this service when the printer is in LAN
    mode. If it's missing, the add-on still works for everything except
    the optional "Also update the printer's AMS display" push.
    """
    try:
        services = await ha_client.list_services()
    except ha_client.HAClientError as exc:
        return {
            "id": "bambu_set_filament_service_available",
            "name": "Printer-push service (bambu_lab.set_filament)",
            "ok": False,
            "severity": "warn",
            "message": f"Could not enumerate HA services: {exc}",
            "hint": (
                "The local stock tracking still works -- only the"
                " optional 'Also update the printer's AMS display'"
                " checkbox is affected."
            ),
            "detail": None,
        }

    bambu = next(
        (entry for entry in services if entry.get("domain") == "bambu_lab"),
        None,
    )
    has_set_filament = bool(
        bambu and "set_filament" in (bambu.get("services") or {})
    )
    if has_set_filament:
        return {
            "id": "bambu_set_filament_service_available",
            "name": "Printer-push service (bambu_lab.set_filament)",
            "ok": True,
            "severity": "ok",
            "message": "bambu_lab.set_filament is available.",
            "hint": None,
            "detail": None,
        }
    return {
        "id": "bambu_set_filament_service_available",
        "name": "Printer-push service (bambu_lab.set_filament)",
        "ok": False,
        "severity": "warn",
        "message": (
            "bambu_lab.set_filament is not registered in Home Assistant."
        ),
        "hint": (
            "Usually means the printer is in Cloud-only mode."
            " Switch it to LAN mode in the ha-bambulab integration if"
            " you want assignments to push tray metadata to the"
            " printer. The local stock and AMS view still work either way."
        ),
        "detail": None,
    }


# ── orchestrator ──────────────────────────────────────────────────────────


async def build_health_report() -> dict[str, Any]:
    """Run every check and return the aggregated report. Never raises."""
    # Step 1 -- cheap, always-runnable checks.
    checks: list[dict[str, Any]] = [
        _check_supervisor_token(),
        _check_database_writable(),
    ]

    # Step 2 -- the HA Core ping. If this fails, the downstream checks
    # that need /api/states will fail with the same error class, but
    # we still run them so the user sees each line item.
    checks.append(await _check_ha_core_reachable())

    # Step 3 -- Bambu-specific checks. The whole block is gated on the
    # `disable_bambu_integration` add-on option so users who don't own
    # a Bambu printer don't see a red setup checklist forever. When
    # gated off we still emit one informational entry so the user can
    # tell from the checklist that the integration is intentionally
    # disabled (not silently broken).
    if get_options().disable_bambu_integration:
        checks.append(
            {
                "id": "bambu_integration",
                "name": "Bambu Lab integration",
                # ok=True so the overall report stays green; the user
                # opted out, this isn't a failure state.
                "ok": True,
                "severity": "ok",
                "message": (
                    "Disabled in add-on options. AMS panel hidden and"
                    " Bambu-specific checks skipped."
                ),
                "hint": None,
                "detail": None,
            }
        )
    else:
        # Step 3a -- shared /api/states fetch feeds the next 3 checks.
        try:
            states = await ha_client.get_all_states()
            states_error: str | None = None
        except ha_client.HAClientError as exc:
            _log.warning("health: /api/states fetch failed: %s", exc)
            states = []
            states_error = str(exc)

        if states_error:
            unavailable = lambda check_id, name: {  # noqa: E731
                "id": check_id,
                "name": name,
                "ok": False,
                "severity": "warn",
                "message": f"Couldn't query HA states: {states_error}",
                "hint": "Fix the earlier 'Home Assistant Core API' check first.",
                "detail": None,
            }
            checks.append(unavailable("ha_bambulab_installed", "ha-bambulab integration"))
            checks.append(unavailable("bambu_printers_found", "Bambu printers detected"))
            checks.append(unavailable("ams_entities_found", "AMS / external spool trays"))
        else:
            checks.append(_check_ha_bambulab_installed(states))
            checks.append(_check_bambu_printers_found(states))
            checks.append(_check_ams_entities_found(states))

        # Step 3b -- service enumeration (independent of /api/states).
        checks.append(await _check_bambu_set_filament_service())

    all_ok = all(c["ok"] for c in checks)
    has_error = any(c["severity"] == "error" for c in checks)
    has_warn = any(c["severity"] == "warn" for c in checks if not c["ok"])

    if all_ok:
        severity = "ok"
        summary = "All systems go."
    elif has_error:
        severity = "error"
        bad = sum(1 for c in checks if not c["ok"])
        summary = (
            f"{bad} issue{'s' if bad != 1 else ''} need attention before the"
            " add-on can do its job."
        )
    elif has_warn:
        severity = "warn"
        bad = sum(1 for c in checks if not c["ok"])
        summary = (
            f"{bad} optional feature{'s' if bad != 1 else ''}"
            f" {'are' if bad != 1 else 'is'} unavailable. Core stock"
            " tracking still works."
        )
    else:
        # Shouldn't reach here -- not-ok with no severity flagged is a bug.
        severity = "ok"
        summary = "All systems go."

    return {
        "ok": all_ok,
        "severity": severity,
        "summary": summary,
        "checks": checks,
    }
