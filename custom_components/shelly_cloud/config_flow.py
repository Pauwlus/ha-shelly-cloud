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
        """Step 1: Add tenant info (Name, Host, Auth Key)."""
        if user_input is not None:
            self.tenant_data = user_input
            return await self.async_step_select_devices()

        # Show form with placeholder for host
        data_schema = {
            "name": selector.TextSelector(),
            "host": selector.TextSelector(
                placeholder="https://shelly-xx-eu.shelly.cloud/"
            ),
            "auth_key": selector.TextSelector()
        }

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema
        )

    async def async_step_select_devices(self, user_input=None):
        """Step 2: Select devices for this tenant."""
        api = ShellyCloudTenantApi(
            self.tenant_data["host"], self.tenant_data["auth_key"]
        )

        # Fetch devices from Shelly Cloud
        devices_resp = await api.get_devices()

        if not devices_resp.get("isok") or "data" not in devices_resp:
            _LOGGER.error("Invalid response from Shelly Cloud: %s", devices_resp)
            devices = {}
        else:
            devices = devices_resp["data"].get("devices", {})

        # Build selector options as list of dicts with 'value' and 'label'
        self.device_options = [
            {"value": device["id"], "label": device.get("name", device["id"])}
            for device in devices.values()
        ]

        if user_input is not None:
            # Store selected devices in tenant data
            self.tenant_data["selected_devices"] = user_input.get("selected_devices", [])
            return self.async_create_entry(
                title=self.tenant_data["name"],
                data=self.tenant_data
            )

        # HA SelectSelector with multiple=True
        data_schema = {
            "selected_devices": selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=self.device_options,
                    multiple=True,
                    mode="dropdown"
                )
            )
        }

        return self.async_show_form(
            step_id="select_devices",
            data_schema=data_schema
        )
