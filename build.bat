@echo off
echo Sweet Progress - Build Script
echo =============================
echo.

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building Sweet Progress.exe...
pyinstaller --onefile --windowed --name="Sweet Progress" --icon=icon-v2.png --add-data="icon-v2.png;." --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox --clean program.py

echo.
if exist "dist\Sweet Progress.exe" (
    echo Build completed successfully!
    echo Executable created at: dist\Sweet Progress.exe
    echo.
    echo Copying icon file to dist folder...
    copy "icon-v2.png" "dist\"
    echo.
    echo Ready for release! Check the dist folder.
) else (
    echo Build failed! Check the error messages above.
)

pause
