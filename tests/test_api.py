#!/usr/bin/env python3
"""
Test script voor Itho Daalderop API calls.
Dit script test de API endpoints van wifi-api.id-c.net
"""

import requests
import json
import os
from datetime import datetime

try:
    import config
except ImportError:
    print("ERROR: config.py niet gevonden!")
    print("Kopieer config.example.py naar config.py en vul je credentials in.")
    exit(1)


class IthoAPI:
    def __init__(self, token=None):
        self.base_url = config.API_BASE_URL
        self.token = token
        self.session = requests.Session()
        
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
            return True
        return False
    
    def test_connection(self):
        """Test basis connectiviteit met de API"""
        print("\n=== Test: Basis Connectiviteit ===")
        
        try:
            # Probeer de swagger UI te bereiken (zonder auth)
            response = requests.get(f"{config.API_BASE_URL}/swagger/ui", timeout=10)
            print(f"Swagger UI Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ API server is bereikbaar")
                return True
            else:
                print("⚠ API server geeft onverwachte status")
                return False
                
        except Exception as e:
            print(f"✗ Fout bij verbinden met API: {e}")
            return False
    
    def get_devices(self):
        """Haal apparaat status op"""
        print("\n=== Test: Apparaat Status ===")
        
        try:
            response = self.session.get(f"{self.base_url}/GetDeviceStatus")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Apparaat status opgehaald")
                print("\nApparaat details:")
                print(json.dumps(data, indent=2))
                return data
            elif response.status_code == 401:
                print("✗ Unauthorized - Token mogelijk verlopen of ongeldig")
            elif response.status_code == 400:
                print("⚠ Bad Request")
                print(f"Response: {response.text}")
            else:
                print(f"⚠ Onverwachte status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
            
            return None
            
        except Exception as e:
            print(f"✗ Fout bij ophalen apparaat status: {e}")
            return None
    
    def get_device_mode(self):
        """Haal apparaat mode op"""
        print("\n=== Test: Apparaat Mode ===")
        
        try:
            response = self.session.get(f"{self.base_url}/GetDeviceMode")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Apparaat mode opgehaald")
                print("\nMode details:")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
            
            return None
            
        except Exception as e:
            print(f"✗ Fout bij ophalen mode: {e}")
            return None
    
    def get_energy_consumption(self):
        """Haal energie verbruik op"""
        print("\n=== Test: Energie Verbruik ===")
        
        try:
            response = self.session.get(f"{self.base_url}/GetEnergyConsumption")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Energie verbruik opgehaald")
                print("\nVerbruik:")
                print(json.dumps(data, indent=2))
                return data
            else:
                print(f"⚠ Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
            
            return None
            
        except Exception as e:
            print(f"✗ Fout bij ophalen verbruik: {e}")
            return None
    
    def explore_endpoints(self):
        """Probeer verschillende endpoints te ontdekken"""
        print("\n=== Test: Endpoint Discovery ===")
        
        # Lijst van beschikbare endpoints volgens Swagger
        endpoints = [
            '/GetDeviceStatus',
            '/GetDeviceMode',
            '/GetDevicePVSettings',
            '/GetEnergyConsumption',
            '/GetSmartGridStatus',
            '/GetEanCode',
            '/GetFault',
            '/GetFaultHistory',
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=5)
                status = response.status_code
                results[endpoint] = status
                
                if status == 200:
                    print(f"✓ {endpoint}: {status} (OK)")
                    try:
                        data = response.json()
                        print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        pass
                elif status == 401:
                    print(f"⚠ {endpoint}: {status} (Unauthorized)")
                elif status == 404:
                    print(f"  {endpoint}: {status} (Not Found)")
                elif status == 400:
                    print(f"⚠ {endpoint}: {status} (Bad Request - mogelijk parameters benodigd)")
                else:
                    print(f"  {endpoint}: {status}")
                    
            except Exception as e:
                print(f"✗ {endpoint}: Error ({e})")
                results[endpoint] = f"Error: {e}"
        
        return results


def main():
    print("🧪 Itho Daalderop API Tests")
    print("="*60)
    
    api = IthoAPI()
    
    # Probeer token te laden
    if not api.load_token_from_file():
        print("\n⚠ Geen token gevonden!")
        print("Run eerst 'python test_auth_selenium.py' om in te loggen en een token te krijgen.")
        
        # Probeer wel de basis connectiviteit te testen
        api.test_connection()
        return 1
    
    # Test 1: Basis connectiviteit
    if not api.test_connection():
        print("\n⚠ API server niet bereikbaar")
        return 1
    
    # Test 2: Endpoint discovery
    api.explore_endpoints()
    
    # Test 3: Haal apparaat data op
    device_status = api.get_devices()
    
    if device_status:
        # Apparaat status succesvol opgehaald
        api.get_device_mode()
        api.get_energy_consumption()
    
    print("\n" + "="*60)
    print("✅ API tests voltooid")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
