#!/usr/bin/env python3
"""
Continuous process tracker that updates the JSON file every 10 seconds.
"""
import subprocess
import json
import os
import time
from datetime import datetime

PROCESSES_FILE = 'AI_Employee_Vault/.running_processes.json'

WATCHER_NAMES = [
    'gmail-watcher',
    'calendar-watcher',
    'slack-watcher',
    'odoo-watcher',
    'filesystem-watcher',
    'whatsapp-watcher'
]

MONITOR_NAMES = [
    'email-approval-monitor',
    'calendar-approval-monitor',
    'slack-approval-monitor',
    'linkedin-approval-monitor',
    'twitter-approval-monitor',
    'facebook-approval-monitor',
    'instagram-approval-monitor'
]

ALL_NAMES = WATCHER_NAMES + MONITOR_NAMES

def find_running_processes():
    """Find all running AI Employee processes."""
    running = []

    try:
        # Get all Python processes
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'python.exe' not in line:
                    continue

                # Check if it's one of our processes
                for name in ALL_NAMES:
                    if name in line.replace('-', '_'):
                        running.append({
                            'name': name,
                            'status': 'online',
                            'type': 'monitor' if 'monitor' in name else 'watcher',
                            'timestamp': datetime.now().isoformat()
                        })
                        break

    except Exception as e:
        print(f"Error: {e}")

    return running

def main():
    print("Process Tracker Started - Logging every 10 seconds...")
    print("Press Ctrl+C to stop")

    try:
        while True:
            # Get running processes
            running = find_running_processes()

            # Save to JSON file
            os.makedirs(os.path.dirname(PROCESSES_FILE), exist_ok=True)

            with open(PROCESSES_FILE, 'w') as f:
                json.dump(running, f, indent=2)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Tracked {len(running)} processes: " +
                  ', '.join([f"{p['type']}: {p['name']}" for p in running]))

            # Wait 10 seconds
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nProcess Tracker Stopped")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
