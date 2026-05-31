"""Runtime swap of the add-on's icon between 'normal' and 'update available'.

Background

The HA Apps grid renders the add-on tile from a single ``icon.png`` baked into
the addon directory. There is no first-class API to render a state-dependent
overlay, and the built-in ``mdiArrowUpBoldCircle`` corner overlay is either
suppressed or too subtle to spot, depending on the HA frontend version.

What this module does

* Periodically asks Supervisor (``GET /addons/self/info``) whether a newer
  version of this add-on is available.
* When the answer flips, swaps the live ``icon.png`` on disk with a
  pre-baked variant -- ``icon_update.png`` when an update is available, the
  plain ``icon.png.original`` (a copy of the shipped clean icon) otherwise.
* Hits ``POST /addons/reload`` so Supervisor re-evaluates
  ``_path_icon_exists`` and serves the new bytes on the next frontend fetch.

Prerequisites in config.yaml
    hassio_api: true
    hassio_role: manager
    map:
      - addons:rw

Failure mode
    Every operation is wrapped in try/except. The swapper is a UX nicety,
    not a critical path -- it must never crash the add-on. All failures are
    logged at warning level and the swapper keeps retrying on its interval.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

import httpx

_log = logging.getLogger("filament_stock.icon_swapper")

SUPERVISOR_URL = "http://supervisor"
SUPERVISOR_TOKEN_ENV = "SUPERVISOR_TOKEN"

# How often to check for an update available. 30 minutes is well under the
# Supervisor's own 3-hour reload-addons cadence (so we'll usually flip before
# the user sees Supervisor's own indicator anywhere else) without spamming
# the Supervisor API.
POLL_INTERVAL_SECONDS = 30 * 60

# Local addons are bind-mounted into the container at /addons/<slug-folder>.
# The slug-folder is the directory name on the host, not the addon slug from
# config.yaml -- the user can rename the folder. We accept either, with
# environment overrides for development / forks.
ADDONS_MOUNT = Path(os.environ.get("FS_ADDONS_MOUNT", "/addons"))
ADDON_FOLDER_ENV = "FS_ADDON_FOLDER"
DEFAULT_ADDON_FOLDER_CANDIDATES = ("addon-filament-stock", "filament_stock")

# These three live next to icon.png inside the addon folder. The .original is
# created on first run by copying the shipped icon.png so we always have a
# clean source to swap back to without having to rebuild the image.
ICON_NAME = "icon.png"
ICON_UPDATE_NAME = "icon_update.png"
ICON_ORIGINAL_NAME = "icon.png.original"


def _supervisor_token() -> Optional[str]:
    return os.environ.get(SUPERVISOR_TOKEN_ENV) or None


def _find_addon_folder() -> Optional[Path]:
    """Return the writable host-mounted addon directory or None."""
    if not ADDONS_MOUNT.exists():
        return None
    explicit = os.environ.get(ADDON_FOLDER_ENV)
    if explicit:
        candidate = ADDONS_MOUNT / explicit
        return candidate if candidate.is_dir() else None
    # Try the well-known folder names first, then fall back to "any folder
    # that contains both icon.png and icon_update.png" so a user who renamed
    # the directory still gets the swap behaviour.
    for name in DEFAULT_ADDON_FOLDER_CANDIDATES:
        candidate = ADDONS_MOUNT / name
        if candidate.is_dir() and (candidate / ICON_UPDATE_NAME).exists():
            return candidate
    try:
        for child in ADDONS_MOUNT.iterdir():
            if not child.is_dir():
                continue
            if (child / ICON_UPDATE_NAME).exists() and (child / ICON_NAME).exists():
                return child
    except OSError:
        return None
    return None


def _ensure_original(folder: Path) -> bool:
    """Make sure icon.png.original exists; return True on success."""
    original = folder / ICON_ORIGINAL_NAME
    if original.exists():
        return True
    src = folder / ICON_NAME
    if not src.exists():
        _log.warning("icon swap: no %s in %s -- cannot create backup", ICON_NAME, folder)
        return False
    try:
        shutil.copyfile(src, original)
    except OSError as exc:
        _log.warning("icon swap: failed to write %s: %r", original, exc)
        return False
    _log.info("icon swap: created backup at %s", original)
    return True


async def _fetch_update_available() -> Optional[bool]:
    """Ask Supervisor whether this add-on has a newer version available.

    Returns None on any error so the caller can leave the icon untouched
    instead of guessing -- flipping the icon based on a transient API hiccup
    would be much worse than just keeping the current state.
    """
    token = _supervisor_token()
    if not token:
        _log.debug("icon swap: no SUPERVISOR_TOKEN, skipping update check")
        return None
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{SUPERVISOR_URL}/addons/self/info", headers=headers
            )
    except httpx.HTTPError as exc:
        _log.debug("icon swap: supervisor unreachable: %r", exc)
        return None
    if resp.status_code != 200:
        _log.debug(
            "icon swap: /addons/self/info returned HTTP %s", resp.status_code
        )
        return None
    try:
        payload = resp.json()
    except ValueError:
        return None
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return None
    # Supervisor returns the field as `update_available` directly. Some older
    # builds use `need_update`; we'll trust either if present.
    if "update_available" in data:
        return bool(data["update_available"])
    if "need_update" in data:
        return bool(data["need_update"])
    return None


async def _reload_supervisor() -> None:
    """Best-effort: ask Supervisor to refresh the addon path cache.

    Required so ``_path_icon_exists`` is re-evaluated and the new bytes get
    served to the frontend on the next request.
    """
    token = _supervisor_token()
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{SUPERVISOR_URL}/store/reload", headers=headers
            )
    except httpx.HTTPError as exc:
        _log.debug("icon swap: store reload failed: %r", exc)
        return
    if resp.status_code >= 400:
        _log.debug(
            "icon swap: /store/reload returned HTTP %s", resp.status_code
        )


def _swap_icon(folder: Path, *, update_available: bool) -> bool:
    """Atomically replace icon.png with the desired variant.

    Returns True if the file was actually changed, False if it was already
    the correct variant (in which case we skip the Supervisor reload to
    avoid pointless API noise).
    """
    target_name = ICON_UPDATE_NAME if update_available else ICON_ORIGINAL_NAME
    src = folder / target_name
    dst = folder / ICON_NAME
    if not src.exists():
        _log.warning("icon swap: source %s missing, cannot swap", src)
        return False
    # Cheap "is the live icon already the variant we want?" check via byte
    # length + first-1KB compare. Avoids writing -> reload churn when nothing
    # actually changed (common case: every poll once steady-state is reached).
    try:
        if dst.exists() and dst.stat().st_size == src.stat().st_size:
            with src.open("rb") as f_src, dst.open("rb") as f_dst:
                if f_src.read(1024) == f_dst.read(1024):
                    return False
    except OSError:
        # If we can't stat/read, fall through to the copy attempt and let
        # that surface the real error.
        pass
    tmp = dst.with_suffix(".tmp")
    try:
        shutil.copyfile(src, tmp)
        os.replace(tmp, dst)
        # Touch the parent directory so Supervisor's mtime-based
        # change-detection on the local repo picks this up reliably.
        os.utime(folder, None)
    except OSError as exc:
        _log.warning("icon swap: write failed: %r", exc)
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        return False
    _log.info(
        "icon swap: copied %s -> %s (update_available=%s)",
        target_name, ICON_NAME, update_available,
    )
    return True


async def _swap_cycle(folder: Path) -> None:
    update_available = await _fetch_update_available()
    if update_available is None:
        return
    changed = _swap_icon(folder, update_available=update_available)
    if changed:
        await _reload_supervisor()


async def run_forever() -> None:
    """Background task entry point.

    Resolves the writable addon folder once, then loops forever sleeping
    POLL_INTERVAL_SECONDS between checks. If the folder cannot be found
    (e.g. ``addons:rw`` map is missing), logs once and exits -- no point
    in spinning a sleeper that can never act.
    """
    folder = _find_addon_folder()
    if folder is None:
        _log.info(
            "icon swap: addon folder under %s not writable -- swapping disabled."
            " Add 'map: [addons:rw]' to config.yaml to enable update indicator.",
            ADDONS_MOUNT,
        )
        return
    if not _ensure_original(folder):
        return
    _log.info(
        "icon swap: active, polling Supervisor every %ds (folder=%s)",
        POLL_INTERVAL_SECONDS, folder,
    )
    # Run one cycle immediately so the first install reflects current state
    # without waiting 30 minutes.
    while True:
        try:
            await _swap_cycle(folder)
        except Exception as exc:  # pragma: no cover -- belt-and-braces
            _log.warning("icon swap: cycle errored: %r", exc)
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
