
# Shelly Cloud (API v2) — Home Assistant custom integration

A HACS-ready custom integration that connects Home Assistant to **Shelly Cloud API v2** using an **auth_key** and cloud **host** (e.g. `https://shelly-xx-eu.shelly.cloud`).

- Supports **multiple accounts/customers** by allowing multiple config entries (provide a distinct *Customer ID* per entry).
- During setup, the integration **discovers devices** via Shelly Cloud and lets you **select** which ones to add.
- Uses **batched polling** (up to 10 device IDs per call) and HA's `DataUpdateCoordinator` to respect the **1 request/second** rate limit.
- Provides **switch** entities (on/off) and common **sensors** (active power, voltage, current, temperature) for supported devices.

> **Note:** This integration talks to Shelly Cloud; it does not require devices to be reachable locally.

## Install (HACS)
1. Add this repository to HACS as a **Custom repository** (category: *Integration*).
2. Install **Shelly Cloud (API v2)**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for *Shelly Cloud (API v2)*.
5. Enter:
   - **Cloud host** (e.g. `https://shelly-xx-eu.shelly.cloud`),
   - **Cloud key (auth_key)**, and
   - Your **Customer ID** (free text to distinguish entries, used for the title and unique ID).
6. Select discovered devices to include.

## Configuration options
- **Polling interval** (seconds): how often to refresh device state from the cloud (default 30s).
- Re-open Options to change the selected device list at any time.

## Privacy & rate limits
- The Shelly Cloud Control API v2 limits requests to **1 per second**. This integration batches device IDs to minimize calls.
- Only the configured host and `auth_key` are used to query the cloud; no data is sent elsewhere.

## Known limitations
- Device discovery relies on the `interface/device/list` endpoint available on Shelly Cloud with `auth_key`. If device enumeration fails on your tenant, you can still proceed by manually entering IDs (via YAML import is not supported, UI only) or temporarily adding them via the app to retrieve the IDs.
- Entities currently target **switch-capable** devices and a set of common **sensors**. Cover/light controls are easy to extend in `switch.py` / additional platforms.

## Development
- Domain: `shelly_cloud_v2`
- Python: Uses `aiohttp` (provided by Home Assistant) and HA helpers only.

