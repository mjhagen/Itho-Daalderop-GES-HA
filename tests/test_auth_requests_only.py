#!/usr/bin/env python3
"""
Test: Kan authenticatie zonder Selenium (alleen requests)?
Dit is nodig voor Home Assistant integratie.
"""

import requests
import re
import json
from urllib.parse import urlencode, urlparse, parse_qs
from bs4 import BeautifulSoup

try:
    import config
except ImportError:
    print("ERROR: config.py niet gevonden!")
    exit(1)


class IthoAuthRequestsOnly:
    """Probeer te authenticeren zonder browser/Selenium"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.token = None
        self.refresh_token = None
    
    def authenticate(self):
        """Volledige auth flow met alleen requests"""
        print("🔐 Authenticatie zonder browser (requests only)")
        print(f"Email: {config.EMAIL}\n")
        
        try:
            # Stap 1: SSO Initiatie
            print("=== STAP 1: SSO Initiatie ===")
            params = {
                'redirect': config.REDIRECT_URI,
                'application_id': config.APPLICATION_ID
            }
            url = f"{config.SSO_INITIATE_URL}?{urlencode(params)}"
            
            response = self.session.get(url, allow_redirects=False)
            print(f"Status: {response.status_code}")
            
            data = response.json()
            if 'sso' not in data:
                print("✗ Geen SSO URL ontvangen")
                return False
            
            azure_url = data['sso']
            print(f"✓ Azure B2C URL ontvangen")
            
            # Stap 2: Haal login pagina op
            print("\n=== STAP 2: Azure B2C Login Pagina ===")
            response = self.session.get(azure_url, allow_redirects=True)
            print(f"Status: {response.status_code}")
            
            # Parse form
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form')
            
            if not form:
                print("✗ Geen form gevonden (JavaScript/SPA probleem)")
                return False
            
            # Verzamel form data
            form_action = form.get('action')
            if not form_action.startswith('http'):
                parsed = urlparse(response.url)
                form_action = f"{parsed.scheme}://{parsed.netloc}{form_action}"
            
            print(f"Form action: {form_action[:80]}...")
            
            # Verzamel alle hidden fields
            form_data = {}
            for input_field in soup.find_all('input', {'type': 'hidden'}):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_data[name] = value
            
            # Voeg credentials toe
            form_data['logonIdentifier'] = config.EMAIL
            form_data['password'] = config.PASSWORD
            
            print(f"Form fields: {len(form_data)} (inclusief {len([k for k in form_data if k not in ['logonIdentifier', 'password']])} hidden)")
            
            # Stap 3: Submit login form
            print("\n=== STAP 3: Login Form Submit ===")
            response = self.session.post(
                form_action,
                data=form_data,
                allow_redirects=True,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': response.url
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Final URL: {response.url[:100]}...")
            
            # Stap 4: Zoek token
            print("\n=== STAP 4: Token Extractie ===")
            
            # Methode 1: In HTML zoeken
            token_pattern = r'climateconnect://login\?token=([A-Za-z0-9_\-\.]+)'
            match = re.search(token_pattern, response.text)
            
            if match:
                self.token = match.group(1)
                print(f"✓ Token gevonden in HTML!")
                self._decode_token()
                return True
            
            # Methode 2: In meta refresh
            soup = BeautifulSoup(response.text, 'html.parser')
            meta = soup.find('meta', {'http-equiv': 'refresh'})
            if meta:
                content = meta.get('content', '')
                match = re.search(token_pattern, content)
                if match:
                    self.token = match.group(1)
                    print(f"✓ Token gevonden in meta refresh!")
                    self._decode_token()
                    return True
            
            # Methode 3: Probeer callback URL te volgen
            if 'callback' in response.url:
                print("Callback URL bereikt, maar geen token in response")
                # Probeer de redirect te volgen
                for redirect_count in range(5):
                    if 'Location' in response.headers:
                        next_url = response.headers['Location']
                        print(f"Redirect {redirect_count + 1}: {next_url[:80]}...")
                        match = re.search(token_pattern, next_url)
                        if match:
                            self.token = match.group(1)
                            print(f"✓ Token gevonden in redirect!")
                            self._decode_token()
                            return True
                        response = self.session.get(next_url, allow_redirects=False)
                    else:
                        break
            
            print("✗ Geen token gevonden")
            print(f"\nResponse preview (eerste 500 chars):")
            print(response.text[:500])
            
            # Check for errors
            if 'error' in response.text.lower():
                print("\n⚠️ Mogelijk een error:")
                error_messages = soup.find_all(['div', 'p'], class_=re.compile('error|alert'))
                for msg in error_messages:
                    print(f"  {msg.get_text(strip=True)}")
            
            return False
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _decode_token(self):
        """Decode JWT token"""
        if not self.token:
            return
        
        try:
            import base64
            parts = self.token.split('.')
            if len(parts) != 3:
                print(f"⚠️ Token heeft {len(parts)} delen (verwacht 3)")
                return
            
            # Decode payload
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            
            print(f"\n✓ Token geldig!")
            print(f"  Expires: {payload_data.get('session', {}).get('expires_at')}")
            
            if 'session' in payload_data and 'refresh_token' in payload_data['session']:
                self.refresh_token = payload_data['session']['refresh_token']
                print(f"  Refresh token: aanwezig ({len(self.refresh_token)} chars)")
            
        except Exception as e:
            print(f"⚠️ Kan token niet decoderen: {e}")


def main():
    print("="*70)
    print(" TEST: Authenticatie zonder Selenium (voor HACS integratie)")
    print("="*70)
    print()
    
    auth = IthoAuthRequestsOnly()
    
    if auth.authenticate():
        print("\n" + "="*70)
        print("✅ SUCCES - Requests-only authenticatie werkt!")
        print("="*70)
        print("\n💡 Dit betekent:")
        print("  • Geen Selenium nodig in Home Assistant")
        print("  • Lightweight Python-only code")
        print("  • Geschikt voor HACS integratie")
        print(f"\n📝 Token opslaan in token.txt...")
        
        with open('token_requests_only.txt', 'w') as f:
            f.write(auth.token)
        
        print("✓ Token opgeslagen in token_requests_only.txt")
        return 0
    else:
        print("\n" + "="*70)
        print("❌ MISLUKT - Requests-only werkt niet")
        print("="*70)
        print("\n💡 Oplossing voor HACS:")
        print("  1. Config Flow: gebruiker voert email + password in")
        print("  2. Als direct login faalt: toon instructies")
        print("  3. Gebruiker logt 1x in met externe tool (ons script)")
        print("  4. Gebruiker kopieert refresh token")
        print("  5. Plakt token in HA configuratie")
        print("  6. Component gebruikt refresh token voor access tokens")
        print("\nAlternatief:")
        print("  • Laat gebruiker 1x via browser inloggen")
        print("  • HA opent externe URL")
        print("  • Callback URL bevat token")
        print("  • HA vangt token op")
        return 1


if __name__ == "__main__":
    exit(main())
