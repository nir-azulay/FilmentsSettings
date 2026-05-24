"""Binary sensor: on whenever at least one filament low-stock alert is firing."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FilamentStockCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: FilamentStockCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FilamentLowStockAlertBinarySensor(coordinator, entry.entry_id)])


class FilamentLowStockAlertBinarySensor(
    CoordinatorEntity[FilamentStockCoordinator], BinarySensorEntity
):
    _attr_has_entity_name = True
    _attr_translation_key = "low_stock_alert"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:alert-circle"

    def __init__(self, coordinator: FilamentStockCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"filament_stock_low_stock_alert_{entry_id}"

    @property
    def name(self) -> str:
        return "Filament low stock alert"

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return bool(self.coordinator.data.alerts)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {}
        alerts = self.coordinator.data.alerts or []
        return {
            "count": len(alerts),
            "alerts": alerts,
        }
