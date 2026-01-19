#!/usr/bin/env python3
"""
Dashboard Merger - Local Machine Only

Merges /Updates/ and /Signals/ from Cloud into Dashboard.md.
This is the single-writer rule implementation: Cloud writes to /Updates/,
Local merges into Dashboard.md.

Usage:
    python dashboard_merger.py --vault AI_Employee_Vault
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def merge_updates_to_dashboard(vault_path: str):
    """
    Merge /Updates/ and /Signals/ into Dashboard.md.

    Cloud writes updates to /Updates/ directory.
    Local reads updates and merges them into Dashboard.md.
    """
    vault = Path(vault_path)
    updates_dir = vault / 'Updates'
    signals_dir = vault / 'Signals'
    dashboard = vault / 'Dashboard.md'

    if not dashboard.exists():
        print(f"[ERROR] Dashboard.md not found at {dashboard}")
        return

    # Read current dashboard
    current_content = dashboard.read_text(encoding='utf-8')

    # Collect all updates
    updates = []
    update_files = []

    # Process /Updates/ directory
    if updates_dir.exists():
        for update_file in sorted(updates_dir.glob('*.md')):
            try:
                content = update_file.read_text(encoding='utf-8')
                updates.append({
                    'source': update_file.name,
                    'content': content,
                    'type': 'update'
                })
                update_files.append(update_file)
            except Exception as e:
                print(f"[ERROR] Could not read {update_file}: {e}")

    # Process /Signals/ directory (real-time alerts)
    if signals_dir.exists():
        for signal_file in sorted(signals_dir.glob('*.md')):
            try:
                content = signal_file.read_text(encoding='utf-8')
                updates.append({
                    'source': signal_file.name,
                    'content': content,
                    'type': 'signal'
                })
                update_files.append(signal_file)
            except Exception as e:
                print(f"[ERROR] Could not read {signal_file}: {e}")

    if not updates:
        print(f"[INFO] No updates or signals to merge")
        return

    print(f"[INFO] Found {len(updates)} updates/signals to merge")

    # Build new section
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_section = f"""

---

## Cloud Updates ({timestamp})

*Merged from Cloud VM via Git sync*

"""

    for update in updates:
        icon = '📡' if update['type'] == 'signal' else '📝'
        new_section += f"\n{icon} **{update['source']}**\n\n"
        new_section += f"{update['content']}\n\n"
        new_section += "---\n"

    # Append to dashboard
    updated_content = current_content + new_section
    dashboard.write_text(updated_content, encoding='utf-8')

    # Delete processed files
    for file in update_files:
        try:
            file.unlink()
            print(f"[OK] Processed: {file.name}")
        except Exception as e:
            print(f"[ERROR] Could not delete {file.name}: {e}")

    print(f"[OK] Merged {len(update_files)} updates into Dashboard.md")

    # Log merge action
    log_file = vault / 'Logs' / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'dashboard_merge',
        'updates_merged': len(updates),
        'sources': [u['source'] for u in updates]
    }

    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"[ERROR] Could not write log: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Merge Cloud updates into Dashboard.md (Local only)"
    )
    parser.add_argument(
        '--vault',
        default='AI_Employee_Vault',
        help='Path to Obsidian vault'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Dashboard Merger - Local Machine")
    print("=" * 60)
    print(f"Vault: {args.vault}")
    print()

    merge_updates_to_dashboard(args.vault)

    print()
    print("=" * 60)
    print("Dashboard Merger: Complete ✅")
    print("=" * 60)


if __name__ == '__main__':
    main()
