# Sweet Progress - Save Game Backup Tool

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A Python-based GUI application for backing up game save files with advanced features and improved user experience.

## Features

### Core Functionality
- **Game Save Backup**: Create backups of game save files with customizable locations
- **Timestamp Support**: Optional timestamped backup folders for version control
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Credit System**: Add author information and notes to backup files

### Enhanced User Interface
- **Smart Dropdown**: Game list ordered by last backup time (newest first, limited to 5 items)
- **Progress Bar**: Real-time progress indication during backup operations
- **Enhanced Logging**: Timestamped log entries with automatic rotation
- **Game List Window**: Table format with Game Title and Last Used columns, plus sorting options (Alphabetical/Last Used)
- **Input Validation**: Comprehensive validation for paths and game titles

### Security & Reliability
- **Path Validation**: Ensures all paths are valid and accessible
- **Permission Checking**: Verifies write permissions before backup
- **Error Handling**: Robust error handling with informative messages
- **Memory Management**: Automatic log rotation to prevent memory issues

## Recent Improvements

### Version 2.0 - Major Updates
1. **Smart Game Ordering**: Dropdown now shows games based on last backup time instead of alphabetical order (limited to 5 most recent)
2. **Backup History Tracking**: Automatic timestamp tracking for each game backup
3. **Enhanced UI**: Progress bar, better error messages, and improved user experience
4. **Game List Table**: Redesigned Game List Window with table format showing Game Title and Last Used columns
5. **Game List Sorting**: Added sorting options (Alphabetical/Last Used) in the Game List Window
6. **Cross-Platform Path Handling**: Proper support for Windows and Unix path separators
7. **Input Validation**: Comprehensive validation for game titles and file paths
8. **Memory Optimization**: Log rotation to prevent memory leaks during long sessions

### Technical Improvements
- Fixed Tkinter initialization issues
- Added proper error handling throughout the application
- Improved config file structure with backup history
- Enhanced file operation safety with permission checks
- Better cross-platform compatibility

## Installation

1. Ensure Python 3.6+ is installed
2. Clone or download this repository
3. Make sure the `Resource/icon.ico` file is present
4. Run `python program.py`

## Usage

1. **Select Game**: Choose from the dropdown (ordered by recent backups) or enter a new game title
2. **Set Paths**: Use browse buttons to select savegame and backup locations
3. **Configure Options**: 
   - Enable/disable timestamped folders
   - Set author information and notes via Credit Setting
4. **Create Backup**: Click "Create Backup" to start the process
5. **Monitor Progress**: Watch the progress bar and log for real-time updates

## Configuration

The application automatically creates a configuration file at:
- Windows: `Resource/savegame_config.json`
- Linux/macOS: `Resource/savegame_config.json`

### Config Structure
```json
{
    "games": {
        "Game Name": {
            "savegame_location": "path/to/savegame",
            "backup_location": "path/to/backup"
        }
    },
    "last_used": {
        "game_title": "Last Game",
        "savegame_location": "path/to/savegame",
        "backup_location": "path/to/backup",
        "author": "Author Name"
    },
    "backup_history": {
        "Game Name": "2024-01-15 14:30:25"
    }
}
```

## File Structure

```
sweet-progress/
├── program.py          # Main application
├── README.md           # This file
├── icon-v2.png         # Application icon
└── Resource/
    └── icon.ico        # Windows icon file
```

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- Standard library modules: os, shutil, json, datetime, sys, getpass, pathlib

## Troubleshooting

### Common Issues
1. **Icon not found**: Ensure `Resource/icon.ico` exists
2. **Permission errors**: Check write permissions for backup location
3. **Path issues**: Use absolute paths or ensure relative paths are correct

### Error Messages
- **"Path is not writable"**: Check folder permissions
- **"Invalid game title"**: Avoid special characters in game names
- **"Source folder not found"**: Verify savegame location exists

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

---

**Sweet Progress** - Making game save backups simple and reliable! 🎮✨
