"""
Base Watcher - Abstract template for all watchers

All watchers should inherit from BaseWatcher and implement
the required methods: check_for_updates() and create_action_file().
"""

import time
import json
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional, Dict

# A2A Messaging imports
try:
    from utils.a2a_messenger import A2AMessenger, MessageType, MessagePriority
    from utils.agent_registry import AgentRegistry, AgentRole, HeartbeatSender
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False


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

    Includes circuit breaker pattern for handling persistent failures.
    """

    def __init__(
        self,
        vault_path: str,
        check_interval: int = 60,
        dry_run: bool = False,
        max_consecutive_failures: int = 5,
        circuit_breaker_backoff: int = 300,
        enable_a2a: bool = True,
        a2a_heartbeat_interval: int = 60,
    ):
        """
        Initialize the watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
            dry_run: If True, log actions but don't create files
            max_consecutive_failures: Max consecutive errors before triggering circuit breaker (default: 5)
            circuit_breaker_backoff: Base backoff time in seconds when circuit breaker triggers (default: 300)
            enable_a2a: Enable A2A messaging (default: True)
            a2a_heartbeat_interval: Seconds between A2A heartbeats (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.logs_path = self.vault_path / "Logs"
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.max_consecutive_failures = max_consecutive_failures
        self.circuit_breaker_backoff = circuit_breaker_backoff
        self.enable_a2a = enable_a2a and A2A_AVAILABLE
        self.a2a_heartbeat_interval = a2a_heartbeat_interval

        # Circuit breaker state
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        self.circuit_breaker_active = False

        self.logger = setup_logging(self.__class__.__name__)
        self._ensure_folders()

        # A2A Messaging components
        self._a2a_messenger: Optional[A2AMessenger] = None
        self._a2a_registry: Optional[AgentRegistry] = None
        self._a2a_heartbeat: Optional[HeartbeatSender] = None

        # Initialize A2A if enabled
        if self.enable_a2a:
            self._init_a2a()

    def _ensure_folders(self) -> None:
        """Ensure required folders exist."""
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # A2A Messaging Methods
    # ========================================================================

    def _init_a2a(self) -> None:
        """Initialize A2A messaging components."""
        try:
            agent_id = self._get_agent_id()

            # Initialize messenger
            self._a2a_messenger = A2AMessenger(
                vault_path=str(self.vault_path),
                agent_id=agent_id
            )

            # Initialize registry
            self._a2a_registry = AgentRegistry(str(self.vault_path))

            # Register this agent
            self._register_as_agent()

            # Start heartbeat sender
            self._a2a_heartbeat = HeartbeatSender(
                registry=self._a2a_registry,
                agent_id=agent_id,
                interval_seconds=self.a2a_heartbeat_interval
            )
            self._a2a_heartbeat.start()

            self.logger.info(f"A2A messaging initialized for agent: {agent_id}")

        except Exception as e:
            self.logger.warning(f"Failed to initialize A2A messaging: {e}")
            self.enable_a2a = False

    def _get_agent_id(self) -> str:
        """
        Get the agent ID for this watcher.

        Default implementation uses the class name in lowercase with hyphens.
        Subclasses can override for custom agent IDs.

        Returns:
            Agent ID string
        """
        # Convert class name to agent ID (e.g., GmailWatcher -> gmail-watcher)
        class_name = self.__class__.__name__
        # Insert hyphens before capital letters (except first)
        import re
        agent_id = re.sub(r'(?<!^)(?=[A-Z])', '-', class_name).lower()
        return agent_id

    def _get_agent_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent.

        Subclasses can override to advertise specific capabilities.

        Returns:
            List of capability strings
        """
        class_name = self.__class__.__name__
        service = class_name.replace("Watcher", "").lower()
        return [
            f"{service}_detection",
            f"{service}_monitoring",
            "action_file_creation"
        ]

    def _get_agent_role(self) -> AgentRole:
        """
        Get the role of this agent.

        Returns:
            AgentRole enum value
        """
        return AgentRole.WATCHER

    def _register_as_agent(self) -> None:
        """Register this watcher as an agent in the registry."""
        if not self._a2a_registry or not self._a2a_messenger:
            return

        agent_id = self._get_agent_id()

        self._a2a_registry.register(
            agent_id=agent_id,
            capabilities=self._get_agent_capabilities(),
            role=self._get_agent_role(),
            metadata={
                "class": self.__class__.__name__,
                "check_interval": self.check_interval,
                "dry_run": self.dry_run,
            }
        )

        self.logger.info(f"Registered agent: {agent_id}")

    def _send_a2a_message(
        self,
        to_agent: str,
        message_type: MessageType = "notification",
        subject: str = "",
        payload: Optional[Dict[str, Any]] = None,
        priority: MessagePriority = "normal",
        correlation_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Send an A2A message to another agent.

        Args:
            to_agent: Recipient agent ID
            message_type: Type of message (request, response, notification, etc.)
            subject: Message subject line
            payload: Message data
            priority: Message priority
            correlation_id: Optional correlation ID for request/response tracking

        Returns:
            Message ID if sent, None if A2A is disabled
        """
        if not self.enable_a2a or not self._a2a_messenger:
            self.logger.debug("A2A messaging disabled, skipping message send")
            return None

        try:
            msg_id = self._a2a_messenger.send_message(
                to_agent=to_agent,
                message_type=message_type,
                subject=subject or f"Message from {self._get_agent_id()}",
                payload=payload or {},
                priority=priority,
                correlation_id=correlation_id,
            )

            self.logger.debug(
                f"Sent A2A message {msg_id} to {to_agent}: {subject}"
            )
            return msg_id

        except Exception as e:
            self.logger.error(f"Failed to send A2A message: {e}")
            return None

    def _receive_a2a_messages(
        self,
        status: Optional[str] = None,
        include_expired: bool = False
    ) -> List[Any]:
        """
        Receive pending A2A messages for this agent.

        Args:
            status: Optional filter by message status
            include_expired: Whether to include expired messages

        Returns:
            List of pending messages
        """
        if not self.enable_a2a or not self._a2a_messenger:
            return []

        try:
            messages = self._a2a_messenger.receive_messages(
                status=status,
                include_expired=include_expired
            )

            if messages:
                self.logger.debug(f"Received {len(messages)} A2A messages")

            return messages

        except Exception as e:
            self.logger.error(f"Failed to receive A2A messages: {e}")
            return []

    def _acknowledge_a2a_message(
        self,
        message_id: str,
        result: str = "success",
        error_message: Optional[str] = None,
        response_payload: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Acknowledge processing of an A2A message.

        Args:
            message_id: Message ID being acknowledged
            result: Processing result ("success" or "failure")
            error_message: Optional error message on failure
            response_payload: Optional response data
        """
        if not self.enable_a2a or not self._a2a_messenger:
            return

        try:
            self._a2a_messenger.acknowledge_message(
                message_id=message_id,
                result=result,
                error_message=error_message,
                response_payload=response_payload
            )

            self.logger.debug(f"Acknowledged A2A message {message_id}: {result}")

        except Exception as e:
            self.logger.error(f"Failed to acknowledge A2A message: {e}")

    def _update_a2a_heartbeat(
        self,
        status: str = "online",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update the heartbeat for this agent.

        Args:
            status: Agent status ("online", "offline", "degraded", "maintenance")
            metadata: Optional metadata to update
        """
        if not self.enable_a2a or not self._a2a_registry:
            return

        try:
            # The HeartbeatSender handles periodic heartbeats automatically
            # This method is for explicit status updates
            agent_id = self._get_agent_id()
            self._a2a_registry.update_status(
                agent_id=agent_id,
                status=self._a2a_registry.AgentStatus(status),
                metadata=metadata
            )

            self.logger.debug(f"Updated A2A heartbeat status: {status}")

        except Exception as e:
            self.logger.error(f"Failed to update heartbeat: {e}")

    def _shutdown_a2a(self) -> None:
        """Shutdown A2A messaging components."""
        if self._a2a_heartbeat:
            self._a2a_heartbeat.stop()

        if self._a2a_registry and self._a2a_messenger:
            agent_id = self._get_agent_id()
            self._a2a_registry.unregister(agent_id)

        self.logger.info("A2A messaging shut down")

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self._shutdown_a2a()
        except Exception:
            pass

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
        Run the watcher loop with circuit breaker pattern.

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
                    # Check if circuit breaker is active
                    if self.circuit_breaker_active:
                        backoff_time = min(
                            self.circuit_breaker_backoff * (2 ** min(self.consecutive_failures - self.max_consecutive_failures, 5)),
                            3600  # Max 1 hour backoff
                        )
                        self.logger.warning(
                            f"Circuit breaker active. Backing off for {backoff_time}s "
                            f"(failures: {self.consecutive_failures})"
                        )
                        time.sleep(backoff_time)

                        # Try to recover
                        self.logger.info("Attempting to recover from circuit breaker...")
                        self.circuit_breaker_active = False

                    # Check for updates
                    items = self.check_for_updates()

                    # Success! Reset failure counter
                    self.consecutive_failures = 0
                    self.last_success_time = time.time()

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
                    self.consecutive_failures += 1
                    self.logger.error(
                        f"Error in watcher loop (failure #{self.consecutive_failures}): {e}"
                    )
                    self.log_action("error", {
                        "error": str(e),
                        "consecutive_failures": self.consecutive_failures
                    })

                    # Check if we should trigger circuit breaker
                    if self.consecutive_failures >= self.max_consecutive_failures:
                        self.circuit_breaker_active = True
                        self.logger.error(
                            f"Circuit breaker triggered after {self.consecutive_failures} consecutive failures"
                        )

                    # Apply exponential backoff for failures
                    if self.consecutive_failures > 3:
                        backoff_seconds = min(
                            self.check_interval * (2 ** (self.consecutive_failures - 3)),
                            self.circuit_breaker_backoff
                        )
                        self.logger.warning(f"Backing off for {backoff_seconds}s due to repeated failures")
                        time.sleep(backoff_seconds)
                    else:
                        time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("Watcher stopped by user")

    def run_once(self) -> List[Any]:
        """
        Run a single check and return detected items.

        Useful for testing and manual triggering.
        """
        return self.check_for_updates()
