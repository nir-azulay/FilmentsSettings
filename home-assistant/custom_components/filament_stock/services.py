"""HA service handlers exposed by the Filament Stock integration.

All services accept (filament_entity_id, color_name) and translate the pair
into a backend color_id via the coordinator snapshot before calling the
add-on's REST API.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    STATUS_IN_STOCK,
    STATUS_ORDERED,
    STATUS_OUT_OF_STOCK,
)
from .coordinator import FilamentStockCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_USE_SPOOL = "use_spool"
SERVICE_MARK_ARRIVED = "mark_arrived"
SERVICE_ADD_PURCHASE = "add_purchase"
SERVICE_SET_STATUS = "set_status"

ATTR_FILAMENT_ENTITY = "filament_entity"
ATTR_COLOR_NAME = "color_name"
ATTR_AMOUNT = "amount"
ATTR_QUANTITY = "quantity"
ATTR_ORDER_ID = "order_id"
ATTR_STATUS = "status"

_STATUS_VALUES = [STATUS_IN_STOCK, STATUS_ORDERED, STATUS_OUT_OF_STOCK]

_SCHEMA_TARGET = {
    vol.Required(ATTR_FILAMENT_ENTITY): cv.entity_id,
    vol.Required(ATTR_COLOR_NAME): cv.string,
}

USE_SPOOL_SCHEMA = vol.Schema(
    {**_SCHEMA_TARGET, vol.Optional(ATTR_AMOUNT, default=1): vol.All(int, vol.Range(min=1))}
)
MARK_ARRIVED_SCHEMA = vol.Schema(
    {
        **_SCHEMA_TARGET,
        vol.Optional(ATTR_QUANTITY): vol.All(int, vol.Range(min=0)),
    }
)
ADD_PURCHASE_SCHEMA = vol.Schema(
    {
        **_SCHEMA_TARGET,
        vol.Required(ATTR_AMOUNT): vol.All(int, vol.Range(min=1)),
        vol.Optional(ATTR_ORDER_ID): cv.string,
    }
)
SET_STATUS_SCHEMA = vol.Schema(
    {**_SCHEMA_TARGET, vol.Required(ATTR_STATUS): vol.In(_STATUS_VALUES)}
)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register all Filament Stock services. Idempotent across multiple entries."""
    if hass.services.has_service(DOMAIN, SERVICE_USE_SPOOL):
        return  # already registered for an earlier entry

    hass.services.async_register(
        DOMAIN, SERVICE_USE_SPOOL, _handle_use_spool(hass), schema=USE_SPOOL_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_MARK_ARRIVED, _handle_mark_arrived(hass), schema=MARK_ARRIVED_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_PURCHASE, _handle_add_purchase(hass), schema=ADD_PURCHASE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_STATUS, _handle_set_status(hass), schema=SET_STATUS_SCHEMA
    )


async def async_unregister_services(hass: HomeAssistant) -> None:
    for svc in (SERVICE_USE_SPOOL, SERVICE_MARK_ARRIVED, SERVICE_ADD_PURCHASE, SERVICE_SET_STATUS):
        if hass.services.has_service(DOMAIN, svc):
            hass.services.async_remove(DOMAIN, svc)


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def _iter_coordinators(hass: HomeAssistant) -> list[FilamentStockCoordinator]:
    return list((hass.data.get(DOMAIN) or {}).values())


def _resolve_filament_id(hass: HomeAssistant, entity_id: str) -> tuple[FilamentStockCoordinator, int] | None:
    """Find which coordinator owns `entity_id` and the underlying filament_id.

    The integration sets unique_id="filament_stock_filament_<id>" so we can
    extract the id from the entity registry without an extra round trip.
    """
    from homeassistant.helpers import entity_registry as er

    ent_reg = er.async_get(hass)
    entry = ent_reg.async_get(entity_id)
    if not entry or entry.platform != DOMAIN:
        return None
    unique_id = entry.unique_id or ""
    prefix = "filament_stock_filament_"
    if not unique_id.startswith(prefix):
        return None
    try:
        filament_id = int(unique_id[len(prefix):])
    except ValueError:
        return None
    # entry.config_entry_id is the ConfigEntry.entry_id that owns this entity.
    coordinator = (hass.data.get(DOMAIN) or {}).get(entry.config_entry_id)
    if coordinator is None:
        return None
    return coordinator, filament_id


def _resolve_color_id(
    coordinator: FilamentStockCoordinator,
    filament_id: int,
    color_name: str,
) -> int | None:
    if not coordinator.data:
        return None
    return coordinator.data.color_id(filament_id, color_name)


def _current_color(
    coordinator: FilamentStockCoordinator,
    filament_id: int,
    color_id: int,
) -> dict[str, Any] | None:
    f = coordinator.data.filament_by_id(filament_id) if coordinator.data else None
    if not f:
        return None
    for c in f.get("colors", []):
        if c.get("id") == color_id:
            return c
    return None


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _handle_use_spool(hass: HomeAssistant):
    async def _handle(call: ServiceCall) -> None:
        entity_id = call.data[ATTR_FILAMENT_ENTITY]
        color_name = call.data[ATTR_COLOR_NAME]
        amount = int(call.data[ATTR_AMOUNT])

        resolved = _resolve_filament_id(hass, entity_id)
        if not resolved:
            _LOGGER.warning("filament_stock.use_spool: %s is not a Filament Stock entity", entity_id)
            return
        coordinator, filament_id = resolved
        color_id = _resolve_color_id(coordinator, filament_id, color_name)
        if color_id is None:
            _LOGGER.warning(
                "filament_stock.use_spool: color %r not found on filament_id=%s",
                color_name,
                filament_id,
            )
            return
        current = _current_color(coordinator, filament_id, color_id) or {}
        new_used = (current.get("quantity_used") or 0) + amount
        new_used = min(new_used, current.get("quantity") or new_used)
        await coordinator.api.update_color(color_id, {"quantity_used": new_used})
        await coordinator.async_request_refresh()

    return _handle


def _handle_mark_arrived(hass: HomeAssistant):
    async def _handle(call: ServiceCall) -> None:
        entity_id = call.data[ATTR_FILAMENT_ENTITY]
        color_name = call.data[ATTR_COLOR_NAME]
        quantity = call.data.get(ATTR_QUANTITY)

        resolved = _resolve_filament_id(hass, entity_id)
        if not resolved:
            return
        coordinator, filament_id = resolved
        color_id = _resolve_color_id(coordinator, filament_id, color_name)
        if color_id is None:
            return
        payload: dict[str, Any] = {"status": STATUS_IN_STOCK}
        if quantity is not None:
            payload["quantity"] = int(quantity)
        await coordinator.api.update_color(color_id, payload)
        await coordinator.async_request_refresh()

    return _handle


def _handle_add_purchase(hass: HomeAssistant):
    async def _handle(call: ServiceCall) -> None:
        entity_id = call.data[ATTR_FILAMENT_ENTITY]
        color_name = call.data[ATTR_COLOR_NAME]
        amount = int(call.data[ATTR_AMOUNT])
        order_id = call.data.get(ATTR_ORDER_ID)

        resolved = _resolve_filament_id(hass, entity_id)
        if not resolved:
            return
        coordinator, filament_id = resolved
        # The backend POST /api/filaments/{id}/colors merges by name when the
        # color already exists (see app/routers/filaments.py find_color_by_name),
        # so we can always POST with the requested name regardless of whether
        # the color is new.
        payload: dict[str, Any] = {
            "color_name": color_name,
            "quantity": amount,
            "status": STATUS_IN_STOCK,
        }
        if order_id:
            payload["order_id"] = order_id
        await coordinator.api.add_color(filament_id, payload)
        await coordinator.async_request_refresh()

    return _handle


def _handle_set_status(hass: HomeAssistant):
    async def _handle(call: ServiceCall) -> None:
        entity_id = call.data[ATTR_FILAMENT_ENTITY]
        color_name = call.data[ATTR_COLOR_NAME]
        status = call.data[ATTR_STATUS]

        resolved = _resolve_filament_id(hass, entity_id)
        if not resolved:
            return
        coordinator, filament_id = resolved
        color_id = _resolve_color_id(coordinator, filament_id, color_name)
        if color_id is None:
            return
        await coordinator.api.update_color(color_id, {"status": status})
        await coordinator.async_request_refresh()

    return _handle
