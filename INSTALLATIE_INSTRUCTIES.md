# Installatie & Herstart Instructies

## Integratie Opnieuw Laden in Home Assistant

Na het updaten van de integratie moet je Home Assistant de wijzigingen laten herladen:

### Optie 1: Herstart Home Assistant (Aanbevolen)
1. Ga naar **Instellingen** → **Systeem** → **Herstarten**
2. Klik op **Herstarten**
3. Wacht tot Home Assistant opnieuw is opgestart
4. Verwijder de oude integratie (als deze er is)
5. Voeg de integratie opnieuw toe

### Optie 2: Herlaad Integratie (Sneller)
1. Ga naar **Instellingen** → **Apparaten & Diensten**
2. Zoek de **Itho Daalderop** integratie
3. Klik op de **drie puntjes** rechts
4. Klik op **Herladen**

### Optie 3: Developer Tools (Voor ontwikkelaars)
1. Ga naar **Ontwikkelaarshulpmiddelen** → **Diensten**
2. Zoek naar `homeassistant.restart`
3. Klik op **Dienst aanroepen**

## Cache Probleem Oplossen

Als je nog steeds oude teksten ziet:

### Browser Cache Legen
1. Open de browser Developer Tools (F12)
2. Klik met rechtermuisknop op de **Vernieuwen** knop
3. Kies **Lege cache en harde opnieuw laden**

OF

1. Druk op **Ctrl + Shift + R** (Windows/Linux)
2. Of **Cmd + Shift + R** (Mac)

### Home Assistant Cache
1. Stop Home Assistant
2. Verwijder de `custom_components/itho_daalderop/__pycache__/` directory
3. Start Home Assistant opnieuw

## Troubleshooting

### "Token is ongeldig of verlopen"

Dit kan betekenen:

1. **Token is echt verlopen** → Log opnieuw in via de Itho app om een nieuwe token te krijgen
2. **Serienummer komt niet overeen** → Controleer of het serienummer klopt
3. **Token extractie mislukt** → Controleer of je de volledige URL hebt geplakt

**Debug stappen:**
1. Ga naar **Instellingen** → **Systeem** → **Logs**
2. Zoek naar `itho_daalderop` errors
3. Check de log voor exacte foutmeldingen

### "Oude instructies zichtbaar"

Dit betekent dat de strings.json niet is herladen:

1. Herstart Home Assistant
2. Leeg browser cache (Ctrl + Shift + R)
3. Verwijder en voeg de integratie opnieuw toe

## Correcte Gebruik

### Stap 1: Serienummer
Voer je boiler serienummer in (bijvoorbeeld: `<SERIAL_NUMBER>`)

### Stap 2: Inloggen
1. Klik op de **login link**
2. Log in met je Itho Daalderop account
3. Je krijgt een **foutmelding** - dit is normaal!
4. Kopieer de **HELE URL** uit de adresbalk:
   ```
   climateconnect://login?token=eyJ0eXAiOiJKV1QiLCJhbGc...
   ```
5. Plak de URL in het invoerveld
6. Klik op **Verzenden**

**Alternatief:** Je kunt ook alleen de token plakken (de lange string die begint met `eyJ...`)

## Versie Historie

- **v0.2.0** - Verbeterde URL/token extractie, betere foutmeldingen
- **v0.1.0** - Initiële release
