@echo off
setlocal enabledelayedexpansion

:: Check if Python is installed
echo Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Downloading and installing Python...
    
    :: Set Python installer URL and temp download path
    set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
    set PYTHON_INSTALLER=%TEMP%\python-installer.exe
    
    :: Download Python installer
    powershell -Command "Invoke-WebRequest -Uri !PYTHON_INSTALLER_URL! -OutFile !PYTHON_INSTALLER!" || (
        echo Failed to download Python installer. Exiting...
        pause
        exit /b 1
    )
    
    :: Install Python silently
    echo Installing Python silently...
    !PYTHON_INSTALLER! /quiet InstallAllUsers=1 PrependPath=1 || (
        echo Python installation failed. Exiting...
        pause
        exit /b 1
    )
    
    echo Python installed successfully.
)

:: Ensure Python is available in the current session
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python312\

:: Upgrade pip and install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

:: Build standalone executable
echo Building standalone executable...
pyinstaller --onefile poe2uncrashfixer.py

echo Installation complete! You can find the exe in the "dist" folder.
pause
