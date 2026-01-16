#!/usr/bin/env python3
"""
Audit Log Cleanup - Maintenance Cron Job

This script runs weekly (Sundays at 3 AM) to clean up old audit logs
and maintain the 90-day retention policy.

Usage:
    python cleanup_old_logs.py --vault AI_Employee_Vault --days 90
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def cleanup_old_logs(vault_path: str, retention_days: int = 90):
    """
    Remove audit logs older than the retention period.

    Args:
        vault_path: Path to the AI Employee Vault
        retention_days: Number of days to retain logs (default: 90)
    """
    logs_path = Path(vault_path) / "Logs"

    if not logs_path.exists():
        print(f"[!] Logs directory does not exist: {logs_path}")
        return

    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    # Find all log files
    log_files = list(logs_path.glob("*.json"))

    if not log_files:
        print("[i] No log files found to clean up")
        return

    deleted_count = 0
    total_size_mb = 0

    for log_file in log_files:
        try:
            # Extract date from filename (format: YYYY-MM-DD.json)
            file_date_str = log_file.stem
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            # Check if file is older than retention period
            if file_date < cutoff_date:
                # Calculate file size before deletion
                file_size_mb = log_file.stat().st_size / (1024 * 1024)
                total_size_mb += file_size_mb

                # Delete the file
                log_file.unlink()
                deleted_count += 1
                print(f"[x] Deleted: {log_file.name} ({file_size_mb:.2f} MB)")

        except ValueError as e:
            print(f"[!] Skipping invalid filename: {log_file.name} - {e}")
            continue
        except Exception as e:
            print(f"[ERROR] Error deleting {log_file.name}: {e}")
            continue

    # Create summary
    timestamp = datetime.now(timezone.utc).isoformat()
    summary = {
        "cleanup_timestamp": timestamp,
        "retention_days": retention_days,
        "cutoff_date": cutoff_date.isoformat(),
        "logs_directory": str(logs_path),
        "log_files_found": len(log_files),
        "logs_deleted": deleted_count,
        "logs_remaining": len(log_files) - deleted_count,
        "space_freed_mb": round(total_size_mb, 2)
    }

    # Print summary
    print(f"\n[*] Cleanup Summary:")
    print(f"   Retention Policy: {retention_days} days")
    print(f"   Cutoff Date: {cutoff_date.strftime('%Y-%m-%d')}")
    print(f"   Log Files Found: {len(log_files)}")
    print(f"   Logs Deleted: {deleted_count}")
    print(f"   Logs Remaining: {len(log_files) - deleted_count}")
    print(f"   Space Freed: {total_size_mb:.2f} MB")
    print(f"   Cleanup Complete: {timestamp}")

    # Save summary to a cleanup log
    cleanup_log_path = logs_path / ".cleanup_history.jsonl"
    try:
        with open(cleanup_log_path, "a") as f:
            f.write(json.dumps(summary) + "\n")
    except Exception as e:
        print(f"[!] Could not write cleanup log: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up old audit logs beyond retention period"
    )
    parser.add_argument(
        "--vault",
        required=True,
        help="Path to the AI Employee Vault"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to retain logs (default: 90)"
    )

    args = parser.parse_args()

    # Validate vault path
    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"ERROR: Vault path does not exist: {vault_path}")
        sys.exit(1)

    # Validate retention days
    if args.days < 1:
        print("ERROR: Retention days must be at least 1")
        sys.exit(1)

    # Run the cleanup
    print(f"[*] Starting audit log cleanup (retention: {args.days} days)...")
    cleanup_old_logs(args.vault, args.days)
    print("[OK] Cleanup complete!")


if __name__ == "__main__":
    main()
