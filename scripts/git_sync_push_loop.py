#!/usr/bin/env python3
"""
Git Sync Loop - Syncs every 10 seconds (Cloud version)
"""
import sys
import time
import subprocess
import os
from pathlib import Path

def main():
    vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"
    script_path = Path(__file__).parent / "git_sync_push.sh"

    print("[Git Sync Push] Starting 10-second sync loop...")
    print(f"[Git Sync Push] Vault: {vault_path}")

    while True:
        try:
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent
            )

            if result.returncode == 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Git push: SUCCESS")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Git push: FAILED - {result.stderr[:100]}")

        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Git push: ERROR - {e}")

        time.sleep(10)

if __name__ == "__main__":
    main()
