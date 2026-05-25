"""Thin wrapper around the Home Assistant Core REST API exposed by Supervisor.

The Supervisor injects the env var ``SUPERVISOR_TOKEN`` into every add-on
container that declares ``homeassistant_api: true`` in ``config.yaml`` and
makes the HA Core API reachable at ``http://supervisor/core/api/...``.

We only need a tiny subset:

* ``GET /states`` -- the full state machine snapshot, which already includes
  every entity's last attributes. The Bambu Lab HACS integration's per-tray
  sensors live in this list, so one call is enough to render the AMS view.
* ``POST /template`` -- render a Jinja2 template. We use this to pull the
  device-registry info (manufacturer / model / friendly name) for each AMS
  entity, which the plain REST ``/api/states`` does not expose. ``POST``
  on this endpoint only RENDERS templates -- it does not call services or
  modify anything in HA.

From add-on 0.6.0 we also expose ``call_service()`` -- a thin wrapper around
``POST /api/services/<domain>/<service>``. The only consumer is the
"assign filament from stock to AMS tray" workflow, which optionally pushes
the new tray metadata to the printer via ``bambu_lab.set_filament``. The
function is intentionally generic so it can be reused for any future
opt-in printer-push features, but callers should treat it as the
"mutates HA state" path and guard it with explicit user consent.
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


async def render_template(template: str) -> str:
    """Render a Jinja2 template via HA Core ``POST /api/template``.

    Returns the rendered string. We use this purely to read device-registry
    info (which the REST ``/api/states`` endpoint doesn't include) by
    iterating ``states.sensor`` and calling ``device_attr(state.entity_id,
    'model')`` etc. for the entities we care about.

    POST /template only RENDERS the template; HA does not execute any service
    calls or otherwise mutate state. We deliberately don't expose a
    ``call_service`` helper -- the add-on stays read-only.
    """
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{SUPERVISOR_BASE}/template",
                headers=headers,
                json={"template": template},
            )
    except httpx.HTTPError as exc:
        raise HAClientError(f"cannot reach Supervisor: {exc!r}") from exc

    if resp.status_code == 401:
        raise HAClientError(
            "Supervisor rejected SUPERVISOR_TOKEN on /template (HTTP 401)."
        )
    if resp.status_code >= 400:
        body = (resp.text or "")[:200]
        raise HAClientError(
            f"HA Core /template returned HTTP {resp.status_code}: {body}"
        )
    # /template returns the rendered text as the raw response body, not JSON.
    return resp.text


async def call_service(
    domain: str,
    service: str,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """Call ``POST /api/services/<domain>/<service>`` on HA Core via Supervisor.

    Returns the (possibly empty) list of states HA reports as changed by the
    service call. Most write services -- including ``bambu_lab.set_filament``
    -- return ``[]`` synchronously and dispatch the actual work in the
    background, so the empty list is normal.

    Raises ``HAClientError`` on any transport / auth / 4xx / 5xx failure so the
    router layer can surface a clean error to the UI.

    This is the only function in this module that *mutates* HA state. Calls
    should only be reachable from code paths the user has explicitly opted
    into (e.g. an "also push to printer" checkbox in the assign dialog).
    """
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{SUPERVISOR_BASE}/services/{domain}/{service}",
                headers=headers,
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise HAClientError(f"cannot reach Supervisor: {exc!r}") from exc

    if resp.status_code == 401:
        raise HAClientError(
            "Supervisor rejected SUPERVISOR_TOKEN on /services (HTTP 401)."
        )
    if resp.status_code == 404:
        raise HAClientError(
            f"HA service '{domain}.{service}' not found (HTTP 404)."
            " Is the ha-bambulab integration installed and the printer added?"
        )
    if resp.status_code >= 400:
        body = (resp.text or "")[:300]
        raise HAClientError(
            f"HA service '{domain}.{service}' returned HTTP {resp.status_code}:"
            f" {body}"
        )

    try:
        data = resp.json()
    except ValueError:
        # Some HA versions return an empty body on success; treat as no changes.
        return []
    if not isinstance(data, list):
        # /services always responds with a list; anything else means the API
        # contract changed and we want to know about it.
        raise HAClientError(
            f"HA /services returned unexpected type {type(data).__name__}"
        )
    return data
