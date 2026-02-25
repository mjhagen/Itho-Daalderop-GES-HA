# Test Scripts

Deze folder bevat test scripts voor ontwikkeling van de integratie.

⚠️ **Let op**: `config.py` en `token.txt` bevatten gevoelige data en zijn uitgesloten van git.

## Bestanden

- **config.example.py** - Template voor configuratie
- **config.py** - Daadwerkelijke credentials (niet in git!)
- **token.txt** - Opgeslagen JWT token (niet in git!)
- **test_auth_selenium.py** - Test authenticatie met Selenium
- **test_api_complete.py** - Test alle API endpoints
- **test_config_flow.py** - Test de complete config flow
- **run_tests.py** - Voer alle tests uit

## Setup

1. Kopieer `config.example.py` naar `config.py`
2. Vul je credentials in
3. Install dependencies: `pip install -r ../requirements.txt`
4. Run tests: `python test_config_flow.py`

## Requirements

- Python 3.11+
- Selenium WebDriver
- Chrome/Chromium browser
