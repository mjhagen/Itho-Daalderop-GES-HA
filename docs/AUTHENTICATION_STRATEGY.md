# Home Assistant Integratie - Authenticatie Strategie

## ❌ Waarom Selenium NIET werkt in HACS

1. **ChromeDriver dependency** - Niet beschikbaar in HA containers
2. **Resource intensief** - Browser kost te veel geheugen
3. **Azure B2C = JavaScript SPA** - Requests-only werkt niet
4. **HACS best practices** - Alleen lightweight Python code

---

## ✅ AANBEVOLEN: Refresh Token Strategie

### Concept

De JWT token die we krijgen bevat een **refresh token** die 1 jaar geldig is:

```json
{
  "session": {
    "state": "...",
    "application_id": "2da3d256-ca0a-4041-84ba-93856efceef9",
    "issued_at": "2026-02-25T11:29:00.000+01:00",
    "expires_at": "2027-02-25T11:29:00.000+01:00",  // 1 JAAR!
    "refresh_token": "eyJraWQiOiJjcGltY29yZ..."      // Refresh token
  },
  "user": {
    "name": "Itho Daalderop",
    "mailaddress": "..."
  }
}
```

### Home Assistant Config Flow

#### Optie A: **Eenvoudigste** (Recommended)

1. **Gebruiker installeert HACS integratie**
2. **Config flow toont instructies:**
   ```
   Stap 1: Download login script
   Stap 2: Run: python itho_login.py
   Stap 3: Kopieer de refresh token
   Stap 4: Plak hieronder
   ```
3. **Gebruiker plakt refresh token** in HA
4. **Component slaat refresh token op** (encrypted storage)
5. **Component vraagt nieuwe access tokens** wanneer nodig

**Voordelen:**
- ✅ Geen complexe dependencies
- ✅ Eenmalige setup
- ✅ Token 1 jaar geldig
- ✅ Automatische refresh

**Nadelen:**
- ⚠️ Gebruiker moet 1x een Python script draaien
- ⚠️ Niet plug-and-play

---

#### Optie B: **Gebruiksvriendelijker** (Complex)

1. **Config flow toont link:**
   ```
   Klik hier om in te loggen:
   https://itho-tussenlaag.bettywebblocks.com/sso/initiate?...
   ```
2. **Gebruiker logt in via browser**
3. **Browser wordt omgeleid naar:** `climateconnect://login?token=...`
4. **Gebruiker kopieert de volledige URL**
5. **Plakt URL in HA**
6. **Component extraheert token** uit URL

**Voordelen:**
- ✅ Geen Python script nodig
- ✅ Werkt op elk platform
- ✅ Gebruiksvriendelijk

**Nadelen:**
- ⚠️ Gebruiker moet URL kopiëren uit console/error
- ⚠️ Technisch voor gemiddelde gebruiker

---

#### Optie C: **Volledig Automatisch** (Meest Complex)

1. **HA start externe browser authorize flow:**
   ```python
   # In config_flow.py
   return self.async_external_step(
       step_id="authorize",
       url="https://itho-tussenlaag.bettywebblocks.com/sso/initiate?..."
   )
   ```
2. **Gebruiker logt in via systeem browser**
3. **HA start lokale callback server** op poort (bijv. 8123)
4. **Modify redirect URI** om naar `http://localhost:8123/api/itho_callback` te wijzen
5. **HA vangt token op**

**Voordelen:**
- ✅ Volledig geïntegreerd in HA
- ✅ Beste gebruikerservaring
- ✅ Geen copy-paste nodig

**Nadelen:**
- ⚠️ Vereist dat redirect URI kan worden aangepast
- ⚠️ API moet localhost callbacks toestaan
- ⚠️ Complexe implementatie

---

## 🎯 Aanbevolen Implementatie: Optie A + B Hybrid

### Setup flow:

```
┌─────────────────────────────────────────────┐
│  Home Assistant Config Flow                 │
├─────────────────────────────────────────────┤
│                                             │
│  Stap 1: Kies authenticatie methode        │
│                                             │
│  ○ Automatisch (kopieer URL)               │
│  ○ Handmatig (gebruik Python script)       │
│                                             │
└─────────────────────────────────────────────┘
```

### Automatisch (Optie B):

```
┌─────────────────────────────────────────────┐
│  Inloggen bij Itho Daalderop               │
├─────────────────────────────────────────────┤
│                                             │
│  1. Klik op onderstaande link:             │
│                                             │
│     [Login bij Itho Daalderop] 🔗          │
│                                             │
│  2. Log in met je Itho account             │
│                                             │
│  3. Je browser krijgt een error:           │
│     "Failed to launch climateconnect://"    │
│                                             │
│  4. Kopieer de VOLLEDIGE URL uit de        │
│     browser console of adresbalk            │
│                                             │
│  5. Plak hieronder:                         │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │ climateconnect://login?token=...   │    │
│  └────────────────────────────────────┘    │
│                                             │
│              [Opslaan]                      │
└─────────────────────────────────────────────┘
```

### Handmatig (Optie A):

```
┌─────────────────────────────────────────────┐
│  Inloggen met Python Script                │
├─────────────────────────────────────────────┤
│                                             │
│  Download en run het login script:         │
│                                             │
│  1. Download:                               │
│     wget https://raw.githubusercontent.     │
│     com/.../itho_login.py                   │
│                                             │
│  2. Installeer dependencies:               │
│     pip install selenium requests           │
│                                             │
│  3. Run script:                             │
│     python itho_login.py                    │
│                                             │
│  4. Kopieer de refresh token en plak        │
│     hieronder:                              │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │ eyJraWQiOiJjcGltY29yZV8wOT...     │    │
│  └────────────────────────────────────┘    │
│                                             │
│              [Opslaan]                      │
└─────────────────────────────────────────────┘
```

---

## 📝 Implementatie Details

### 1. Token Storage (encrypted)

```python
# In __init__.py
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.storage import Store

class IthoTokenStore:
    """Veilig opslaan van tokens"""
    
    def __init__(self, hass):
        self.store = Store(hass, version=1, key="itho_daalderop_tokens")
    
    async def async_save_token(self, token_data):
        """Sla token encrypted op"""
        await self.store.async_save({
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': token_data['expires_at']
        })
    
    async def async_load_token(self):
        """Laad token"""
        return await self.store.async_load()
```

### 2. Token Refresh Logic

```python
# In api.py
class IthoAPI:
    """API client met automatische token refresh"""
    
    async def async_refresh_token_if_needed(self):
        """Check en refresh token indien nodig"""
        token_data = await self.token_store.async_load_token()
        
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        
        # Refresh 1 uur voor expiry
        if expires_at - timedelta(hours=1) < datetime.now():
            new_token = await self._async_refresh_token(
                token_data['refresh_token']
            )
            await self.token_store.async_save_token(new_token)
            return new_token
        
        return token_data
    
    async def _async_refresh_token(self, refresh_token):
        """Refresh de access token"""
        # TODO: Implementeer refresh endpoint
        # Dit moet onderzocht worden in de API documentatie
        pass
```

### 3. Config Flow

```python
# In config_flow.py
class IthoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor Itho Daalderop"""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Kies authenticatie methode"""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("auth_method"): vol.In({
                        "url": "Automatisch (kopieer URL)",
                        "script": "Handmatig (Python script)"
                    })
                })
            )
        
        if user_input["auth_method"] == "url":
            return await self.async_step_auth_url()
        else:
            return await self.async_step_auth_script()
    
    async def async_step_auth_url(self, user_input=None):
        """Authenticatie via URL"""
        if user_input is None:
            # Genereer SSO URL
            sso_url = await self._async_get_sso_url()
            
            return self.async_show_form(
                step_id="auth_url",
                data_schema=vol.Schema({
                    vol.Required("callback_url"): str,
                }),
                description_placeholders={
                    "login_url": sso_url
                }
            )
        
        # Extract token from URL
        token = self._extract_token_from_url(user_input["callback_url"])
        
        # Validate token
        if await self._async_validate_token(token):
            return self.async_create_entry(
                title="Itho Daalderop Boiler",
                data={"token": token}
            )
        
        return self.async_abort(reason="invalid_token")
```

---

## ⚡ Snelle Start voor Gebruikers

### Voor gemiddelde gebruiker (Optie B):
1. Installeer integratie via HACS
2. Ga naar Instellingen → Integraties → Toevoegen
3. Kies "Itho Daalderop"
4. Klik op login link
5. Log in
6. Kopieer URL uit browser console
7. Plak in HA
8. Klaar! ✅

### Voor gevorderde gebruiker (Optie A):
1. Download login script
2. Run: `python itho_login.py`
3. Kopieer refresh token
4. Plak in HA config flow
5. Klaar! ✅

---

## 🔄 Token Lifecycle

```
Initial Setup (1x)
    ↓
Login via Browser/Script
    ↓
Verkrijg JWT Token (1 jaar geldig)
    ↓
Extract Refresh Token
    ↓
Opslaan in HA (encrypted)
    ↓
    ├─→ Elke API call:
    │   ├─ Check token expiry
    │   ├─ Refresh indien < 1 uur geldig
    │   └─ Gebruik access token
    │
    └─→ Na 1 jaar:
        └─ Automatische refresh met refresh token
            (of opnieuw inloggen als refresh faalt)
```

---

## ✅ Conclusie

**Beste aanpak voor HACS:**
- Hybride Optie A + B
- Gebruiker kiest zelf: automatisch (URL) of handmatig (script)
- Refresh token strategie voor lange termijn
- Geen Selenium in HA zelf nodig
- Token wordt veilig opgeslagen
- Automatische refresh

**Next steps:**
1. Onderzoek refresh token endpoint in API
2. Implementeer config flow met beide opties
3. Maak standalone login script voor distributie
4. Test token refresh mechanisme
5. Documentatie schrijven
