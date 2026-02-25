#!/usr/bin/env python3
"""
Test script voor Itho Daalderop authenticatie flow.
Dit script test de complete OAuth/SSO flow en haalt een JWT token op.
"""

import requests
import re
import json
from urllib.parse import parse_qs, urlparse, urlencode
from bs4 import BeautifulSoup

try:
    import config
except ImportError:
    print("ERROR: config.py niet gevonden!")
    print("Kopieer config.example.py naar config.py en vul je credentials in.")
    exit(1)


class IthoAuthenticator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.token = None
        self.refresh_token = None
    
    def step1_initiate_sso(self):
        """Stap 1: Initieer de SSO flow"""
        print("\n=== STAP 1: SSO Initiatie ===")
        
        params = {
            'redirect': config.REDIRECT_URI,
            'application_id': config.APPLICATION_ID
        }
        
        url = f"{config.SSO_INITIATE_URL}?{urlencode(params)}"
        print(f"URL: {url}")
        
        response = self.session.get(url, allow_redirects=False)
        print(f"Status: {response.status_code}")
        
        # Parse JSON response
        try:
            data = response.json()
            if 'sso' in data:
                sso_url = data['sso']
                print(f"✓ SSO URL ontvangen")
                print(f"Azure B2C URL: {sso_url[:100]}...")
                return sso_url
        except:
            pass
        
        return None
    
    def step2_login(self, sso_url):
        """Stap 2: Login met email en wachtwoord via Azure B2C"""
        print("\n=== STAP 2: Azure B2C Login ===")
        
        # Ga naar de Azure B2C login pagina
        response = self.session.get(sso_url, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Login URL: {response.url[:100]}...")
        
        # Parse de login pagina
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the form (Azure B2C gebruikt meestal een form met id zoals 'localAccountForm')
        form = soup.find('form', {'id': re.compile('.*Account.*|.*login.*|.*signin.*', re.I)})
        if not form:
            form = soup.find('form')
        
        if not form:
            print("✗ Geen login form gevonden")
            print("Response preview:")
            print(response.text[:1000])
            return None
        
        print(f"✓ Login form gevonden")
        
        # Bepaal form action
        form_action = form.get('action')
        if form_action:
            if form_action.startswith('http'):
                login_url = form_action
            elif form_action.startswith('/'):
                parsed = urlparse(response.url)
                login_url = f"{parsed.scheme}://{parsed.netloc}{form_action}"
            else:
                login_url = response.url
        else:
            login_url = response.url
        
        # Verzamel alle hidden fields
        login_data = {}
        for input_field in form.find_all('input', {'type': 'hidden'}):
            name = input_field.get('name')
            value = input_field.get('value', '')
            if name:
                login_data[name] = value
        
        # Voeg credentials toe (Azure B2C gebruikt meestal 'signInName' en 'password')
        # Maar kan ook 'email' en 'password' zijn
        email_field = form.find('input', {'type': 'email'}) or form.find('input', {'name': re.compile('email|signInName|username', re.I)})
        password_field = form.find('input', {'type': 'password'})
        
        if email_field:
            email_name = email_field.get('name', 'signInName')
        else:
            email_name = 'signInName'
        
        if password_field:
            password_name = password_field.get('name', 'password')
        else:
            password_name = 'password'
        
        login_data[email_name] = config.EMAIL
        login_data[password_name] = config.PASSWORD
        
        print(f"Login form action: {login_url[:100]}...")
        print(f"Email field: {email_name}")
        print(f"Hidden fields: {list(login_data.keys())}")
        
        # Verstuur login
        response = self.session.post(login_url, data=login_data, allow_redirects=True)
        print(f"Status na login: {response.status_code}")
        print(f"Final URL: {response.url[:100]}...")
        
        return response
    
    def step3_extract_token(self, response):
        """Stap 3: Extraheer JWT token uit de response"""
        print("\n=== STAP 3: Token Extractie ===")
        
        # Zoek naar de climateconnect:// URL in de HTML
        # Het kan in een meta refresh tag staan of in JavaScript
        
        # Probeer 1: Zoek in de hele HTML naar het token pattern
        token_pattern = r'climateconnect://login\?token=([A-Za-z0-9_\-\.]+)'
        match = re.search(token_pattern, response.text)
        
        if match:
            self.token = match.group(1)
            print(f"✓ Token gevonden (eerste 50 chars): {self.token[:50]}...")
            
            # Probeer het token te decoderen
            self._decode_token()
            return True
        
        # Probeer 2: Zoek in JavaScript of meta tags
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check meta refresh
        meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            match = re.search(token_pattern, content)
            if match:
                self.token = match.group(1)
                print(f"✓ Token gevonden in meta refresh (eerste 50 chars): {self.token[:50]}...")
                self._decode_token()
                return True
        
        # Check voor error messages
        if 'error' in response.text.lower() or 'failed' in response.text.lower():
            print("⚠ Mogelijk een error in de response:")
            # Zoek naar error messages
            error_divs = soup.find_all(['div', 'span', 'p'], class_=re.compile('error|alert|danger'))
            for div in error_divs:
                print(f"  {div.get_text(strip=True)}")
        
        print("✗ Geen token gevonden in de response")
        print("\nResponse URL:", response.url)
        print("Response preview (eerste 500 chars):")
        print(response.text[:500])
        
        return False
    
    def _decode_token(self):
        """Decode het JWT token om de inhoud te zien"""
        if not self.token:
            return
        
        try:
            import base64
            
            # JWT bestaat uit 3 delen gescheiden door punten
            parts = self.token.split('.')
            if len(parts) != 3:
                print(f"⚠ Token heeft niet 3 delen: {len(parts)}")
                return
            
            # Decode de payload (deel 2)
            payload = parts[1]
            # Voeg padding toe indien nodig
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            
            print("\n📋 Token inhoud:")
            print(json.dumps(payload_data, indent=2))
            
            # Haal refresh token op indien aanwezig
            if 'session' in payload_data and 'refresh_token' in payload_data['session']:
                self.refresh_token = payload_data['session']['refresh_token']
                print(f"\n✓ Refresh token gevonden (eerste 50 chars): {self.refresh_token[:50]}...")
            
        except Exception as e:
            print(f"⚠ Fout bij decoderen token: {e}")
    
    def authenticate(self):
        """Voer de complete authenticatie flow uit"""
        print("🚀 Start authenticatie flow voor Itho Daalderop")
        print(f"Email: {config.EMAIL}")
        
        try:
            # Stap 1: Initieer SSO en haal Azure B2C URL op
            sso_url = self.step1_initiate_sso()
            if not sso_url:
                print(f"✗ SSO initiatie failed: geen SSO URL ontvangen")
                return False
            
            # Stap 2: Login via Azure B2C
            response = self.step2_login(sso_url)
            if not response or response.status_code not in [200, 302]:
                print(f"✗ Login failed: {response.status_code if response else 'geen response'}")
                return False
            
            # Stap 3: Extract token
            if self.step3_extract_token(response):
                print("\n✅ Authenticatie succesvol!")
                print(f"\nJe kunt nu de API gebruiken met deze token:")
                print(f"Authorization: Bearer {self.token}")
                return True
            else:
                print("\n✗ Authenticatie failed: geen token verkregen")
                return False
                
        except Exception as e:
            print(f"\n✗ Error tijdens authenticatie: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    auth = IthoAuthenticator()
    
    if auth.authenticate():
        print("\n" + "="*60)
        print("AUTHENTICATIE GEGEVENS")
        print("="*60)
        print(f"\nAccess Token:")
        print(auth.token)
        if auth.refresh_token:
            print(f"\nRefresh Token (eerste 100 chars):")
            print(auth.refresh_token[:100] + "...")
        print("\n" + "="*60)
        
        # Sla token op voor gebruik in API tests
        with open('token.txt', 'w') as f:
            f.write(auth.token)
        print("\n💾 Token opgeslagen in token.txt")
        
        return 0
    else:
        print("\n❌ Authenticatie mislukt")
        return 1


if __name__ == "__main__":
    exit(main())
