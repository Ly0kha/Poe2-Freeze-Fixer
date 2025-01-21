@echo off
echo Running the script...
python poe2crashfixer.py
if %errorlevel% neq 0 (
    echo Failed to run the script.
    pause
    exit /b 1
)
pauses