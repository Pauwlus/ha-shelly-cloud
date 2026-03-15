import logging
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN
from .api import ShellyCloudTenantApi

_LOGGER = logging.getLogger(__name__)


class MultiShellyCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Multi Shelly Cloud."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step 1: Add tenant info."""

        if user_input is not None:
            self.tenant_data = user_input
            return await self.async_step_select_devices()

        data_schema = {
            "name": selector.TextSelector(
                selector.TextSelectorConfig()
            ),
            "host": selector.TextSelector(
                selector.TextSelectorConfig(
                    placeholder="https://shelly-xx-eu.shelly.cloud/"
                )
            ),
            "auth_key": selector.TextSelector(
                selector.TextSelectorConfig()
            ),
        }

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    async def async_step_select_devices(self, user_input=None):
        """Step 2: Select devices."""

        api = ShellyCloudTenantApi(
            self.tenant_data["host"],
            self.tenant_data["auth_key"]
        )

        devices_resp = await api.get_devices()

        if not isinstance(devices_resp, dict):
            _LOGGER.error("Invalid response from Shelly Cloud: %s", devices_resp)
            devices = {}

        elif not devices_resp.get("isok"):
            _LOGGER.error("Shelly API error: %s", devices_resp)
            devices = {}

        else:
            devices = devices_resp.get("data", {}).get("devices", {})

        options = []

        if isinstance(devices, dict):
            for dev in devices.values():
                device_id = dev.get("id")
                name = dev.get("name") or device_id

                if device_id:
                    options.append(
                        {
                            "value": device_id,
                            "label": name
                        }
                    )

        if user_input is not None:
            selected = user_input.get("selected_devices", [])

            self.tenant_data["selected_devices"] = selected

            return self.async_create_entry(
                title=self.tenant_data["name"],
                data=self.tenant_data,
            )

        data_schema = {
            "selected_devices": selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options,
                    multiple=True,
                    mode="dropdown",
                )
            )
        }

        return self.async_show_form(
            step_id="select_devices",
            data_schema=data_schema,
        )
