#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Approval Monitor

Watches the /Approved/ folder for approved LinkedIn posts and publishes them.
This is the human-in-the-loop component - it only posts after you approve.

Usage:
    python linkedin_approval_monitor.py --vault .
"""

import sys
import time
import subprocess
import argparse
import os
import re
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    # Save original print before overriding
    _original_print = print

    # Create a safe print function that handles Unicode encoding errors
    def safe_print(*args, **kwargs):
        """Print function that safely handles Unicode characters on Windows."""
        # Convert all args to strings safely
        safe_args = []
        for arg in args:
            try:
                # Try to encode as ASCII with replacement for unsupported chars
                safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
            except:
                safe_args.append(str(arg))
        _original_print(*safe_args, **kwargs)

    # Override print for this module
    print = safe_print


class LinkedInApprovalHandler(FileSystemEventHandler):
    """
    Handles approved LinkedIn post files.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        # Check LINKEDIN_DRY_RUN environment variable, default to dry_run parameter
        env_dry_run = os.getenv('LINKEDIN_DRY_RUN', 'true').lower() == 'true'
        self.dry_run = dry_run or env_dry_run

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        """Called when a file is created in /Approved/ folder."""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Only process LinkedIn approval files
        if not filepath.name.startswith("LINKEDIN_POST_"):
            return

        if not filepath.suffix == ".md":
            return

        print(f"\n[OK] Detected approved post: {filepath.name}")
        self.process_approved_post(filepath)

    def process_approved_post(self, filepath: Path):
        """
        Process an approved LinkedIn post.

        Args:
            filepath: Path to approved post file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract the post content from between the ```
            post_content = self._extract_post_content(content)

            if not post_content:
                print(f"[ERROR] Could not extract post content from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"POST CONTENT TO PUBLISH:")
            print(f"{'='*60}")
            print(post_content)  # safe_print handles encoding
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("linkedin_post_approved", {
                "file": filepath.name,
                "content_length": len(post_content),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would post to LinkedIn")
                self._move_to_done(filepath)
                return

            # Publish to LinkedIn
            print("[INFO] Publishing to LinkedIn...")
            success = self._publish_to_linkedin(post_content)

            if success:
                print("[OK] Successfully published to LinkedIn!")
                self._log_action("linkedin_post_published", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })
                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to publish to LinkedIn")
                self._log_action("linkedin_post_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("linkedin_post_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_post_content(self, content: str) -> str:
        """Extract post content from approval file."""
        # Find content between ```
        match = re.search(r'```(.+?)```', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _publish_to_linkedin(self, content: str) -> bool:
        """
        Publish content to LinkedIn using the linkedin_poster script.

        Args:
            content: Post content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the linkedin_poster.py path
            # The poster script is in the parent directory of the vault
            vault_root = self.vault_path.parent if self.vault_path.name == "AI_Employee_Vault" else self.vault_path
            poster_script = vault_root / "scripts" / "social-media" / "linkedin_poster.py"

            if not poster_script.exists():
                print(f"[ERROR] LinkedIn poster script not found: {poster_script}")
                return False

            # Call the linkedin_poster script
            # Set PYTHONIOENCODING to ensure UTF-8 handling in subprocess
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            result = subprocess.run(
                ["python", str(poster_script), content],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=180  # 3 minutes timeout
            )

            # Print output for visibility
            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(f"[STDERR] {result.stderr}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("[ERROR] LinkedIn poster timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error running linkedin_poster: {e}")
            return False

    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        try:
            done_path = self.done_folder / filepath.name
            filepath.rename(done_path)
            print(f"[OK] Moved to Done: {done_path.name}")
        except Exception as e:
            print(f"[ERROR] Could not move to Done: {e}")

    def _log_action(self, action: str, details: dict):
        """Log action to daily log file."""
        log_file = self.logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        import json

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "linkedin_approval_monitor",
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
        description="Monitor /Approved/ folder and publish LinkedIn posts"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't actually post"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)
    approved_folder = vault_path / "Approved"
    approved_folder.mkdir(parents=True, exist_ok=True)

    # Create handler first to get the actual dry_run state (from env or args)
    event_handler = LinkedInApprovalHandler(args.vault, args.dry_run)

    print("=" * 60)
    print("LinkedIn Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if event_handler.dry_run else 'LIVE'}")
    print("=" * 60)
    print("\n[INFO] Waiting for approved posts...")
    print("[INFO] Press Ctrl+C to stop\n")

    observer = Observer()
    observer.schedule(event_handler, str(approved_folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Stopping monitor...")
        observer.stop()
    observer.join()

    print("[OK] Monitor stopped")


if __name__ == "__main__":
    main()
