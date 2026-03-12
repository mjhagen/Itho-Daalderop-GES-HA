# Itho Daalderop API - Test Resultaten

## ✅ Test Status: GESLAAGD

**Test datum**: 25 februari 2026  
**Boiler**: `<SERIAL_NUMBER>`  
**API Token**: Geldig tot 25 februari 2027

---

## 📊 Beschikbare Data voor Home Assistant

### 1. **Device Status** (`/GetDeviceStatus`)
✅ Werkt - Alle waardes stabiel

```json
{
  "boilerContent": 0.81,           // 81% vol - SENSOR
  "boostActive": false,            // Boost mode - BINARY SENSOR
  "deviceMode": "Holiday",         // Huidige mode - SENSOR
  "devicePowerMeasured": 0.0,      // Huidig vermogen (kW) - SENSOR
  "deviceSoftwareVersion": "14.89.132",  // Software versie - SENSOR
  "deviceState": "Offline",        // Online status - BINARY SENSOR
  "energyConsumption": 0.04,       // Niet betrouwbaar als live totalizer; lijkt traag/statisch
  "energySaving": 0.0,             // Energie besparing (kWh) - SENSOR
  "pvPowerConsumption": 0.413,     // PV verbruik (kW) - SENSOR
  "pvPowerProduction": 0.0,        // PV productie (kW) - SENSOR
  "pvPowerNet": -0.376,            // PV netto (-0.376 = teruglevering) - SENSOR
  "legionellaPreventionTimer": 168 // Legionella timer (uren) - SENSOR
}
```

**Mogelijke Home Assistant Sensors:**
- ✅ Boiler inhoud percentage
- ✅ Boost status (aan/uit)
- ✅ Apparaat mode (SmartControl/Schedule/Continuous/Holiday)
- ✅ Huidig vermogen (kW)
- ✅ Software versie
- ✅ Online/Offline status
- ⚠️ `energyConsumption` uit `GetDeviceStatus` lijkt geen betrouwbare live oplopende kWh teller
- ✅ Energie besparing
- ✅ PV verbruik van net
- ✅ PV productie naar net
- ✅ PV netto (positief = gebruik, negatief = teruglevering)
- ✅ Legionella preventie timer
- ❌ Geen gemeten watertemperatuur veld zichtbaar in `GetDeviceStatus`

---

### 2. **Device Mode** (`/GetDeviceMode`)
✅ Werkt - Inclusief schema

```json
{
  "deviceMode": "Holiday",
  "schedule": {
    "0": { "0": 10 },  // Maandag om 00:00 = 10°C
    "1": { "0": 10 },  // Dinsdag
    "2": { "0": 10 },  // Woensdag
    "3": { "0": 10 },  // Donderdag
    "4": { "0": 10 },  // Vrijdag
    "5": { "0": 10 },  // Zaterdag
    "6": { "0": 10 }   // Zondag
  },
  "serialNumber": "<SERIAL_NUMBER>",
  "temperature": 75.0  // Setpoint temperatuur
}
```

**Mogelijke Home Assistant Entities:**
- ✅ SELECT entity voor mode (SmartControl/Schedule/Continuous/Holiday)
- ✅ CLIMATE entity met temperatuur setpoint (75°C)
- ✅ 7 losse schedule sensors (maandag t/m zondag)
- ✅ Schema configuratie per dag als attributen/gestructureerde data

**Device Modes:**
- `0` = SmartControl
- `1` = Schedule (volgens schema)
- `2` = Continuous (altijd aan)
- `3` = Holiday (vakantie mode)
- `4` = (onbekend)

---

### 3. **PV Settings** (`/GetDevicePVSettings`)
✅ Werkt - Zonnepanelen configuratie

```json
{
  "pvDecisionTimeout": 900.0,          // 15 minuten wachttijd
  "pvFunctionActiveAndP1Data": 1.0,    // PV functie actief met P1 data
  "pvSampleTimeout": 1000.0,           // Sample interval (ms)
  "pvSetpoint": 85.0,                  // PV target temp (°C)
  "pvSetpointHysteresis": 5.0,         // Hysterese (°C)
  "pvStartLimit": 1.6,                 // Start bij 1.6 kW overschot
  "pvStopLimit": 0.5,                  // Stop bij 0.5 kW
  "pvSwitchLimit": 10.0                // Switch limiet
}
```

**Mogelijke Home Assistant Entities:**
- ✅ PV functie aan/uit
- ✅ PV setpoint temperatuur configuratie
- ✅ PV start/stop limieten (kW)

---

### 4. **SmartGrid Status** (`/GetSmartGridStatus`)
✅ Werkt - Historische smart grid data

```json
{
  "count": 6,
  "results": [
    { "duration": 112, "powerConsumption": 12.7 },  // 112 min @ 12.7W
    { "duration": 140, "powerConsumption": 18.1 },
    { "duration": 390, "powerConsumption": 28.5 },
    { "duration": 60, "powerConsumption": 9.7 },
    { "duration": 498, "powerConsumption": 35.2 },
    { "duration": 280, "powerConsumption": 24.7 }
  ]
}
```

**Mogelijke Home Assistant Sensors:**
- ✅ SmartGrid sessie duur
- ✅ SmartGrid gemiddeld verbruik
- ✅ Aantal SmartGrid sessies

---

### 5. **Energy Consumption** (`/GetEnergyConsumption`)
✅ Werkt - Geeft historische intervaldata terug

```json
{
  "data": [
    {
      "consumption": 4.24467737222222,
      "consumptionNotDeliveredToNet": 0.0,
      "costs": 1.061169343055555,
      "previousConsumption": 7.32940556111111,
      "previousConsumptionNotDeliveredToNet": 0.0,
      "previousCosts": 1.8323513902777775,
      "timeStamp": 1773273600000,
      "previousTimeStamp": 1772668800000,
      "pvAverageNetPower": 0.0,
      "pvActualConPower": 0.0,
      "pvActualProdPower": 0.0
    }
  ],
  "deviceId": "dbabb1af-9dfb-4484-8bc5-e8a40ccfd5ec",
  "interval": "Day",
  "serialNumber": "#<SERIAL_NUMBER>"
}
```

**Parameters:**
- `serialNumber`: `<SERIAL_NUMBER>`
- `startDate`: Epoch timestamp (ms)
- `endDate`: Epoch timestamp (ms)
- `interval`: "Day", "Week", "Month", "Year"
- `includePreviousPeriod`: true/false
- `refreshCache`: true/false

**Waarnemingen:**
- `GetEnergyConsumption` geeft **periodetotalen** terug per `interval`, geen live totaalstand
- `consumption` is kWh voor het interval
- `costs` lijkt direct uit `consumption` afgeleid
- `device_status.energyConsumption` kan tegelijk op een lage/statische waarde blijven staan (dus niet gebruiken als enige bron voor live energy tracking)

**Mogelijke Home Assistant Entities:**
- ✅ Energie verbruik per dag/week/maand
- ✅ Vergelijking met vorige periode
- ✅ Kosten berekening
- ✅ Extra attributen voor PV-gerelateerde energievelden uit de history API

---

### 6. **Fault Info** (`/GetFault` & `/GetFaultHistory`)
✅ Werkt - Momenteel geen fouten

```json
{
  "message": {
    "code": "0x0000010001",
    "message": "No Fault code found"
  }
}
```

**Mogelijke Home Assistant Entities:**
- ✅ Binary sensor voor fout aanwezig (ja/nee)
- ✅ Sensor met laatste fout code
- ✅ Sensor met fout timestamp
- ✅ History view met laatste 8 fouten

---

### 7. **EAN Code** (`/GetEanCode`)
⚠️ Werkt niet - Geen adres geconfigureerd
```json
{
  "result": { "eanCode": "" },
  "message": {
    "code": "0x0000030001",
    "message": "A valid address could not be found"
  }
}
```

---

## 🔧 Beschikbare Acties (POST endpoints)

### 1. **Boost Boiler** (`/BoostBoiler`)
```json
{
  "serialNumber": "<SERIAL_NUMBER>",
  "activateBoost": true  // of false
}
```
**Home Assistant Service**: `itho_daalderop.boost_boiler`

---

### 2. **Update Device Mode** (`/UpdateDeviceMode`)
```json
{
  "serialNumber": "<SERIAL_NUMBER>",
  "deviceMode": 0,  // 0-4
  "temperature": 75.0,
  "schedule": {
    "0": { "0": 10, "8": 60, "17": 65 }  // Ma: 10°C @ 00:00, 60°C @ 08:00, etc.
  }
}
```
**Home Assistant Services**: 
- `itho_daalderop.set_mode`
- `itho_daalderop.set_temperature`
- `itho_daalderop.set_schedule`

---

### 3. **Update PV Settings** (`/UpdateDevicePVSettings`)
```json
{
  "serialNumber": "<SERIAL_NUMBER>",
  "pvSetpoint": 85.0,
  "pvStartLimit": 1.6,
  "pvStopLimit": 0.5,
  ...
}
```
**Home Assistant Service**: `itho_daalderop.configure_pv`

---

## 📝 Opmerkingen

1. **Device Power is kW, niet W**: live polling liet waarden rond 1.88 zien tijdens verwarmen; dat kan alleen logisch kW zijn
2. **Geen gemeten watertemperatuur gevonden**: `GetDeviceStatus` bevat geen `deviceTemperatureMeasured`; alleen `GetDeviceMode.temperature` (setpoint) is betrouwbaar beschikbaar
3. **`energyConsumption` in `GetDeviceStatus` is niet live genoeg**: deze bleef op 0.27 kWh staan terwijl het apparaat actief ~1.88 kW trok
4. **Gebruik `GetEnergyConsumption` voor historie**: deze endpoint geeft echte dag/week/maand totalen, kosten en vergelijking met vorige periode
5. **PV Integratie is apparaat-afhankelijk**: bij de live boiler waren alle PV velden 0.0
6. **Fault endpoints gedragen zich netjes**: `GetFault` geeft alleen `message`; `GetFaultHistory` geeft `count` + `results`
7. **Token Geldigheid**: 1 jaar geldig, bevat refresh token voor verlenging

---

## 🎯 Aanbevolen Home Assistant Integratie

### Sensors (15+)
1. Boiler inhoud (%)
2. Boost status (aan/uit)
3. Device mode (dropdown)
4. Huidig vermogen (kW)
5. Online status (aan/uit)
6. Energie verbruik totaal (kWh, bij voorkeur lokaal geïntegreerd of via utility meters)
7. Energie besparing (kWh)
8. PV verbruik (kW)
9. PV productie (kW)
10. PV netto (kW)
11. Legionella timer (uren)
12. Software versie
13. SmartGrid sessies
14. Laatste fout code
15. Doeltemperatuur / setpoint
16. Schedule Monday
17. Schedule Tuesday
18. Schedule Wednesday
19. Schedule Thursday
20. Schedule Friday
21. Schedule Saturday
22. Schedule Sunday

### Climate Entity
- Setpoint temperatuur (10-75°C)
- Huidige mode (SmartControl/Schedule/Continuous/Holiday)

### Services
1. Boost boiler (aan/uit)
2. Wijzig mode
3. Stel temperatuur in
4. Configureer schema
5. Update PV instellingen

---

## 🔬 Live polling update (12 maart 2026)

Met `./test_config.json` zijn de endpoints opnieuw live gepolled op een online boiler (`<SERIAL_NUMBER>`).

Belangrijkste bevindingen:
- `GetDeviceStatus.devicePowerMeasured = 1.88` tijdens actief verwarmen → eenheid is praktisch zeker **kW**
- `GetDeviceStatus.energyConsumption = 0.27` bleef gelijk terwijl het apparaat actief vermogen trok → geen betrouwbare live totalizer
- `GetEnergyConsumption` gaf wel geldige dag/week/maand data terug, inclusief:
  - `consumption`
  - `costs`
  - `previousConsumption`
  - `previousCosts`
  - `timeStamp`
  - `previousTimeStamp`
- `GetDeviceStatus` bevat **geen** gemeten watertemperatuur veld
- `GetDeviceMode.temperature = 70.0` is bruikbaar als **target temperature / setpoint**
- `GetFault` en `GetFaultHistory` geven nette lege responses zonder fouten
- `GetEanCode` gaf 404 met payload `"A valid address could not be found"`

## ✅ Conclusie

De API is bruikbaar, maar niet elk veld betekent wat het op het eerste gezicht lijkt:
- vermogensvelden zijn bruikbaar voor live monitoring
- de history endpoint is bruikbaar voor energie-rapportage
- temperatuur lijkt beperkt tot setpoint
- sommige statusvelden (`energyConsumption`) zijn niet geschikt als live bron zonder extra logica

De integratie moet dus deels leunen op:
- `GetDeviceStatus` voor live status
- `GetDeviceMode` voor setpoint
- `GetEnergyConsumption` voor historie/vergelijking
- lokale afleiding/integratie waar de cloud-API geen goede live teller geeft
