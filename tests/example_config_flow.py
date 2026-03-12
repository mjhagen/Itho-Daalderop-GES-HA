"""
Config flow voor Itho Daalderop HACS integratie
Demonstreert de gebruiksvriendelijke login flow
"""
from __future__ import annotations

import logging
import re
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "itho_daalderop"

# API Configuration
SSO_INITIATE_URL = "https://itho-tussenlaag.bettywebblocks.com/sso/initiate"
APPLICATION_ID = "2da3d256-ca0a-4041-84ba-93856efceef9"
REDIRECT_URI = "climateconnect://login"


class IthoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Itho Daalderop."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._sso_url = None
        self._serial_number = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - ask for serial number."""
        errors = {}

        if user_input is not None:
            # Valideer serial number format (bijv. <SERIAL_NUMBER>)
            serial = user_input.get("serial_number", "").strip()
            
            if len(serial) < 5:
                errors["serial_number"] = "invalid_serial"
            else:
                self._serial_number = serial
                # Ga naar de authenticatie stap
                return await self.async_step_auth()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("serial_number"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "help_text": "Voer het serienummer van je Itho Daalderop boiler in. "
                            "Dit vind je op het typeplaatje van de boiler of in de Itho app."
            },
        )

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Start de externe authenticatie flow."""
        
        # Genereer de SSO login URL
        params = f"redirect={REDIRECT_URI}&application_id={APPLICATION_ID}"
        self._sso_url = f"{SSO_INITIATE_URL}?{params}"
        
        # Haal de daadwerkelijke Azure B2C URL op
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(self._sso_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "sso" in data:
                        azure_url = data["sso"]
                        
                        # Open externe browser met Azure B2C login
                        return self.async_external_step(
                            step_id="auth_callback",
                            url=azure_url
                        )
        except Exception as err:
            _LOGGER.error("Failed to get SSO URL: %s", err)
            return self.async_abort(reason="cannot_connect")
        
        return self.async_abort(reason="unknown")

    async def async_step_auth_callback(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the callback from external authentication."""
        
        # Na de externe step, toon een formulier waar de gebruiker 
        # de callback URL kan plakken
        errors = {}

        if user_input is not None:
            callback_url = user_input.get("callback_url", "").strip()
            
            # Extract token from climateconnect://login?token=...
            token = self._extract_token_from_url(callback_url)
            
            if token:
                # Valideer de token
                if await self._async_validate_token(token):
                    # Extract refresh token en andere data
                    token_data = self._decode_token(token)
                    
                    # Configuratie opslaan
                    return self.async_create_entry(
                        title=f"Itho Boiler {self._serial_number}",
                        data={
                            "serial_number": self._serial_number,
                            "access_token": token,
                            "refresh_token": token_data.get("refresh_token"),
                            "expires_at": token_data.get("expires_at"),
                            "user_email": token_data.get("user", {}).get("mailaddress"),
                        },
                    )
                else:
                    errors["callback_url"] = "invalid_token"
            else:
                errors["callback_url"] = "invalid_url"

        # Toon instructies en URL input veld
        return self.async_show_form(
            step_id="auth_callback",
            data_schema=vol.Schema(
                {
                    vol.Required("callback_url"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "instructions": self._get_callback_instructions()
            },
        )

    def _get_callback_instructions(self) -> str:
        """Geef duidelijke instructies aan de gebruiker."""
        return """
**Authenticatie voltooid?**

Na het inloggen krijg je een foutmelding in de browser:
`Failed to launch 'climateconnect://login?token=...'`

Dit is normaal! Volg deze stappen:

1. **Open de browser console** (meestal F12 of Ctrl+Shift+I)
2. Zoek naar de regel met `Failed to launch 'climateconnect://login?token=...`
3. **Kopieer de VOLLEDIGE URL** die begint met `climateconnect://login?token=`
4. **Plak deze hieronder** in het tekstveld
5. Klik op "Verzenden"

**Alternatief:** Kijk in de adresbalk van je browser - soms staat de URL daar ook.

**Voorbeeld URL:**
```
climateconnect://login?token=eyJ0eXAiOiJKV1QiLCJhbGc...
```
        """

    def _extract_token_from_url(self, url: str) -> str | None:
        """Extract JWT token from callback URL."""
        # Pattern: climateconnect://login?token=XXXXX
        pattern = r'climateconnect://login\?token=([A-Za-z0-9_\-\.]+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        # Probeer ook als er alleen de token is geplakt
        # (als gebruiker alleen het token deel kopieert)
        if url.startswith("eyJ"):  # JWT tokens beginnen meestal met eyJ
            return url
        
        return None

    def _decode_token(self, token: str) -> dict[str, Any]:
        """Decode JWT token om data te extraheren."""
        import base64
        import json
        
        try:
            # Split JWT in delen
            parts = token.split('.')
            if len(parts) != 3:
                return {}
            
            # Decode payload (deel 2)
            payload = parts[1]
            # Voeg padding toe
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            data = json.loads(decoded)
            
            # Haal belangrijke velden eruit
            return {
                "refresh_token": data.get("session", {}).get("refresh_token"),
                "expires_at": data.get("session", {}).get("expires_at"),
                "user": data.get("user", {}),
            }
            
        except Exception as err:
            _LOGGER.error("Failed to decode token: %s", err)
            return {}

    async def _async_validate_token(self, token: str) -> bool:
        """Valideer de token door een test API call te doen."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        
        # Test de token met een simpele API call
        api_url = "https://wifi-api.id-c.net/api/GetDeviceStatus"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        params = {"serialNumber": self._serial_number}
        
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(api_url, headers=headers, params=params) as response:
                # 200 = token werkt, 404 = token werkt maar serial niet gevonden
                # 401 = token is invalid
                return response.status in [200, 404]
        except Exception as err:
            _LOGGER.error("Token validation failed: %s", err)
            return False


# Voorbeeld translations/en.json voor de strings:
TRANSLATIONS_EXAMPLE = {
    "config": {
        "step": {
            "user": {
                "title": "Itho Daalderop Boiler Setup",
                "description": "Voer het serienummer van je boiler in.\n\n{help_text}",
                "data": {
                    "serial_number": "Serienummer"
                }
            },
            "auth_callback": {
                "title": "Authenticatie afronden",
                "description": "{instructions}",
                "data": {
                    "callback_url": "Callback URL (climateconnect://login?token=...)"
                }
            }
        },
        "error": {
            "invalid_serial": "Ongeldig serienummer",
            "invalid_token": "Token is ongeldig of verlopen",
            "invalid_url": "De URL is niet correct. Controleer of je de volledige URL hebt gekopieerd.",
            "cannot_connect": "Kan niet verbinden met Itho Daalderop servers"
        },
        "abort": {
            "already_configured": "Dit apparaat is al geconfigureerd",
            "cannot_connect": "Kan niet verbinden met Itho Daalderop servers",
            "unknown": "Onbekende fout opgetreden"
        }
    }
}
