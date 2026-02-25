#!/usr/bin/env python3
"""
Complete test flow voor Itho Daalderop authenticatie en API.
Dit script voert eerst authenticatie uit en test daarna de API.
"""

import sys
from test_auth import IthoAuthenticator
from test_api import IthoAPI


def main():
    print("="*70)
    print(" Itho Daalderop - Complete Test Flow")
    print("="*70)
    
    # Stap 1: Authenticatie
    print("\n🔐 FASE 1: AUTHENTICATIE")
    print("-"*70)
    
    auth = IthoAuthenticator()
    if not auth.authenticate():
        print("\n❌ Authenticatie mislukt. Stop.")
        return 1
    
    # Sla token op
    with open('token.txt', 'w') as f:
        f.write(auth.token)
    print("💾 Token opgeslagen in token.txt")
    
    # Stap 2: API Tests
    print("\n\n🌐 FASE 2: API TESTS")
    print("-"*70)
    
    api = IthoAPI(token=auth.token)
    
    # Test connectiviteit
    if not api.test_connection():
        print("\n⚠ API niet bereikbaar, maar authenticatie was wel succesvol")
        return 0
    
    # Ontdek endpoints
    api.explore_endpoints()
    
    # Haal apparaten op
    devices = api.get_devices()
    
    if devices and isinstance(devices, list) and len(devices) > 0:
        print(f"\n✓ {len(devices)} apparaat(en) gevonden")
        
        # Test eerste apparaat
        first_device = devices[0]
        device_id = first_device.get('id') or first_device.get('device_id')
        
        if device_id:
            api.get_device_status(device_id)
            api.get_measurements(device_id, limit=5)
    
    print("\n" + "="*70)
    print("✅ COMPLETE TEST FLOW AFGEROND")
    print("="*70)
    print("\nJe kunt nu:")
    print("  1. De token gebruiken voor API calls (zie token.txt)")
    print("  2. De API verder verkennen met test_api.py")
    print("  3. Beginnen met de Home Assistant integratie")
    
    return 0


if __name__ == "__main__":
    exit(main())
