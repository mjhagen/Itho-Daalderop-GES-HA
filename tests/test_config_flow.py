#!/usr/bin/env python3
"""
Test de Config Flow stappen zoals ze in Home Assistant zouden werken.
Dit simuleert de gebruikerservaring zonder volledige HA setup.
"""

import requests
import re
import json
import base64
import webbrowser
from urllib.parse import urlencode

try:
    import config
except ImportError:
    print("ERROR: config.py niet gevonden!")
    exit(1)


class ConfigFlowSimulator:
    """Simuleer de Home Assistant Config Flow"""
    
    def __init__(self):
        self.serial_number = None
        self.sso_url = None
        self.azure_url = None
        self.token = None
        self.refresh_token = None
        
        # API Configuration
        self.SSO_INITIATE_URL = "https://itho-tussenlaag.bettywebblocks.com/sso/initiate"
        self.APPLICATION_ID = "2da3d256-ca0a-4041-84ba-93856efceef9"
        self.REDIRECT_URI = "climateconnect://login"
        self.API_BASE_URL = "https://wifi-api.id-c.net/api"
    
    def step_1_user_input(self):
        """Stap 1: Vraag om serienummer (zoals in HA)"""
        print("="*70)
        print("STAP 1: Itho Daalderop Boiler Setup")
        print("="*70)
        print()
        print("Home Assistant heeft alleen het SERIENUMMER nodig.")
        print("Je email/wachtwoord voer je later in de BROWSER in.")
        print()
        print("Serienummer vind je:")
        print("  • Op het typeplaatje van de boiler")
        print("  • In de Itho Daalderop app")
        print()
        
        serial = input("Serienummer: ").strip()
        
        if len(serial) < 5:
            print("❌ Ongeldig serienummer (te kort)")
            return False
        
        self.serial_number = serial
        print(f"✅ Serienummer: {self.serial_number}")
        return True
    
    def step_2_generate_auth_url(self):
        """Stap 2: Genereer authenticatie URL"""
        print()
        print("="*70)
        print("STAP 2: SSO URL genereren")
        print("="*70)
        print()
        
        # Bouw SSO URL
        params = urlencode({
            'redirect': self.REDIRECT_URI,
            'application_id': self.APPLICATION_ID
        })
        self.sso_url = f"{self.SSO_INITIATE_URL}?{params}"
        
        print(f"SSO URL: {self.sso_url}")
        
        # Haal Azure B2C URL op
        try:
            response = requests.get(self.sso_url)
            if response.status_code == 200:
                data = response.json()
                if 'sso' in data:
                    self.azure_url = data['sso']
                    print(f"✅ Azure B2C URL ontvangen")
                    print(f"   {self.azure_url[:80]}...")
                    return True
        except Exception as e:
            print(f"❌ Fout bij ophalen SSO URL: {e}")
            return False
        
        print("❌ Geen Azure URL ontvangen")
        return False
    
    def step_3_open_browser(self):
        """Stap 3: Open browser (async_external_step in HA)"""
        print()
        print("="*70)
        print("STAP 3: Browser openen voor authenticatie")
        print("="*70)
        print()
        print("🌐 De browser opent automatisch de Azure B2C login pagina")
        print()
        print("📋 WAT JE MOET DOEN:")
        print("─"*70)
        print("  1. Browser opent naar Itho login pagina")
        print("  2. Log in met JE EIGEN Itho Daalderop account:")
        print("     • Email: Jouw Itho account email")
        print("     • Wachtwoord: Jouw Itho account wachtwoord")
        print()
        print("  3. Na succesvol inloggen krijg je een FOUTMELDING")
        print("     ❌ 'Failed to launch climateconnect://login...'")
        print()
        print("  4. Dit is NORMAAL en VERWACHT!")
        print("     De authenticatie is gelukt, maar de custom URL")
        print("     wordt niet herkend door je browser.")
        print()
        print("─"*70)
        print()
        print("⚠️  LET OP:")
        print("   Home Assistant vraagt NIET om je email/wachtwoord!")
        print("   Je logt in via de browser met je eigen credentials.")
        print("   HA krijgt alleen het serienummer + een tijdelijke token.")
        print()
        
        choice = input("Browser openen? (j/n): ").strip().lower()
        
        if choice == 'j':
            print()
            print("🌐 Browser wordt geopend...")
            print("   Let op de console/ontwikkelaartools (F12)!")
            print()
            webbrowser.open(self.azure_url)
            return True
        else:
            print()
            print(f"💡 Open deze URL handmatig in je browser:")
            print(f"   {self.azure_url}")
            print()
            return True
    
    def step_4_get_callback_url(self):
        """Stap 4: Vraag om callback URL (zoals in HA form)"""
        print()
        print("="*70)
        print("STAP 4: Authenticatie afronden")
        print("="*70)
        print()
        print("📋 INSTRUCTIES:")
        print("─"*70)
        print()
        print("Na het inloggen krijg je een foutmelding:")
        print("  ❌ Failed to launch 'climateconnect://login?token=...'")
        print()
        print("Dit is NORMAAL! De authenticatie is gelukt!")
        print()
        print("Stappen:")
        print("  1. Open Browser Console (F12 of Ctrl+Shift+I)")
        print("  2. Zoek de regel met 'Failed to launch'")
        print("  3. Kopieer de VOLLEDIGE URL die begint met:")
        print("     climateconnect://login?token=...")
        print("  4. Plak hieronder")
        print()
        print("💡 TIP: De URL kan ook in de adresbalk staan")
        print()
        print("─"*70)
        print()
        
        callback_url = input("Plak de callback URL hier: ").strip()
        
        if not callback_url:
            print("❌ Geen URL ingevoerd")
            return False
        
        print()
        print(f"📥 Ontvangen URL (eerste 100 chars): {callback_url[:100]}...")
        
        # Extract token
        token = self._extract_token_from_url(callback_url)
        
        if token:
            self.token = token
            print(f"✅ Token geëxtraheerd (lengte: {len(token)} chars)")
            print(f"   Eerste 50 chars: {token[:50]}...")
            return True
        else:
            print("❌ Geen geldige token gevonden in URL")
            print()
            print("Controleer of de URL begint met:")
            print("  climateconnect://login?token=")
            print()
            print("Of als je alleen de token hebt, plak dan alleen:")
            print("  eyJ0eXAiOiJKV1QiLCJhbGci...")
            return False
    
    def _extract_token_from_url(self, url):
        """Extract JWT token from callback URL"""
        # Pattern: climateconnect://login?token=XXXXX
        pattern = r'climateconnect://login\?token=([A-Za-z0-9_\-\.]+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        # Probeer ook als alleen token is geplakt
        if url.startswith("eyJ"):  # JWT tokens beginnen meestal met eyJ
            return url
        
        return None
    
    def step_5_validate_token(self):
        """Stap 5: Valideer token met API call"""
        print()
        print("="*70)
        print("STAP 5: Token valideren")
        print("="*70)
        print()
        
        # Decode token eerst
        token_data = self._decode_token()
        
        if not token_data:
            print("❌ Kon token niet decoderen")
            return False
        
        print("✅ Token gedecoded:")
        print(f"   Gebruiker: {token_data.get('user', {}).get('name', 'Onbekend')}")
        print(f"   Email: {token_data.get('user', {}).get('mailaddress', 'Onbekend')}")
        print(f"   Verloopt: {token_data.get('expires_at', 'Onbekend')}")
        
        if token_data.get('refresh_token'):
            self.refresh_token = token_data['refresh_token']
            print(f"   ✅ Refresh token aanwezig ({len(self.refresh_token)} chars)")
        
        print()
        print("🧪 Token valideren met test API call...")
        
        # Test met GetDeviceStatus
        api_url = f"{self.API_BASE_URL}/GetDeviceStatus"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        params = {"serialNumber": self.serial_number}
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                print("✅ API Call succesvol! Token is geldig!")
                data = response.json()
                
                # Toon wat data
                result = data.get('result', {})
                print()
                print("📊 Boiler data opgehaald:")
                print(f"   Boiler inhoud: {result.get('boilerContent', 0)*100:.0f}%")
                print(f"   Device mode: {result.get('deviceMode', 'Onbekend')}")
                print(f"   Status: {result.get('deviceState', 'Onbekend')}")
                print(f"   Software: {result.get('deviceSoftwareVersion', 'Onbekend')}")
                return True
                
            elif response.status_code == 404:
                print("⚠️  Token is geldig, maar serienummer niet gevonden")
                print("    (Dit kan betekenen dat de boiler niet aan dit account gekoppeld is)")
                return True  # Token is geldig, alleen serial klopt niet
                
            elif response.status_code == 401:
                print("❌ Token is ONGELDIG of verlopen")
                print(f"   Response: {response.text[:200]}")
                return False
                
            else:
                print(f"⚠️  Onverwachte status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Fout bij API call: {e}")
            return False
    
    def _decode_token(self):
        """Decode JWT token"""
        if not self.token:
            return None
        
        try:
            parts = self.token.split('.')
            if len(parts) != 3:
                print(f"⚠️  Token heeft {len(parts)} delen (verwacht 3)")
                return None
            
            # Decode payload
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            data = json.loads(decoded)
            
            return {
                "refresh_token": data.get("session", {}).get("refresh_token"),
                "expires_at": data.get("session", {}).get("expires_at"),
                "user": data.get("user", {}),
            }
            
        except Exception as e:
            print(f"❌ Fout bij decoderen token: {e}")
            return None
    
    def step_6_summary(self):
        """Stap 6: Toon samenvatting zoals HA zou doen"""
        print()
        print("="*70)
        print("✅ CONFIGURATIE VOLTOOID")
        print("="*70)
        print()
        print("Je Itho Daalderop boiler is succesvol geconfigureerd!")
        print()
        print("📋 Configuratie details:")
        print(f"   Serial number: {self.serial_number}")
        print(f"   Access token: {self.token[:30]}... ({len(self.token)} chars)")
        
        if self.refresh_token:
            print(f"   Refresh token: {self.refresh_token[:30]}... ({len(self.refresh_token)} chars)")
        
        print()
        print("💾 Deze gegevens zouden in Home Assistant worden opgeslagen:")
        
        config_data = {
            "serial_number": self.serial_number,
            "access_token": self.token,
            "refresh_token": self.refresh_token,
        }
        
        print(json.dumps(config_data, indent=2)[:500] + "...")
        print()
        print("🎉 In Home Assistant zou je nu je boiler können bedienen!")
        print()
    
    def run_full_flow(self):
        """Run de complete config flow"""
        print()
        print("🏠 HOME ASSISTANT CONFIG FLOW SIMULATOR")
        print("="*70)
        print()
        print("Deze test simuleert de stappen die een gebruiker doorloopt")
        print("bij het toevoegen van de Itho Daalderop integratie in HA.")
        print()
        
        # Stap 1: Serienummer
        if not self.step_1_user_input():
            print("\n❌ Gestopt bij stap 1")
            return False
        
        # Stap 2: SSO URL genereren
        if not self.step_2_generate_auth_url():
            print("\n❌ Gestopt bij stap 2")
            return False
        
        # Stap 3: Browser openen
        if not self.step_3_open_browser():
            print("\n❌ Gestopt bij stap 3")
            return False
        
        # Stap 4: Callback URL
        if not self.step_4_get_callback_url():
            print("\n❌ Gestopt bij stap 4")
            return False
        
        # Stap 5: Token validatie
        if not self.step_5_validate_token():
            print("\n❌ Gestopt bij stap 5")
            return False
        
        # Stap 6: Samenvatting
        self.step_6_summary()
        
        return True


def main():
    simulator = ConfigFlowSimulator()
    
    success = simulator.run_full_flow()
    
    if success:
        print("="*70)
        print("✅ ALLE STAPPEN SUCCESVOL GETEST!")
        print("="*70)
        print()
        print("💡 Volgende stappen:")
        print("   1. Deze flow werkt zoals verwacht")
        print("   2. We kunnen nu de volledige HACS integratie bouwen")
        print("   3. Config flow implementeren zoals getest")
        print("   4. Sensors en climate entity toevoegen")
        print()
        return 0
    else:
        print()
        print("="*70)
        print("❌ TEST MISLUKT")
        print("="*70)
        print()
        print("Probeer opnieuw of check de stappen.")
        print()
        return 1


if __name__ == "__main__":
    exit(main())
