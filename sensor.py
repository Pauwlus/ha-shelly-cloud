
import aiohttp

LOGIN_URL = "https://shelly.cloud/api/login"
DEVICE_URL = "https://shelly.cloud/api/devices"

class ShellyCloudApi:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

    async def login(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(LOGIN_URL, json={
                "email": self.username,
                "password": self.password
            }) as resp:
                data = await resp.json()
                self.token = data.get("token")

    async def get_devices(self):
        if not self.token:
            await self.login()
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(DEVICE_URL, headers=headers) as resp:
                return await resp.json()
