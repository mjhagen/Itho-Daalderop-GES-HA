"""Switch platform for Itho Daalderop integration."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IthoDataUpdateCoordinator
from .const import CONF_SERIAL_NUMBER, DOMAIN, MODE_HOLIDAY, MODE_SMART_CONTROL


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Itho switches."""
    coordinator: IthoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    serial_number = entry.data[CONF_SERIAL_NUMBER]

    switches = [
        IthoBoostSwitch(coordinator, serial_number),
        IthoHolidayModeSwitch(coordinator, serial_number),
        IthoPvEnabledSwitch(coordinator, serial_number),
    ]

    async_add_entities(switches)


class IthoBoostSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control boiler boost mode."""

    _OPTIMISTIC_STATE_TIMEOUT = timedelta(minutes=5)

    def __init__(
        self, coordinator: IthoDataUpdateCoordinator, serial_number: str
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._serial_number = serial_number
        self._attr_unique_id = f"{serial_number}_boost"
        self._attr_name = "Boost Mode"
        self._attr_icon = "mdi:rocket-launch"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
        }
        self._optimistic_state: bool | None = None
        self._optimistic_until: datetime | None = None

    def _actual_state(self) -> bool | None:
        """Return the state reported by the API."""
        if self.coordinator.data and "device_status" in self.coordinator.data:
            value = self.coordinator.data["device_status"].get("boostActive")
            if value is not None:
                return bool(value)
        return None

    def _set_optimistic_state(self, state: bool) -> None:
        """Temporarily keep the UI in the requested state."""
        self._optimistic_state = state
        self._optimistic_until = datetime.now() + self._OPTIMISTIC_STATE_TIMEOUT

    @property
    def is_on(self) -> bool | None:
        """Return true if boost is active."""
        actual_state = self._actual_state()

        if self._optimistic_state is not None:
            if actual_state == self._optimistic_state:
                self._optimistic_state = None
                self._optimistic_until = None
                return actual_state

            if self._optimistic_until and datetime.now() < self._optimistic_until:
                return self._optimistic_state

            self._optimistic_state = None
            self._optimistic_until = None

        return actual_state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes for debugging state sync."""
        actual_state = self._actual_state()
        attributes: dict[str, Any] = {
            "api_boost_active": actual_state,
        }
        if self._optimistic_state is not None:
            attributes["optimistic_boost_state"] = self._optimistic_state
        if self._optimistic_until is not None:
            attributes["optimistic_until"] = self._optimistic_until.isoformat()
        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on boost mode."""
        success = await self.coordinator.api_client.async_boost_boiler(activate=True)
        if success:
            self._set_optimistic_state(True)
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off boost mode."""
        success = await self.coordinator.api_client.async_boost_boiler(activate=False)
        if success:
            self._set_optimistic_state(False)
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()


class IthoHolidayModeSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable Holiday mode (vacation mode)."""

    def __init__(
        self, coordinator: IthoDataUpdateCoordinator, serial_number: str
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._serial_number = serial_number
        self._attr_unique_id = f"{serial_number}_holiday_mode"
        self._attr_name = "Vakantie Modus"
        self._attr_icon = "mdi:palm-tree"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if Holiday mode is active."""
        if self.coordinator.data and "device_mode" in self.coordinator.data:
            current_mode = self.coordinator.data["device_mode"].get("deviceMode")
            return current_mode == MODE_HOLIDAY
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable Holiday mode."""
        current_temperature = None
        if self.coordinator.data:
            current_temperature = self.coordinator.data.get("device_mode", {}).get("temperature")

        success = await self.coordinator.api_client.async_set_device_mode(
            MODE_HOLIDAY,
            temperature=current_temperature,
        )
        if success:
            await self.coordinator.async_refresh_settings()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable Holiday mode (switch to SmartControl)."""
        current_temperature = None
        if self.coordinator.data:
            current_temperature = self.coordinator.data.get("device_mode", {}).get("temperature")

        success = await self.coordinator.api_client.async_set_device_mode(
            MODE_SMART_CONTROL,
            temperature=current_temperature,
        )
        if success:
            await self.coordinator.async_refresh_settings()


class IthoPvEnabledSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable PV function."""

    def __init__(
        self, coordinator: IthoDataUpdateCoordinator, serial_number: str
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._serial_number = serial_number
        self._attr_unique_id = f"{serial_number}_pv_enabled"
        self._attr_name = "PV Function"
        self._attr_icon = "mdi:solar-power"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if PV function is enabled."""
        if self.coordinator.data and "pv_settings" in self.coordinator.data:
            return self.coordinator.data["pv_settings"].get("pvEnabled", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable PV function."""
        success = await self.coordinator.api_client.async_set_pv_settings(
            pv_enabled=True
        )
        if success:
            await self.coordinator.async_refresh_settings()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable PV function."""
        success = await self.coordinator.api_client.async_set_pv_settings(
            pv_enabled=False
        )
        if success:
            await self.coordinator.async_refresh_settings()
