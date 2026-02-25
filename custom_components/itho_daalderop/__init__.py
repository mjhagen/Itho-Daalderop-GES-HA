"""The Itho Daalderop integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IthoApiClient
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WATER_HEATER]


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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class IthoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Itho data."""

    def __init__(self, hass: HomeAssistant, api_client: IthoApiClient) -> None:
        """Initialize."""
        self.api_client = api_client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Fetch all data in parallel
            device_status = await self.api_client.async_get_device_status()
            device_mode = await self.api_client.async_get_device_mode()
            pv_settings = await self.api_client.async_get_pv_settings()
            energy = await self.api_client.async_get_energy_consumption()

            return {
                "device_status": device_status,
                "device_mode": device_mode,
                "pv_settings": pv_settings,
                "energy": energy,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
