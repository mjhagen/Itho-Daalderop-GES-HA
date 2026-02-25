# Itho Daalderop Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integratie voor Itho Daalderop warmtepompboilers met Cloud Connect functionaliteit.

## Functies

✅ **Automatische authenticatie** via Azure B2C (geen username/password in HA nodig)  
✅ **12+ Sensors** (water level, temperatuur, power, PV data, etc.)  
✅ **Water Heater Entity** voor volledige boiler controle  
✅ **4 Bedrijfsmodi** (SmartControl, Schedule, Continuous, Holiday)  
✅ **PV integratie** monitoring (zonnepaneel overschot gebruik)  
✅ **Token geldig 1 jaar** via automatische refresh  

## Installatie via HACS

Zie de [volledige installatie gids](docs/HACS_INSTALL_GUIDE.md) voor gedetailleerde instructies.

### Quick Start

#### Optie 1: Custom Repository (Aanbevolen voor testing)

1. Open **HACS** in Home Assistant
2. Klik op **Integrations**
3. Klik rechtsbovenin op de **︙** (drie puntjes)
4. Selecteer **Custom repositories**
5. Voeg toe:
   - **Repository**: `https://github.com/marinuz/itho-daalderop-ha`
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
4. Voer het **serienummer** van je boiler in (bijv. `VPR242600095`)
5. Er opent een browser naar de Itho login pagina
6. Log in met je **Itho Daalderop account**
7. Na inloggen krijg je een foutmelding - dit is normaal!
8. Open **Browser Console** (F12)
9. Kopieer de URL die begint met `climateconnect://login?token=...`
10. Plak deze in Home Assistant
11. Klaar! Je boiler is nu beschikbaar in HA

## Entiteiten

### Water Heater
- **Besturing**: Temperatuur instelbaar (10-75°C)
- **Modi**: Eco (SmartControl), Auto (Schedule), Heat Pump (Continuous), Off (Holiday)

### Sensors
- **Boiler Content**: Vulgraad van de boiler (%)
- **Device Mode**: Huidige bedrijfsmodus
- **Device State**: Status van het apparaat
- **Device Power**: Stroomverbruik (W)
- **Water Temperature**: Huidige watertemperatuur (°C)
- **Software Version**: Firmware versie
- **Legionella Timer**: Tijd tot volgende legionella preventie (uur)
- **PV Net Power**: Netto PV vermogen (kW)
- **PV Enabled**: PV functie aan/uit
- **PV Start/Stop Limit**: PV controle limieten (kW)
- **Energy Consumption**: Energieverbruik (kWh)

## Services

De integratie biedt een Water Heater entity met standaard Home Assistant services:

- `water_heater.set_temperature` - Stel doeltemperatuur in
- `water_heater.set_operation_mode` - Wijzig bedrijfsmodus

## Troubleshooting

### Kan geen login URL kopiëren?
- Open Browser Console met **F12** of **Ctrl+Shift+I**
- Zoek naar de regel met "Failed to launch"
- De URL staat ook vaak in de **adresbalk** van de browser

### Token werkt niet?
- Zorg dat je de **volledige URL** kopieert, inclusief `climateconnect://login?token=`
- Token is 1 jaar geldig, daarna opnieuw inloggen

### Boiler reageert niet?
- Controleer of het serienummer correct is (hoofdletters!)
- Controleer of de boiler online is in de Itho app

## Licentie

MIT License - zie [LICENSE](LICENSE) voor details.

## Bijdragen

Bijdragen zijn welkom! Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor richtlijnen.

## Support

- 📚 [Documentatie](docs/)
- 🐛 [Issues](https://github.com/yourusername/itho-daalderop-ha/issues)
- 💬 [Discussions](https://github.com/yourusername/itho-daalderop-ha/discussions)

## Credits

Ontwikkeld door de Home Assistant community.  
Gebaseerd op de Itho Daalderop Cloud Connect API.
