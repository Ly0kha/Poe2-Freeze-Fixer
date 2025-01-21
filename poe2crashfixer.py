# -----------------------------------------------------------
# POE2CrashFixer
# Author: Ly0kha
# -----------------------------------------------------------
# Description:
# A Python tool to fix freezing issues in Path of Exile 2 caused by
# the Windows 24H2 update and AMD X3D CPUs. Dynamically adjusts CPU
# core affinity during game loading to prevent system lock-ups.
# -----------------------------------------------------------
# License:
# This script is provided as-is, with no warranty. Use it at your
# own risk. Redistribution or modification is permitted with
# proper attribution to the original author.
# -----------------------------------------------------------

import os
import re
import sys
import time
import psutil
import threading
import logging
from ctypes import windll

# ------------------- Configuration -------------------
GAME_PROCESS_NAMES = ["PathOfExileSteam.exe"]

start_game_pattern = re.compile(
    r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+\d+\s+[A-Fa-f0-9]+\s+\[INFO\s+Client\s+\d+\]\s+\[ENGINE\]\s+Init\s*$",
    re.IGNORECASE,
)
start_load_pattern = re.compile(
    r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+\d+\s+[A-Fa-f0-9]+\s+\[INFO\s+Client\s+\d+\]\s+\[SHADER\]\s+Delay:\s+OFF\s*$",
    re.IGNORECASE,
)
end_load_pattern = re.compile(
    r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+\d+\s+[A-Fa-f0-9]+\s+\[INFO\s+Client\s+\d+\]\s+\[SHADER\]\s+Delay:\s+ON\s*$",
    re.IGNORECASE,
)

try:
    CORES_TO_PARK = int(os.getenv("CORES_TO_PARK", 4))
except ValueError:
    CORES_TO_PARK = 4

logging.basicConfig(level=logging.DEBUG, format="%(message)s")
logger = logging.getLogger("POE2CrashFixer")

class Color:
    INFO = "\033[32m"
    WARN = "\033[33m"
    ERROR = "\033[31m"
    RESET = "\033[0m"

is_loading = False
stop_flag = False

# ------------------- Functions -------------------

def get_number_processors():
    num = psutil.cpu_count(logical=True)
    if num is None:
        logger.error(f"{Color.ERROR}Cannot detect CPU cores.{Color.RESET}")
        sys.exit(1)
    proc = psutil.Process()
    try:
        proc.cpu_affinity(list(range(num)))
        return num
    except:
        pass
    for i in range(num, 0, -1):
        try:
            proc.cpu_affinity(list(range(i)))
            return i
        except:
            continue
    logger.error(f"{Color.ERROR}Cannot finalize CPU core detection.{Color.RESET}")
    sys.exit(1)

NUM_CORES = get_number_processors()
logger.info(f"{Color.INFO}Detected {NUM_CORES} processors.{Color.RESET}")

def get_game_process():
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() in [x.lower() for x in GAME_PROCESS_NAMES]:
                return proc
        except:
            pass
    return None

def get_game_directory():
    proc = get_game_process()
    if proc:
        try:
            return proc.cwd()
        except Exception as e:
            logger.error(f"{Color.ERROR}Failed to get game directory: {e}{Color.RESET}")
    return None

def get_log_file_path():
    game_directory = get_game_directory()
    if game_directory:
        client_txt_path = os.path.join(game_directory, "logs", "client.txt")
        if os.path.exists(client_txt_path):
            return client_txt_path
        else:
            logger.error(f"{Color.ERROR}Log file not found in detected game directory: {client_txt_path}{Color.RESET}")
    else:
        logger.error(f"{Color.ERROR}Failed to detect game directory. Is the game running?{Color.RESET}")
    return None

def park_cores():
    global is_loading
    allowed = list(range(max(0, NUM_CORES - CORES_TO_PARK)))
    proc = get_game_process()
    if proc:
        try:
            proc.cpu_affinity(allowed)
            logger.info(f"{Color.INFO}Parked cores -> {allowed}{Color.RESET}")
            is_loading = True
        except Exception as e:
            logger.error(f"{Color.ERROR}Failed to park cores: {e}{Color.RESET}")
    else:
        logger.error(f"{Color.ERROR}No game process found for parking.{Color.RESET}")

def resume_cores():
    global is_loading
    allowed = list(range(NUM_CORES))
    proc = get_game_process()
    if proc:
        try:
            proc.cpu_affinity(allowed)
            logger.info(f"{Color.INFO}Resumed full cores -> {allowed}{Color.RESET}")
            is_loading = False
        except Exception as e:
            logger.error(f"{Color.ERROR}Failed to resume cores: {e}{Color.RESET}")
    else:
        logger.error(f"{Color.ERROR}No game process found for resuming.{Color.RESET}")

def monitor_log_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)
            while not stop_flag:
                line = f.readline()
                if not line:
                    time.sleep(0.02)
                    continue
                line = line.strip()
                if start_game_pattern.match(line) or start_load_pattern.match(line):
                    logger.info(f"{Color.INFO}Loading event detected.{Color.RESET}")
                    park_cores()
                elif end_load_pattern.match(line):
                    logger.info(f"{Color.INFO}End loading event detected.{Color.RESET}")
                    resume_cores()
    except FileNotFoundError:
        logger.error(f"{Color.ERROR}Log file not found: {path}{Color.RESET}")
    except Exception as e:
        logger.error(f"{Color.ERROR}Error reading log: {e}{Color.RESET}")

def main():
    log_path = get_log_file_path()
    if not log_path:
        sys.exit(f"{Color.ERROR}Could not find the game's log file. Exiting...{Color.RESET}")
    t = threading.Thread(target=monitor_log_file, args=(log_path,), daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        global stop_flag
        stop_flag = True
        logger.info(f"{Color.INFO}Exiting...{Color.RESET}")

# ------------------- Entry Point -------------------

if __name__ == "__main__":
    main()
