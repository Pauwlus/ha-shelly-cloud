
from __future__ import annotations

import voluptuous as vol
from typing import Any, Dict, List

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import DOMAIN, CONF_HOST, CONF_AUTH_KEY, CONF_CUSTOMER_ID, CONF_DEVICE_IDS, CONF_POLLING_INTERVAL
from .api import ShellyCloudApi

class ShellyCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            auth_key = user_input[CONF_AUTH_KEY]
            cust_id = user_input[CONF_CUSTOMER_ID]

            # Unique by customer_id + host
            await self.async_set_unique_id(f"{cust_id}@{host}")
            self._abort_if_unique_id_configured()

            api = ShellyCloudApi(self.hass, host, auth_key)
            devices = await api.list_devices()
            if not devices:
                errors["base"] = "cannot_list_devices"
            else:
                self._devices = devices
                self._data = user_input
                return await self.async_step_select_devices()

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_AUTH_KEY): str,
            vol.Required(CONF_CUSTOMER_ID): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_select_devices(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            device_ids: List[str] = user_input[CONF_DEVICE_IDS]
            data = dict(self._data)
            data[CONF_DEVICE_IDS] = device_ids
            title = f"Shelly Cloud: {self._data[CONF_CUSTOMER_ID]}"
            return self.async_create_entry(title=title, data=data)

        options = [(d.get("id"), f"{d.get('name')} ({d.get('id')})") for d in self._devices]
        schema = vol.Schema({
            vol.Required(CONF_DEVICE_IDS): selector({
                "select": {
                    "options": [{"value": v, "label": l} for v, l in options],
                    "multiple": True,
                    "mode": "dropdown",
                }
            })
        })
        return self.async_show_form(step_id="select_devices", data_schema=schema)

    async def async_step_import(self, user_input: Dict[str, Any]) -> FlowResult:
        # Not used
        return self.async_abort(reason="not_supported")


class ShellyCloudOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Required(CONF_POLLING_INTERVAL, default=self.config_entry.options.get(CONF_POLLING_INTERVAL, 30)): int,
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)

    async def async_step_reconfigure(self, user_input=None):
        return await self.async_step_init(user_input)
