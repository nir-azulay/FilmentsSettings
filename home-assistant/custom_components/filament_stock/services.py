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
ATTR_PACKAGING = "packaging"

_STATUS_VALUES = [STATUS_IN_STOCK, STATUS_ORDERED, STATUS_OUT_OF_STOCK]
_PACKAGING_SPOOL = "spool"
_PACKAGING_REFILL = "refill"
_PACKAGING_AUTO = "auto"  # decrement spool first, then refill
_PACKAGING_VALUES = [_PACKAGING_SPOOL, _PACKAGING_REFILL, _PACKAGING_AUTO]

_SCHEMA_TARGET = {
    vol.Required(ATTR_FILAMENT_ENTITY): cv.entity_id,
    vol.Required(ATTR_COLOR_NAME): cv.string,
}

USE_SPOOL_SCHEMA = vol.Schema(
    {
        **_SCHEMA_TARGET,
        vol.Optional(ATTR_AMOUNT, default=1): vol.All(int, vol.Range(min=1)),
        # auto = decrement whichever counter has stock (spool first). spool/refill
        # forces a specific counter. Existing blueprints that omit this default to
        # "auto" so old refill-only filaments still get decremented correctly.
        vol.Optional(ATTR_PACKAGING, default=_PACKAGING_AUTO): vol.In(_PACKAGING_VALUES),
    }
)
MARK_ARRIVED_SCHEMA = vol.Schema(
    {
        **_SCHEMA_TARGET,
        vol.Optional(ATTR_QUANTITY): vol.All(int, vol.Range(min=0)),
        vol.Optional(ATTR_PACKAGING, default=_PACKAGING_SPOOL): vol.In(
            [_PACKAGING_SPOOL, _PACKAGING_REFILL]
        ),
    }
)
ADD_PURCHASE_SCHEMA = vol.Schema(
    {
        **_SCHEMA_TARGET,
        vol.Required(ATTR_AMOUNT): vol.All(int, vol.Range(min=1)),
        vol.Optional(ATTR_ORDER_ID): cv.string,
        vol.Optional(ATTR_PACKAGING, default=_PACKAGING_SPOOL): vol.In(
            [_PACKAGING_SPOOL, _PACKAGING_REFILL]
        ),
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
        packaging = call.data.get(ATTR_PACKAGING, _PACKAGING_AUTO)

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
        payload = _split_use_payload(current, amount, packaging)
        if not payload:
            _LOGGER.warning(
                "filament_stock.use_spool: no %s stock for color %r",
                packaging,
                color_name,
            )
            return
        await coordinator.api.update_color(color_id, payload)
        await coordinator.async_request_refresh()

    return _handle


def _split_use_payload(
    current: dict[str, Any], amount: int, packaging: str
) -> dict[str, int]:
    """Decide which counters to bump given the user's packaging preference."""
    qty_spool = current.get("quantity") or 0
    used_spool = current.get("quantity_used") or 0
    qty_refill = current.get("quantity_refill") or 0
    used_refill = current.get("used_refill") or 0
    avail_spool = max(0, qty_spool - used_spool)
    avail_refill = max(0, qty_refill - used_refill)

    payload: dict[str, int] = {}
    remaining = amount

    if packaging == _PACKAGING_SPOOL:
        take = min(remaining, avail_spool)
        if take > 0:
            payload["quantity_used"] = used_spool + take
        return payload

    if packaging == _PACKAGING_REFILL:
        take = min(remaining, avail_refill)
        if take > 0:
            payload["used_refill"] = used_refill + take
        return payload

    # auto: spool first, refill for the rest
    take_spool = min(remaining, avail_spool)
    if take_spool > 0:
        payload["quantity_used"] = used_spool + take_spool
        remaining -= take_spool
    if remaining > 0:
        take_refill = min(remaining, avail_refill)
        if take_refill > 0:
            payload["used_refill"] = used_refill + take_refill
    return payload


def _handle_mark_arrived(hass: HomeAssistant):
    async def _handle(call: ServiceCall) -> None:
        entity_id = call.data[ATTR_FILAMENT_ENTITY]
        color_name = call.data[ATTR_COLOR_NAME]
        quantity = call.data.get(ATTR_QUANTITY)
        packaging = call.data.get(ATTR_PACKAGING, _PACKAGING_SPOOL)

        resolved = _resolve_filament_id(hass, entity_id)
        if not resolved:
            return
        coordinator, filament_id = resolved
        color_id = _resolve_color_id(coordinator, filament_id, color_name)
        if color_id is None:
            return
        payload: dict[str, Any] = {"status": STATUS_IN_STOCK}
        if quantity is not None:
            key = "quantity_refill" if packaging == _PACKAGING_REFILL else "quantity"
            payload[key] = int(quantity)
        await coordinator.api.update_color(color_id, payload)
        await coordinator.async_request_refresh()

    return _handle


def _handle_add_purchase(hass: HomeAssistant):
    async def _handle(call: ServiceCall) -> None:
        entity_id = call.data[ATTR_FILAMENT_ENTITY]
        color_name = call.data[ATTR_COLOR_NAME]
        amount = int(call.data[ATTR_AMOUNT])
        order_id = call.data.get(ATTR_ORDER_ID)
        packaging = call.data.get(ATTR_PACKAGING, _PACKAGING_SPOOL)

        resolved = _resolve_filament_id(hass, entity_id)
        if not resolved:
            return
        coordinator, filament_id = resolved
        # The backend POST /api/filaments/{id}/colors merges by name when the
        # color already exists (see app/routers/filaments.py find_color_by_name)
        # and adds to whichever counter is in the payload, so we just route the
        # amount into the right field.
        payload: dict[str, Any] = {
            "color_name": color_name,
            "status": STATUS_IN_STOCK,
        }
        if packaging == _PACKAGING_REFILL:
            payload["quantity_refill"] = amount
        else:
            payload["quantity"] = amount
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
