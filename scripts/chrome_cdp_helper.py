#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome CDP Helper - Ensures Chrome is running with CDP enabled.

Provides functionality to check if Chrome CDP is running and start it if needed.
"""

import os
import sys
import subprocess
import socket
from pathlib import Path

# Configuration
CDP_PORT = 9222
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\Users\User\AppData\Local\Google\Chrome\User Data"
STARTUP_SCRIPT = Path(__file__).parent.parent / "start_chrome.bat"


def is_chrome_cdp_running() -> bool:
    """Check if Chrome CDP is running on port 9222."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(("127.0.0.1", CDP_PORT))
            s.close()
        return True
    except:
        return False


def ensure_chrome_cdp() -> bool:
    """
    Ensure Chrome CDP is running.

    Returns:
        True if Chrome CDP is running, False otherwise
    """
    if is_chrome_cdp_running():
        print("[Chrome CDP] Already running on port 9222")
        return True

    print("[Chrome CDP] Not running - starting Chrome...")

    # Kill any existing Chrome processes first
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "chrome.exe", "/T"],
            capture_output=True,
            timeout=5
        )
    except:
        pass

    # Start Chrome using the batch script
    try:
        subprocess.Popen(
            ["cmd", "/c", str(STARTUP_SCRIPT)],
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

        # Wait for Chrome to start
        import time
        time.sleep(8)

        # Check if CDP is now running
        if is_chrome_cdp_running():
            print("[Chrome CDP] Successfully started Chrome CDP!")
            return True
        else:
            print("[Chrome CDP] Chrome started but CDP not ready yet")
            return False

    except Exception as e:
        print(f"[Chrome CDP] Error starting Chrome: {e}")
        return False


if __name__ == "__main__":
    if ensure_chrome_cdp():
        print("Chrome CDP is ready!")
    else:
        print("Failed to start Chrome CDP")
        sys.exit(1)
