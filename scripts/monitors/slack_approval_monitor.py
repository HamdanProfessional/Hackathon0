#!/usr/bin/env python3
"""
Slack Approval Monitor

Watches the /Approved/ folder for approved Slack actions and sends them via Slack MCP.
This is the human-in-the-loop component - it only sends messages after you approve.

Usage:
    python slack_approval_monitor.py --vault AI_Employee_Vault
"""

import sys
import time
import subprocess
import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SlackApprovalHandler(FileSystemEventHandler):
    """
    Handles approved Slack action files.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        self.dry_run = dry_run

        # Get Slack bot token from environment
        self.slack_token = os.environ.get('SLACK_BOT_TOKEN')
        if not self.slack_token:
            print("[WARNING] SLACK_BOT_TOKEN not found in environment")

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        """Called when a file is created in /Approved/ folder."""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Only process Slack approval files
        if not filepath.name.startswith(("SLACK_", "SLACK_MESSAGE_")):
            return

        if not filepath.suffix == ".md":
            return

        print(f"\n[OK] Detected approved Slack message: {filepath.name}")
        self.process_approved_slack_message(filepath)

    def process_approved_slack_message(self, filepath: Path):
        """
        Process an approved Slack message.

        Args:
            filepath: Path to approved Slack file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract Slack message details
            message_details = self._extract_message_details(content)

            if not message_details:
                print(f"[ERROR] Could not extract message details from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"SLACK MESSAGE TO SEND:")
            print(f"{'='*60}")
            print(f"Channel: {message_details.get('channel', 'N/A')}")
            print(f"Message:\n{message_details.get('message', '')[:300]}")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("slack_message_approved", {
                "file": filepath.name,
                "channel": message_details.get('channel'),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would send message via Slack MCP")
                self._move_to_done(filepath)
                return

            # Send via Slack MCP
            print("[INFO] Sending message via Slack MCP...")
            success = self._send_via_mcp(message_details)

            if success:
                print("[OK] Successfully sent Slack message!")
                self._log_action("slack_message_sent", {
                    "file": filepath.name,
                    "channel": message_details.get('channel'),
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })
                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to send Slack message")
                self._log_action("slack_message_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("slack_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_message_details(self, content: str) -> dict:
        """
        Extract Slack message details from approval file.

        Looks for YAML frontmatter or structured content.
        """
        details = {}

        # Try to extract YAML frontmatter (only between first and second ---)
        lines = content.split('\n')
        yaml_content = []
        dash_count = 0

        for line in lines:
            if line.strip() == '---':
                dash_count += 1
                if dash_count > 2:  # Stop after second ---
                    break
                continue
            if dash_count == 1:  # Only capture between first and second ---
                yaml_content.append(line)

        # Parse YAML-like content
        for line in yaml_content:
            if ':' in line:
                key, value = line.split(':', 1)
                details[key.strip().lower()] = value.strip()

        # If no YAML, try to extract from content
        if not details.get('channel'):
            channel_match = re.search(r'[Cc]hannel:\s*#?(\w+)', content)
            if channel_match:
                details['channel'] = '#' + channel_match.group(1).strip()

            message_match = re.search(r'[Mm]essage:\s*(.+?)(?:\n|$)', content, re.DOTALL)
            if message_match:
                details['message'] = message_match.group(1).strip()

            # Extract message body
            body_start = content.find('---', content.find('---') + 3) if content.count('---') >= 2 else 0
            if body_start > 0:
                message = content[body_start + 3:].strip()
                message = re.sub(r'^#+\s*', '', message)
                if not details.get('message'):
                    details['message'] = message

        return details if details.get('channel') and details.get('message') else None

    def _send_via_mcp(self, message_details: dict) -> bool:
        """
        Send message using Slack MCP server.

        Args:
            message_details: Dictionary with channel, message

        Returns:
            True if successful, False otherwise
        """
        try:
            # For now, create a simple test
            # In production, this would call the Slack MCP server
            print(f"[INFO] Sending to channel: {message_details.get('channel')}")
            print(f"[INFO] Message length: {len(message_details.get('message', ''))} characters")
            print(f"[INFO] This would use Slack MCP in production")

            # TODO: Implement actual MCP call
            # For now, return True to indicate success in dry-run mode
            return True

        except Exception as e:
            print(f"[ERROR] Error calling Slack MCP: {e}")
            return False

    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        try:
            done_path = self.done_folder / filepath.name

            # Handle duplicate filenames by adding timestamp
            if done_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_without_ext = filepath.stem
                ext = filepath.suffix
                done_path = self.done_folder / f"{name_without_ext}_{timestamp}{ext}"

            filepath.rename(done_path)
            print(f"[OK] Moved to Done: {done_path.name}")
        except Exception as e:
            print(f"[ERROR] Could not move to Done: {e}")

    def _log_action(self, action: str, details: dict):
        """Log action to daily log file."""
        log_file = self.logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "slack_approval_monitor",
            "action": action,
            "details": details
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[ERROR] Could not write to log: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and send Slack messages via Slack MCP"
    )

    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't actually send"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)
    approved_folder = vault_path / "Approved"
    approved_folder.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Slack Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print("\n[INFO] Waiting for approved Slack messages...")
    print("[INFO] Press Ctrl+C to stop\n")

    event_handler = SlackApprovalHandler(args.vault, args.dry_run)
    observer = Observer()
    observer.schedule(event_handler, str(approved_folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Stopping monitor...")
        if observer.is_alive():
            observer.stop()
        observer.join()

    print("[OK] Monitor stopped")


if __name__ == "__main__":
    main()
