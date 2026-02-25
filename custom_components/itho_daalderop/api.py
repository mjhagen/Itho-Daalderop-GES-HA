"""API client for Itho Daalderop."""
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class IthoApiClient:
    """API client for Itho Daalderop boiler."""

    def __init__(self, hass: HomeAssistant, serial_number: str, access_token: str) -> None:
        """Initialize the API client."""
        self.hass = hass
        self.serial_number = serial_number
        self.access_token = access_token
        self._session = async_get_clientsession(hass)

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def async_get_device_status(self) -> dict[str, Any]:
        """Get device status from API."""
        url = f"{API_BASE_URL}/GetDeviceStatus"
        params = {"serialNumber": self.serial_number}

        try:
            async with self._session.get(
                url, headers=self._get_headers(), params=params, timeout=10
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("result", {})
        except Exception as err:
            _LOGGER.error("Error fetching device status: %s", err)
            raise

    async def async_get_device_mode(self) -> dict[str, Any]:
        """Get device mode from API."""
        url = f"{API_BASE_URL}/GetDeviceMode"
        params = {"serialNumber": self.serial_number}

        try:
            async with self._session.get(
                url, headers=self._get_headers(), params=params, timeout=10
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("result", {})
        except Exception as err:
            _LOGGER.error("Error fetching device mode: %s", err)
            raise

    async def async_get_pv_settings(self) -> dict[str, Any]:
        """Get PV settings from API."""
        url = f"{API_BASE_URL}/GetDevicePVSettings"
        params = {"serialNumber": self.serial_number}

        try:
            async with self._session.get(
                url, headers=self._get_headers(), params=params, timeout=10
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("result", {})
        except Exception as err:
            _LOGGER.error("Error fetching PV settings: %s", err)
            raise

    async def async_get_energy_consumption(self) -> dict[str, Any]:
        """Get energy consumption from API."""
        url = f"{API_BASE_URL}/GetEnergyConsumption"
        params = {"serialNumber": self.serial_number}

        try:
            async with self._session.get(
                url, headers=self._get_headers(), params=params, timeout=10
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("result", {})
        except Exception as err:
            _LOGGER.error("Error fetching energy consumption: %s", err)
            raise

    async def async_set_device_mode(self, mode: str, schedule: str | None = None) -> bool:
        """Set device mode."""
        url = f"{API_BASE_URL}/UpdateDeviceMode"
        
        payload = {
            "serialNumber": self.serial_number,
            "deviceMode": mode,
        }
        
        if schedule:
            payload["deviceSchedule"] = schedule

        try:
            async with self._session.post(
                url, headers=self._get_headers(), json=payload, timeout=10
            ) as response:
                response.raise_for_status()
                return True
        except Exception as err:
            _LOGGER.error("Error setting device mode: %s", err)
            return False

    async def async_boost_boiler(self) -> bool:
        """Activate boiler boost."""
        url = f"{API_BASE_URL}/BoostBoiler"
        
        payload = {
            "serialNumber": self.serial_number,
        }

        try:
            async with self._session.post(
                url, headers=self._get_headers(), json=payload, timeout=10
            ) as response:
                response.raise_for_status()
                return True
        except Exception as err:
            _LOGGER.error("Error boosting boiler: %s", err)
            return False

    async def async_set_temperature(self, temperature: float) -> bool:
        """Set target temperature."""
        url = f"{API_BASE_URL}/UpdateDeviceTemperature"
        
        payload = {
            "serialNumber": self.serial_number,
            "temperature": temperature,
        }

        try:
            async with self._session.post(
                url, headers=self._get_headers(), json=payload, timeout=10
            ) as response:
                response.raise_for_status()
                return True
        except Exception as err:
            _LOGGER.error("Error setting temperature: %s", err)
            return False
