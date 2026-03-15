# Multi Shelly Cloud Home Assistant Integration (HACS)

Supports multiple Shelly tenants with cloud authentication keys and per-tenant device selection.

## Features
- Multi-tenant support
- Per-tenant device selection
- Async polling with DataUpdateCoordinator
- Power and Temperature sensors
- HACS-ready and Home Assistant 2024/2025 compatible

## Installation
1. Add repository to HACS → Integrations → Custom Repositories → Type: Integration
2. Install the integration
3. Restart Home Assistant
4. Add tenants via config flow, then select which devices to integrate

## Tenant Configuration
- Name: Friendly name for HA
- Host: Shelly Cloud host (mandatory)
- Authentication Key: Cloud API key (mandatory)
- Selected Devices: Choose which devices to add in HA
