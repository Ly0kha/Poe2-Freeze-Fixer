# POE2CrashFixer

**POE2CrashFixer** is a tool to fix freezing issues in **Path of Exile 2** caused by the **Windows 24H2 update** and **AMD X3D CPUs**. The freezes happen during loading screens and can lock up your system. This tool dynamically adjusts CPU core usage to prevent these crashes.

---

## Features

- Automatically detects the game process.
- Monitors the game's `client.txt` log file for loading events.
- Disables (parks) some CPU cores during loading to prevent freezing.
- Restores full CPU usage after loading is complete.
- Lightweight and runs in the background.

---

## Requirements

- **Windows** (requires Administrator permissions).
- **Python 3.7 or newer** (automatically installed via `install.bat`).

---

## Installation

1. **Download the tool**:
   - Click the **Code** button and select **Download ZIP**.
   - Extract the ZIP file to a folder on your computer.

2. **Install the tool**:
   - Open the folder where you extracted the files.
   - Right-click on `install.bat` and select **Run as Administrator**.
   - This will install Python (if needed) and set up all required dependencies.

---

## How to Use

1. **Run the tool**:
   - After installation, right-click on `run.bat` and select **Run as Administrator**.
   - The tool will:
     - Detect the running game process.
     - Monitor `client.txt` for loading events.
     - Adjust CPU usage dynamically.

2. **Logs**:
   - The console will display real-time logs:
     - **Green**: Everything is working.
     - **Yellow**: Warnings.
     - **Red**: Errors.

---

## Example Logs

**During loading**:
[INFO] Detected 16 CPU cores. [INFO] PathOfExileSteam.exe process found. [INFO] Loading detected. Parking cores -> allowed cores: [0, 1, 2, 3]


**After loading**:
[INFO] Loading complete. Restoring all cores -> allowed cores: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

---

## Troubleshooting

1. **Run as Administrator**:
   - The tool needs Administrator permissions to change CPU settings.

2. **Log file not found**:
   - Ensure the game has a `logs/client.txt` file.
   - Restart the game if the file doesn’t exist.

3. **Python not installed**:
   - Run `install.bat` to ensure Python and all dependencies are installed.

---
