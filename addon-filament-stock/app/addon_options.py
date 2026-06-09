"""Reader for Home Assistant add-on user options.

When the user clicks **Save** in the add-on's Configuration tab, Supervisor
writes the resolved option values to ``/data/options.json`` inside the
container. The file is regenerated on every add-on restart, so we read it
once at startup and treat the in-memory dict as the source of truth for
the lifetime of the process.

When the add-on is run outside Supervisor (e.g. local dev, smoke tests),
``/data/options.json`` doesn't exist and we fall back to the schema's
defaults. The defaults declared here MUST stay in sync with the
``options:`` block in ``config.yaml``.

To add a new option:

  1. Add an entry to ``options:`` and ``schema:`` in ``config.yaml``.
  2. Add the same default to ``DEFAULTS`` below.
  3. Read it via ``get_options().some_field`` from any backend code.
  4. (Frontend) Expose it through the ``/api/config`` endpoint if the UI
     needs to honour it.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger("filament_stock.options")

# Supervisor's options-file path. Override via env for local dev.
OPTIONS_PATH = os.environ.get("FILAMENT_STOCK_OPTIONS_PATH", "/data/options.json")


@dataclass(frozen=True)
class AddonOptions:
    """Resolved add-on configuration values.

    Field defaults MUST match the ``options:`` block in ``config.yaml`` so
    that what a user sees in the HA Configuration tab matches what the
    backend uses when no overrides are present.
    """

    # When False, the Assign-from-stock dialog hides the "Is the replaced
    # spool empty?" prompt and always returns replaced spools to stock.
    ask_if_replaced_spool_empty: bool = False
    # When True, the "Also update the printer's AMS display" checkbox in
    # the Assign-from-stock dialog is pre-ticked when the dialog opens.
    default_push_to_printer: bool = False
    # Default low-stock warning threshold for newly created filaments
    # (existing rows keep their own per-filament threshold). Clamped to
    # 1..100 by the schema; we clamp again here defensively.
    default_low_stock_threshold: int = 1
    # When True (default), seed_filaments() populates the DB on first run
    # with a curated list of common filaments. When False, the user starts
    # from an empty stock.
    seed_demo_filaments_on_first_run: bool = True
    # AMS Status panel polling interval in seconds. Clamped 5..300.
    ams_poll_interval_seconds: int = 15
    # Master opt-out for Bambu Lab integration. When True the AMS panel
    # is hidden in the frontend and the doctor's Bambu-related checks
    # are skipped (replaced with a single info-level "disabled" line).
    # Default False -> integration ON, same behaviour as pre-0.12.0.
    disable_bambu_integration: bool = False
    # External HA URL for QR code links on spool labels (0.15.0).
    ha_external_url: str = ""
    # Bluetooth MAC address of the Niimbot B21 Pro (0.15.0).
    niimbot_address: str = ""


DEFAULTS = AddonOptions()


def _coerce_bool(value: Any, default: bool) -> bool:
    """Be liberal in what we accept -- HA validates the schema, but a
    hand-edited options.json could still slip through with a string."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "1", "yes", "on"):
            return True
        if v in ("false", "0", "no", "off"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _coerce_int(value: Any, default: int, *, lo: int, hi: int) -> int:
    """Parse + clamp an int. HA's schema validates the range, but we
    clamp again defensively in case options.json was edited by hand."""
    try:
        if isinstance(value, bool):
            # bool is a subclass of int; reject explicitly so True doesn't
            # become 1 silently.
            return default
        if isinstance(value, (int, float)):
            n = int(value)
        elif isinstance(value, str) and value.strip():
            n = int(float(value.strip()))
        else:
            return default
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


def _load_from_disk() -> dict[str, Any]:
    """Return the raw dict from /data/options.json, or {} if missing/broken."""
    if not os.path.exists(OPTIONS_PATH):
        _log.info(
            "Add-on options file not found at %s; using compiled-in defaults."
            " This is normal when running outside HA Supervisor.",
            OPTIONS_PATH,
        )
        return {}
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            _log.warning(
                "Add-on options at %s is not a JSON object (got %s);"
                " using defaults.",
                OPTIONS_PATH,
                type(data).__name__,
            )
            return {}
        return data
    except (OSError, json.JSONDecodeError) as exc:
        _log.warning(
            "Failed to read add-on options at %s: %r. Falling back to defaults.",
            OPTIONS_PATH,
            exc,
        )
        return {}


_cached: AddonOptions | None = None


def get_options() -> AddonOptions:
    """Return the resolved add-on options, loading and caching on first call.

    Cached for the process lifetime -- Supervisor restarts the container
    when the user changes options, so the cache is always fresh.
    """
    global _cached
    if _cached is not None:
        return _cached

    raw = _load_from_disk()
    resolved = AddonOptions(
        ask_if_replaced_spool_empty=_coerce_bool(
            raw.get("ask_if_replaced_spool_empty"),
            DEFAULTS.ask_if_replaced_spool_empty,
        ),
        default_push_to_printer=_coerce_bool(
            raw.get("default_push_to_printer"),
            DEFAULTS.default_push_to_printer,
        ),
        default_low_stock_threshold=_coerce_int(
            raw.get("default_low_stock_threshold"),
            DEFAULTS.default_low_stock_threshold,
            lo=1,
            hi=100,
        ),
        seed_demo_filaments_on_first_run=_coerce_bool(
            raw.get("seed_demo_filaments_on_first_run"),
            DEFAULTS.seed_demo_filaments_on_first_run,
        ),
        ams_poll_interval_seconds=_coerce_int(
            raw.get("ams_poll_interval_seconds"),
            DEFAULTS.ams_poll_interval_seconds,
            lo=5,
            hi=300,
        ),
        disable_bambu_integration=_coerce_bool(
            raw.get("disable_bambu_integration"),
            DEFAULTS.disable_bambu_integration,
        ),
        ha_external_url=str(raw.get("ha_external_url", "") or "").strip(),
        niimbot_address=str(raw.get("niimbot_address", "") or "").strip(),
    )
    _log.info("Add-on options resolved: %s", resolved)
    _cached = resolved
    return resolved


def reset_cache_for_tests() -> None:
    """Drop the cached value so tests can re-load with a fresh options.json."""
    global _cached
    _cached = None


ADDON_VERSION = "0.18.3"


def options_as_dict() -> dict[str, Any]:
    """Public dict shape for the /api/config endpoint."""
    opts = get_options()
    return {
        "addon_version": ADDON_VERSION,
        "ask_if_replaced_spool_empty": opts.ask_if_replaced_spool_empty,
        "default_push_to_printer": opts.default_push_to_printer,
        "default_low_stock_threshold": opts.default_low_stock_threshold,
        "seed_demo_filaments_on_first_run": opts.seed_demo_filaments_on_first_run,
        "ams_poll_interval_seconds": opts.ams_poll_interval_seconds,
        "disable_bambu_integration": opts.disable_bambu_integration,
        "ha_external_url": opts.ha_external_url,
        "niimbot_address": opts.niimbot_address,
    }
