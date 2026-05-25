"""Config and options flow for Filament Stock."""

from __future__ import annotations

import logging
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

_LOGGER = logging.getLogger(__name__)

# Custom add-ons have unpredictable container hostnames on the hassio docker
# network. Documented patterns we have observed in the wild:
#   - http://<slug>:<port>                       (older Supervisor builds)
#   - http://addon_<slug>:<port>                 (some configurations)
#   - http://local_<slug>:<port>                 (when installed from a local
#                                                 custom repository)
#   - http://<slug_with_underscores_to_dashes>   (DNS-safe variant)
# We probe all of them when the user hits Submit. The first one whose
# /api/health responds 200 wins.
_PORT = "8099"
_BASE_URL_CANDIDATES = [
    f"http://addon_filament_stock:{_PORT}",
    f"http://local_filament_stock:{_PORT}",
    f"http://filament_stock:{_PORT}",
    f"http://addon-filament-stock:{_PORT}",
    f"http://local-filament-stock:{_PORT}",
    f"http://filament-stock:{_PORT}",
]


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


async def _probe(session, base_url: str) -> bool:
    """Return True if base_url responds 200 to /api/health."""
    api = FilamentStockApi(session, base_url)
    try:
        await api.health()
    except FilamentStockApiError as err:
        _LOGGER.debug("probe %s failed: %s", base_url, err)
        return False
    return True


class FilamentStockConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Filament Stock."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        session = async_get_clientsession(self.hass)

        if user_input is not None:
            user_base = user_input[CONF_BASE_URL].rstrip("/")

            # If the user accepted the default, treat it as "auto-discover":
            # probe every known candidate URL and pick the first working one.
            # If the user entered something custom, only try that.
            candidates: list[str]
            if user_base == DEFAULT_BASE_URL.rstrip("/"):
                candidates = list(dict.fromkeys([user_base] + _BASE_URL_CANDIDATES))
            else:
                candidates = [user_base]

            resolved: str | None = None
            for url in candidates:
                if await _probe(session, url):
                    resolved = url
                    break

            if resolved is None:
                errors["base"] = "cannot_connect"
            else:
                if resolved != user_base:
                    _LOGGER.info(
                        "Filament Stock: auto-discovered add-on at %s "
                        "(default %s did not respond)",
                        resolved,
                        user_base,
                    )
                # Only one instance: the add-on hosts one DB.
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Filament Stock",
                    data={
                        CONF_BASE_URL: resolved,
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
