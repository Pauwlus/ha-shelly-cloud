import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN
from .api import ShellyCloudTenantApi

class MultiShellyCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # After tenant info, go to device selection step
            self.tenant_data = user_input
            return await self.async_step_select_devices()
        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("host"): str,
            vol.Required("auth_key"): str
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_select_devices(self, user_input=None):
        api = ShellyCloudTenantApi(self.tenant_data["host"], self.tenant_data["auth_key"])
        devices = await api.get_devices()
        self.device_options = {d["id"]: d.get("name", d["id"]) for d in devices}
        if user_input is not None:
            self.tenant_data["selected_devices"] = user_input.get("selected_devices", [])
            return self.async_create_entry(title=self.tenant_data["name"], data=self.tenant_data)
        schema = vol.Schema({
            vol.Required("selected_devices", default=list(self.device_options.keys())): vol.MultiSelect(self.device_options)
        })
        return self.async_show_form(step_id="select_devices", data_schema=schema)
