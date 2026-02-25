"""Constants for the Itho Daalderop integration."""

DOMAIN = "itho_daalderop"

# API Configuration
SSO_INITIATE_URL = "https://itho-tussenlaag.bettywebblocks.com/sso/initiate"
API_BASE_URL = "https://wifi-api.id-c.net/api"
APPLICATION_ID = "2da3d256-ca0a-4041-84ba-93856efceef9"
REDIRECT_URI = "climateconnect://login"

# Config entry data keys
CONF_SERIAL_NUMBER = "serial_number"
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"

# Update interval
UPDATE_INTERVAL = 60  # seconds

# Device modes
MODE_SMART_CONTROL = "SmartControl"
MODE_SCHEDULE = "Schedule"
MODE_CONTINUOUS = "Continuous"
MODE_HOLIDAY = "Holiday"

DEVICE_MODES = [
    MODE_SMART_CONTROL,
    MODE_SCHEDULE,
    MODE_CONTINUOUS,
    MODE_HOLIDAY,
]
