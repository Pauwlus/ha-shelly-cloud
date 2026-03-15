import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class ShellyCloudTenantApi:
    def __init__(self, host: str, auth_key: str):
        self.host = host
        self.auth_key = auth_key

    async def get_devices(self):
        """Return a list of device dictionaries from Shelly Cloud."""
        url = f"{self.host}/interface/device/list?auth_key={self.auth_key}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    data = await resp.json()
            except Exception as e:
                _LOGGER.error("Failed to fetch devices: %s", e)
                return []

        # Check if response is valid
        if not data.get("isok") or "data" not in data or "devices" not in data["data"]:
            _LOGGER.error("Invalid response from Shelly Cloud: %s", data)
            return []

        devices_dict = data["data"]["devices"]

        # Convert dict of devices to list
        devices_list = []
        for device_id, device_info in devices_dict.items():
            # Ensure each device has an 'id' field (some do already, fallback to dict key)
            device_info.setdefault("id", device_id)
            devices_list.append(device_info)

        return devices_list
