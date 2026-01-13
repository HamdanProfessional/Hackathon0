#!/usr/bin/env python3
"""
Monitoring Agent - Monitor system health
"""

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime


def check_pm2_processes():
    """Check PM2 process status"""
    print("PM2 Processes:\n")

    result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True)
    if result.returncode != 0:
        print("  ❌ PM2 not running")
        return []

    processes = json.loads(result.stdout)

    for proc in processes:
        name = proc['name']
        status = proc['pm2_env']['status']
        pid = proc.get('pid', 'N/A')
        cpu = proc.get('monit', {}).get('cpu', 'N/A')
        memory = proc.get('monit', {}).get('memory', 'N/A')

        status_icon = "✅" if status == "online" else "❌"
        print(f"  {status_icon} {name} (PID: {pid}, CPU: {cpu}%, MEM: {memory/1024/1024:.0f}MB if memory != 'N/A' else memory})")

    return processes


def check_vault_folders(vault_path: str = "AI_Employee_Vault"):
    """Check vault folder sizes"""
    vault = Path(vault_path)

    print(f"\nVault Folders ({vault_path}):\n")

    folders = ['Inbox', 'Needs_Action', 'Pending_Approval', 'Approved', 'Done', 'Logs']

    for folder in folders:
        folder_path = vault / folder
        if folder_path.exists():
            files = list(folder_path.glob('*'))
            size = sum(f.stat().st_size for f in files if f.is_file())
            print(f"  📁 {folder}: {len(files)} files ({size/1024:.1f}KB)")
        else:
            print(f"  ✗ {folder}: Not found")


def main():
    parser = argparse.ArgumentParser(description='Monitoring Agent')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Vault path')
    parser.add_argument('--dashboard', action='store_true', help='Generate dashboard')

    args = parser.parse_args()

    print("📊 System Health Monitor\n")
    print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    check_pm2_processes()
    check_vault_folders(args.vault)

    print("\n✅ Health check complete")


if __name__ == '__main__':
    main()
