"""The Itho Daalderop integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
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

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]

# Service schemas
SERVICE_BOOST_BOILER = "boost_boiler"
SERVICE_SET_SCHEDULE = "set_schedule"

BOOST_BOILER_SCHEMA = vol.Schema(
    {
        vol.Optional("activate", default=True): cv.boolean,
    }
)

SET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required("schedule"): dict,  # Schedule object with day:hour:temp mappings
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
            success = await coordinator.api_client.async_boost_boiler(activate=activate)
            if success:
                await coordinator.async_request_refresh()
    
    async def handle_set_schedule(call: ServiceCall) -> None:
        """Handle set schedule service call."""
        schedule = call.data.get("schedule")
        _LOGGER.info("Set schedule service called with schedule: %s", schedule)
        
        # Get coordinator from first entry (assumes single device)
        coordinators = list(hass.data[DOMAIN].values())
        if coordinators:
            coordinator = coordinators[0]
            # Set to Schedule mode with the provided schedule
            current_temperature = None
            if coordinator.data:
                current_temperature = coordinator.data.get("device_mode", {}).get("temperature")

            success = await coordinator.api_client.async_set_device_mode(
                mode="Schedule",
                temperature=current_temperature,
                schedule=schedule,
            )
            if success:
                await coordinator.async_refresh_settings()
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_BOOST_BOILER,
        handle_boost_boiler,
        schema=BOOST_BOILER_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SCHEDULE,
        handle_set_schedule,
        schema=SET_SCHEDULE_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove services if this was the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_BOOST_BOILER)
            hass.services.async_remove(DOMAIN, SERVICE_SET_SCHEDULE)

    return unload_ok


class IthoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Itho data."""

    def __init__(self, hass: HomeAssistant, api_client: IthoApiClient) -> None:
        """Initialize."""
        self.api_client = api_client
        self._update_count = 0  # Track updates for selective polling
        self._force_full_refresh = False  # Force fetch all data on next update
        self._energy_history_interval = 30  # Fetch slow history endpoint every ~60 min
        self._calculated_energy_total: float | None = None
        self._last_power_kw: float | None = None
        self._last_energy_timestamp: datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def async_force_refresh(self) -> None:
        """Force a full refresh of all data on next update."""
        self._force_full_refresh = True
        await self.async_request_refresh()

    async def async_refresh_settings(self) -> None:
        """Refresh only settings data (mode + PV) without waiting for next poll."""
        try:
            device_mode = await self.api_client.async_get_device_mode()
            pv_settings = await self.api_client.async_get_pv_settings()
            
            # Update data without triggering full refresh
            if self.data:
                self.data["device_mode"] = device_mode
                self.data["pv_settings"] = pv_settings
                self.async_set_updated_data(self.data)
            
            _LOGGER.debug("Settings data refreshed after user change")
        except Exception as err:
            _LOGGER.warning("Failed to refresh settings: %s", err)

    def _update_calculated_energy(self, device_status: dict[str, Any]) -> None:
        """Maintain a locally integrated total energy value in kWh."""
        now = datetime.now()
        raw_energy = device_status.get("energyConsumption")
        current_power = device_status.get("devicePowerMeasured")

        current_power_kw = float(current_power) if isinstance(current_power, int | float) else None
        raw_energy_kwh = float(raw_energy) if isinstance(raw_energy, int | float) else None

        if self._calculated_energy_total is None:
            self._calculated_energy_total = raw_energy_kwh if raw_energy_kwh is not None else 0.0
        elif (
            self._last_energy_timestamp is not None
            and self._last_power_kw is not None
            and current_power_kw is not None
        ):
            elapsed_hours = (now - self._last_energy_timestamp).total_seconds() / 3600
            if elapsed_hours > 0:
                average_power_kw = max((self._last_power_kw + current_power_kw) / 2, 0)
                self._calculated_energy_total += average_power_kw * elapsed_hours

        if raw_energy_kwh is not None and raw_energy_kwh > self._calculated_energy_total:
            self._calculated_energy_total = raw_energy_kwh

        self._last_power_kw = current_power_kw
        self._last_energy_timestamp = now
        device_status["energyConsumptionIntegrated"] = round(self._calculated_energy_total, 3)

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            self._update_count += 1
            
            # Always fetch critical real-time data (device status)
            device_status = await self.api_client.async_get_device_status()
            self._update_calculated_energy(device_status)
            
            # Fetch settings only every 5th update OR when forced
            # Settings (mode, PV) rarely change - only when user changes them
            should_fetch_settings = (
                self._update_count % 5 == 1 
                or not self.data 
                or self._force_full_refresh
            )
            
            if should_fetch_settings:
                _LOGGER.debug(
                    "Fetching settings data (update #%d, forced=%s)", 
                    self._update_count,
                    self._force_full_refresh
                )
                device_mode = await self.api_client.async_get_device_mode()
                pv_settings = await self.api_client.async_get_pv_settings()
            else:
                # Reuse previous settings data
                device_mode = self.data.get("device_mode", {}) if self.data else {}
                pv_settings = self.data.get("pv_settings", {}) if self.data else {}

            should_fetch_energy = (
                self._update_count % self._energy_history_interval == 1
                or not self.data
                or self._force_full_refresh
            )

            if should_fetch_energy:
                _LOGGER.debug(
                    "Fetching energy history data (update #%d, forced=%s)",
                    self._update_count,
                    self._force_full_refresh,
                )
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                energy = await self.api_client.async_get_energy_consumption(
                    start_date=start_date,
                    end_date=end_date,
                    interval="Day",
                    include_previous_period=True,
                )
            else:
                energy = self.data.get("energy", {}) if self.data else {}

            self._force_full_refresh = False  # Reset flag after optional fetches

            return {
                "device_status": device_status,
                "device_mode": device_mode,
                "pv_settings": pv_settings,
                "energy": energy,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
