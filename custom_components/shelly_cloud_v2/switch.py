
from __future__ import annotations

from typing import Any, Dict, Optional
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    # Meta for names
    devices = await api.list_devices()
    meta = {d["id"]: d for d in devices}

    entities = []
    for did in entry.data.get("device_ids", []):
        name = meta.get(did, {}).get("name", did)
        code = meta.get(did, {}).get("code")
        entities.append(ShellyCloudSwitch(coordinator, api, did, 0, name, code))
    async_add_entities(entities)


class ShellyCloudSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, api, device_id: str, channel: int, name: str, code: Optional[str]):
        super().__init__(coordinator)
        self.api = api
        self._device_id = device_id
        self._channel = channel
        self._meta_name = name
        self._code = code
        self._attr_name = "Relay"
        self._attr_unique_id = f"{device_id}-switch-{channel}"

    @property
    def is_on(self) -> bool:
        data = self.coordinator.data.get(self._device_id) or {}
        status = data.get("status") or {}
        switch0 = status.get("switch:%d" % self._channel) or {}
        return bool(switch0.get("output"))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.api.set_switch(self._device_id, True, self._channel)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.api.set_switch(self._device_id, False, self._channel)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._meta_name,
            manufacturer="Shelly",
            model=self._code,
        )
