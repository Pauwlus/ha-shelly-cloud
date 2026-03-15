from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ShellyCloudCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, selected_devices: list):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60)
        )
        self.api = api
        self.selected_devices = selected_devices

    async def _async_update_data(self):
        devices = await self.api.get_devices()
        # Filter only selected devices
        if self.selected_devices:
            devices = [d for d in devices if d["id"] in self.selected_devices]
        return devices
