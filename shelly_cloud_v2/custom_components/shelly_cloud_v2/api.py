
from __future__ import annotations

import asyncio
import time
import logging
from typing import Any, Dict, List, Optional

from aiohttp import ClientSession, ClientResponseError
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

RATE_LIMIT_SECONDS = 1.0

class ShellyCloudApi:
    """Minimal Shelly Cloud API v2 client with auth_key support."""

    def __init__(self, hass: HomeAssistant, host: str, auth_key: str) -> None:
        self.hass = hass
        self.host = host.rstrip('/')
        self.auth_key = auth_key
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def _throttled_post_json(self, url: str, json_data: Any) -> Any:
        async with self._lock:
            # Respect 1 req/sec
            delta = time.time() - self._last_call
            if delta < RATE_LIMIT_SECONDS:
                await asyncio.sleep(RATE_LIMIT_SECONDS - delta)
            self._last_call = time.time()

            async with ClientSession() as sess:
                async with sess.post(url, json=json_data, headers={"Content-Type": "application/json"}) as resp:
                    resp.raise_for_status()
                    return await resp.json()

    async def _throttled_get(self, url: str) -> Any:
        async with self._lock:
            delta = time.time() - self._last_call
            if delta < RATE_LIMIT_SECONDS:
                await asyncio.sleep(RATE_LIMIT_SECONDS - delta)
            self._last_call = time.time()
            async with ClientSession() as sess:
                async with sess.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.json()

    async def list_devices(self) -> List[Dict[str, Any]]:
        """Return list of devices for the account via interface endpoint.
        Fallback to empty list on error; config_flow will handle errors.
        """
        url = f"{self.host}/interface/device/list?auth_key={self.auth_key}"
        try:
            data = await self._throttled_get(url)
            # Expected format: { "devices": [ {"id": "abcd", "name": "...", "code": "SHPLG-S", ...}, ...]}
            devices = data.get("devices") or data.get("data") or data
            if isinstance(devices, dict) and "devices" in devices:
                devices = devices["devices"]
            if not isinstance(devices, list):
                _LOGGER.debug("Unexpected list_devices payload: %s", data)
                return []
            # Normalize fields
            norm = []
            for d in devices:
                did = d.get("id") or d.get("device_id") or d.get("_id")
                name = d.get("name") or d.get("device_name") or d.get("description") or did
                code = d.get("code") or d.get("type")
                norm.append({"id": did, "name": name, "code": code})
            return [x for x in norm if x.get("id")]
        except Exception as exc:
            _LOGGER.warning("Shelly list_devices failed: %s", exc)
            return []

    async def get_states_v2(self, ids: List[str], *, select: Optional[List[str]] = None, pick: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
        if not ids:
            return []
        url = f"{self.host}/v2/devices/api/get?auth_key={self.auth_key}"
        body: Dict[str, Any] = {"ids": ids}
        if select:
            body["select"] = select
        if pick:
            body["pick"] = pick
        return await self._throttled_post_json(url, body)

    async def set_switch(self, device_id: str, on: bool, channel: int = 0) -> None:
        url = f"{self.host}/v2/devices/api/set/switch?auth_key={self.auth_key}"
        body = {"id": device_id, "channel": channel, "on": on}
        await self._throttled_post_json(url, body)
