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

GAME_PROCESS_NAMES = ["PathOfExileSteam.exe"]
LOG_FILE_NAME = "client.txt"

START_GAME_PATTERN = re.compile(
    r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+\d+\s+[A-Fa-f0-9]+\s+\[INFO\s+Client\s+\d+\]\s+\[ENGINE\]\s+Init\s*$"
)
START_LOAD_PATTERN = re.compile(
    r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+\d+\s+[A-Fa-f0-9]+\s+\[INFO\s+Client\s+\d+\]\s+\[SHADER\]\s+Delay:\s+OFF\s*$"
)
END_LOAD_PATTERN = re.compile(
    r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+\d+\s+[A-Fa-f0-9]+\s+\[INFO\s+Client\s+\d+\]\s+\[SHADER\]\s+Delay:\s+ON\s*$"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("POE2DynamicCoreFixer")

stop_flag = False
is_loading = False
NUM_CORES = psutil.cpu_count(logical=True) or 1
logger.info(f"Detected {NUM_CORES} total CPU cores.")

def calculate_cores():
    rest_cores = max(1, int(NUM_CORES * 0.8))
    load_cores = NUM_CORES
    return rest_cores, load_cores

REST_CORES, LOAD_CORES = calculate_cores()
logger.info(f"Default core configuration: Resting with {REST_CORES} cores, Loading with {LOAD_CORES} cores.")

def get_game_process():
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"] in GAME_PROCESS_NAMES:
                return proc
        except Exception:
            continue
    return None

def park_cores(cores_to_use: int):
    proc = get_game_process()
    if not proc:
        logger.error("Game process not found while trying to set CPU affinity.")
        return
    try:
        allowed = list(range(min(cores_to_use, NUM_CORES)))
        proc.cpu_affinity(allowed)
        logger.info(f"Active cores: {allowed}")
    except Exception as e:
        logger.error(f"Failed to set CPU affinity: {e}")

def on_loading_start():
    global is_loading
    is_loading = True
    logger.info(f"Loading start detected. Enabling {LOAD_CORES} cores for faster loading.")
    park_cores(LOAD_CORES)

def on_loading_end():
    global is_loading
    is_loading = False
    logger.info(f"Loading end detected. Returning to {REST_CORES} cores at rest.")
    park_cores(REST_CORES)

def get_log_file_path():
    proc = get_game_process()
    if not proc:
        logger.error("Could not find game process.")
        return None
    try:
        game_dir = proc.cwd()
        if not game_dir:
            logger.error("Could not determine game directory from process.")
            return None
        log_path = os.path.join(game_dir, "logs", LOG_FILE_NAME)
        if not os.path.exists(log_path):
            logger.error(f"Log file not found: {log_path}")
            return None
        return log_path
    except Exception as e:
        logger.error(f"Could not construct log path: {e}")
        return None

def monitor_log_file(path):
    on_loading_end()
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)
            while not stop_flag:
                line = f.readline()
                if not line:
                    time.sleep(0.05)
                    continue
                line = line.strip()
                if START_GAME_PATTERN.match(line) or START_LOAD_PATTERN.match(line):
                    on_loading_start()
                elif END_LOAD_PATTERN.match(line):
                    on_loading_end()
    except FileNotFoundError:
        logger.error(f"Log file not found at runtime: {path}")
    except Exception as e:
        logger.error(f"Error reading log file: {e}")

def main():
    log_path = get_log_file_path()
    if not log_path:
        logger.critical("Exiting. Log file is not found or game not detected.")
        sys.exit(1)
    logger.info(f"Monitoring log file: {log_path}")
    t = threading.Thread(target=monitor_log_file, args=(log_path,), daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        global stop_flag
        stop_flag = True
        logger.info("Exiting...")

if __name__ == "__main__":
    main()
