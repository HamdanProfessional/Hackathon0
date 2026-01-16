#!/usr/bin/env python3
"""
Simple process tracker for AI Employee dashboard.
Uses wmi command on Windows to track running processes.
"""
import subprocess
import json
import os
from datetime import datetime

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

def get_running_processes():
    """Get all running Python processes related to AI Employee using WMIC on Windows."""
    running = []

    # Try using tasklist with wmic to get process info
    try:
        # Get all Python processes
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True,
            text=True,
            check=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')

            # Skip header
            for line in lines[1:]:  # Skip header line
                if not line.strip():
                    continue

                parts = line.split(',')
                if len(parts) < 2:
                    continue

                pid = parts[1].strip() if len(parts) > 1 else ''
                cmdline = parts[-1].strip() if len(parts) > 5 else ''

                if not cmdline or 'python.exe' not in cmdline.lower():
                    continue

                # Check if it's one of our processes
                for name in ALL_NAMES:
                    if name in cmdline:
                        # Parse CPU and memory from tasklist (format is like "1234" and parseable)
                        try:
                            mem_str = parts[4].strip() if len(parts) > 4 else '0'
                            memory = float(mem_str.replace(',', '')) if mem_str.replace(',', '') else 0
                        except:
                            memory = 0

                        running.append({
                            'name': name,
                            'type': 'monitor' if 'monitor' in name else 'watcher',
                            'pid': int(pid) if pid else 0,
                            'status': 'online',
                            'cpu': 0,  # tasklist doesn't provide CPU by default
                            'memory': memory / 1024,  # Convert KB to MB
                            'uptime': datetime.now().isoformat(),
                            'lastError': None
                        })
                        break
    except Exception as e:
        print(f"Error getting processes: {e}", file=sys.stderr)

    return running

def get_wmi_process_info(pid):
    """Get detailed info about a process using WMIC."""
    try:
        result = subprocess.run(
            ['wmic', 'PROCESS', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/Value'],
            capture_output=True,
            text=True,
            check=True
        )

        if result.returncode == 0:
            return result.stdout.strip()
        return ""
    except:
        return ""

if __name__ == '__main__':
    processes = get_running_processes()
    print(f"Found {len(processes)} running AI Employee processes:")
    for p in processes:
        print(f"  - {p['type']}: {p['name']} (PID: {p['pid']}, Mem: {p['memory']:.1f} MB)")

    # Also check the dashboard server itself
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq node.exe', '/FI', 'IMAGENAME NOT LIKE python.exe'],
            capture_output=True,
            text=True,
            check=True
        )

        node_count = 0
        if result.returncode == 0:
            node_count = result.stdout.count('node.exe')

    except:
        pass

    print(f"\nDashboard Server: {'Running' if node_count > 0 else 'Not Detected'}")
    print(f"\nTo start watchers, run: START_ALL_WATCHERS.bat")
