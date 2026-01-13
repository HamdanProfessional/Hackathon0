"""
Base Watcher - Abstract template for all watchers

All watchers should inherit from BaseWatcher and implement
the required methods: check_for_updates() and create_action_file().
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


def setup_logging(name: str) -> logging.Logger:
    """Set up logging for a watcher."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers.

    Watchers continuously monitor external sources (Gmail, Calendar, etc.)
    and create markdown action files in the vault's Needs_Action folder
    when new items are detected.
    """

    def __init__(
        self,
        vault_path: str,
        check_interval: int = 60,
        dry_run: bool = False,
    ):
        """
        Initialize the watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
            dry_run: If True, log actions but don't create files
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.logs_path = self.vault_path / "Logs"
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.logger = setup_logging(self.__class__.__name__)
        self._ensure_folders()

    def _ensure_folders(self) -> None:
        """Ensure required folders exist."""
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new updates from the monitored source.

        Returns:
            List of new items to process (empty if none)
        """
        pass

    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file in the Needs_Action folder.

        Args:
            item: An item from check_for_updates()

        Returns:
            Path to the created file, or None if not created
        """
        pass

    @abstractmethod
    def get_item_id(self, item: Any) -> str:
        """
        Get a unique identifier for an item.

        Used to track processed items and avoid duplicates.
        """
        pass

    def log_action(self, action_type: str, details: dict) -> None:
        """
        Log an action to the daily log file.

        Args:
            action_type: Type of action (e.g., "email_detected", "created_file")
            details: Dictionary of action details
        """
        log_file = self.logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "watcher": self.__class__.__name__,
            "action_type": action_type,
            "details": details,
        }

        # Append to log file (JSONL format)
        with open(log_file, "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(log_entry) + "\n")

    def process_item(self, item: Any) -> Optional[Path]:
        """
        Process a single item: create action file and log.

        Args:
            item: Item from check_for_updates()

        Returns:
            Path to created file, or None
        """
        item_id = self.get_item_id(item)
        self.logger.info(f"Processing item: {item_id}")

        if not self.dry_run:
            filepath = self.create_action_file(item)
            if filepath:
                self.log_action("created_action_file", {
                    "item_id": item_id,
                    "file": str(filepath),
                })
                return filepath
        else:
            self.logger.info(f"[DRY RUN] Would create action file for: {item_id}")
            return None

    def run(self, duration: Optional[int] = None) -> None:
        """
        Run the watcher loop.

        Args:
            duration: Run for this many seconds, or None to run forever
        """
        self.logger.info(
            f"Starting {self.__class__.__name__} "
            f"(interval: {self.check_interval}s, dry_run: {self.dry_run})"
        )

        start_time = time.time()
        processed_ids = set()

        try:
            while True:
                try:
                    # Check for updates
                    items = self.check_for_updates()

                    # Filter out already processed items
                    new_items = [
                        item for item in items
                        if self.get_item_id(item) not in processed_ids
                    ]

                    if new_items:
                        self.logger.info(f"Found {len(new_items)} new items")

                        for item in new_items:
                            self.process_item(item)
                            processed_ids.add(self.get_item_id(item))

                    # Check if we should stop
                    if duration and (time.time() - start_time) >= duration:
                        self.logger.info("Duration reached, stopping watcher")
                        break

                except Exception as e:
                    self.logger.error(f"Error in watcher loop: {e}")
                    self.log_action("error", {"error": str(e)})

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("Watcher stopped by user")

    def run_once(self) -> List[Any]:
        """
        Run a single check and return detected items.

        Useful for testing and manual triggering.
        """
        return self.check_for_updates()
