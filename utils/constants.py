"""Constants and configuration values for Sweet Progress application"""

# Application metadata
APP_NAME = "Sweet Progress"
APP_VERSION = "2.7.2"
APP_DESCRIPTION = "Save Game Backup Tool"

# UI Configuration
WINDOW_WIDTH = 560
WINDOW_HEIGHT = 460
MIN_WINDOW_WIDTH = 560
MIN_WINDOW_HEIGHT = 420

# Logging Configuration
MAX_LOG_LINES = 1000
LOG_RETENTION_DAYS = 30

# Backup Configuration
MAX_RECENT_GAMES = 5
# Get default author from system username
import getpass
try:
    DEFAULT_AUTHOR = getpass.getuser()
except Exception:
    DEFAULT_AUTHOR = "User"
# Path Display Options
PATH_DISPLAY_OPTIONS = ["Auto", "Game Path", "Standard"]
TIMESTAMP_OPTIONS = ["Enable", "Disable"]