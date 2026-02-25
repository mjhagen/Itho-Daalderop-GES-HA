#!/usr/bin/env python3
"""
Uitgebreide API test met correcte parameters
"""

import requests
import json
import os
from datetime import datetime, timedelta

try:
    import config
except ImportError:
    print("ERROR: config.py niet gevonden!")
    exit(1)


class IthoAPIComplete:
    def __init__(self, token=None):
        self.base_url = config.API_BASE_URL
        self.token = token
        self.session = requests.Session()
        self.serial_number = None
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
    
    def load_token_from_file(self):
        """Laad token uit token.txt"""
        if os.path.exists('token.txt'):
            with open('token.txt', 'r') as f:
                self.token = f.read().strip()
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                })
            print(f"✓ Token geladen uit token.txt")
            
            # Probeer serial number uit JWT te halen
            self._extract_serial_from_token()
            return True
        return False
    
    def _extract_serial_from_token(self):
        """Probeer serial number uit JWT token te halen"""
        try:
            import base64
            parts = self.token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.urlsafe_b64decode(payload)
                payload_data = json.loads(decoded)
                # Zoek naar serial number in payload
                if 'device' in payload_data:
                    self.serial_number = payload_data['device'].get('serial_number')
                print(f"Token payload keys: {list(payload_data.keys())}")
        except Exception as e:
            print(f"Kon serial number niet uit token halen: {e}")
    
    def get_ean_code(self):
        """Haal EAN code op (geen parameters nodig)"""
        print("\n=== EAN Code ===")
        
        try:
            response = self.session.get(f"{self.base_url}/GetEanCode")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ EAN code opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"✗ Fout: {e}")
            return None
    
    def set_serial_number(self, serial):
        """Stel serial number in voor tests"""
        self.serial_number = serial
        print(f"✓ Serial number ingesteld: {serial}")
    
    def get_device_status(self):
        """Haal apparaat status op"""
        if not self.serial_number:
            print("⚠ Geen serial number! Gebruik set_serial_number() eerst.")
            return None
        
        print("\n=== Apparaat Status ===")
        
        try:
            params = {'serialNumber': self.serial_number}
            response = self.session.get(f"{self.base_url}/GetDeviceStatus", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Apparaat status opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"✗ Fout: {e}")
            return None
    
    def get_device_mode(self):
        """Haal apparaat mode op"""
        if not self.serial_number:
            print("⚠ Geen serial number!")
            return None
        
        print("\n=== Apparaat Mode ===")
        
        try:
            params = {'serialNumber': self.serial_number}
            response = self.session.get(f"{self.base_url}/GetDeviceMode", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Apparaat mode opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"✗ Fout: {e}")
            return None
    
    def get_energy_consumption(self, days=7, interval='Day'):
        """Haal energie verbruik op"""
        if not self.serial_number:
            print("⚠ Geen serial number!")
            return None
        
        print(f"\n=== Energie Verbruik (laatste {days} dagen) ===")
        
        try:
            # Bereken timestamps in milliseconds (epoch)
            now = datetime.now()
            start = now - timedelta(days=days)
            
            start_ms = int(start.timestamp() * 1000)
            end_ms = int(now.timestamp() * 1000)
            
            params = {
                'serialNumber': self.serial_number,
                'startDate': start_ms,
                'endDate': end_ms,
                'interval': interval,
                'includePreviousPeriod': False,
                'refreshCache': False
            }
            
            response = self.session.get(f"{self.base_url}/GetEnergyConsumption", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Energie verbruik opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"⚠ Fout: {e}")
            return None
    
    def get_smart_grid_status(self):
        """Haal SmartGrid status op"""
        if not self.serial_number:
            print("⚠ Geen serial number!")
            return None
        
        print("\n=== SmartGrid Status ===")
        
        try:
            params = {'serialNumber': self.serial_number}
            response = self.session.get(f"{self.base_url}/GetSmartGridStatus", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ SmartGrid status opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"✗ Fout: {e}")
            return None
    
    def get_pv_settings(self):
        """Haal PV instellingen op"""
        if not self.serial_number:
            print("⚠ Geen serial number!")
            return None
        
        print("\n=== PV Instellingen ===")
        
        try:
            params = {'serialNumber': self.serial_number}
            response = self.session.get(f"{self.base_url}/GetDevicePVSettings", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ PV instellingen opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"✗ Fout: {e}")
            return None
    
    def get_fault(self):
        """Haal laatste fout op"""
        if not self.serial_number:
            print("⚠ Geen serial number!")
            return None
        
        print("\n=== Laatste Fout ===")
        
        try:
            params = {'serialNumber': self.serial_number}
            response = self.session.get(f"{self.base_url}/GetFault", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Fout info opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"✗ Fout: {e}")
            return None
    
    def get_fault_history(self):
        """Haal fout geschiedenis op"""
        if not self.serial_number:
            print("⚠ Geen serial number!")
            return None
        
        print("\n=== Fout Geschiedenis ===")
        
        try:
            params = {'serialNumber': self.serial_number}
            response = self.session.get(f"{self.base_url}/GetFaultHistory", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Fout geschiedenis opgehaald")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
        except Exception as e:
            print(f"✗ Fout: {e}")
            return None


def main():
    print("="*70)
    print(" Itho Daalderop API - Complete Tests")
    print("="*70)
    
    api = IthoAPIComplete()
    
    # Laad token
    if not api.load_token_from_file():
        print("\n⚠ Geen token gevonden!")
        print("Run eerst 'python test_auth_selenium.py' om in te loggen.")
        return 1
    
    # Probeer EAN code op te halen (geen serial number nodig)
    api.get_ean_code()
    
    # Vraag gebruiker om serial number
    print("\n" + "-"*70)
    print("💡 TIP: Kijk op je boiler of in de app voor het serienummer")
    print("-"*70)
    serial = input("\nVoer het serienummer van je boiler in (of laat leeg om over te slaan): ").strip()
    
    if serial:
        api.set_serial_number(serial)
        
        # Test alle endpoints
        api.get_device_status()
        api.get_device_mode()
        api.get_pv_settings()
        api.get_smart_grid_status()
        api.get_energy_consumption(days=7)
        api.get_fault()
        api.get_fault_history()
        
        print("\n" + "="*70)
        print("✅ ALLE API TESTS VOLTOOID")
        print("="*70)
        print("\n📊 Je kunt nu beginnen met de Home Assistant integratie!")
    else:
        print("\n⚠ Zonder serienummer kunnen we alleen EAN code ophalen.")
        print("Voer het script opnieuw uit met een serienummer voor volledige tests.")
    
    return 0


if __name__ == "__main__":
    exit(main())
