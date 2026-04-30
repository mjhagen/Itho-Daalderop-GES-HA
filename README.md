# Itho Daalderop Home Assistant Integration

<p align="center">
  <img src="icon.svg" width="200" alt="Itho Daalderop Integration Icon"/>
</p>

<p align="center">
  <a href="https://github.com/custom-components/hacs"><img src="https://img.shields.io/badge/HACS-Custom-orange.svg" alt="HACS"></a>
  <a href="https://github.com/marinuz/Itho-Daalderop-GES-HA/releases"><img src="https://img.shields.io/github/release/marinuz/Itho-Daalderop-GES-HA.svg" alt="GitHub Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/marinuz/Itho-Daalderop-GES-HA.svg" alt="License"></a>
</p>

Home Assistant integratie voor Itho Daalderop boilers via de Climate Connect cloud API.

## ✨ Features

### 🎛️ Boiler controle
- ✅ **Water Heater entity** voor de hoofd-besturing van de boiler
- ✅ **Temperatuurregeling** (10-75°C) met feedback uit de API
- ✅ **Bedrijfsmodus select** voor SmartControl, Schedule, Continuous en Holiday
- ✅ **Vakantie modus** als aparte schakelaar
- ✅ **Boost functie** als schakelaar en service, inclusief status feedback
- ✅ **Weekprogramma service** voor het aanpassen van schedules

### ☀️ PV / Smart-grid ondersteuning
- ✅ **PV functie aan/uit** schakelbaar, waar ondersteund door het boilermodel
- ✅ **Instelbare start/stop limieten** voor PV overschot (kW)
- ✅ **PV doeltemperatuur** configureerbaar (°C)
- ✅ **Live PV monitoring**: verbruik, productie en netto vermogen
- ℹ️ PV-entiteiten worden niet aangemaakt voor bekende modellen waarvan de API alleen niet-functionele nulwaarden teruggeeft.

### 📊 Monitoring
- ✅ Boiler inhoud percentage
- ✅ Actueel opgenomen vermogen (kW)
- ✅ Doeltemperatuur uit de device mode API
- ✅ Energieverbruik en energiebesparing (kWh)
- ✅ Per-dag schedule sensors met schakelmomenten en temperaturen
- ✅ Legionella preventie timer
- ✅ Software versie
- ✅ Online/offline status

### 🔒 Betrouwbaarheid
- ✅ **Token-based authenticatie** (geen wachtwoord in Home Assistant)
- ✅ **Retry logic** voor tijdelijke netwerk/API fouten
- ✅ **Selectieve polling**: snelle statusupdates, minder vaak trage settings/history endpoints
- ✅ **HACS compatible** met integratie-iconen/logo's

## Installatie via HACS

Zie de [volledige installatie gids](docs/HACS_INSTALL_GUIDE.md) voor gedetailleerde instructies.

### Quick Start

#### Optie 1: Custom Repository

1. Open **HACS** in Home Assistant
2. Klik op **Integrations**
3. Klik rechtsbovenin op de **︙** (drie puntjes)
4. Selecteer **Custom repositories**
5. Voeg toe:
   - **Repository**: `https://github.com/marinuz/Itho-Daalderop-GES-HA.git`
   - **Category**: `Integration`
6. Klik op **Add**
7. Zoek naar "Itho Daalderop" en klik op **Download**
8. Herstart Home Assistant

### Optie 2: Handmatige installatie

1. Download deze repository
2. Kopieer de `custom_components/itho_daalderop` folder naar je Home Assistant `custom_components` directory
3. Herstart Home Assistant

## Configuratie

1. Ga naar **Instellingen** → **Apparaten & Services**
2. Klik op **+ Integratie toevoegen**
3. Zoek naar **Itho Daalderop**
4. Voer het **serienummer** van je boiler in (bijv. `<SERIAL_NUMBER>`)
5. Er opent een browser naar de Itho login pagina
6. Log in met je **Itho Daalderop account**
7. Na inloggen krijg je een foutmelding - dit is normaal!
8. Open **Browser Console** (F12)
9. Kopieer de URL die begint met `climateconnect://login?token=...`
10. Plak deze in Home Assistant
11. Klaar! Je boiler is nu beschikbaar in Home Assistant

## Entiteiten

### 🌡️ Water Heater
**Hoofdentiteit voor boiler besturing**
- **Temperatuur**: 10-75°C instelbaar
- **Modi**:
  - `Eco` (SmartControl) - slimme automatische modus
  - `Auto` (Schedule) - volgens weekschema
  - `Heat Pump` (Continuous) - continu aan
  - `Off` (Holiday) - vakantie modus
- **Attributen**: belangrijkste status-, energie- en PV-data beschikbaar als attributes

### 🔽 Select
- **Device Mode**
  - Opties: `SmartControl`, `Schedule`, `Continuous`, `Holiday`
  - Behoudt waar mogelijk bestaande temperatuur en schedule bij mode-wijzigingen

### 🔘 Switches
- **Boost Mode** 🚀
  - Activeer/deactiveer snelle opwarming
  - Houdt tijdelijk de gekozen UI-status vast totdat de API-status is bijgewerkt

- **Vakantie Modus** 🏝️
  - Zet de boiler in Holiday mode
  - Uitzetten schakelt terug naar SmartControl

- **PV Function** ☀️
  - Schakel PV-overschot verwarming aan/uit
  - Alleen beschikbaar op modellen met ondersteunde PV/smart-grid instellingen

### 🔢 Numbers
- **Temperatuur Instelling** (10-75°C, stap 1)
  - Doeltemperatuur voor de boiler

- **PV Start Limit** (0-10 kW, stap 0.1)
  - Start boiler boven deze PV/netto limiet

- **PV Stop Limit** (0-10 kW, stap 0.1)
  - Stop boiler onder deze limiet

- **PV Target Temperature** (40-90°C, stap 1)
  - Doeltemperatuur voor PV-modus

PV numbers zijn alleen beschikbaar wanneer PV/smart-grid instellingen ondersteund worden.

### 📊 Sensors
**Device Status**
- `Boiler Content` - Vulgraad (%)
- `Device State` - Online/offline/status uit de API
- `Device Power` - Actueel vermogen (kW)
- `Target Temperature` - Ingestelde doeltemperatuur (°C)
- `Software Version` - Firmware versie
- `Legionella Prevention Timer` - Tijd tot preventie (uur)

**Energy Monitoring**
- `Energy Consumption` - Totaal/verrekend verbruik (kWh)
- `Energy Saving` - Totale besparing (kWh)

**Schedule Monitoring**
- `Schedule Monday` t/m `Schedule Sunday` - Dagelijkse schakelmomenten en temperaturen
- Schedule attributes bevatten gestructureerde entries met `time`, `hour`, `minute` en `temperature`

**PV Monitoring**
- `PV Net Power` - Netto vermogen (kW, negatief kan teruglevering betekenen)
- `PV Power Consumption` - Afname van net (kW)
- `PV Power Production` - Levering aan net (kW)

**PV Settings (read-only sensors)**
- `PV Enabled` - Status (On/Off)
- `PV Start Limit` - Huidige startwaarde (kW)
- `PV Stop Limit` - Huidige stopwaarde (kW)

PV sensors zijn alleen beschikbaar wanneer PV/smart-grid instellingen ondersteund worden.

## Services

De integratie ondersteunt standaard Home Assistant services en eigen services.

### Water Heater Services (Home Assistant standaard)
```yaml
# Stel temperatuur in
service: water_heater.set_temperature
target:
  entity_id: water_heater.itho_boiler_vpr242600095
data:
  temperature: 60

# Wijzig bedrijfsmodus
service: water_heater.set_operation_mode
target:
  entity_id: water_heater.itho_boiler_vpr242600095
data:
  operation_mode: "eco"  # eco, auto, heat_pump, off
```

### Custom Services
```yaml
# Activeer boost mode
service: itho_daalderop.boost_boiler
data:
  activate: true

# Stel een weekprogramma in
service: itho_daalderop.set_schedule
data:
  schedule:
    "0": {"0": 10, "800": 60, "17:30": 65}
    "1": {"0": 10, "800": 60, "17:30": 65}
```

Voor `set_schedule` zijn dagen `0-6` maandag-zondag. Tijdstippen mogen als uur (`8`), HHMM (`800`, `1730`) of `HH:MM` worden opgegeven. De integratie zet dit om naar het formaat dat de Climate Connect API verwacht.

## Automatisering Voorbeelden

### PV Overschot Optimalisatie
```yaml
automation:
  - alias: "Boiler: Warm water bij zonne-overschot"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_power_surplus
        above: 2.0  # 2 kW overschot
    condition:
      - condition: state
        entity_id: switch.pv_function
        state: "on"
    action:
      - service: number.set_value
        target:
          entity_id: number.pv_target_temperature
        data:
          value: 75
```

### Boost bij lage boiler inhoud
```yaml
automation:
  - alias: "Boiler: Boost bij laag niveau"
    trigger:
      - platform: numeric_state
        entity_id: sensor.boiler_content
        below: 20
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.boost_mode
```

### Nacht tarief optimalisatie
```yaml
automation:
  - alias: "Boiler: Opwarmen tijdens nacht tarief"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: water_heater.set_temperature
        target:
          entity_id: water_heater.itho_boiler
        data:
          temperature: 75
      - service: water_heater.set_operation_mode
        target:
          entity_id: water_heater.itho_boiler
        data:
          operation_mode: "heat_pump"
```

## Polling en API gedrag

- Device status wordt iedere `30` seconden opgehaald.
- Device mode en PV settings worden minder vaak opgehaald, en direct na eigen wijzigingen ververst.
- Energiehistorie wordt minder frequent opgehaald; de `Energy Consumption` sensor gebruikt daarnaast lokaal geïntegreerd vermogen wanneer beschikbaar.
- De Climate Connect API kan traag reageren. Timeouts en retries zijn hierop afgestemd.

## Troubleshooting

### Kan geen login URL kopiëren?
- Open Browser Console met **F12** of **Ctrl+Shift+I**
- Zoek naar de regel met "Failed to launch"
- De URL staat ook vaak in de **adresbalk** van de browser

### Token werkt niet?
- Zorg dat je de **volledige URL** kopieert, inclusief `climateconnect://login?token=`
- Token is lang geldig, maar kan opnieuw nodig zijn als de API authenticatie wijzigt

### Boiler reageert niet?
- Controleer of het serienummer correct is (hoofdletters!)
- Controleer of de boiler online is in de Itho app
- Houd rekening met vertraging in de cloud API; sommige wijzigingen zijn niet direct zichtbaar

### PV-entiteiten ontbreken?
- Sommige boilermodellen geven via de API alleen nulwaarden terug voor PV/smart-grid instellingen. Voor bekende niet-ondersteunde modellen worden PV-entiteiten daarom verborgen.

## Licentie

MIT License - zie [LICENSE](LICENSE) voor details.

## Bijdragen

Bijdragen zijn welkom! Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor richtlijnen.

## Support

- 📚 [Documentatie](docs/)
- 🐛 [Issues](https://github.com/marinuz/Itho-Daalderop-GES-HA/issues)
- 💬 [Discussions](https://github.com/marinuz/Itho-Daalderop-GES-HA/discussions)

## Credits

Ontwikkeld door de Home Assistant community.  
Gebaseerd op de Itho Daalderop Climate Connect API.
