# Sweet Progress - Save Game Backup Tool

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange.svg)

A Python-based GUI application for backing up game save files with advanced features, improved user experience, and modular architecture for easy maintenance and extensibility.

## Features

### Core Functionality
- **Game Save Backup**: Create backups of game save files with customizable locations
- **Timestamp Support**: Optional timestamped backup folders for version control
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Credit System**: Add author information and notes to backup files
- **Smart Path Detection**: Automatically detect game directories and provide path masking options

### Enhanced User Interface
- **Smart Dropdown**: Game list ordered by last backup time (newest first, limited to 5 items)
- **Progress Bar**: Real-time progress indication during backup operations
- **Enhanced Logging**: Timestamped log entries with automatic rotation
- **Game List Window**: Table format with Game Title and Last Used columns, plus sorting options (Alphabetical/Last Used)
- **Path Preview**: Preview how paths will appear in README.txt files
- **Input Validation**: Comprehensive validation for paths and game titles

### Security & Reliability
- **Path Validation**: Ensures all paths are valid and accessible
- **Permission Checking**: Verifies write permissions before backup
- **Error Handling**: Robust error handling with informative messages
- **Memory Management**: Automatic log rotation to prevent memory issues
- **Path Masking**: Secure sharing of savegame locations with username and Steam ID masking

## Architecture

The application follows a modular architecture for better maintainability and extensibility:

```
sweet-progress/
├── program.py              # Main entry point
├── README.md               # This file
├── icon-v2.png             # Application icon
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── path_utils.py       # Path handling and validation
│   └── resource_utils.py   # Resource path management
├── config/                 # Configuration management
│   ├── __init__.py
│   └── config_manager.py   # Config loading/saving
├── backup/                 # Backup functionality
│   ├── __init__.py
│   └── backup_manager.py   # Backup operations
├── ui/                     # User interface modules
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   └── windows.py          # Additional windows (list, settings, preview)
└── Resource/
    └── icon.ico            # Windows icon file
```

### Module Overview

- **`utils/`**: Contains utility functions for path handling, validation, and resource management
- **`config/`**: Manages application configuration, preferences, and backup history
- **`backup/`**: Handles all backup-related operations with progress tracking
- **`ui/`**: Contains all user interface components and windows
- **`program.py`**: Clean entry point that initializes the application

## Installation

### Prerequisites
- Python 3.8 or higher
- tkinter (usually included with Python)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sweet-progress.git
   cd sweet-progress
   ```

2. Ensure the `Resource/icon.ico` file is present

3. Run the application:
   ```bash
   python program.py
   ```

### Development Setup
For development and contribution:
```bash
git clone https://github.com/yourusername/sweet-progress.git
cd sweet-progress
# Make your changes
python program.py
```

## Usage

1. **Select Game**: Choose from the dropdown (ordered by recent backups) or enter a new game title
2. **Set Paths**: Use browse buttons to select savegame and backup locations
3. **Configure Options**: 
   - **Path Display**: Choose between Auto, Game Path, or Standard masking
   - **Timestamp**: Enable/disable timestamped folders
   - **Credit Setting**: Set author information and notes
4. **Preview Paths**: Use the Preview button to see how paths will appear in README.txt
5. **Create Backup**: Click "Create Backup" to start the process
6. **Monitor Progress**: Watch the progress bar and log for real-time updates

### Path Display Options
- **Auto**: Smart detection - uses Game Path for game directories, Standard for others
- **Game Path**: Uses `(path-to-game)/relative-path` format for sharing
- **Standard**: Uses full path with username and Steam ID masking

## Configuration

The application automatically creates a configuration file at:
- Windows: `Resource/savegame_config.json`
- Linux/macOS: `Resource/savegame_config.json`

### Config Structure
```json
{
    "games": {
        "<game_id>": {
            "id": "<game_id>",
            "game_title": "Game Name",
            "savegame_location": "path/to/savegame",
            "backup_location": "path/to/backup"
        }
    },
    "last_used": {
        "game_title": "Last Game",
        "savegame_location": "path/to/savegame",
        "backup_location": "path/to/backup"
    },
    "backup_history": {
        "<game_id>": "YYYY-MM-DD HH:MM:SS"
    },
    "preferences": {
        "path_display": "Auto",
        "timestamp_option": "Disable"
    }
}
```

## Development

### Project Structure
The application is organized into logical modules:

- **`utils/path_utils.py`**: Path handling, validation, and masking functions
- **`utils/resource_utils.py`**: Resource path management and constants
- **`config/config_manager.py`**: Configuration loading, saving, and management
- **`backup/backup_manager.py`**: Backup operations with progress tracking
- **`ui/main_window.py`**: Main application window and UI logic
- **`ui/windows.py`**: Additional windows (GameListWindow, CreditSettingWindow, PathPreviewWindow)

### Adding New Features
1. **UI Changes**: Modify files in the `ui/` directory
2. **Backup Logic**: Update `backup/backup_manager.py`
3. **Configuration**: Extend `config/config_manager.py`
4. **Utilities**: Add new functions to `utils/` modules

### Code Style
- Follow PEP 8 guidelines
- Use descriptive variable and function names
- Add docstrings for all public functions
- Keep modules focused on single responsibilities

## Requirements

- Python 3.8+
- tkinter (usually included with Python)
- Standard library modules: os, shutil, json, datetime, sys, getpass, pathlib

## Troubleshooting

### Common Issues
1. **Icon not found**: Ensure `Resource/icon.ico` exists
2. **Permission errors**: Check write permissions for backup location
3. **Path issues**: Use absolute paths or ensure relative paths are correct
4. **Import errors**: Ensure all modules are in the correct directories

### Error Messages
- **"Path is not writable"**: Check folder permissions
- **"Invalid game title"**: Avoid special characters in game names
- **"Source folder not found"**: Verify savegame location exists
- **"Module not found"**: Check that all required modules are present

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow the modular architecture
4. **Test your changes**: Ensure the application works correctly
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines
- Follow the existing modular architecture
- Add appropriate error handling
- Update documentation for new features
- Test on multiple platforms if possible
- Keep commits atomic and well-described

## License

This project is open source and available under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and tkinter
- Icons and resources included in the project
- Community feedback and contributions

---

**Sweet Progress** - Making game save backups simple, reliable, and maintainable! 🎮✨

*Built with modular architecture for the future.*
