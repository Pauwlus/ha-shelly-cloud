from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPower, UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    tenant = hass.data[DOMAIN][entry.entry_id]
    coordinator = tenant["coordinator"]
    devices = coordinator.data or []
    sensors = []
    for dev in devices:
        if "power" in dev:
            sensors.append(ShellyPowerSensor(coordinator, dev))
        if "temperature" in dev:
            sensors.append(ShellyTemperatureSensor(coordinator, dev))
    async_add_entities(sensors)

class ShellyPowerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self.device = device
        self._attr_name = f"{device.get('name','Shelly')} Power"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
    @property
    def native_value(self):
        return self.device.get("power")

class ShellyTemperatureSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self.device = device
        self._attr_name = f"{device.get('name','Shelly')} Temperature"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    @property
    def native_value(self):
        return self.device.get("temperature")
