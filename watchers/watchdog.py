"""
Watchdog Process - Monitor and restart critical processes

This script monitors all watcher processes and automatically restarts them
if they fail, ensuring your AI Employee runs 24/7.

Usage:
    python watchdog.py --vault . --all

The watchdog can monitor specific watchers:
    python watchdog.py --vault . --watchers gmail_watcher calendar_watcher xero_watcher

Or monitor all watchers defined in the orchestrator configuration.
"""

import subprocess
import time
import signal
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Watchdog:
    """
    Monitors watcher processes and restarts them if they fail.

    Features:
    - Monitors multiple watcher processes
    - Auto-restart on failure
    - Log all restarts for audit trail
    - Handles graceful shutdown
    - Supports manual restart commands via signals
    """

    # Default watchers to monitor
    DEFAULT_WATCHERS = {
        "gmail_watcher": {
            "command": "python -m watchers.gmail_watcher",
            "args": ["--vault", ".", "--credentials", "client_secret.json"],
            "priority": 1,  # Priority 1 = Critical
        },
        "calendar_watcher": {
            "command": "python -m watchers.calendar_watcher",
            "args": ["--vault", ".", "--credentials", "client_secret.json"],
            "priority": 1,  # Priority 1 = Critical
        },
        "xero_watcher": {
            "command": "python -m watchers.xero_watcher",
            "args": ["--vault", ".", "--credentials", ".xero_credentials.json"],
            "priority": 2,  # Priority 2 = Important but can wait
        },
    }

    def __init__(
        self,
        vault_path: str,
        watchers: Optional[Dict[str, Dict]] = None,
        check_interval: int = 60,
        restart_delay: int = 30,
    ):
        """
        Initialize the watchdog.

        Args:
            vault_path: Path to Obsidian vault
            watchers: Dict of watcher configurations
            check_interval: Seconds between checks (default: 60)
            restart_delay: Seconds to wait before restarting a failed process
        """
        self.vault_path = Path(vault_path)
        self.watchers = watchers or self.DEFAULT_WATCHERS
        self.check_interval = check_interval
        self.restart_delay = restart_delay
        self.processes: Dict[str, subprocess.Popen] = {}
        self.startup_delay = 5  # Wait 5 seconds between each process startup
        self.logs_path = self.vault_path / "Logs"
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _shutdown(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info("Shutdown signal received, stopping all watchers...")
        self.stop_all()
        exit(0)

    def start_process(self, name: str, config: Dict) -> Optional[subprocess.Popen]:
        """Start a watcher process."""
        try:
            cmd = config["command"]
            args = config.get("args", []).split() if isinstance(config.get("args"), []) else []

            # Add vault_path to arguments
            if "--vault" not in args:
                args.extend(["--vault", str(self.vault_path)])

            logger.info(f"Starting {name}: {' '.join([cmd] + args)}")

            process = subprocess.Popen(
                cmd,
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.vault_path
            )

            logger.info(f"Started {name} (PID: {process.pid})")
            return process
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return None

    def stop_process(self, name: str) -> bool:
        """Stop a watcher process."""
        if name not in self.processes:
            logger.warning(f"Process {name} not running")
            return False

        try:
            process = self.processes[name]
            logger.info(f"Stopping {name} (PID: {process.pid})")
            process.terminate()
            process.wait(timeout=10)
            del self.processes[name]
            logger.info(f"Stopped {name}")
            return True
        except Exception as e:
            logger.error(f"Error stopping {name}: {e}")
            return False

    def is_running(self, name: str) -> bool:
        """Check if a process is currently running."""
        if name not in self.processes:
            return False

        process = self.processes[name]
        try:
            return process.poll() is None
        except Exception as e:
            logger.error(f"Error checking {name}: {e}")
            return False

    def restart_process(self, name: str, config: Dict) -> bool:
        """Restart a watcher process after failure."""
        logger.warning(f"Restarting {name}...")

        # Stop the process if running
        self.stop_process(name)
        self.start_process(name, config)
        time.sleep(self.restart_delay)

        return self.is_running(name)

    def check_and_restart_all(self) -> None:
        """Check all watchers and restart failed ones."""
        for name, config in self.get_all_watchers().items():
            if config["priority"] == 1:
                # Critical processes always checked
                if not self.is_running(name):
                    logger.error(f"Critical watcher {name} not running, restarting...")
                    self.restart_process(name, config)
            elif config["priority"] == 2:
                # Check only on every 3rd cycle
                # (checked via counter below)
                pass

    def monitor(self) -> None:
        """Continuously monitor all watchers and restart as needed."""
        logger.info("Watchdog starting...")
        self.start_all()

        try:
            cycle_count = 0
            while True:
                try:
                    cycle_count += 1

                    # Always check critical processes
                    for name, config in self.get_all_watchers().items():
                        if config["priority"] == 1:
                            if not self.is_running(name):
                                self.log_action("restart", {
                                    "watcher": name,
                                    "reason": "Critical watcher not running",
                                    "previous_state": "not_running"
                                })
                                self.restart_process(name, config)

                    # Check Priority 2 processes every 3 cycles
                    if cycle_count % 3 == 0:
                        for name, config in self.get_all_watchers().items():
                            if config["priority"] == 2:
                                if not self.is_running(name):
                                    self.log_action("restart", {
                                        "watcher": name,
                                        "reason": "Secondary watcher not running",
                                        "previous_state": "not_running"
                                    })
                                    self.restart_process(name, config)

                    # Log periodic status every hour
                    if cycle_count % 60 == 0:
                        self.log_status()

                    time.sleep(self.check_interval)

                except Exception as e:
                    logger.error(f"Error in watchdog loop: {e}")
                    self.log_action("error", {"error": str(e)})
                    time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Watchdog stopped by user")
            self.stop_all()

    def get_all_watchers(self) -> Dict:
        """Return all configured watchers."""
        return self.watchers

    def start_all(self) -> None:
        """Start all configured watchers."""
        for name, config in self.get_all_watchers().items():
            if config["priority"] == 1:
                # Start critical processes first
                self.start_process(name, config)
                time.sleep(self.startup_delay)

        # Then start priority 2 processes
        for name, config in self.get_all_watchers().items():
            if config["priority"] == 2:
                self.start_process(name, config)
                time.sleep(self.startup_delay)

    def stop_all(self) -> None:
        """Stop all running processes."""
        for name in self.processes:
            self.stop_process(name)

    def log_action(self, action_type: str, details: Dict) -> None:
        """Log an action to the audit log."""
        log_file = self.logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "watchdog",
            "action_type": action_type,
            "details": details
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to log action: {e}")

    def log_status(self) -> None:
        """Log current status of all watchers."""
        status_summary = []

        for name, config in self.get_all_watchers().items():
            is_running = self.is_running(name)
            priority = config["priority"]

            status_summary.append({
                "watcher": name,
                "priority": priority,
                "status": "running" if is_running else "stopped",
                "pid": self.processes[name].pid if name in self.processes else None
            })

        self.log_action("status", {"watchers": status_summary})


def main():
    """Entry point for the watchdog."""
    parser = argparse.ArgumentParser(
        description="Watchdog for Personal AI Employee - Monitor and restart watchers",
        epilog="""
Examples:
  # Monitor all watchers
  python watchdog.py --vault .

  # Monitor specific watchers
  python watchdog.py --vault . --watchers gmail_watcher calendar_watcher

  # Check once and exit
  python watchdog.py --vault . --once
        """
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault (default: current directory)"
    )

    parser.add_argument(
        "--watchers",
        nargs="*",
        default=None,
        help="Specific watchers to monitor (default: all)"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )

    parser.add_argument(
        "--restart-delay",
        type=int,
        default=30,
        help="Seconds to wait before restarting failed processes (default: 30)"
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Check once and exit"
    )

    args = parser.parse_args()

    # Create watchdog
    watchdog = Watchdog(
        vault_path=args.vault,
        watchers=None,  # Use defaults
        check_interval=args.interval,
        restart_delay=args.restart_delay
    )

    if args.once:
        # Check once and exit
        if args.watchers:
            watchers = args.watchers
        else:
            watchers = ["gmail_watcher", "calendar_watcher", "xero_watcher"]

        for watcher in watchers:
            if watchdog.is_running(watcher):
                print(f"✓ {watcher} is running")
            else:
                print(f"✗ {watcher} is not running")

        # Show status
        watchdog.log_status()
    else:
        # Run continuous monitoring loop
        watchdog.monitor()


if __name__ == "__main__":
    main()
