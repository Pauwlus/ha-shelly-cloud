
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_DEVICE_IDS,
    CONF_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
)
from .api import ShellyCloudApi

_LOGGER = logging.getLogger(__name__)

class ShellyCloudCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator that batches v2 state requests for selected devices."""

    def __init__(self, hass: HomeAssistant, api: ShellyCloudApi, entry: ConfigEntry) -> None:
        self.api = api
        self.entry = entry
        interval = entry.options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

    async def _async_setup(self) -> None:
        # nothing special to fetch once
        return

    async def _async_update_data(self) -> Dict[str, Any]:
        ids: List[str] = self.entry.data.get(CONF_DEVICE_IDS, [])
        result: Dict[str, Any] = {}
        if not ids:
            return result
        # chunk by 10 ids as per API guidance
        CHUNK = 10
        try:
            for i in range(0, len(ids), CHUNK):
                chunk = ids[i:i+CHUNK]
                states = await self.api.get_states_v2(chunk, select=["status", "settings"])  # type: ignore[arg-type]
                # states is a list of state dicts, each with 'id', 'status', 'settings', etc.
                for st in states or []:
                    did = st.get("id")
                    if did:
                        result[did] = st
        except Exception as exc:
            raise UpdateFailed(str(exc)) from exc
        return result
