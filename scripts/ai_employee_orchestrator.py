#!/usr/bin/env python3
"""
AI Employee Orchestrator - Continuous Claude Code Execution

This is the HEART of the AI Employee system. It:
1. Monitors /Needs_Action/ for new items
2. Invokes Claude Code to process each item
3. Maintains human-in-the-loop approval
4. Completes the autonomous agent loop

This transforms the system from "automation" to "AI Employee".
"""
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from watchers.base_watcher import BaseWatcher


class AIEmployeeOrchestrator:
    """
    Orchestrates continuous AI Employee operation.

    The AI Employee works like this:
    1. Watchers detect events → create files in /Needs_Action/
    2. This orchestrator detects new items → invokes Claude Code
    3. Claude Code reads, thinks, plans, executes (with approval if needed)
    4. Items move to Done/ when complete
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval

        self.needs_action = self.vault_path / "Needs_Action"
        self.in_progress = self.vault_path / "In_Progress"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.done = self.vault_path / "Done"

        # Create folders
        for folder in [self.needs_action, self.in_progress,
                       self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # State tracking
        self.processed_items = set()
        self.state_file = self.vault_path / ".orchestrator_state.json"
        self._load_state()

        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.vault_path / 'Logs' / 'orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_state(self):
        """Load processed items from state file."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                self.processed_items = set(data.get("processed_items", []))
                self.logger.info(f"Loaded state: {len(self.processed_items)} processed items")
            except Exception as e:
                self.logger.warning(f"Could not load state: {e}")

    def _save_state(self):
        """Save processed items to state file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "processed_items": list(self.processed_items),
                "last_updated": datetime.now().isoformat()
            }
            self.state_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.warning(f"Could not save state: {e}")

    def _get_new_items(self) -> List[Path]:
        """Get new items from Needs_Action that haven't been processed."""
        if not self.needs_action.exists():
            return []

        # Get all markdown files recursively
        all_items = list(self.needs_action.rglob("*.md"))
        new_items = [
            item for item in all_items
            if item.name not in self.processed_items
        ]

        return sorted(new_items, key=lambda p: p.stat().st_mtime)

    def _invoke_claude_code(self, item_path: Path) -> bool:
        """
        Invoke Claude Code to process an item.

        This uses Claude Code CLI to process a single item with
        the AI Employee instructions.
        """
        self.logger.info(f"Invoking Claude Code for: {item_path.name}")

        # Create a temporary prompt file for this item
        prompt_file = item_path.with_suffix('.prompt.md')

        prompt_content = f"""# AI Employee Task Processing

You are processing an item detected by the AI Employee system.

## Task Item
**File:** {item_path.relative_to(self.vault_path)}

**Instructions:**
1. Read the item file to understand what needs to be done
2. Check Dashboard.md for context
3. Check Company_Handbook.md for rules
4. Think about the best approach
5. Execute the task using available tools and skills
6. For external actions (email, social media, payments):
   - Create approval request in Pending_Approval/
   - Wait for human approval (monitor Approved/ folder)
   - Execute after approval
7. Move completed item to Done/
8. Update relevant files

## Available Skills:
- email-manager: Send/reply to emails
- calendar-manager: Create/update calendar events
- slack-manager: Send Slack messages
- linkedin-manager: Post to LinkedIn
- twitter-manager: Post to Twitter/X
- facebook-instagram-manager: Post to Facebook/Instagram
- whatsapp-manager: Send WhatsApp messages
- odoo-manager: Accounting operations
- content-generator: Generate content
- weekly-briefing: Generate business summaries
- approval-manager: Manage approval workflow

## Important Rules:
- Always get human approval for external actions
- Follow Company_Handbook.md rules
- Log all actions
- Be thorough and thoughtful
- Create clear documentation

Process this item now. When complete, move it to Done/ and output:
```
<promise>ITEM_COMPLETE:{item_path.name}</promise>
```
"""

        prompt_file.write_text(prompt_content)

        # Invoke Claude Code via the Ralph item processor
        try:
            # Use the ralph item processor script
            ralph_script = project_root / ".claude" / "skills" / "ralph" / "scripts" / "ralph-process-item.sh"

            result = subprocess.run(
                ["bash", str(ralph_script), str(item_path.relative_to(self.vault_path))],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per item
                encoding='utf-8',
                errors='replace'
            )

            combined_output = result.stdout + result.stderr
            self.logger.info(f"Claude Code output: {combined_output[-1000:]}")

            # Check for completion
            if "ITEM_COMPLETE" in combined_output:
                self.logger.info(f"[OK] Item completed: {item_path.name}")
                return True
            else:
                self.logger.warning(f"[WARN] Item may not be complete: {item_path.name}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"[ERROR] Timeout processing: {item_path.name}")
            return False
        except Exception as e:
            self.logger.error(f"[ERROR] Error invoking Claude Code: {e}")
            return False
        finally:
            # Clean up prompt file
            if prompt_file.exists():
                prompt_file.unlink()

    def _process_item(self, item_path: Path):
        """Process a single item."""
        item_name = item_path.name

        # Move to in-progress first
        in_progress = self.in_progress / item_name
        item_path.rename(in_progress)

        self.logger.info(f"Processing: {item_name}")

        # Invoke Claude Code
        success = self._invoke_claude_code(in_progress)

        if success:
            # Mark as processed
            self.processed_items.add(item_name)
            self._save_state()

            # Try to move to Done if not already there
            done_path = self.done / item_name
            if in_progress.exists():
                in_progress.rename(done_path)
                self.logger.info(f"[OK] Moved to Done/: {item_name}")
        else:
            # Move back to needs_action for retry
            needs_action = self.needs_action / item_name
            if in_progress.exists():
                in_progress.rename(needs_action)
                self.logger.warning(f"[WARN] Returned to Needs_Action/: {item_name}")

    def run_once(self):
        """Run one processing cycle."""
        self.logger.info("=" * 60)
        self.logger.info("AI Employee Orchestrator - Checking for new items")
        self.logger.info("=" * 60)

        new_items = self._get_new_items()

        if not new_items:
            self.logger.info("No new items to process")
            return

        self.logger.info(f"Found {len(new_items)} new items")

        # Process each item
        for item_path in new_items:
            self._process_item(item_path)
            # Small delay between items
            time.sleep(2)

    def run(self):
        """Run continuous loop."""
        self.logger.info("[START] Starting AI Employee Orchestrator")
        self.logger.info(f"[DIR] Vault: {self.vault_path}")
        self.logger.info(f"[LOOP] Check interval: {self.check_interval}s")

        try:
            while True:
                self.run_once()
                self.logger.info(f"Waiting {self.check_interval}s before next check...")
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("[STOP] Stopped by user")
        except Exception as e:
            self.logger.error(f"[FATAL] Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Employee Orchestrator - Continuous Claude Code execution"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to vault (default: AI_Employee_Vault)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )

    args = parser.parse_args()

    orchestrator = AIEmployeeOrchestrator(
        vault_path=args.vault,
        check_interval=args.interval
    )

    if args.once:
        orchestrator.run_once()
    else:
        orchestrator.run()


if __name__ == "__main__":
    main()
