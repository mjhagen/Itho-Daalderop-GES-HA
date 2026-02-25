"""The Itho Daalderop integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IthoApiClient
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.WATER_HEATER]

# Service schemas
SERVICE_BOOST_BOILER = "boost_boiler"
BOOST_BOILER_SCHEMA = vol.Schema(
    {
        vol.Optional("activate", default=True): cv.boolean,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Itho Daalderop from a config entry."""
    serial_number = entry.data[CONF_SERIAL_NUMBER]
    access_token = entry.data[CONF_ACCESS_TOKEN]

    # Create API client
    api_client = IthoApiClient(hass, serial_number, access_token)

    # Create update coordinator
    coordinator = IthoDataUpdateCoordinator(hass, api_client)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_boost_boiler(call: ServiceCall) -> None:
        """Handle boost boiler service call."""
        activate = call.data.get("activate", True)
        _LOGGER.info("Boost boiler service called: activate=%s", activate)
        
        # Get coordinator from first entry (assumes single device)
        coordinators = list(hass.data[DOMAIN].values())
        if coordinators:
            coordinator = coordinators[0]
            await coordinator.api_client.async_boost_boiler()
            await coordinator.async_request_refresh()
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_BOOST_BOILER,
        handle_boost_boiler,
        schema=BOOST_BOILER_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove services if this was the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_BOOST_BOILER)

    return unload_ok


class IthoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Itho data."""

    def __init__(self, hass: HomeAssistant, api_client: IthoApiClient) -> None:
        """Initialize."""
        self.api_client = api_client
        self._update_count = 0  # Track updates for selective polling

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            self._update_count += 1
            
            # Always fetch critical data (device status and mode)
            device_status = await self.api_client.async_get_device_status()
            device_mode = await self.api_client.async_get_device_mode()
            
            # Only fetch PV settings every 5th update (once per 10 minutes)
            # PV settings rarely change, so no need to poll frequently
            if self._update_count % 5 == 1 or not hasattr(self.data, "get") or "pv_settings" not in self.data:
                _LOGGER.debug("Fetching PV settings (update #%d)", self._update_count)
                pv_settings = await self.api_client.async_get_pv_settings()
            else:
                # Reuse previous PV settings
                pv_settings = self.data.get("pv_settings", {}) if self.data else {}
            
            # Note: GetEnergyConsumption requires startDate, endDate, interval parameters
            # This can be added as a service call when needed
            # energy = await self.api_client.async_get_energy_consumption()

            return {
                "device_status": device_status,
                "device_mode": device_mode,
                "pv_settings": pv_settings,
                "energy": {},  # Empty for now, can be populated via service call
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
