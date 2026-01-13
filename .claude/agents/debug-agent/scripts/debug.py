#!/usr/bin/env python3
"""
Debug Agent - Analyze logs and suggest fixes
"""

import argparse
import re
from pathlib import Path
from datetime import datetime


ERROR_PATTERNS = {
    'auth_error': {
        'patterns': [
            r'Authentication failed',
            r'Invalid credentials',
            r'401 Unauthorized',
            r'auth.*error'
        ],
        'solution': 'Check credentials in .env or token files. Refresh OAuth tokens if expired.'
    },
    'rate_limit': {
        'patterns': [
            r'429',
            r'rate.*limit',
            r'too.*many.*requests'
        ],
        'solution': 'Implement exponential backoff. Reduce check interval. Use rate limiting headers.'
    },
    'connection_error': {
        'patterns': [
            r'Connection.*timeout',
            r'Network.*error',
            r'Failed to establish'
        ],
        'solution': 'Check internet connection. Verify API endpoint URL. Increase timeout value.'
    },
    'permission_error': {
        'patterns': [
            r'Permission denied',
            r'Access.*denied',
            r'403 Forbidden'
        ],
        'solution': 'Check file permissions. Verify API scopes. Ensure vault path is correct.'
    },
    'import_error': {
        'patterns': [
            r'ModuleNotFoundError',
            r'ImportError',
            r'No module named'
        ],
        'solution': 'Install missing dependencies: pip install -r requirements.txt'
    }
}


def analyze_log(log_file: Path):
    """Analyze log file for errors"""
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        return

    content = log_file.read_text()
    errors_found = []

    for error_type, config in ERROR_PATTERNS.items():
        for pattern in config['patterns']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                errors_found.append({
                    'type': error_type,
                    'count': len(matches),
                    'solution': config['solution']
                })

    return errors_found


def check_pm2_process(process_name: str):
    """Check PM2 process status"""
    import subprocess

    try:
        result = subprocess.run(
            ['pm2', 'jlist'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("❌ PM2 not running")
            return

        import json
        processes = json.loads(result.stdout)

        for proc in processes:
            if proc['name'] == process_name:
                status = proc['pm2_env']['status']
                if status == 'online':
                    print(f"✅ {process_name} is running (PID: {proc['pid']})")
                else:
                    print(f"❌ {process_name} status: {status}")

                    if status == 'errored':
                        print("\n📋 Recent errors:")
                        print(proc['pm2_env'].get('pm_err_log_path'))

                return

        print(f"❌ Process {process_name} not found in PM2")

    except Exception as e:
        print(f"❌ Error checking PM2: {e}")


def main():
    parser = argparse.ArgumentParser(description='Debug Agent')
    parser.add_argument('process', nargs='?', help='Process name to debug')
    parser.add_argument('--log', help='Specific log file to analyze')
    parser.add_argument('--check-all', action='store_true',
                       help='Check all PM2 processes')

    args = parser.parse_args()

    print("🔍 Debug Agent")
    print()

    if args.check_all:
        # Check all PM2 processes
        print("Checking all PM2 processes...\n")
        check_pm2_process("*")

    elif args.process:
        # Check specific process
        print(f"Checking {args.process}...\n")
        check_pm2_process(args.process)

        # Analyze logs
        log_path = Path(f"~/.pm2/logs/{args.process}-error.log").expanduser()
        if log_path.exists():
            print(f"\n📋 Analyzing logs: {log_path}\n")
            errors = analyze_log(log_path)

            if errors:
                print("Issues found:")
                for error in errors:
                    print(f"\n⚠️  {error['type'].replace('_', ' ').title()}")
                    print(f"   Occurrences: {error['count']}")
                    print(f"   💡 Solution: {error['solution']}")
            else:
                print("✅ No errors detected in logs")
        else:
            print(f"Log file not found: {log_path}")

    elif args.log:
        # Analyze specific log file
        print(f"Analyzing {args.log}...\n")
        errors = analyze_log(Path(args.log))

        if errors:
            print("Issues found:")
            for error in errors:
                print(f"\n⚠️  {error['type']}")
                print(f"   Count: {error['count']}")
                print(f"   💡 {error['solution']}")
        else:
            print("✅ No errors detected")

    else:
        print("Usage:")
        print("  debug.py <process_name>")
        print("  debug.py --log <log_file>")
        print("  debug.py --check-all")


if __name__ == '__main__':
    main()
