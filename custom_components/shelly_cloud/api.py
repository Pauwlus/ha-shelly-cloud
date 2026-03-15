import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class ShellyCloudTenantApi:
    def __init__(self, host: str, auth_key: str):
        self.host = host
        self.auth_key = auth_key

    async def get_devices(self):
        headers = {"Authorization": f"Bearer {self.auth_key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.host}/devices", headers=headers) as resp:
                try:
                    data = await resp.json()
                except Exception as e:
                    _LOGGER.error("Failed to parse devices JSON: %s", e)
                    return []

                # Handle if the JSON is a dict with 'devices' key
                if isinstance(data, dict) and "devices" in data:
                    return data["devices"]
                # Handle if JSON is already a list
                if isinstance(data, list):
                    return data
                # Unexpected format
                _LOGGER.error("Unexpected devices data format: %s", type(data))
                return []
