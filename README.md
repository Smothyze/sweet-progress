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

## License
MIT License - See LICENSE file for details

---

Would you like me to add any additional sections like troubleshooting, contribution guidelines, or a more detailed technical explanation of any part?