#!/usr/bin/env python3
"""
Claim Manager for Platinum Tier Work-Zone Specialization.

Implements claim-by-move rule to prevent double-work between cloud and local agents.

Architecture:
- Cloud agent claims items -> moves to In_Progress/cloud-agent/
- Local agent claims items -> moves to In_Progress/local-agent/
- First to move wins, other agent ignores already-claimed items
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ClaimManager:
    """
    Manages work claims between cloud and local agents using claim-by-move rule.

    This prevents double-work by ensuring only one agent works on an item at a time.
    """

    def __init__(self, vault_path: str, agent_name: str):
        """
        Initialize claim manager.

        Args:
            vault_path: Path to the vault
            agent_name: Name of this agent ('cloud-agent' or 'local-agent')
        """
        self.vault_path = Path(vault_path)
        self.agent_name = agent_name
        self.needs_action = self.vault_path / "Needs_Action"
        self.in_progress = self.vault_path / "In_Progress" / agent_name
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.done = self.vault_path / "Done"

        # Ensure directories exist
        self.in_progress.mkdir(parents=True, exist_ok=True)

    def claim_item(self, item_path: Path) -> bool:
        """
        Try to claim an item by moving it to In_Progress/<agent>/.

        Args:
            item_path: Path to the item in Needs_Action/

        Returns:
            True if claim successful, False if already claimed by another agent
        """
        filename = item_path.name

        # First check if already claimed by another agent
        if self._is_already_claimed(filename):
            logger.info(f"Item {filename} already claimed by another agent")
            return False

        # Try to claim the item (may fail if another agent claimed between check and move)
        destination = self.in_progress / filename
        try:
            shutil.move(str(item_path), str(destination))
            self._log_claim(filename, "claimed", destination)
            logger.info(f"Agent {self.agent_name} claimed {filename}")
            return True
        except FileNotFoundError:
            # Item was claimed by another agent between our check and move
            logger.info(f"Item {filename} was claimed by another agent during attempt")
            return False

    def _is_already_claimed(self, filename: str) -> bool:
        """
        Check if item is already claimed by another agent.

        Args:
            filename: Name of the item to check

        Returns:
            True if claimed by another agent, False otherwise
        """
        in_progress_dir = self.vault_path / "In_Progress"

        if not in_progress_dir.exists():
            return False

        # Check all agent directories except our own
        for agent_dir in in_progress_dir.iterdir():
            if agent_dir.name == self.agent_name:
                continue

            claimed_file = agent_dir / filename
            if claimed_file.exists():
                return True

        return False

    def release_to_pending(self, item_path: Path) -> Path:
        """
        Move completed work to Pending_Approval/.

        Args:
            item_path: Path to the item in In_Progress/<agent>/

        Returns:
            Path to the item in Pending_Approval/
        """
        filename = item_path.name
        destination = self.pending_approval / filename

        shutil.move(str(item_path), str(destination))
        self._log_claim(filename, "released_to_pending", destination)
        logger.info(f"Agent {self.agent_name} released {filename} to Pending_Approval")

        return destination

    def move_to_approved(self, item_path: Path) -> Path:
        """
        Move item from Pending_Approval to Approved (after human approval).

        Args:
            item_path: Path to the item in Pending_Approval/

        Returns:
            Path to the item in Approved/
        """
        filename = item_path.name
        destination = self.approved / filename

        shutil.move(str(item_path), str(destination))
        self._log_claim(filename, "approved", destination)
        logger.info(f"Item {filename} moved to Approved")

        return destination

    def move_to_done(self, item_path: Path) -> Path:
        """
        Move item from Approved to Done (after execution).

        Args:
            item_path: Path to the item in Approved/

        Returns:
            Path to the item in Done/
        """
        filename = item_path.name
        destination = self.done / filename

        shutil.move(str(item_path), str(destination))
        self._log_claim(filename, "done", destination)
        logger.info(f"Item {filename} moved to Done")

        return destination

    def _log_claim(self, filename: str, action: str, item_path: Path):
        """
        Log claim/release action.

        Args:
            filename: Name of the item
            action: Action performed (claimed, released_to_pending, approved, done)
            item_path: Path to the item
        """
        claim_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "item": filename,
            "action": action,
            "path": str(item_path)
        }

        logs_dir = self.vault_path / "Logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_claims.json"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(claim_log) + "\n")

    def list_claimed_items(self) -> list:
        """
        List all items currently claimed by this agent.

        Returns:
            List of Path objects for claimed items
        """
        if not self.in_progress.exists():
            return []

        return list(self.in_progress.glob("*.md"))

    def list_available_items(self) -> list:
        """
        List all items available to be claimed in Needs_Action/.

        Returns:
            List of Path objects for available items
        """
        if not self.needs_action.exists():
            return []

        return list(self.needs_action.glob("*.md"))


class CloudClaimManager(ClaimManager):
    """
    Cloud-specific claim manager with draft-only behavior.
    """

    def __init__(self, vault_path: str):
        # Use "cloud" to match domain folder structure In_Progress/cloud/
        super().__init__(vault_path, "cloud")

    def create_draft_reply(self, original_item: Path, draft_content: str) -> Path:
        """
        Create a draft reply in Pending_Approval/ from original item.

        Args:
            original_item: Path to the original item
            draft_content: Content of the draft reply

        Returns:
            Path to the draft in Pending_Approval/
        """
        # Parse original filename to extract metadata
        original_name = original_item.stem

        # Create draft filename
        draft_name = f"DRAFT_{original_name}.md"
        draft_path = self.pending_approval / draft_name

        # Write draft content
        with open(draft_path, "w", encoding="utf-8") as f:
            f.write(draft_content)

        self._log_claim(draft_name, "draft_created", draft_path)
        logger.info(f"Cloud agent created draft {draft_name}")

        # Move original to Done (cloud processing complete)
        self.move_to_done(original_item)

        return draft_path


class LocalClaimManager(ClaimManager):
    """
    Local-specific claim manager with execution capabilities.
    """

    def __init__(self, vault_path: str):
        # Use "local" to match domain folder structure In_Progress/local/
        super().__init__(vault_path, "local")

    def execute_approved_action(self, item_path: Path) -> bool:
        """
        Execute an approved action (called by approval monitors).

        Args:
            item_path: Path to the approved item

        Returns:
            True if execution successful, False otherwise
        """
        # This is a placeholder - actual execution is done by approval monitors
        # This method just tracks the execution
        self._log_claim(item_path.name, "executed", item_path)
        return True


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage work claims between cloud and local")
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Path to vault")
    parser.add_argument("--agent", required=True, choices=["cloud", "local"], help="Agent name")
    parser.add_argument("--list", action="store_true", help="List claimed items")
    parser.add_argument("--available", action="store_true", help="List available items")

    args = parser.parse_args()

    # Create appropriate manager
    if args.agent == "cloud":
        manager = CloudClaimManager(args.vault)
    else:
        manager = LocalClaimManager(args.vault)

    # List claimed items
    if args.list:
        claimed = manager.list_claimed_items()
        print(f"Items claimed by {args.agent}:")
        for item in claimed:
            print(f"  - {item.name}")

    # List available items
    if args.available:
        available = manager.list_available_items()
        print(f"Items available for {args.agent}:")
        for item in available:
            print(f"  - {item.name}")
