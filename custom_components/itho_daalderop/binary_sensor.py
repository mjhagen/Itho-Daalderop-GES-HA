"""Connection diagnostics for Itho Daalderop."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IthoDataUpdateCoordinator
from .const import CONF_SERIAL_NUMBER, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Itho connection diagnostic."""
    coordinator: IthoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [IthoConnectionBinarySensor(coordinator, entry.data[CONF_SERIAL_NUMBER])]
    )


class IthoConnectionBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Report whether cloud polling and boiler telemetry remain healthy."""

    _attr_name = "Itho Boiler Connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:cloud-check"

    def __init__(
        self,
        coordinator: IthoDataUpdateCoordinator,
        serial_number: str,
    ) -> None:
        """Initialize the connection diagnostic."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{serial_number}_connection_health"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
            "name": f"Itho Boiler {serial_number}",
            "manufacturer": "Itho Daalderop",
            "model": "Water Heater",
        }

    @property
    def available(self) -> bool:
        """Keep the diagnostic available when the data coordinator fails."""
        return True

    @property
    def is_on(self) -> bool:
        """Return true only for a healthy, fresh connection."""
        return self.coordinator.connection_status == "connected"

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        """Expose timestamps and status useful for troubleshooting."""
        return {
            "connection_status": self.coordinator.connection_status,
            "last_poll_attempt": (
                self.coordinator.last_poll_attempt.isoformat()
                if self.coordinator.last_poll_attempt
                else None
            ),
            "last_successful_update": (
                self.coordinator.last_successful_update.isoformat()
                if self.coordinator.last_successful_update
                else None
            ),
            "last_telemetry_change": (
                self.coordinator.last_payload_change.isoformat()
                if self.coordinator.last_payload_change
                else None
            ),
            "consecutive_failures": self.coordinator.consecutive_failures,
            "reconnect_entity": "button.reconnect_itho_account",
        }
