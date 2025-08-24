#!/usr/bin/env python3
"""
Build script for creating Sweet Progress.exe using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building Sweet Progress.exe...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=Sweet Progress",        # Executable name
        "--icon=icon-v2.png",          # Application icon
        "--add-data=icon-v2.png;.",    # Include icon file
        "--hidden-import=tkinter",      # Ensure tkinter is included
        "--hidden-import=tkinter.ttk",  # Include ttk widgets
        "--hidden-import=tkinter.filedialog",  # Include file dialogs
        "--hidden-import=tkinter.messagebox",  # Include message boxes
        "--clean",                      # Clean cache before building
        "program.py"                    # Main script
    ]
    
    try:
        subprocess.check_call(cmd)
        print("Build completed successfully!")
        
        # Check if executable was created
        exe_path = Path("dist/Sweet Progress.exe")
        if exe_path.exists():
            print(f"Executable created at: {exe_path.absolute()}")
            
            # Copy icon to dist folder for reference
            if Path("icon-v2.png").exists():
                shutil.copy2("icon-v2.png", "dist/")
                print("Icon file copied to dist folder")
        else:
            print("Error: Executable not found in dist folder")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)

def main():
    """Main build process"""
    print("Sweet Progress - Build Script")
    print("=" * 40)
    
    # Install PyInstaller if needed
    install_pyinstaller()
    
    # Build executable
    build_executable()
    
    print("\nBuild process completed!")
    print("Check the 'dist' folder for your executable.")

if __name__ == "__main__":
    main()
