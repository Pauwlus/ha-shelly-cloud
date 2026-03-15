
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data.get("devices", [])
    sensors = []
    for dev in devices:
        if "power" in dev:
            sensors.append(ShellyPowerSensor(coordinator, dev))
    async_add_entities(sensors)

class ShellyPowerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self.device = device
        self._attr_name = device.get("name", "Shelly Power")
        self._attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        return self.device.get("power")
