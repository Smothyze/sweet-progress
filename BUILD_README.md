# Building Sweet Progress.exe

This guide explains how to create the `Sweet Progress.exe` executable file from the source code.

## 🚀 Quick Start (Windows)

### Option 1: Use the Batch File (Easiest)
1. Double-click `build.bat`
2. Wait for the build to complete
3. Find `Sweet Progress.exe` in the `dist/` folder

### Option 2: Use Python Script
1. Open Command Prompt in the project folder
2. Run: `python build_exe.py`
3. Find `Sweet Progress.exe` in the `dist/` folder

## 🔧 Manual Build

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Steps
1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   pyinstaller --onefile --windowed --name="Sweet Progress" --icon=icon-v2.png --add-data="icon-v2.png;." --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox --clean program.py
   ```

3. **Find your executable**:
   - Look in the `dist/` folder
   - The file will be named `Sweet Progress.exe`

## 📁 Output

After building, you'll find:
- `dist/Sweet Progress.exe` - Your executable file
- `dist/icon-v2.png` - Application icon (copied for reference)
- `build/` folder - Build cache (can be deleted)

## ⚠️ Troubleshooting

### Common Issues

**"pyinstaller is not recognized"**
- Install PyInstaller: `pip install pyinstaller`
- Make sure Python and pip are in your PATH

**Build fails with import errors**
- Try adding more hidden imports as needed
- Check that all required files are present

**Executable is very large**
- This is normal for PyInstaller one-file builds
- The executable includes Python runtime and all dependencies

**Antivirus flags the executable**
- This is a false positive common with PyInstaller
- Add the folder to your antivirus exclusions

## 🎯 Build Options Explained

- `--onefile`: Creates a single executable file
- `--windowed`: No console window when running
- `--name`: Sets the executable name
- `--icon`: Sets the application icon
- `--add-data`: Includes additional files
- `--hidden-import`: Ensures modules are included
- `--clean`: Cleans cache before building

## 📝 Notes

- The first build may take several minutes
- Subsequent builds are faster due to caching
- The executable will be larger than the source code
- Test the executable on a clean system to ensure it works

## 🆘 Need Help?

- Check the [main README](README.md)
- Open an [issue on GitHub](https://github.com/Smothyze/sweet-progress/issues)
- Check [PyInstaller documentation](https://pyinstaller.org/)
