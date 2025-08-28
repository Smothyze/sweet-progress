"""Constants and configuration values for Sweet Progress application"""

# Application metadata
APP_NAME = "Sweet Progress"
APP_VERSION = "2.5.5"
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
BACKUP_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
DISPLAY_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# File Extensions
EXECUTABLE_EXTENSIONS = {'.exe', '.app', '.sh', '.bat', '.cmd'}

# Path Display Options
PATH_DISPLAY_OPTIONS = ["Auto", "Game Path", "Standard"]
TIMESTAMP_OPTIONS = ["Enable", "Disable"]

# Validation Rules
MIN_GAME_TITLE_LENGTH = 1
MAX_GAME_TITLE_LENGTH = 100
INVALID_CHARS = ['<', '>', ':', '"', '|', '?', '*', '\\', '/'] 