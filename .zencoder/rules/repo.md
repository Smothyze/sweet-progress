---
description: Repository Information Overview
alwaysApply: true
---

# Sweet Progress Information

## Summary
Sweet Progress is a cross-platform Python application designed to simplify the process of backing up game save files. It provides an intuitive GUI interface for managing game backups with features like automatic Steam folder detection, smart path masking, and comprehensive backup history tracking.

## Structure
- **backup/**: Core backup operations and functionality
- **config/**: Configuration management and persistence
- **ui/**: User interface components and windows
- **utils/**: Utility functions, logging, and path handling
- **Resource/**: Application resources and logs
- **build scripts**: build.bat and build_exe.py for executable creation

## Language & Runtime
**Language**: Python
**Version**: 3.8+
**Build System**: setuptools, PyInstaller
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- tkinter (GUI framework)
- Standard library modules (os, sys, json, datetime, getpass, pathlib, shutil, uuid)

**Development Dependencies**:
- pytest>=7.0.0 (Testing)
- black>=22.0.0 (Code formatting)
- flake8>=5.0.0 (Linting)
- mypy>=1.0.0 (Type checking)
- PyInstaller (Executable building)

## Build & Installation
```bash
# Run directly
python program.py

# Install for development
pip install -e .

# Build executable (Windows)
python build_exe.py
# or
build.bat
```

## Main Files
**Entry Point**: program.py
**Configuration**: Resource/savegame_config.json
**Core Components**:
- ui/main_window.py: Main application window
- backup/backup_manager.py: Core backup operations
- config/config_manager.py: Configuration handling
- utils/: Various utility modules

## Project Structure
The application follows a clean, modular architecture:
- **program.py**: Main entry point that initializes the application
- **ui/**: Contains all user interface components
- **backup/**: Handles backup operations and progress tracking
- **config/**: Manages configuration loading/saving
- **utils/**: Provides utility functions for logging, path handling, etc.
- **Resource/**: Stores application resources and logs

The application uses a JSON-based configuration system stored in Resource/savegame_config.json, which tracks game information, backup history, and user preferences. The modular design separates concerns between UI, backup logic, configuration, and utilities.