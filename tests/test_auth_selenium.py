#!/usr/bin/env python3
"""
Test script voor Itho Daalderop authenticatie met Selenium.
Dit script gebruikt een headless browser om de Azure B2C login uit te voeren.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json
import base64
from urllib.parse import urlencode

try:
    import config
except ImportError:
    print("ERROR: config.py niet gevonden!")
    print("Kopieer config.example.py naar config.py en vul je credentials in.")
    exit(1)


class IthoAuthenticatorSelenium:
    def __init__(self, headless=True):
        self.token = None
        self.refresh_token = None
        self.headless = headless
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        print("🌐 Chrome WebDriver aan het opstarten...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Maak driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
        print("✓ WebDriver gereed")
    
    def cleanup(self):
        """Sluit driver"""
        if self.driver:
            self.driver.quit()
    
    def authenticate(self):
        """Voer de complete authenticatie flow uit met Selenium"""
        print("🚀 Start authenticatie flow voor Itho Daalderop (Selenium)")
        print(f"Email: {config.EMAIL}")
        
        try:
            # Setup WebDriver
            self.setup_driver()
            
            # Stap 1: Haal SSO URL op
            print("\n=== STAP 1: SSO URL ophalen ===")
            params = {
                'redirect': config.REDIRECT_URI,
                'application_id': config.APPLICATION_ID
            }
            
            import requests
            url = f"{config.SSO_INITIATE_URL}?{urlencode(params)}"
            response = requests.get(url)
            data = response.json()
            
            if 'sso' not in data:
                print("✗ Geen SSO URL ontvangen")
                return False
            
            sso_url = data['sso']
            print(f"✓ SSO URL ontvangen: {sso_url[:100]}...")
            
            # Stap 2: Open Azure B2C login pagina
            print("\n=== STAP 2: Azure B2C Login Pagina ===")
            self.driver.get(sso_url)
            print(f"✓ Pagina geladen: {self.driver.title}")
            
            # Wacht tot de pagina geladen is
            time.sleep(2)
            
            # Zoek naar email/username veld - Azure B2C gebruikt verschillende mogelijke IDs
            print("\n=== STAP 3: Credentials Invullen ===")
            
            email_field = None
            possible_email_selectors = [
                (By.ID, 'logonIdentifier'),
                (By.ID, 'signInName'),
                (By.ID, 'email'),
                (By.NAME, 'logonIdentifier'),
                (By.NAME, 'signInName'),
                (By.CSS_SELECTOR, 'input[type="email"]'),
                (By.CSS_SELECTOR, 'input[placeholder*="email"]'),
            ]
            
            for by, selector in possible_email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    print(f"✓ Email veld gevonden: {selector}")
                    break
                except:
                    continue
            
            if not email_field:
                print("✗ Geen email veld gevonden")
                print("Pagina HTML:")
                print(self.driver.page_source[:2000])
                return False
            
            # Vul email in
            email_field.clear()
            email_field.send_keys(config.EMAIL)
            print(f"✓ Email ingevuld")
            
            # Zoek password veld
            password_field = None
            possible_password_selectors = [
                (By.ID, 'password'),
                (By.NAME, 'password'),
                (By.CSS_SELECTOR, 'input[type="password"]'),
            ]
            
            for by, selector in possible_password_selectors:
                try:
                    password_field = self.driver.find_element(by, selector)
                    print(f"✓ Password veld gevonden: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                print("✗ Geen password veld gevonden")
                return False
            
            # Vul password in
            password_field.clear()
            password_field.send_keys(config.PASSWORD)
            print(f"✓ Password ingevuld")
            
            # Zoek en klik submit button
            print("\n=== STAP 4: Inloggen ===")
            
            submit_button = None
            possible_submit_selectors = [
                (By.ID, 'next'),
                (By.ID, 'continue'),
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.CSS_SELECTOR, 'button#next'),
                (By.CSS_SELECTOR, 'input[type="submit"]'),
            ]
            
            for by, selector in possible_submit_selectors:
                try:
                    submit_button = self.driver.find_element(by, selector)
                    print(f"✓ Submit button gevonden: {selector}")
                    break
                except:
                    continue
            
            if not submit_button:
                print("✗ Geen submit button gevonden")
                return False
            
            # Klik submit
            submit_button.click()
            print("✓ Submit button geklikt")
            
            # Wacht op redirect
            print("\n=== STAP 5: Token Extractie ===")
            time.sleep(3)
            
            # Check for errors
            try:
                error_element = self.driver.find_element(By.CSS_SELECTOR, '.error, .alert-danger, [role="alert"]')
                if error_element and error_element.text:
                    print(f"⚠ Error op pagina: {error_element.text}")
            except:
                pass
            
            # De token zou moeten verschijnen in een failed protocol handler
            # Check browser console logs
            print(f"Current URL: {self.driver.current_url}")
            
            # Wacht op volgende redirect/pagina
            time.sleep(3)
            
            # Check browser logs voor de climateconnect:// URL
            logs = []
            try:
                logs = self.driver.get_log('browser')
                for log in logs:
                    message = log.get('message', '')
                    if 'climateconnect' in message.lower():
                        print(f"Browser log: {message}")
                        # Extract token from log message
                        token_pattern = r'climateconnect://login\?token=([A-Za-z0-9_\-\.]+)'
                        match = re.search(token_pattern, message)
                        if match:
                            self.token = match.group(1)
                            print(f"✓ Token gevonden in browser log!")
                            self._decode_token()
                            return True
            except Exception as e:
                print(f"Kon browser logs niet ophalen: {e}")
            
            # Zoek in de paginabron naar de token
            page_source = self.driver.page_source
            token_pattern = r'climateconnect://login\?token=([A-Za-z0-9_\-\.]+)'
            match = re.search(token_pattern, page_source)
            
            if match:
                self.token = match.group(1)
                print(f"✓ Token gevonden in pagina (eerste 50 chars): {self.token[:50]}...")
                self._decode_token()
                return True
            
            # Check voor meta refresh tag
            try:
                meta_refresh = self.driver.find_element(By.CSS_SELECTOR, 'meta[http-equiv="refresh"]')
                content = meta_refresh.get_attribute('content')
                if content:
                    match = re.search(token_pattern, content)
                    if match:
                        self.token = match.group(1)
                        print(f"✓ Token gevonden in meta refresh!")
                        self._decode_token()
                        return True
            except:
                pass
            
            # Wacht nog langer en controleer opnieuw
            print("⏳ Wacht op volgende redirect...")
            time.sleep(5)
            
            # Check opnieuw
            page_source = self.driver.page_source
            print(f"URL na wachten: {self.driver.current_url}")
            
            # Haal browser console logs op
            try:
                logs = self.driver.get_log('browser')
                print(f"\n📝 Browser Console Logs ({len(logs)} entries):")
                for log in logs:
                    message = log.get('message', '')
                    print(f"  {message}")
                    if 'climateconnect' in message.lower():
                        token_pattern = r'climateconnect://login\?token=([A-Za-z0-9_\-\.]+)'
                        match = re.search(token_pattern, message)
                        if match:
                            self.token = match.group(1)
                            print(f"✓ Token gevonden in browser log!")
                            self._decode_token()
                            return True
            except Exception as e:
                print(f"Browser logs niet beschikbaar: {e}")
            
            # Laatste poging: zoek in HTML
            match = re.search(token_pattern, page_source)
            if match:
                self.token = match.group(1)
                print(f"✓ Token gevonden (eerste 50 chars): {self.token[:50]}...")
                self._decode_token()
                return True
            
            print("✗ Geen JWT token gevonden")
            print(f"Final URL: {self.driver.current_url}")
            print("\nPagina preview (eerste 2000 chars):")
            print(page_source[:2000])
            
            return False
            
        except Exception as e:
            print(f"\n✗ Error tijdens authenticatie: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.cleanup()
    
    def _decode_token(self):
        """Decode het JWT token om de inhoud te zien"""
        if not self.token:
            return
        
        try:
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


def main():
    print("Wil je de browser zien tijdens het inloggen? (j/n): ", end="")
    headless_input = input().strip().lower()
    headless = headless_input != 'j'
    
    auth = IthoAuthenticatorSelenium(headless=headless)
    
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
