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

        data_schema = {
            "name": selector.TextSelector(),
            "host": selector.TextSelector(),
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
        devices = await api.get_devices()

        # Handle dict vs list
        if isinstance(devices, dict) and "devices" in devices:
            devices = devices["devices"]
        elif not isinstance(devices, list):
            _LOGGER.error("Unexpected devices data format: %s", type(devices))
            devices = []

        # Build options for selector
        self.device_options = {d["id"]: d.get("name", d["id"]) for d in devices}

        if user_input is not None:
            self.tenant_data["selected_devices"] = user_input.get("selected_devices", [])
            return self.async_create_entry(
                title=self.tenant_data["name"],
                data=self.tenant_data
            )

        # Use HA SelectSelector with multiple=True
        data_schema = {
            "selected_devices": selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(self.device_options.keys()),
                    multiple=True,
                    mode="dropdown"
                )
            )
        }

        return self.async_show_form(
            step_id="select_devices",
            data_schema=data_schema
        )
