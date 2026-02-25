# Contributing to Itho Daalderop Integration

Bedankt voor je interesse om bij te dragen! 🎉

## Development Setup

1. **Clone de repository**
   ```bash
   git clone https://github.com/yourusername/itho-daalderop-ha.git
   cd itho-daalderop-ha
   ```

2. **Test setup**
   ```bash
   cd tests
   pip install -r requirements.txt
   cp config.example.py config.py
   # Vul je credentials in config.py
   python test_config_flow.py
   ```

3. **Installeer in Home Assistant**
   - Kopieer `custom_components/itho_daalderop` naar je HA `custom_components` folder
   - Herstart Home Assistant
   - Test de integratie

## Code Richtlijnen

- Volg [Home Assistant development guidelines](https://developers.home-assistant.io/docs/development_index)
- Gebruik **type hints** voor alle functies
- Voeg **docstrings** toe aan classes en methods
- Test je code met echte hardware indien mogelijk
- Update de **README.md** bij nieuwe features

## Pull Requests

1. Fork de repository
2. Maak een feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit je changes (`git commit -m 'Add some AmazingFeature'`)
4. Push naar de branch (`git push origin feature/AmazingFeature`)
5. Open een Pull Request

## Testen

Voordat je een PR indient:

- [ ] Test de config flow volledig
- [ ] Test alle sensors tonen correcte data
- [ ] Test water heater controls werken
- [ ] Check logs op warnings/errors
- [ ] Update documentatie indien nodig

## Documentatie

Aanvullende documentatie staat in de `docs/` folder:

- [AUTHENTICATION_STRATEGY.md](docs/AUTHENTICATION_STRATEGY.md) - Auth methode uitleg
- [CONFIG_FLOW_GUIDE.md](docs/CONFIG_FLOW_GUIDE.md) - Config flow details
- [TEST_RESULTS.md](docs/TEST_RESULTS.md) - API endpoints documentatie

## Vragen?

Open gerust een [Issue](https://github.com/yourusername/itho-daalderop-ha/issues) voor vragen of suggesties!
