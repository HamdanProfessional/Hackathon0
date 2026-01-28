#!/usr/bin/env python3
"""
Cross-Domain Action Coordinator

Enables multi-domain actions from a single request.

Example:
  Drop file in Inbox with:
    - Send email to Anus
    - Send WhatsApp message about the email

  Result:
    - Email sent to Anus
    - WhatsApp message sent to you about the email

Usage:
    python cross_domain_coordinator.py --vault AI_Employee_Vault --once
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CrossDomainCoordinator:
    """
    Coordinates actions across multiple domains.

    Handles:
    1. Parsing cross-domain action files
    2. Creating individual action files for each domain
    3. Tracking completion of all sub-actions
    4. Moving parent file to Done/ when complete
    """

    SUPPORTED_DOMAINS = {
        "email": "email",
        "whatsapp": "whatsapp",
        "slack": "slack",
        "linkedin": "linkedin",
        "twitter": "twitter",
        "facebook": "facebook",
        "instagram": "instagram"
    }

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / "Approved"
        self.done = self.vault_path / "Done"
        self.in_progress = self.vault_path / "In_Progress"
        self.logs = self.vault_path / "Logs"

        # Create folders
        for folder in [self.approved, self.done, self.in_progress, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # State tracking
        self.state_file = self.vault_path / ".cross_domain_state.json"
        self.tracking = {}  # parent_file -> {actions: {}, completed: []}

        # Logging
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'cross_domain.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        self._load_state()

    def _load_state(self):
        """Load tracking state from file."""
        if self.state_file.exists():
            try:
                self.tracking = json.loads(self.state_file.read_text())
                self.logger.info(f"Loaded state: {len(self.tracking)} items tracked")
            except Exception as e:
                self.logger.warning(f"Could not load state: {e}")

    def _save_state(self):
        """Save tracking state to file."""
        try:
            self.state_file.write_text(json.dumps(self.tracking, indent=2))
        except Exception as e:
            self.logger.warning(f"Could not save state: {e}")

    def find_cross_domain_actions(self) -> List[Path]:
        """Find all cross-domain action files in Approved/."""
        if not self.approved.exists():
            return []

        # Find files with type: cross_domain in frontmatter
        cross_domain_files = []
        for filepath in self.approved.glob("*.md"):
            try:
                content = filepath.read_text()
                if "type: cross_domain" in content[:500]:
                    cross_domain_files.append(filepath)
            except Exception:
                pass

        return sorted(cross_domain_files, key=lambda p: p.stat().st_mtime)

    def parse_cross_domain_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Parse a cross-domain action file.

        Returns:
            Dict with actions list and metadata
        """
        try:
            content = filepath.read_text()

            # Extract YAML frontmatter
            if "---" not in content:
                return None

            parts = content.split("---")
            if len(parts) < 3:
                return None

            # Parse YAML frontmatter
            frontmatter = parts[1]
            try:
                data = yaml.safe_load(frontmatter)
            except yaml.YAMLError as e:
                self.logger.error(f"Error parsing YAML: {e}")
                return None

            # Validate structure
            if not isinstance(data, dict) or "actions" not in data:
                self.logger.error(f"Invalid cross-domain file format")
                return None

            return data

        except Exception as e:
            self.logger.error(f"Error parsing file: {e}")
            return None

    def create_action_file(self, parent_file: str, action: Dict, index: int) -> Path:
        """
        Create an individual domain-specific action file.

        Args:
            parent_file: Parent cross-domain filename
            action: Action dict with domain and parameters
            index: Action index for unique naming

        Returns:
            Path to created action file
        """
        domain = action.get("domain", "").lower()
        params = action

        # Determine file type and naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parent_stem = Path(parent_file).stem

        if domain == "email":
            filename = f"EMAIL_CROSS_DOMAIN_{timestamp}_{index}.md"
            file_content = f"""---
type: email
source: cross_domain_coordinator
parent_file: {parent_file}
action_index: {index}
priority: high
status: approved
created: {datetime.now().isoformat()}
---

# Cross-Domain Email Action

**To:** {params.get('target', 'unknown')}
**Subject:** {params.get('subject', 'No Subject')}

```
{params.get('body', '')}
```

---
*Generated by Cross-Domain Action Coordinator*
*Parent: {parent_file}*
"""
        elif domain == "whatsapp":
            filename = f"WHATSAPP_CROSS_DOMAIN_{timestamp}_{index}.md"
            file_content = f"""---
type: whatsapp_message
contact: {params.get('target', 'unknown')}
status: approved
created: {datetime.now().isoformat()}
---

```
{params.get('message', '')}
```

---
*Generated by Cross-Domain Action Coordinator*
*Parent: {parent_file}*
"""
        elif domain == "slack":
            filename = f"SLACK_CROSS_DOMAIN_{timestamp}_{index}.md"
            file_content = f"""---
type: slack_message
channel: {params.get('channel', '#general')}
status: approved
created: {datetime.now().isoformat()}
---

```
{params.get('message', '')}
```

---
*Generated by Cross-Domain Action Coordinator*
*Parent: {parent_file}*
"""
        elif domain in ["linkedin", "twitter", "facebook", "instagram"]:
            filename = f"{domain.upper()}_POST_CROSS_DOMAIN_{timestamp}_{index}.md"
            file_content = f"""---
type: {domain}_post
platform: {domain}
action: post_to_{domain}
priority: high
status: approved
created: {datetime.now().isoformat()}
---

```
{params.get('message', params.get('content', ''))}
```

---
*Generated by Cross-Domain Action Coordinator*
*Parent: {parent_file}*
"""
        else:
            self.logger.warning(f"Unsupported domain: {domain}")
            return None

        # Write action file to Approved/
        action_path = self.approved / filename
        action_path.write_text(file_content, encoding='utf-8')

        self.logger.info(f"Created action file: {filename}")
        return action_path

    def process_cross_domain_action(self, filepath: Path):
        """
        Process a cross-domain action file.

        Creates individual action files for each domain.
        """
        self.logger.info(f"Processing cross-domain action: {filepath.name}")

        # Parse the file
        data = self.parse_cross_domain_file(filepath)
        if not data:
            self.logger.error(f"Could not parse cross-domain file")
            return

        actions = data.get("actions", [])
        if not actions:
            self.logger.error("No actions found in file")
            return

        self.logger.info(f"Found {len(actions)} actions")

        # Initialize tracking for this parent file
        parent_id = filepath.name
        self.tracking[parent_id] = {
            "actions": {},
            "completed": [],
            "total": len(actions),
            "created_at": datetime.now().isoformat()
        }

        # Create individual action files
        for i, action in enumerate(actions):
            domain = action.get("domain", "").lower()

            if domain not in self.SUPPORTED_DOMAINS:
                self.logger.warning(f"Skipping unsupported domain: {domain}")
                continue

            action_path = self.create_action_file(parent_id, action, i)

            if action_path:
                # Track this action
                action_id = action_path.name
                self.tracking[parent_id]["actions"][action_id] = {
                    "domain": domain,
                    "status": "created",
                    "created_at": datetime.now().isoformat()
                }

        # Save state
        self._save_state()

        # Move parent file to In_Progress
        in_progress = self.in_progress / filepath.name
        filepath.rename(in_progress)
        self.logger.info(f"Moved to In_Progress: {filepath.name}")

    def check_action_completion(self, parent_id: str) -> bool:
        """
        Check if all sub-actions for a parent file are complete.

        Args:
            parent_id: Parent filename

        Returns:
            True if all actions are complete
        """
        if parent_id not in self.tracking:
            return False

        tracking_data = self.tracking[parent_id]
        actions = tracking_data["actions"]

        # Check if all action files have been moved to Done/
        all_complete = True
        completed = []

        for action_id, action_data in actions.items():
            if action_data["status"] == "complete":
                completed.append(action_id)
                continue

            # Check if the action file is done
            action_file = self.approved / action_id
            done_file = self.done / action_id

            if not action_file.exists() and done_file.exists():
                # Action is complete
                action_data["status"] = "complete"
                action_data["completed_at"] = datetime.now().isoformat()
                completed.append(action_id)
                self.logger.info(f"Action complete: {action_id}")
            else:
                all_complete = False

        tracking_data["completed"] = completed
        self._save_state()

        return all_complete

    def complete_parent_file(self, parent_id: str):
        """
        Complete a cross-domain action by moving parent file to Done/.

        Args:
            parent_id: Parent filename
        """
        if parent_id not in self.tracking:
            return

        in_progress = self.in_progress / parent_id
        done_path = self.done / parent_id

        if in_progress.exists():
            in_progress.rename(done_path)
            self.logger.info(f"Completed cross-domain action: {parent_id}")

        # Clean up tracking
        del self.tracking[parent_id]
        self._save_state()

        # Create summary
        self._create_summary(parent_id)

    def _create_summary(self, parent_id: str):
        """Create a summary of completed cross-domain action."""
        if parent_id in self.tracking:
            tracking_data = self.tracking[parent_id]
        else:
            # Use saved data
            summary_state = self._load_parent_state(parent_id)
            if not summary_state:
                return
            tracking_data = summary_state

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.vault_path / "Briefings" / f"CrossDomain_Complete_{timestamp}.md"

        summary_content = f"""---
type: cross_domain_summary
created: {datetime.now().isoformat()}
---

# Cross-Domain Action Complete

**Parent File:** {parent_id}
**Completed:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Actions Executed

"""

        for action_id, action_data in tracking_data.get("actions", {}).items():
            summary_content += f"- **{action_data.get('domain', 'unknown').upper()}:** {action_id}\n"
            summary_content += f"  Status: {action_data.get('status', 'unknown')}\n"

        summary_content += f"""
## Summary
- Total Actions: {tracking_data.get('total', 0)}
- Completed: {len(tracking_data.get('completed', []))}
- All Actions Complete: ✅

---
*Generated by Cross-Domain Action Coordinator*
"""

        summary_file.write_text(summary_content, encoding='utf-8')
        self.logger.info(f"Created summary: {summary_file.name}")

    def _load_parent_state(self, parent_id: str) -> Optional[Dict]:
        """Load saved state for a parent file."""
        # This would need to be implemented for persistent tracking
        return None

    async def run_once(self):
        """Run one processing cycle."""
        self.logger.info("=" * 60)
        self.logger.info("Cross-Domain Coordinator - Checking for actions")
        self.logger.info("=" * 60)

        # Process new cross-domain files
        cross_domain_files = self.find_cross_domain_actions()

        if cross_domain_files:
            self.logger.info(f"Found {len(cross_domain_files)} cross-domain actions")

            for filepath in cross_domain_files:
                self.process_cross_domain_action(filepath)

        # Check completion status
        to_complete = []
        for parent_id in list(self.tracking.keys()):
            if self.check_action_completion(parent_id):
                to_complete.append(parent_id)

        # Complete finished actions
        for parent_id in to_complete:
            self.complete_parent_file(parent_id)

        if not cross_domain_files and not to_complete:
            self.logger.info("No new cross-domain actions to process")

    async def run(self):
        """Run continuous loop."""
        self.logger.info("[START] Starting Cross-Domain Coordinator")
        self.logger.info(f"[DIR] Vault: {self.vault_path}")

        try:
            while True:
                await self.run_once()
                await asyncio.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            self.logger.info("[STOP] Stopped by user")
        except Exception as e:
            self.logger.error(f"[FATAL] Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cross-Domain Action Coordinator"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to vault"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )

    args = parser.parse_args()

    coordinator = CrossDomainCoordinator(args.vault)

    if args.once:
        asyncio.run(coordinator.run_once())
    else:
        asyncio.run(coordinator.run())


if __name__ == "__main__":
    main()
