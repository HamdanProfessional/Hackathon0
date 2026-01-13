#!/usr/bin/env python3
"""
Deployment Agent - Deploy AI Employee to new machine
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_prerequisites():
    """Check system prerequisites"""
    print("Checking prerequisites...\n")

    checks = []

    # Python version
    result = subprocess.run(['python', '--version'], capture_output=True)
    python_version = result.stdout.decode()
    checks.append(('Python 3.13+', '3.13' in python_version or '3.14' in python_version))

    # Node.js
    result = subprocess.run(['node', '--version'], capture_output=True)
    node_ok = result.returncode == 0
    checks.append(('Node.js', node_ok))

    # PM2
    result = subprocess.run(['pm2', '--version'], capture_output=True)
    pm2_ok = result.returncode == 0
    checks.append(('PM2', pm2_ok))

    all_pass = True
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_pass = False

    return all_pass


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...\n")

    subprocess.run(['pip', 'install', 'slack-sdk', 'playwright'])
    subprocess.run(['npm', 'install', '-g', 'pm2'])
    subprocess.run(['playwright', 'install', 'chromium'])

    print("✅ Dependencies installed")


def main():
    parser = argparse.ArgumentParser(description='Deployment Agent')
    parser.add_argument('--check', action='store_true', help='Check prerequisites only')
    parser.add_argument('--install', action='store_true', help='Install dependencies')
    parser.add_argument('--full', action='store_true', help='Full deployment')

    args = parser.parse_args()

    print("🚀 Deployment Agent\n")

    if args.check or args.full:
        if not check_prerequisites():
            print("\n❌ Prerequisites check failed")
            sys.exit(1)

    if args.install or args.full:
        install_dependencies()

    print("\n✅ Deployment complete!")


if __name__ == '__main__':
    main()
