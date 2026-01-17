#!/usr/bin/env python3
"""
Dashboard Update Merger for Platinum Tier.

Merges updates from cloud into local Dashboard.md (single writer rule).

Cloud writes to Updates/ folder -> Local merges into Dashboard.md

This ensures Dashboard.md is only written by local agent, preventing conflicts.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DashboardUpdateMerger:
    """
    Merges cloud updates into local Dashboard.md.
    """

    def __init__(self, vault_path: str, local_mode: bool = True):
        """
        Initialize merger.

        Args:
            vault_path: Path to the vault
            local_mode: True if running on local machine (writes Dashboard.md)
        """
        self.vault_path = Path(vault_path)
        self.updates_path = self.vault_path / 'Updates'
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        self.local_mode = local_mode

    def get_pending_updates(self) -> list:
        """
        Get list of pending update files.

        Returns:
            List of Path objects for update files
        """
        if not self.updates_path.exists():
            return []

        updates = []
        for file in self.updates_path.glob('*.json'):
            updates.append(file)

        return sorted(updates, key=lambda p: p.stat().st_mtime)

    def process_health_update(self, update_file: Path) -> dict:
        """
        Process a health update file.

        Args:
            update_file: Path to the update file

        Returns:
            Update data dictionary
        """
        with open(update_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Processing health update: {update_file.name}")

        return data

    def merge_into_dashboard(self, updates: list):
        """
        Merge updates into Dashboard.md.

        Args:
            updates: List of update data dictionaries
        """
        # Only local machine writes to Dashboard.md
        if not self.local_mode:
            logger.info("Skipping Dashboard.md update (not in local mode)")
            return

        # Read current Dashboard.md
        dashboard_content = ""
        if self.dashboard_path.exists():
            with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()

        # Build update section
        update_section = "\n## Cloud Updates\n\n"
        update_section += f"_Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"

        # Process health updates
        health_updates = [u for u in updates if 'cloud_health' in u.get('source', '')]

        if health_updates:
            latest_health = health_updates[-1]['data']

            update_section += "### System Health\n\n"
            update_section += f"- **Hostname:** {latest_health.get('hostname', 'N/A')}\n"
            update_section += f"- **Uptime:** {latest_health.get('system', {}).get('uptime', 'N/A')}\n"
            update_section += f"- **CPU:** {latest_health.get('system', {}).get('cpu_percent', 0):.1f}%\n"
            update_section += f"- **Memory:** {latest_health.get('memory', {}).get('percent', 0):.1f}%\n"
            update_section += f"- **Disk:** {latest_health.get('disk', {}).get('percent', 0):.1f}%\n\n"

            # Process status
            update_section += "### Cloud Processes\n\n"
            processes = latest_health.get('processes', {})
            for name, status in processes.items():
                if name == 'error':
                    continue
                status_emoji = "✅" if status.get('status') == 'online' else "❌"
                update_section += f"- {status_emoji} **{name}**: {status.get('status', 'unknown')} "
                update_section += f"(CPU: {status.get('cpu', 0):.1f}%, "
                update_section += f"Mem: {status.get('memory_mb', 0):.1f}MB)\n"

            # Alerts
            alerts = latest_health.get('alerts', [])
            if alerts:
                update_section += "\n### Alerts\n\n"
                for alert in alerts:
                    update_section += f"- ⚠️ {alert}\n"

        # Check if update section already exists
        if "## Cloud Updates" in dashboard_content:
            # Replace existing section
            lines = dashboard_content.split('\n')
            new_lines = []
            in_update_section = False

            for line in lines:
                if line.startswith("## Cloud Updates"):
                    new_lines.append(update_section.strip())
                    in_update_section = True
                    # Skip existing update section content
                    continue
                if in_update_section:
                    if line.startswith("## ") and not line.startswith("## Cloud Updates"):
                        in_update_section = False
                        new_lines.append(line)
                    continue
                new_lines.append(line)

            dashboard_content = '\n'.join(new_lines)
        else:
            # Append to end
            dashboard_content += "\n" + update_section

        # Write updated Dashboard.md
        with open(self.dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

        logger.info(f"Dashboard.md updated with {len(updates)} updates")

    def archive_processed_updates(self, updates: list):
        """
        Archive processed updates.

        Args:
            updates: List of update dictionaries
        """
        archive_dir = self.vault_path / 'Logs' / 'Processed_Updates'
        archive_dir.mkdir(parents=True, exist_ok=True)

        for update in updates:
            source_file = update.get('source_file')
            if source_file and Path(source_file).exists():
                # Move to archive
                archive_path = archive_dir / Path(source_file).name
                Path(source_file).rename(archive_path)
                logger.info(f"Archived update: {archive_path.name}")

    def run_once(self):
        """Run a single merge cycle."""
        try:
            # Get pending updates
            update_files = self.get_pending_updates()

            if not update_files:
                logger.info("No pending updates")
                return

            logger.info(f"Found {len(update_files)} pending updates")

            # Process updates
            updates = []
            for update_file in update_files:
                try:
                    data = self.process_health_update(update_file)
                    updates.append({
                        'source': update_file.name,
                        'source_file': str(update_file),
                        'data': data
                    })
                except Exception as e:
                    logger.error(f"Failed to process update {update_file}: {e}")

            # Merge into Dashboard
            if updates:
                self.merge_into_dashboard(updates)

                # Archive processed updates
                self.archive_processed_updates(updates)

        except Exception as e:
            logger.error(f"Merge cycle failed: {e}")

    def run_continuous(self, interval: int = 60):
        """
        Run continuous merge loop.

        Args:
            interval: Check interval in seconds
        """
        logger.info(f"Starting dashboard update merger (interval: {interval}s)")

        import time
        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                logger.info("Dashboard merger stopped by user")
                break
            except Exception as e:
                logger.error(f"Dashboard merger error: {e}")

            time.sleep(interval)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Merge dashboard updates from cloud")
    parser.add_argument(
        '--vault',
        default=os.getenv('VAULT_PATH', 'AI_Employee_Vault'),
        help='Path to vault'
    )
    parser.add_argument(
        '--local-mode',
        action='store_true',
        default=True,
        help='Run in local mode (writes to Dashboard.md)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (for continuous mode)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )

    args = parser.parse_args()

    merger = DashboardUpdateMerger(args.vault, args.local_mode)

    if args.once:
        merger.run_once()
    else:
        merger.run_continuous(args.interval)


if __name__ == '__main__':
    main()
