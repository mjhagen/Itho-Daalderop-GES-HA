"""Config flow for Itho Daalderop integration."""
from __future__ import annotations

import base64
import json
import logging
import re
from typing import Any
from urllib.parse import urlencode

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import IthoApiClient
from .const import (
    APPLICATION_ID,
    CONF_ACCESS_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    REDIRECT_URI,
    SSO_INITIATE_URL,
)

_LOGGER = logging.getLogger(__name__)


class IthoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Itho Daalderop."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.serial_number: str | None = None
        self.azure_url: str | None = None
        self.access_token: str | None = None
        self.refresh_token: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - ask for serial number."""
        errors: dict[str, str] = {}

        if user_input is not None:
            serial_number = user_input[CONF_SERIAL_NUMBER].strip().upper()
            
            # Validate serial number
            if len(serial_number) < 5:
                errors[CONF_SERIAL_NUMBER] = "invalid_serial"
            else:
                self.serial_number = serial_number
                return await self.async_step_auth()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERIAL_NUMBER): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "serial_help": "Serienummer van je boiler (bijv. VPR242600095)"
            },
        )

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Get Azure B2C login URL and open browser."""
        # Build SSO URL
        params = urlencode({
            "redirect": REDIRECT_URI,
            "application_id": APPLICATION_ID,
        })
        sso_url = f"{SSO_INITIATE_URL}?{params}"

        # Get Azure B2C URL
        session = async_get_clientsession(self.hass)
        
        try:
            async with session.get(sso_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    self.azure_url = data.get("sso")
                    
                    if not self.azure_url:
                        return self.async_abort(reason="no_azure_url")
                    
                    # Open browser and wait for callback
                    return await self.async_step_auth_callback()
                    
        except Exception as err:
            _LOGGER.error("Error getting Azure URL: %s", err)
            return self.async_abort(reason="cannot_connect")

    async def async_step_auth_callback(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the callback from Azure B2C login."""
        errors: dict[str, str] = {}

        if user_input is not None:
            callback_url = user_input.get("callback_url", "").strip()
            
            # Extract token from URL
            token = self._extract_token_from_url(callback_url)
            
            if not token:
                errors["callback_url"] = "invalid_callback"
            else:
                self.access_token = token
                
                # Decode token to get refresh token
                token_data = self._decode_token(token)
                
                if token_data and token_data.get("refresh_token"):
                    self.refresh_token = token_data["refresh_token"]
                
                # Validate token with API call
                if await self._async_validate_token():
                    # Create config entry
                    return self.async_create_entry(
                        title=f"Itho Boiler {self.serial_number}",
                        data={
                            CONF_SERIAL_NUMBER: self.serial_number,
                            CONF_ACCESS_TOKEN: self.access_token,
                            CONF_REFRESH_TOKEN: self.refresh_token,
                        },
                    )
                else:
                    errors["callback_url"] = "invalid_token"

        # Show form with browser link
        return self.async_show_form(
            step_id="auth_callback",
            data_schema=vol.Schema(
                {
                    vol.Required("callback_url"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "login_url": self.azure_url,
                "instructions": (
                    "1. Klik op de link hieronder om in te loggen\n"
                    "2. Log in met je Itho Daalderop account\n"
                    "3. Na inloggen krijg je een foutmelding\n"
                    "4. Open de browser console (F12)\n"
                    "5. Kopieer de URL die begint met: climateconnect://login?token=...\n"
                    "6. Plak de URL hieronder"
                ),
            },
        )

    def _extract_token_from_url(self, url: str) -> str | None:
        """Extract JWT token from callback URL."""
        # Pattern: climateconnect://login?token=XXXXX
        pattern = r"climateconnect://login\?token=([A-Za-z0-9_\-\.]+)"
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        # Also try if only token is pasted
        if url.startswith("eyJ"):  # JWT tokens usually start with eyJ
            return url
        
        return None

    def _decode_token(self, token: str) -> dict[str, Any] | None:
        """Decode JWT token to extract refresh token."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            
            # Decode payload
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            data = json.loads(decoded)
            
            return {
                "refresh_token": data.get("session", {}).get("refresh_token"),
                "expires_at": data.get("session", {}).get("expires_at"),
                "user": data.get("user", {}),
            }
            
        except Exception as err:
            _LOGGER.error("Error decoding token: %s", err)
            return None

    async def _async_validate_token(self) -> bool:
        """Validate token by making a test API call."""
        if not self.access_token or not self.serial_number:
            return False
        
        try:
            api_client = IthoApiClient(
                self.hass, self.serial_number, self.access_token
            )
            
            # Try to get device status
            await api_client.async_get_device_status()
            return True
            
        except Exception as err:
            _LOGGER.error("Token validation failed: %s", err)
            return False
