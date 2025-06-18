# Save Game Backup Tool

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A user-friendly tool to backup game save files with automatic path remembering functionality.

## Features

### Core Features
- 🎮 **Game Title Management**
  - Dropdown list of previously used game titles
  - Auto-fill paths when selecting existing games
  - Save new game configurations automatically

- 📂 **Directory Browsing**
  - Native file dialogs for path selection
  - Support for both savegame and backup locations
  - Path validation before backup

- 🔄 **Backup Functionality**
  - Complete folder backup with timestamp
  - Automatic creation of credit/readme file
  - Overwrite protection for existing backups

### User Experience
- 📝 **Configuration Saving**
  - JSON-based configuration storage
  - Remembers last used settings
  - Per-game path configurations

- 📊 **Logging & Feedback**
  - Real-time operation logging
  - Success/failure notifications
  - Detailed error messages

## How to Use

### Basic Usage
1. **Enter Game Title**
   - Type a new game title or select from dropdown
   - Existing games will auto-fill their paths

2. **Select Paths**
   - Click "Browse..." to select:
     - Savegame location (your game's save folder)
     - Backup location (where to store backups)

3. **Create Backup**
   - Click "Create Backup" button
   - View progress in the log area
   - Receive confirmation when complete

### Advanced Features
- **Editing Existing Games**
  - Select from dropdown
  - Modify paths as needed
  - New paths are saved automatically

- **Configuration File**
  - Stored as `savegame_backup_config.json`
  - Can be edited manually if needed
  - Located in the same folder as the executable

### Command Line Version
For advanced users, the core backup functionality can be called directly:

```python
from savegame_backup import backup_savegame_with_credit

backup_savegame_with_credit(
    source_folder="C:/path/to/savegame",
    backup_directory="D:/path/to/backups",
    game_name="Your Game Name"
)
```

## Requirements
- Python 3.8+
- Windows (for .exe version)
- tkinter (usually included with Python)

## Installation
1. Download the latest release
2. Run `savegame_backup.exe` (Windows)
   - Or run `python savegame_backup.py` if using source

## License
MIT License - See LICENSE file for details

---

Would you like me to add any additional sections like troubleshooting, contribution guidelines, or a more detailed technical explanation of any part?