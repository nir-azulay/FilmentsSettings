"""Sensor entities for the Filament Stock integration.

One `sensor.filament_<brand>_<material>` per filament. State = total available
spools (sum of quantity - quantity_used over in_stock colors). All per-color
detail is exposed as attributes so Lovelace cards and templates can drill in.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, STATUS_IN_STOCK
from .coordinator import FilamentStockCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: FilamentStockCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Per-filament sensors are added dynamically. On first refresh we create one
    # per filament that already exists; thereafter we listen for new filaments
    # appearing in the snapshot and add entities for them too.
    known: set[int] = set()

    @callback
    def _sync_entities() -> None:
        new_entities: list[FilamentStockSensor] = []
        for f in coordinator.data.filaments if coordinator.data else []:
            fid = f.get("id")
            if fid is None or fid in known:
                continue
            known.add(fid)
            new_entities.append(FilamentStockSensor(coordinator, fid))
        # Per-instance summary sensor for low-stock count.
        if "_count_added" not in known:
            new_entities.append(FilamentLowStockCountSensor(coordinator, entry.entry_id))
            # sentinel marker; not a real fid but keeps it from re-adding
            known.add(-1)
        if new_entities:
            async_add_entities(new_entities)

    _sync_entities()
    entry.async_on_unload(coordinator.async_add_listener(_sync_entities))


class FilamentStockSensor(CoordinatorEntity[FilamentStockCoordinator], SensorEntity):
    """Total available spools for one filament, with per-color attributes."""

    _attr_has_entity_name = True
    _attr_translation_key = "filament_total"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "spools"
    _attr_icon = "mdi:printer-3d-nozzle"
    _attr_device_class = None

    def __init__(self, coordinator: FilamentStockCoordinator, filament_id: int) -> None:
        super().__init__(coordinator)
        self._filament_id = filament_id
        self._attr_unique_id = f"filament_stock_filament_{filament_id}"

    @property
    def _filament(self) -> dict[str, Any] | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.filament_by_id(self._filament_id)

    @property
    def available(self) -> bool:
        return super().available and self._filament is not None

    @property
    def name(self) -> str | None:
        f = self._filament
        if not f:
            return None
        # has_entity_name + this name -> "<device_name> <name>", but the device
        # name already includes brand+material so we return None to use device
        # name verbatim and avoid duplication.
        return None

    @property
    def native_value(self) -> int | None:
        f = self._filament
        if not f:
            return None
        total = 0
        for c in f.get("colors", []):
            if (c.get("status") or STATUS_IN_STOCK) != STATUS_IN_STOCK:
                continue
            total += max(0, (c.get("quantity") or 0) - (c.get("quantity_used") or 0))
        return total

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        f = self._filament
        if not f:
            return {}
        colors = []
        for c in f.get("colors", []):
            qty = c.get("quantity") or 0
            used = c.get("quantity_used") or 0
            colors.append(
                {
                    "name": c.get("color_name"),
                    "hex": c.get("color_hex"),
                    "status": c.get("status") or STATUS_IN_STOCK,
                    "quantity": qty,
                    "used": used,
                    "available": max(0, qty - used),
                    "order_id": c.get("order_id"),
                }
            )
        return {
            "filament_id": f.get("id"),
            "brand": f.get("brand"),
            "material": f.get("material"),
            "filament_type": f.get("filament_type"),
            "packaging_type": f.get("packaging_type") or "spool",
            "density": f.get("density"),
            "bed_temp": f.get("bed_temp"),
            "nozzle_temp_min": f.get("nozzle_temp_min"),
            "nozzle_temp_max": f.get("nozzle_temp_max"),
            "amazon_url": f.get("amazon_url") or None,
            "low_stock_threshold": f.get("low_stock_threshold"),
            "colors": colors,
            "colors_count": len(colors),
        }

    @property
    def device_info(self) -> DeviceInfo:
        f = self._filament or {}
        brand = f.get("brand") or "Filament"
        material = f.get("material") or f"#{self._filament_id}"
        return DeviceInfo(
            identifiers={(DOMAIN, f"filament_{self._filament_id}")},
            name=f"{brand} {material}",
            manufacturer=MANUFACTURER,
            model=f.get("filament_type") or None,
            configuration_url=f.get("amazon_url") or None,
        )


class FilamentLowStockCountSensor(
    CoordinatorEntity[FilamentStockCoordinator], SensorEntity
):
    """Count of currently-firing low-stock alerts."""

    _attr_has_entity_name = True
    _attr_translation_key = "low_stock_count"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "alerts"
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator: FilamentStockCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"filament_stock_low_stock_count_{entry_id}"

    @property
    def name(self) -> str:
        return "Filament low stock count"

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return len(self.coordinator.data.alerts or [])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {}
        return {"alerts": self.coordinator.data.alerts or []}
