"""Config and options flow for Filament Stock."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FilamentStockApi, FilamentStockApiError
from .const import (
    CONF_BASE_URL,
    CONF_POLL_INTERVAL,
    DEFAULT_BASE_URL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    d = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_BASE_URL, default=d.get(CONF_BASE_URL, DEFAULT_BASE_URL)): str,
            vol.Required(
                CONF_POLL_INTERVAL, default=d.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
            ): vol.All(int, vol.Range(min=5, max=3600)),
        }
    )


class FilamentStockConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Filament Stock."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            session = async_get_clientsession(self.hass)
            api = FilamentStockApi(session, base_url)
            try:
                await api.health()
            except FilamentStockApiError:
                errors["base"] = "cannot_connect"
            else:
                # Only one instance: the add-on hosts one DB.
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Filament Stock",
                    data={
                        CONF_BASE_URL: base_url,
                        CONF_POLL_INTERVAL: user_input[CONF_POLL_INTERVAL],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return FilamentStockOptionsFlow(config_entry)


class FilamentStockOptionsFlow(OptionsFlow):
    """Edit poll interval.

    AMS tray <-> filament binding is handled automatically in the blueprints
    via the Bambu integration's `filament_id` + `color` tray attributes; no
    manual mapping table is needed.
    """

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        default_poll = self._entry.options.get(
            CONF_POLL_INTERVAL,
            self._entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_POLL_INTERVAL, default=default_poll): vol.All(
                    int, vol.Range(min=5, max=3600)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
