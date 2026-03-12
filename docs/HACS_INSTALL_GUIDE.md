# HACS Test Installatie Gids

Deze gids legt uit hoe je de Itho Daalderop integratie als test kunt toevoegen aan HACS.

## Methode 1: Via GitHub (Aanbevolen)

### Stap 1: Repository op GitHub zetten

1. Maak een **nieuw GitHub repository** aan (bijv. `itho-daalderop-ha`)
2. Upload de volgende bestanden:
   ```
   /custom_components/itho_daalderop/
   ├── __init__.py
   ├── api.py
   ├── config_flow.py
   ├── const.py
   ├── manifest.json
   ├── sensor.py
   ├── strings.json
   ├── water_heater.py
   └── translations/
       └── nl.json
   
   /hacs.json
   /INTEGRATION_README.md (hernoem naar README.md)
   ```

3. **Commit en push** naar GitHub

### Stap 2: Toevoegen aan HACS

1. Open **Home Assistant** 
2. Ga naar **HACS** → **Integrations**
3. Klik rechtsbovenin op **︙** (drie puntjes)
4. Selecteer **Custom repositories**
5. Voeg toe:
   - **Repository**: `https://github.com/JOUWUSERNAME/itho-daalderop-ha`
   - **Category**: `Integration`
6. Klik op **Add**
7. Zoek naar "Itho Daalderop"
8. Klik op **Download**
9. **Herstart Home Assistant**

### Stap 3: Configureren

1. Ga naar **Instellingen** → **Apparaten & Services**
2. Klik **+ Integratie toevoegen**
3. Zoek **Itho Daalderop**
4. Volg de configuratie stappen (zoals getest!)

---

## Methode 2: Handmatige Installatie (Direct testen)

Sneller voor lokaal testen zonder GitHub:

### Stap 1: Kopieer bestanden naar Home Assistant

1. Via **SSH** of **Samba** verbinden met je HA instance
2. Navigeer naar: `/config/custom_components/`
3. Maak folder: `itho_daalderop`
4. Kopieer alle bestanden uit `custom_components/itho_daalderop/` naar deze folder

   ```bash
   # Via SSH op Home Assistant:
   cd /config/custom_components/
   mkdir -p itho_daalderop/translations
   
   # Upload de bestanden:
   # - __init__.py
   # - api.py
   # - config_flow.py
   # - const.py
   # - manifest.json
   # - sensor.py
   # - strings.json
   # - water_heater.py
   # - translations/nl.json
   ```

### Stap 2: Herstart Home Assistant

1. Ga naar **Instellingen** → **Systeem**
2. Klik op **Herstarten**

### Stap 3: Integratie toevoegen

1. Na herstart: **Instellingen** → **Apparaten & Services**
2. **+ Integratie toevoegen**
3. Zoek **Itho Daalderop**
4. Configureren met serienummer + login

---

## Testen

### Test 1: Config Flow
- Voer serienummer in: `<SERIAL_NUMBER>`
- Login via browser
- Kopieer callback URL
- Controleer of token wordt geaccepteerd

### Test 2: Sensors
Na configuratie check deze entities:
- `sensor.itho_boiler_SERIAL_boiler_content`
- `sensor.itho_boiler_SERIAL_device_mode`
- `sensor.itho_boiler_SERIAL_device_power`
- `sensor.itho_boiler_SERIAL_water_temperature`
- `sensor.itho_boiler_SERIAL_pv_net_power`

### Test 3: Water Heater
- `water_heater.itho_boiler_SERIAL`
- Probeer temperatuur aanpassen
- Probeer modus wijzigen (Eco/Auto/Heat Pump/Off)

---

## Troubleshooting

### "Platform error sensor" in logs

Check het logboek:
```
Instellingen → Systeem → Logboeken
```

Zoek naar fouten met `itho_daalderop`.

### Entities verschijnen niet

1. Check of integratie is toegevoegd: **Apparaten & Services**
2. Herstart HA opnieuw
3. Check logs voor errors

### API errors (401/403)

- Token mogelijk verlopen
- Verwijder integratie en voeg opnieuw toe
- Log opnieuw in

### Sensors tonen "Unknown"

- Wacht 60 seconden (update interval)
- Check of boiler online is
- Controleer serienummer is correct (UPPERCASE!)

---

## Development Tips

### Logs bekijken

Voeg toe aan `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.itho_daalderop: debug
```

Herstart HA en check **Logboeken** voor debug info.

### Live testen van wijzigingen

Na code wijzigingen:
1. **Developer Tools** → **YAML** → **Reload: All**
2. Of: volledige herstart

### Valideren voor productie

Voordat je publiceert op HACS:

1. ✅ Test config flow volledig
2. ✅ Test alle sensors hebben data
3. ✅ Test water heater controls werken
4. ✅ Test token refresh (na 24u)
5. ✅ Check logs voor warnings/errors
6. ✅ Test met meerdere serienummers

---

## Voor HACS Publicatie

Als je de integratie wilt publiceren op HACS (officieel):

1. Repository moet **publiek** zijn op GitHub
2. Voeg **releases** toe met versienummers (v0.1.0)
3. Voldoe aan [HACS guidelines](https://hacs.xyz/docs/publish/integration)
4. Submit via [HACS default repository](https://github.com/hacs/default)

Voor nu is **custom repository** prima voor testen! 🚀
