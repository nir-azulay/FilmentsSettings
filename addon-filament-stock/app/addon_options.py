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
    )
    _log.info("Add-on options resolved: %s", resolved)
    _cached = resolved
    return resolved


def reset_cache_for_tests() -> None:
    """Drop the cached value so tests can re-load with a fresh options.json."""
    global _cached
    _cached = None


def options_as_dict() -> dict[str, Any]:
    """Public dict shape for the /api/config endpoint."""
    opts = get_options()
    return {
        "ask_if_replaced_spool_empty": opts.ask_if_replaced_spool_empty,
    }
