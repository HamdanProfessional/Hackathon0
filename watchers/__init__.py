"""
Personal AI Employee - Watchers Package

This package contains watcher scripts that monitor external sources
(Gmail, Calendar, etc.) and create action files in the Obsidian vault.
"""

from .base_watcher import BaseWatcher

__all__ = ["BaseWatcher"]
