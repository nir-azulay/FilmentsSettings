"""Thin wrapper around the Home Assistant Core REST API exposed by Supervisor.

The Supervisor injects the env var ``SUPERVISOR_TOKEN`` into every add-on
container that declares ``homeassistant_api: true`` in ``config.yaml`` and
makes the HA Core API reachable at ``http://supervisor/core/api/...``.

We only need a tiny subset:

* ``GET /states`` -- the full state machine snapshot, which already includes
  every entity's last attributes. The Bambu Lab HACS integration's per-tray
  sensors live in this list, so one call is enough to render the AMS view.

The client is read-only: no POSTs, no service calls. That keeps the add-on
safe to ship with the broad ``homeassistant_api`` permission (which would
otherwise let it mutate anything in HA).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

_log = logging.getLogger("filament_stock.ha")

# Supervisor's internal hostname. Stable across HA OS / Supervised installs.
SUPERVISOR_BASE = "http://supervisor/core/api"
SUPERVISOR_TOKEN_ENV = "SUPERVISOR_TOKEN"

# Connection budget: HA Core can be slow during a config reload. 8s total is
# enough to ride through that without freezing the add-on UI for a long time
# if something is actually broken.
_TIMEOUT = httpx.Timeout(connect=3.0, read=8.0, write=3.0, pool=3.0)


class HAClientError(RuntimeError):
    """Raised when the HA Core API call cannot complete.

    Includes a hint string suitable for surfacing to the user (e.g. "the add-on
    is missing ``homeassistant_api: true``").
    """


def _token() -> str:
    tok = os.environ.get(SUPERVISOR_TOKEN_ENV)
    if not tok:
        raise HAClientError(
            "SUPERVISOR_TOKEN is not set. The add-on needs"
            " 'homeassistant_api: true' in config.yaml and a restart."
        )
    return tok


async def get_all_states() -> list[dict[str, Any]]:
    """Return the full ``/api/states`` snapshot from HA Core.

    Each element looks like::

        {
            "entity_id": "sensor.h2s_ams_1_tray_4",
            "state": "SUNLU PETG High Speed",
            "attributes": {
                "filament_id": "P759ffa0",
                "color": "#1a1a1aff",
                "remain": 73,
                "active": false,
                ...
            },
            "last_changed": "...",
            "last_updated": "...",
        }

    Raises ``HAClientError`` on any transport / auth failure so the router
    layer can convert it to a clean HTTP error for the UI.
    """
    headers = {"Authorization": f"Bearer {_token()}"}
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{SUPERVISOR_BASE}/states", headers=headers)
    except httpx.HTTPError as exc:
        raise HAClientError(f"cannot reach Supervisor: {exc!r}") from exc

    if resp.status_code == 401:
        raise HAClientError(
            "Supervisor rejected SUPERVISOR_TOKEN (HTTP 401). Restart the"
            " add-on so Supervisor re-injects a fresh token."
        )
    if resp.status_code >= 400:
        # Truncate body to keep the log line readable.
        body = (resp.text or "")[:200]
        raise HAClientError(
            f"HA Core /states returned HTTP {resp.status_code}: {body}"
        )

    payload = resp.json()
    if not isinstance(payload, list):
        raise HAClientError(
            f"HA Core /states returned unexpected type {type(payload).__name__}"
        )
    _log.debug("Fetched %d states from HA Core", len(payload))
    return payload
