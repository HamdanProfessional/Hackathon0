#!/usr/bin/env python3
"""
Deduplication Helper for Watchers

Provides persistent deduplication for all watchers using a state file.
This prevents duplicate action files when watchers restart.

Usage:
    from watchers.deduplication import Deduplication

    dedup = Deduplication(
        vault_path="AI_Employee_Vault",
        state_file=".gmail_state.json",
        item_prefix="EMAIL"
    )

    # Check if item is already processed
    if dedup.is_processed(item_id):
        return

    # Mark as processed and save
    dedup.mark_processed(item_id)
"""

import json
import logging
from pathlib import Path
from typing import Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Deduplication:
    """
    Persistent deduplication using a state file.

    Survives PM2 restarts and provides consistent deduplication
    across all watcher runs.
    """

    def __init__(
        self,
        vault_path: str,
        state_file: str,
        item_prefix: str = "ITEM",
        scan_folders: bool = False,
        max_processed_items: int = 10000
    ):
        """
        Initialize deduplication system.

        Args:
            vault_path: Path to the Obsidian vault
            state_file: Name of state file (e.g., ".gmail_state.json")
            item_prefix: Prefix for item IDs (e.g., "EMAIL", "EVENT")
            scan_folders: If True, scan existing files on first run (default: False for performance)
            max_processed_items: Maximum number of items to keep in memory (LRU eviction)
        """
        self.vault_path = Path(vault_path)
        self.state_file = self.vault_path / state_file
        self.item_prefix = item_prefix
        self.scan_folders = scan_folders
        self.max_processed_items = max_processed_items

        self.processed_items: Set[str] = set()

        # Load existing state
        self._load_state()

    def _load_state(self):
        """Load processed items from state file or scan existing files."""
        # Try loading from persistent state file first (fast and reliable)
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                loaded_ids = set(state_data.get('processed_items', []))
                self.processed_items.update(loaded_ids)
                logger.info(f"Loaded {len(loaded_ids)} {self.item_prefix} items from state file")
                return
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")

        # Fallback: Scan existing files if enabled
        if self.scan_folders:
            logger.info(f"State file not found, scanning existing {self.item_prefix} files...")
            folders_to_scan = [
                self.vault_path / 'Needs_Action',
                self.vault_path / 'Pending_Approval',
                self.vault_path / 'Approved',
                self.vault_path / 'Done'
            ]

            total_loaded = 0
            for folder in folders_to_scan:
                if not folder.exists():
                    continue

                try:
                    existing_files = list(folder.glob(f"{self.item_prefix}_*.md"))
                    for filepath in existing_files:
                        # Extract item ID from frontmatter or filename
                        item_id = self._extract_item_id_from_file(filepath)
                        if item_id:
                            self.processed_items.add(item_id)
                            total_loaded += 1

                except Exception as e:
                    logger.debug(f"Could not scan folder {folder}: {e}")

            logger.info(f"Loaded {total_loaded} {self.item_prefix} items from existing files")

            # Save to state file for next time
            if total_loaded > 0:
                self._save_state()

    def _extract_item_id_from_file(self, filepath: Path) -> Optional[str]:
        """
        Extract item ID from an existing action file.

        Looks for ID in frontmatter first, falls back to filename.
        """
        try:
            content = filepath.read_text(encoding='utf-8')

            # Try to extract ID from frontmatter
            if '---' in content:
                frontmatter = content.split('---')[1]
                for field in ['message_id', 'event_id', 'item_id', 'id']:
                    if f'{field}:' in frontmatter:
                        # Extract the value after the field name
                        for line in frontmatter.split('\n'):
                            if line.strip().startswith(f'{field}:'):
                                value = line.split(':', 1)[1].strip()
                                if value and value != 'unknown':
                                    return f"{self.item_prefix}_{value}"

            # Fallback: extract from filename
            # Format: PREFIX_YYYYMMDD_HHMMSS_description.md or PREFIX_ID.md
            stem = filepath.stem
            if stem.startswith(f"{self.item_prefix}_"):
                # Remove prefix
                id_part = stem[len(f"{self.item_prefix}_"):]
                # Use first 8 chars as ID (if it looks like a hash or short ID)
                if len(id_part) >= 8:
                    return f"{self.item_prefix}_{id_part[:8]}"
                elif len(id_part) > 0:
                    return f"{self.item_prefix}_{id_part}"

        except Exception as e:
            logger.debug(f"Could not extract ID from {filepath.name}: {e}")

        return None

    def _save_state(self):
        """Save processed items to persistent state file."""
        try:
            state_data = {
                'processed_items': list(self.processed_items),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
            logger.debug(f"Saved {len(self.processed_items)} {self.item_prefix} items to state file")
        except Exception as e:
            logger.warning(f"Could not save state file: {e}")

    def is_processed(self, item_id: str) -> bool:
        """
        Check if an item has already been processed.

        Args:
            item_id: The ID to check (without prefix)

        Returns:
            True if already processed
        """
        full_id = f"{self.item_prefix}_{item_id}"
        return full_id in self.processed_items

    def mark_processed(self, item_id: str, save: bool = True):
        """
        Mark an item as processed and optionally save state.

        Implements LRU eviction when max_processed_items is reached.

        Args:
            item_id: The ID to mark (without prefix)
            save: Whether to save state immediately (default: True)
        """
        full_id = f"{self.item_prefix}_{item_id}"
        self.processed_items.add(full_id)

        # Enforce size limit with LRU eviction (remove oldest 10% if at limit)
        if len(self.processed_items) > self.max_processed_items:
            # Convert to list to remove oldest items (first items in set are oldest)
            items_list = list(self.processed_items)
            items_to_remove = len(items_list) // 10  # Remove 10%
            for old_item in items_list[:items_to_remove]:
                self.processed_items.discard(old_item)
            logger.debug(f"LRU eviction: removed {items_to_remove} old items (max: {self.max_processed_items})")

        if save:
            self._save_state()

    def get_id_from_content(self, sender: str, content: str, **kwargs) -> str:
        """
        Generate a stable ID from content (for content-based deduplication).

        Args:
            sender: Sender/source identifier
            content: Message/event content
            **kwargs: Additional fields to include in hash

        Returns:
            Stable 8-character hash
        """
        import hashlib

        # Create hash from sender + content (first 100 chars)
        hash_input = sender + content[:100]

        # Add any additional fields
        if kwargs:
            for key, value in sorted(kwargs.items()):
                hash_input += str(value)[:50]

        return hashlib.md5(hash_input.encode()).hexdigest()[:8]

    def get_count(self) -> int:
        """Get the number of processed items."""
        return len(self.processed_items)
