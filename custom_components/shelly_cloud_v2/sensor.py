
from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import (POWER_WATT, ELECTRIC_POTENTIAL_VOLT,
                                 ELECTRIC_CURRENT_AMPERE, UnitOfTemperature)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTR_DEVICE_NAME, ATTR_DEVICE_CODE

_LOGGER = logging.getLogger(__name__)

SENSOR_KEYS = {
    "apower": ("Power", POWER_WATT, SensorDeviceClass.POWER),
    "voltage": ("Voltage", ELECTRIC_POTENTIAL_VOLT, SensorDeviceClass.VOLTAGE),
    "current": ("Current", ELECTRIC_CURRENT_AMPERE, SensorDeviceClass.CURRENT),
    "temperature": ("Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
}

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    # Fetch device list for names/codes
    devices = await api.list_devices()
    meta = {d["id"]: d for d in devices}

    entities: List[SensorEntity] = []

    for did in entry.data.get("device_ids", []):
        entities.extend(_build_device_sensors(did, coordinator, meta.get(did)))

    async_add_entities(entities)


def _build_device_sensors(device_id: str, coordinator, meta: Optional[Dict[str, Any]]):
    name = (meta or {}).get("name", device_id)
    code = (meta or {}).get("code")

    # We create generic sensors and read values from coordinator on update
    sensors: List[SensorEntity] = []
    for key, (title, unit, device_class) in SENSOR_KEYS.items():
        sensors.append(ShellyCloudMetricSensor(coordinator, device_id, key, title, unit, device_class, name, code))
    return sensors


class ShellyCloudMetricSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str, key: str, title: str, unit, device_class, name: str, code: Optional[str]):
        super().__init__(coordinator)
        self._device_id = device_id
        self._key = key
        self._attr_name = title
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._meta_name = name
        self._code = code
        self._attr_unique_id = f"{device_id}-{key}"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self._device_id) or {}
        # For plus/gen2, metrics are under status['switch:0'] typically
        status = data.get("status") or {}
        switch0 = status.get("switch:0") or {}
        val = switch0.get(self._key)
        if isinstance(val, dict) and "tC" in val:
            return val.get("tC")
        return val

    @property
    def available(self) -> bool:
        data = self.coordinator.data.get(self._device_id) or {}
        return bool(data)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._meta_name,
            manufacturer="Shelly",
            model=self._code,
        )
