"""
Orchestrator - Master process for running all watchers

This script manages multiple watcher processes and handles
the coordination between them.

Usage:
    python orchestrator.py --vault . --credentials client_secret.json
"""

import argparse
import logging
import signal
import sys
from pathlib import Path
from typing import List, Optional
import subprocess
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WatcherProcess:
    """Represents a running watcher process."""

    def __init__(self, name: str, module: str, args: List[str]):
        self.name = name
        self.module = module
        self.args = args
        self.process: Optional[subprocess.Popen] = None

    def start(self) -> None:
        """Start the watcher process."""
        cmd = [sys.executable, "-m", self.module] + self.args
        logger.info(f"Starting {self.name}: {' '.join(cmd)}")
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def stop(self) -> None:
        """Stop the watcher process."""
        if self.process:
            logger.info(f"Stopping {self.name}")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

    def is_running(self) -> bool:
        """Check if the process is still running."""
        return self.process is not None and self.process.poll() is None


class Orchestrator:
    """Manages multiple watcher processes."""

    def __init__(self, vault_path: str, credentials_path: str, dry_run: bool = False):
        self.vault_path = vault_path
        self.credentials_path = credentials_path
        self.dry_run = dry_run
        self.watchers: List[WatcherProcess] = []
        self.running = False

    def add_watcher(self, name: str, module: str, extra_args: List[str] = None) -> None:
        """Add a watcher to be managed."""
        args = [
            "--vault", self.vault_path,
            "--credentials", self.credentials_path,
        ]
        if self.dry_run:
            args.append("--dry-run")
        if extra_args:
            args.extend(extra_args)

        self.watchers.append(WatcherProcess(name, module, args))

    def start(self) -> None:
        """Start all watchers."""
        self.running = True
        for watcher in self.watchers:
            watcher.start()
            time.sleep(1)  # Stagger starts

    def stop(self) -> None:
        """Stop all watchers."""
        self.running = False
        for watcher in reversed(self.watchers):
            watcher.stop()

    def monitor(self) -> None:
        """Monitor all watchers and restart if needed."""
        logger.info("Orchestrator monitoring started")

        try:
            while self.running:
                for watcher in self.watchers:
                    if not watcher.is_running():
                        logger.warning(f"{watcher.name} stopped, restarting...")
                        watcher.start()

                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()

    def status(self) -> None:
        """Print status of all watchers."""
        print("\n=== Orchestrator Status ===")
        for watcher in self.watchers:
            status = "Running" if watcher.is_running() else "Stopped"
            print(f"  {watcher.name}: {status}")
        print("==========================\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Orchestrator for Personal AI Employee watchers"
    )
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault (default: current directory)"
    )
    parser.add_argument(
        "--credentials",
        default="client_secret.json",
        help="Path to OAuth credentials.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without creating files"
    )
    parser.add_argument(
        "--no-calendar",
        action="store_true",
        help="Skip calendar watcher"
    )
    parser.add_argument(
        "--no-gmail",
        action="store_true",
        help="Skip Gmail watcher"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show status and exit"
    )

    args = parser.parse_args()

    orchestrator = Orchestrator(
        vault_path=args.vault,
        credentials_path=args.credentials,
        dry_run=args.dry_run
    )

    # Add watchers
    if not args.no_gmail:
        orchestrator.add_watcher("Gmail Watcher", "watchers.gmail_watcher")

    if not args.no_calendar:
        orchestrator.add_watcher(
            "Calendar Watcher",
            "watchers.calendar_watcher",
            ["--look-ahead", "24"]
        )

    if args.status:
        orchestrator.start()
        time.sleep(2)
        orchestrator.status()
        orchestrator.stop()
        return

    # Handle shutdown gracefully
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        orchestrator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start and monitor
    orchestrator.start()
    orchestrator.monitor()


if __name__ == "__main__":
    main()
