# Sweet Progress - Save Game Backup Tool

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange.svg)
![Version](https://img.shields.io/badge/Version-2.7.0-brightgreen.svg)
![Type Hints](https://img.shields.io/badge/Type%20Hints-Enabled-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

> **A professional and user-friendly tool for backing up game save files with advanced features like Steam detection, path masking, and comprehensive backup management.**

## 🎯 Overview

Sweet Progress is a cross-platform Python application designed to simplify the process of backing up game save files. Built with a modular architecture and modern Python practices, it provides an intuitive GUI interface for managing game backups with features like automatic Steam folder detection, smart path masking, and comprehensive backup history tracking.

## ✨ Key Features

### 🎮 Core Backup Functionality
- **Smart Game Detection**: Automatically detect and manage multiple game save locations
- **Steam Integration**: Automatic Steam folder detection with special path masking
- **Cross-Platform Support**: Works seamlessly on Windows, Linux, and macOS
- **Timestamped Backups**: Optional timestamped backup folders for version control
- **Author Attribution**: Automatic system username detection and custom credit system

### 🎨 Enhanced User Interface
- **Modern GUI**: Clean, intuitive interface built with tkinter
- **Smart Dropdown**: Game list ordered by recent backup activity
- **Real-time Progress**: Live progress indication during backup operations
- **Game Management**: Comprehensive game list with sorting and filtering options

### 🔒 Security & Reliability
- **Path Validation**: Comprehensive path validation and permission checking
- **Smart Path Masking**: Secure sharing with username, Steam ID, and folder detection
- **Error Handling**: Advanced error handling with custom exception classes
- **Professional Logging**: Centralized logging system with automatic rotation
- **Type Safety**: Full type hints throughout the codebase

### 📁 Advanced Backup Options
- **Folder Backup**: Primary backup method for save game directories
- **Registry Backup**: Additional registry backup functionality
- **Path Display Options**: Auto, Game Path, or Standard masking modes
- **Backup History**: Track and manage backup history with timestamps

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- tkinter (usually included with Python)

### Installation
```bash
# Clone the repository
git clone https://github.com/Smothyze/sweet-progress.git
cd sweet-progress

# Run directly
python program.py

# Or install for development
pip install -e .
```

### First Run
1. **Select Game**: Choose from recent games or enter a new title
2. **Set Paths**: Browse for savegame and backup locations
3. **Configure Your Preferences**: You can your custom cofig on option menu bar and go to Preferences
4. **Create Backup**: Click "Create Backup" and monitor progress
5. **Manage Games**: Use the List button to view and manage all games

## 🏗️ Architecture

The application follows a clean, modular architecture for maintainability and extensibility:

```
sweet-progress/
├── program.py              # Main entry point
├── ui/                     # User interface modules
│   ├── main_window.py      # Main application window
│   └── windows.py          # Additional windows (list, settings, preview)
├── backup/                 # Backup functionality
│   └── backup_manager.py   # Core backup operations
├── config/                 # Configuration management
│   └── config_manager.py   # Config loading/saving
├── utils/                  # Utility modules
│   ├── constants.py        # Configuration constants
│   ├── exceptions.py       # Custom exception classes
│   ├── logger.py           # Centralized logging system
│   ├── path_utils.py       # Path handling and validation
│   └── resource_utils.py   # Resource path management
└── Resource/               # Application resources
    ├── icon.ico           # Windows icon file
    └── logs/              # Log files directory
```

## 🔧 Configuration

The application automatically creates and manages configuration files:

- **Config Location**: `Resource/savegame_config.json`
- **Logs**: `Resource/logs/` (auto-created)
- **Backup History**: Automatic tracking of all backup operations

### Configuration Structure
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
    "backup_history": {
        "<game_id>": "YYYY-MM-DD HH:MM:SS"
    },
    "preferences": {
        "path_display": "Auto",
        "timestamp_option": "Disable"
    }
}
```

## 🎯 Path Masking & Steam Detection

### Automatic Detection
- **Steam Paths**: Automatically marked as `(steam-folder)/relative-path`
- **Game Directories**: Marked as `(path-to-game)/relative-path`
- **Standard Paths**: Username masked as `(pc-name)`, Steam ID as `(steam-id)`

### Display Options
- **Auto**: Smart detection based on path type
- **Game Path**: Always use game directory masking
- **Standard**: Always use standard masking

## 🛠️ Development

### Project Structure
- **`ui/`**: All user interface components and windows
- **`backup/`**: Backup operations and progress tracking
- **`config/`**: Configuration management and persistence
- **`utils/`**: Utility functions, logging, and path handling

### Code Quality
- **Type Hints**: Comprehensive type annotations throughout
- **Error Handling**: Custom exception classes for specific scenarios
- **Logging**: Centralized logging with file rotation
- **Testing**: Support for pytest, black, flake8, and mypy

### Adding Features
1. **UI Changes**: Modify files in the `ui/` directory
2. **Backup Logic**: Update `backup/backup_manager.py`
3. **Configuration**: Extend `config/config_manager.py`
4. **Utilities**: Add new functions to `utils/` modules

## 📋 Requirements

### Core Dependencies
- Python 3.8+
- tkinter (GUI framework)
- Standard library modules (os, sys, json, datetime, getpass, pathlib, shutil, uuid)

### Development Dependencies (Optional)
```
pytest>=7.0.0      # Testing
black>=22.0.0      # Code formatting
flake8>=5.0.0      # Linting
mypy>=1.0.0        # Type checking
```

## 🐛 Troubleshooting

### Common Issues
- **Icon not found**: Ensure `Resource/icon.ico` exists
- **Permission errors**: Check write permissions for backup location
- **Path issues**: Use absolute paths or verify relative path correctness
- **Configuration errors**: Check log files in `Resource/logs/`

### Getting Help
- Check the log files in `Resource/logs/` for detailed error information
- Verify all required modules are present
- Ensure proper file permissions for backup locations

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow the existing modular architecture
4. **Test your changes**: Ensure the application works correctly
5. **Commit and push**: `git commit -m 'Add amazing feature'`
6. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 and existing code style
- Use descriptive names and add docstrings
- Implement proper error handling with custom exceptions
- Use type hints for all new functions
- Update documentation for new features
- Test on multiple platforms when possible

## 📄 License

This project is open source and available under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and tkinter
- Enhanced with modern Python development practices
- Community feedback and contributions
- Icons and resources included in the project

---

**Sweet Progress** - Making game save backups simple, reliable, and maintainable! 🎮✨

*Built with modular architecture and modern Python practices for the future.*

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

[![GitHub stars](https://img.shields.io/github/stars/Smothyze/sweet-progress?style=social)](https://github.com/Smothyze/sweet-progress)
[![GitHub forks](https://img.shields.io/github/forks/Smothyze/sweet-progress?style=social)](https://github.com/Smothyze/sweet-progress)
[![GitHub issues](https://img.shields.io/github/issues/Smothyze/sweet-progress)](https://github.com/Smothyze/sweet-progress/issues)

</div>
