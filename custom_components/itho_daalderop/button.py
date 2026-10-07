"""Reconnect action for Itho Daalderop."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SERIAL_NUMBER, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the reconnect button."""
    async_add_entities([IthoReconnectButton(entry)])


class IthoReconnectButton(ButtonEntity):
    """Start Home Assistant's reauthentication flow for this config entry."""

    _attr_name = "Reconnect Itho Account"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:account-sync"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the reconnect button."""
        self._entry = entry
        serial_number = entry.data[CONF_SERIAL_NUMBER]
        self._attr_unique_id = f"{serial_number}_reconnect_account"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial_number)},
            "name": f"Itho Boiler {serial_number}",
            "manufacturer": "Itho Daalderop",
            "model": "Water Heater",
        }

    async def async_press(self) -> None:
        """Open a reauth flow without replacing the existing config entry."""
        self._entry.async_start_reauth(self.hass, data=dict(self._entry.data))
