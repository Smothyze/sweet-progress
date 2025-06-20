# Sweet Progress - Portable Game Save Backup Tool

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A user-friendly tool to backup game save files with automatic path remembering functionality.

## 🚀 Download
You can download the latest portable version from the [Releases](https://github.com/your-username/sweet-progress/releases) page.

## 🎮 Features

### Core Functionality
- **Game Save Backup**: Create backups of your game save files
- **Smart Path Management**: Remember your previous backup locations
- **Author Customization**: Add your name to backup credits
- **Timestamp Protection**: Prevent overwriting with timestamped folders
- **Cross-Platform Paths**: Automatically adjust paths for different users

### User Interface
- **Intuitive GUI**: Easy-to-use interface with dropdown menus
- **Real-time Logging**: See backup progress and status
- **Error Handling**: Clear error messages and validation
- **Configuration Saving**: Your settings are remembered automatically

## 🚀 Quick Start

### Portable Usage (No Installation Required)
1. Extract the ZIP file to any location
2. Double-click `Sweet Progress.exe` to run
3. Start backing up your game saves immediately!

**Note**: Keep the `Resource` folder in the same directory as the executable for proper functionality.

## 📁 File Structure

The application creates the following structure:
```
Backup Location/
├── Game Name/
│   ├── Savegame Folder/
│   │   └── (your save files)
│   └── Readme.txt (backup information)
└── Game Name/
    └── 2024-01-15_14-30-25/ (if timestamp enabled)
        ├── Savegame Folder/
        │   └── (your save files)
        └── Readme.txt
```

## ⚙️ Configuration

The application automatically creates a configuration file at:
```
[Application Folder]/Resource/savegame_config.json
```
This file stores your game paths, last used settings, and author information.

## 🔧 Building from Source

If you want to build the application from source, follow these steps:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-username/sweet-progress.git
   cd sweet-progress
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```sh
   python program.py
   ```

4. **Build the executable:**
   ```sh
   python build.py
   ```
   This will create a `Sweet Progress.exe` in the `dist` folder.

## 🛠️ Troubleshooting

- **"Icon file not detected"**: Ensure the `Resource` folder is in the same directory as the executable.
- **"Access Denied" errors**: Run `Sweet Progress.exe` as an Administrator.
- **Application won't start**: Ensure you're on Windows 10/11 and check if your antivirus is blocking the app.

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Sweet Progress** - Making game save backups simple and reliable! 🎮✨
