# Config Flow Strategie - Voor HACS Integratie

## ✅ BESTE OPLOSSING: Gebruiker Doorsturen

Je hebt helemaal gelijk - dit is **veel handiger**! Home Assistant heeft hier ingebouwde ondersteuning voor.

---

## 📱 Gebruikerservaring Flow

### Stap 1: Integratie Toevoegen
```
┌─────────────────────────────────────────┐
│  Itho Daalderop Boiler Setup           │
├─────────────────────────────────────────┤
│                                         │
│  Voer het serienummer van je boiler    │
│  in. Dit vind je op het typeplaatje    │
│  of in de Itho app.                    │
│                                         │
│  Serienummer:                           │
│  ┌───────────────────────────────────┐ │
│  │ <SERIAL_NUMBER>                  │ │
│  └───────────────────────────────────┘ │
│                                         │
│              [Volgende]                 │
└─────────────────────────────────────────┘
```

### Stap 2: Browser Opent Automatisch
```
Home Assistant opent automatisch je browser en stuurt je door naar:
https://climateforlifeportal.b2clogin.com/...

┌─────────────────────────────────────────┐
│  🌐 Itho Daalderop Login               │
├─────────────────────────────────────────┤
│                                         │
│  Email:                                 │
│  ┌───────────────────────────────────┐ │
│  │ jouw@email.com                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│  Wachtwoord:                            │
│  ┌───────────────────────────────────┐ │
│  │ ************                      │ │
│  └───────────────────────────────────┘ │
│                                         │
│              [Inloggen]                 │
└─────────────────────────────────────────┘
```

### Stap 3: Browser Error (Dit is Normaal!)
```
❌ Browser toont error:

Failed to launch 'climateconnect://login?token=eyJ0eXAiOiJKV1Qi...'
because the scheme does not have a registered handler.

✅ DIT IS GOED! Dit betekent dat de login is gelukt!
```

### Stap 4: Kopieer URL
```
Je ziet deze error in de Console (F12) of soms in de adresbalk.

De URL ziet er zo uit:
climateconnect://login?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

Kopieer de VOLLEDIGE URL!
```

### Stap 5: Plak in Home Assistant
```
┌─────────────────────────────────────────┐
│  Authenticatie Afronden                 │
├─────────────────────────────────────────┤
│                                         │
│  Na het inloggen krijg je een          │
│  foutmelding. Dit is normaal!           │
│                                         │
│  1. Open browser console (F12)         │
│  2. Zoek de regel met:                 │
│     "Failed to launch                   │
│     'climateconnect://login?token='"    │
│  3. Kopieer de volledige URL           │
│  4. Plak hieronder:                     │
│                                         │
│  Callback URL:                          │
│  ┌───────────────────────────────────┐ │
│  │ climateconnect://login?token=eyJ  │ │
│  │ 0eXAiOiJKV1QiLCJhbGciOiJIUzI1N...│ │
│  └───────────────────────────────────┘ │
│                                         │
│  💡 Tip: Soms staat de URL ook in de   │
│     adresbalk van je browser            │
│                                         │
│              [Opslaan]                  │
└─────────────────────────────────────────┘
```

### Stap 6: Klaar! ✅
```
┌─────────────────────────────────────────┐
│  ✅ Configuratie Voltooid               │
├─────────────────────────────────────────┤
│                                         │
│  Je Itho Daalderop boiler is succesvol │
│  toegevoegd aan Home Assistant!         │
│                                         │
│  Boiler: <SERIAL_NUMBER>              │
│  Gebruiker: jouw@email.com             │
│  Token geldig tot: 2027-02-25          │
│                                         │
│  Je kunt nu je boiler bedienen via HA! │
│                                         │
│              [Sluiten]                  │
└─────────────────────────────────────────┘
```

---

## 💻 Technische Implementatie

### Config Flow Code (voorbeeld gemaakt)

Zie: `example_config_flow.py`

**Belangrijkste functies:**

1. **`async_external_step()`** - Opent browser met login URL
2. **`async_step_auth_callback()`** - Vangt callback op
3. **Token extractie** uit `climateconnect://login?token=...`
4. **Token validatie** met test API call
5. **Veilige opslag** van refresh token

### Home Assistant Helper

```python
# In de config flow
return self.async_external_step(
    step_id="auth_callback",
    url="https://climateforlifeportal.b2clogin.com/..."
)
```

Dit opent automatisch de standaard browser van de gebruiker!

---

## 🎨 Gebruikerservaring Verbeteringen

### Optie 1: Duidelijke Instructies (Aanbevolen)
✅ Toon screenshots in de documentatie  
✅ Animeerde GIF die de stappen laat zien  
✅ Video tutorial op GitHub  
✅ Duidelijke foutmeldingen met hulp

### Optie 2: Browser Extension (Advanced)
Een browser extensie die automatisch de URL vangt en naar HA stuurt.

### Optie 3: QR Code (Mobile)
Voor mobiele gebruikers: toon QR code die naar login leidt.

---

## 📋 Vergelijking Methodes

| Methode | Gebruikerservaring | Technische Complexiteit | Betrouwbaarheid |
|---------|-------------------|------------------------|-----------------|
| **🌐 Browser Redirect** | ⭐⭐⭐⭐⭐ Beste | ⭐⭐⭐ Midden | ⭐⭐⭐⭐⭐ |
| Python Script | ⭐⭐ Matig | ⭐⭐⭐⭐ Moeilijk | ⭐⭐⭐⭐ |
| Selenium in HA | ❌ Onmogelijk | ❌ Onmogelijk | ❌ |
| Requests-only | ❌ Werkt niet | ⭐⭐⭐⭐⭐ | ❌ |

**Winner:** 🌐 **Browser Redirect met async_external_step**

---

## ✅ Voordelen van Deze Methode

1. **Gebruiksvriendelijk**
   - Geen extra software nodig
   - Werkt op elk platform (Windows/Mac/Linux)
   - Browser opent automatisch
   - Duidelijke instructies

2. **Betrouwbaar**
   - Token is 1 jaar geldig
   - Automatische refresh
   - Veilige opslag in HA

3. **Onderhoudbaar**
   - Geen dependencies buiten Python
   - Standaard HA patterns
   - Makkelijk te debuggen

4. **HACS Compliant**
   - Geen extra binaries nodig
   - Pure Python
   - Best practices

---

## 🔧 Implementatie Details

### 1. Strings File (translations/en.json)

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Itho Daalderop Boiler Setup",
        "description": "Voer het serienummer van je boiler in.\n\n{help_text}",
        "data": {
          "serial_number": "Serial Number"
        }
      },
      "auth_callback": {
        "title": "Complete Authentication",
        "description": "{instructions}",
        "data": {
          "callback_url": "Callback URL"
        }
      }
    },
    "error": {
      "invalid_serial": "Invalid serial number",
      "invalid_token": "Token is invalid or expired",
      "invalid_url": "The URL is not correct",
      "cannot_connect": "Cannot connect to Itho servers"
    }
  }
}
```

### 2. Manifest (manifest.json)

```json
{
  "domain": "itho_daalderop",
  "name": "Itho Daalderop",
  "codeowners": ["@username"],
  "config_flow": true,
  "documentation": "https://github.com/username/itho-daalderop",
  "iot_class": "cloud_polling",
  "issue_tracker": "https://github.com/username/itho-daalderop/issues",
  "requirements": [],
  "version": "1.0.0"
}
```

### 3. Token Refresh (api.py)

```python
async def async_refresh_access_token(self):
    """Refresh access token using refresh token."""
    # TODO: Onderzoek refresh endpoint
    # Waarschijnlijk: POST naar token endpoint met refresh_token
    pass
```

---

## 📸 Screenshots voor Documentatie

### Screenshot 1: Browser Console
```
[!] Failed to launch 'climateconnect://login?token=...'
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Kopieer deze hele regel!
```

### Screenshot 2: Browser Adresbalk (alternatief)
```
🔒 https://confirmed?...  ← Soms hier
```

---

## 🎯 Next Steps

1. ✅ Config flow gemaakt (`example_config_flow.py`)
2. ⏭️ Token refresh mechanisme implementeren
3. ⏭️ Volledige HACS component structuur opzetten
4. ⏭️ Screenshots en GIFs maken voor documentatie
5. ⏭️ Testing met echte gebruikers

---

## 💡 Extra Tips voor Gebruikers

### Troubleshooting Guide

**Q: Ik zie geen foutmelding in de browser**
A: Open de Console met F12 (of Cmd+Option+I op Mac)

**Q: De URL is te lang om te kopiëren**
A: Gebruik Ctrl+A om alles te selecteren, dan Ctrl+C

**Q: Ik zie wel een error maar geen URL**
A: Kijk in het "Console" tabblad, niet in "Elements" of "Network"

**Q: Mijn token werkt niet**
A: Zorg dat je de VOLLEDIGE URL kopieert, inclusief "climateconnect://login?token="

---

## ✨ Conclusie

De **browser redirect methode** is de beste oplossing:

✅ Gebruiksvriendelijk  
✅ Geen extra software  
✅ Werkt op alle platforms  
✅ HACS compliant  
✅ Betrouwbaar  
✅ Onderhoudbaar  

**Ready to implement!** 🚀
