#!/usr/bin/env python3
"""
Migration Agent - Migrate vault data and configs
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime


def backup_path(path: Path):
    """Backup a path"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = path.parent / f"{path.name}_backup_{timestamp}"

    if path.is_dir():
        shutil.copytree(path, backup)
    else:
        shutil.copy2(path, backup)

    print(f"✅ Backed up to: {backup}")
    return backup


def migrate_files(source: Path, target: Path):
    """Migrate files from source to target"""
    print(f"\nMigrating {source} -> {target}")

    # Backup
    if target.exists():
        backup_path(target)

    # Move files
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
        print(f"✅ Migrated {len(list(target.glob('*')))} files")
    else:
        shutil.copy2(source, target)
        print(f"✅ Migrated: {target}")


def update_configs(old_path: str, new_path: str):
    """Update configs with new path"""
    print(f"\nUpdating configs: {old_path} -> {new_path}")

    pm2_config = Path('process-manager/pm2.config.js')
    if pm2_config.exists():
        content = pm2_config.read_text()
        content = content.replace(old_path, new_path)
        pm2_config.write_text(content)
        print("✅ Updated pm2.config.js")


def main():
    parser = argparse.ArgumentParser(description='Migration Agent')
    parser.add_argument('--source', required=True, help='Source path')
    parser.add_argument('--target', required=True, help='Target path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')

    args = parser.parse_args()

    print("🔄 Migration Agent\n")

    source = Path(args.source)
    target = Path(args.target)

    if not source.exists():
        print(f"❌ Source not found: {source}")
        return

    if args.dry_run:
        print(f"Would migrate {source} -> {target}")
        print("(Dry run - no changes made)")
    else:
        migrate_files(source, target)
        if source.is_dir() and source.name in ['vault', 'AI_Employee_Vault']:
            update_configs(str(source), str(target))

    print("\n✅ Migration complete")


if __name__ == '__main__':
    main()
