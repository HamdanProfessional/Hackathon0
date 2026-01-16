#!/usr/bin/env python3
"""
Simple process tracker for AI Employee dashboard.
Tracks running Python processes for watchers and monitors.
"""
import os
import psutil
import json
from datetime import datetime

WATCHER_PROCESSES = [
    {'name': 'gmail-watcher', 'module': 'watchers.gmail_watcher', 'file': 'run_gmail_watcher.py'},
    {'name': 'calendar-watcher', 'module': 'watchers.calendar_watcher', 'file': 'run_calendar_watcher.py'},
    {'name': 'slack-watcher', 'module': 'watchers.slack_watcher', 'file': 'run_slack_watcher.py'},
    {'name': 'odoo-watcher', 'module': 'watchers.odoo_watcher', 'file': 'run_odoo_watcher.py'},
    {'name': 'filesystem-watcher', 'module': 'watchers.filesystem_watcher', 'file': 'run_filesystem_watcher.py'},
    {'name': 'whatsapp-watcher', 'module': 'watchers.whatsapp_watcher', 'file': 'run_whatsapp_watcher.py'},
]

MONITOR_PROCESSES = [
    {'name': 'email-approval-monitor', 'file': 'scripts/monitors/email_approval_monitor.py'},
    {'name': 'calendar-approval-monitor', 'file': 'scripts/monitors/calendar_approval_monitor.py'},
    {'name': 'slack-approval-monitor', 'file': 'scripts/monitors/slack_approval_monitor.py'},
    {'name': 'linkedin-approval-monitor', 'file': 'scripts/social-media/linkedin_approval_monitor.py'},
    {'name': 'twitter-approval-monitor', 'file': 'scripts/social-media/twitter_approval_monitor.py'},
    {'name': 'facebook-approval-monitor', 'file': 'scripts/social-media/facebook-approval-monitor.py'},
    {
      'name': 'instagram-approval-monitor',
      'file': 'scripts/social-media/instagram-approval-monitor.py',
      'args': ['--vault', 'C:\\Users\\User\\Desktop\\AI_EMPLOYEE_APP\\AI_Employee_Vault']
    },
]

def get_running_processes():
    """Get all running Python processes related to AI Employee."""
    running = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'status', 'cpu', 'memory']):
        try:
            # Check if it's a Python process
            if not proc.info['name'] or 'python' not in proc.info['name'].lower():
                continue

            cmd = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            proc_path = cmd.split()[0] if cmd else ''

            # Check if it's related to our watchers/monitors
            for watcher in WATCHER_PROCESSES:
                if watcher['file'] in proc_path:
                    running.append({
                        'name': watcher['name'],
                        'type': 'watcher',
                        'pid': proc.info['pid'],
                        'status': 'online',
                        'cpu': proc.info['cpu'],
                        'memory': proc.info['memory'] / 1024 / 1024,
                        'uptime': proc.info['create_time']
                    })
                    break

            for monitor in MONITOR_PROCESSES:
                if monitor['file'] in proc_path:
                    running.append({
                        'name': monitor['name'],
                        'type': 'monitor',
                        'pid': proc.info['pid'],
                        'status': 'online',
                        'cpu': proc.info['cpu'] if 'cpu' in proc.info else 0,
                        'memory': proc.info['memory'] / 1024 / 1024 if 'memory' in proc.info else 0,
                        'uptime': proc.info['create_time']
                    })
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return running

if __name__ == '__main__':
    processes = get_running_processes()
    print(f"Found {len(processes)} running AI Employee processes:")
    for p in processes:
        print(f"  - {p['type']}: {p['name']} (PID: {p['pid']}, CPU: {p['cpu']:.1f}%, Mem: {p['memory']:.1f} MB)")
