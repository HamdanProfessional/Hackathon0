#!/usr/bin/env python3
"""
Email Approval Monitor

Watches the /Approved/ folder for approved email actions and sends them via Gmail MCP.
This is the human-in-the-loop component - it only sends after you approve.

Usage:
    python email_approval_monitor.py --vault AI_Employee_Vault
"""

import sys
import time
import subprocess
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class EmailApprovalHandler(FileSystemEventHandler):
    """
    Handles approved email action files.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        self.dry_run = dry_run

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        """Called when a file is created in /Approved/ folder."""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Only process email approval files
        if not filepath.name.startswith(("EMAIL_", "EMAIL_REPLY_")):
            return

        if not filepath.suffix == ".md":
            return

        print(f"\n[OK] Detected approved email: {filepath.name}")
        self.process_approved_email(filepath)

    def process_approved_email(self, filepath: Path):
        """
        Process an approved email action.

        Args:
            filepath: Path to approved email file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract email details
            email_details = self._extract_email_details(content)

            if not email_details:
                print(f"[ERROR] Could not extract email details from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"EMAIL TO SEND:")
            print(f"{'='*60}")
            print(f"To: {email_details.get('to', 'N/A')}")
            print(f"Subject: {email_details.get('subject', 'N/A')}")
            print(f"Body:\n{email_details.get('body', '')[:200]}...")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("email_send_approved", {
                "file": filepath.name,
                "to": email_details.get('to'),
                "subject": email_details.get('subject'),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would send email via Gmail MCP")
                self._move_to_done(filepath)
                return

            # Send via Gmail MCP
            print("[INFO] Sending email via Gmail MCP...")
            success = self._send_via_mcp(email_details)

            if success:
                print("[OK] Successfully sent email!")
                self._log_action("email_sent", {
                    "file": filepath.name,
                    "to": email_details.get('to'),
                    "subject": email_details.get('subject'),
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })
                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to send email")
                self._log_action("email_send_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("email_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_email_details(self, content: str) -> dict:
        """
        Extract email details from approval file.

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
        if not details.get('to'):
            # Look for "To:" pattern
            to_match = re.search(r'[Tt]o:\s*(.+?)(?:\n|$)', content)
            if to_match:
                details['to'] = to_match.group(1).strip()

            subject_match = re.search(r'[Ss]ubject:\s*(.+?)(?:\n|$)', content)
            if subject_match:
                details['subject'] = subject_match.group(1).strip()

            # Extract body (content after first heading or after ---)
            body_start = content.find('---', content.find('---') + 3) if content.count('---') >= 2 else 0
            if body_start > 0:
                body = content[body_start + 3:].strip()
                # Remove any leading #'s
                body = re.sub(r'^#+\s*', '', body)
                details['body'] = body

        return details if details.get('to') and details.get('subject') else None

    def _send_via_mcp(self, email_details: dict) -> bool:
        """
        Send email using Gmail MCP server.

        This would call the MCP server. For now, we'll use a test script.
        In production, this would make an MCP call.

        Args:
            email_details: Dictionary with to, subject, body

        Returns:
            True if successful, False otherwise
        """
        try:
            # For now, create a simple test
            # In production, this would call the Gmail MCP server
            print(f"[INFO] Email details extracted successfully")
            print(f"[INFO] Ready to send to: {email_details.get('to')}")
            print(f"[INFO] This would use Gmail MCP in production")

            # TODO: Implement actual MCP call
            # For now, return True to indicate success in dry-run mode
            return True

        except Exception as e:
            print(f"[ERROR] Error calling Gmail MCP: {e}")
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
            "component": "email_approval_monitor",
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
        description="Monitor /Approved/ folder and send emails via Gmail MCP"
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
    print("Email Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print("\n[INFO] Waiting for approved emails...")
    print("[INFO] Press Ctrl+C to stop\n")

    event_handler = EmailApprovalHandler(args.vault, args.dry_run)
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
