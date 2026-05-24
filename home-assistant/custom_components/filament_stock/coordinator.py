"""DataUpdateCoordinator: single source of truth for filament data in HA.

Polls the add-on every poll_interval seconds and caches the result for all
sensors and services to read.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FilamentStockApi, FilamentStockApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class FilamentStockData:
    """Snapshot fetched from the add-on each poll cycle."""

    filaments: list[dict[str, Any]] = field(default_factory=list)
    alerts: list[dict[str, Any]] = field(default_factory=list)

    def filament_by_id(self, filament_id: int) -> dict[str, Any] | None:
        for f in self.filaments:
            if f.get("id") == filament_id:
                return f
        return None

    def color_id(self, filament_id: int, color_name: str) -> int | None:
        """Resolve (filament_id, color_name) -> color_stocks.id via the cached snapshot."""
        f = self.filament_by_id(filament_id)
        if not f:
            return None
        target = color_name.strip().casefold()
        for c in f.get("colors", []):
            if (c.get("color_name") or "").strip().casefold() == target:
                return c.get("id")
        return None


class FilamentStockCoordinator(DataUpdateCoordinator[FilamentStockData]):
    """Coordinator owning a single FilamentStockData snapshot."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: FilamentStockApi,
        *,
        poll_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self._api = api

    @property
    def api(self) -> FilamentStockApi:
        return self._api

    async def _async_update_data(self) -> FilamentStockData:
        try:
            filaments = await self._api.list_filaments()
            alerts = await self._api.list_alerts()
        except FilamentStockApiError as err:
            raise UpdateFailed(str(err)) from err
        return FilamentStockData(filaments=filaments, alerts=alerts)
