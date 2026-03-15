import aiohttp

class ShellyCloudTenantApi:
    def __init__(self, host: str, auth_key: str):
        self.host = host
        self.auth_key = auth_key

    async def get_devices(self):
        headers = {"Authorization": f"Bearer {self.auth_key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.host}/devices", headers=headers) as resp:
                return await resp.json()
