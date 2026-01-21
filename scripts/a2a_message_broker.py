#!/usr/bin/env python3
"""
A2A Message Broker

Routes messages between agents in the AI Employee system. The broker:
1. Monitors the Outbox/ for new messages
2. Routes messages to recipient agent inboxes
3. Handles delivery retries with exponential backoff
4. Cleans up expired messages
5. Monitors agent health via heartbeats

This should be run as a PM2 process for continuous operation.

Usage:
    python -m scripts.a2a_message_broker --vault AI_Employee_Vault

    Or with PM2:
    pm2 start process-manager/pm2.config.js --only a2a-message-broker
"""

import os
import sys
import argparse
import time
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.a2a_messenger import (
    A2AMessenger, Message, MessageQueue, MessageStatus,
    MessagePriority, MessageType
)
from utils.agent_registry import AgentRegistry, AgentStatus, AgentRole, HeartbeatSender


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('a2a_broker.log')
    ]
)
logger = logging.getLogger(__name__)


class A2AMessageBroker:
    """
    Message broker for routing A2A messages between agents.

    The broker continuously monitors the message queues and routes messages
    from outboxes to recipient inboxes. It handles retries, expiration,
    and cleanup of old messages.

    Architecture:
        1. Poll Outbox/ for new messages
        2. Move to Pending/
        3. Route to Signals/Inbox/<recipient_agent>/
        4. Handle failures with retries
        5. Clean up expired/completed messages
    """

    def __init__(
        self,
        vault_path: str,
        check_interval_seconds: int = 5,
        heartbeat_interval_seconds: int = 60
    ):
        """
        Initialize message broker.

        Args:
            vault_path: Path to AI_Employee_Vault
            check_interval_seconds: How often to check for new messages
            heartbeat_interval_seconds: How often to send broker heartbeat
        """
        self.vault_path = Path(vault_path)
        self.signals_path = self.vault_path / "Signals"
        self.check_interval = check_interval_seconds
        self.heartbeat_interval = heartbeat_interval_seconds

        # Initialize components
        self.registry = AgentRegistry(str(self.vault_path))
        self.queue = MessageQueue(str(self.vault_path), "broker")

        # Track broker state
        self._running = False
        self._shutdown_requested = False

        # Statistics
        self.stats = {
            "messages_routed": 0,
            "messages_failed": 0,
            "messages_retried": 0,
            "messages_expired": 0,
            "expired_cleaned": 0,
            "started_at": None,
        }

        logger.info(f"A2A Message Broker initialized for vault: {vault_path}")

    def _register_broker(self) -> None:
        """Register the broker as an agent in the registry."""
        self.registry.register(
            agent_id="a2a-message-broker",
            capabilities=[
                "message_routing",
                "message_retry",
                "expiration_handling",
                "agent_health_monitoring"
            ],
            role=AgentRole.PROCESSOR,
            version="1.0.0",
            metadata={
                "check_interval": self.check_interval,
                "heartbeat_interval": self.heartbeat_interval,
            }
        )

        # Start heartbeat sender
        self.heartbeat = HeartbeatSender(
            registry=self.registry,
            agent_id="a2a-message-broker",
            interval_seconds=self.heartbeat_interval
        )
        self.heartbeat.start()

        logger.info("Broker registered in agent registry")

    def _unregister_broker(self) -> None:
        """Unregister the broker on shutdown."""
        self.heartbeat.stop()
        self.registry.unregister("a2a-message-broker")
        logger.info("Broker unregistered from agent registry")

    def route_messages(self) -> int:
        """
        Route pending messages to recipient inboxes.

        Returns:
            Number of messages routed
        """
        routed = 0

        # Get all messages in Pending/
        pending_messages = self.queue.get_messages("pending")

        for message in pending_messages:
            try:
                # Check if expired
                if message.is_expired():
                    self._handle_expired_message(message)
                    self.stats["messages_expired"] += 1
                    continue

                # Handle broadcasts
                if message.message_type == "broadcast" or not message.to_agent:
                    self._handle_broadcast(message)
                    routed += 1
                    continue

                # Check if recipient exists
                if not self.registry.is_agent_online(message.to_agent):
                    # Agent offline, will retry
                    logger.warning(
                        f"Recipient {message.to_agent} offline, "
                        f"message {message.message_id} will retry"
                    )
                    self._schedule_retry(message)
                    continue

                # Route to recipient inbox
                self._deliver_message(message)
                routed += 1
                self.stats["messages_routed"] += 1

            except Exception as e:
                logger.error(f"Error routing message {message.message_id}: {e}")
                self._handle_delivery_error(message, str(e))

        return routed

    def _deliver_message(self, message: Message) -> None:
        """
        Deliver a message to the recipient's inbox.

        Args:
            message: Message to deliver
        """
        recipient = message.to_agent

        # Create recipient queue
        recipient_queue = MessageQueue(str(self.vault_path), recipient)

        # Ensure recipient inbox exists
        recipient_queue.inbox_path.mkdir(parents=True, exist_ok=True)

        # Update message status
        message.status = "pending"
        message.delivered_at = datetime.now().isoformat()

        # Write to recipient inbox
        filename = f"{message.message_id}.md"
        dest_path = recipient_queue.inbox_path / filename

        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(message.to_markdown())

        # Move from Pending/ to Completed/ (for routing tracking)
        self.queue.move_message(
            message.message_id,
            "pending",
            "completed"
        )

        logger.info(
            f"Delivered message {message.message_id} "
            f"from {message.from_agent} to {recipient}"
        )

    def _handle_broadcast(self, message: Message) -> None:
        """
        Handle a broadcast message by delivering to all online agents.

        Args:
            message: Broadcast message to handle
        """
        online_agents = self.registry.get_all_agents(include_offline=False)

        # Skip the sender
        recipients = [a for a in online_agents if a.agent_id != message.from_agent]

        delivered_count = 0
        for agent in recipients:
            try:
                # Create a copy for each recipient
                recipient_message = Message(
                    message_id=self._generate_broadcast_copy_id(message.message_id, agent.agent_id),
                    timestamp=message.timestamp,
                    expires=message.expires,
                    priority=message.priority,
                    from_agent=message.from_agent,
                    to_agent=agent.agent_id,
                    message_type="notification",  # Broadcasts become notifications
                    correlation_id=message.message_id,  # Track original
                    subject=f"[Broadcast] {message.subject}",
                    payload=message.payload,
                )

                recipient_queue = MessageQueue(str(self.vault_path), agent.agent_id)
                filename = f"{recipient_message.message_id}.md"
                dest_path = recipient_queue.inbox_path / filename

                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(recipient_message.to_markdown())

                delivered_count += 1

            except Exception as e:
                logger.error(f"Error delivering broadcast to {agent.agent_id}: {e}")

        # Move original to Completed/
        self.queue.move_message(message.message_id, "pending", "completed")

        logger.info(
            f"Broadcast {message.message_id} delivered to {delivered_count}/{len(recipients)} agents"
        )

    def _generate_broadcast_copy_id(self, original_id: str, recipient: str) -> str:
        """Generate message ID for broadcast copy."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{original_id}_to_{recipient}_{timestamp}"

    def _schedule_retry(self, message: Message) -> None:
        """
        Schedule a message for retry.

        Args:
            message: Message to retry
        """
        message.retry_count += 1

        if not message.should_retry():
            # Max retries exceeded, move to dead letter
            self.queue.move_message(message.message_id, "pending", "dead_letter")
            self.stats["messages_failed"] += 1
            logger.error(
                f"Message {message.message_id} exceeded max retries, "
                f"moved to Dead_Letter"
            )
            return

        # Calculate backoff delay (exponential: 2^retry_count seconds)
        backoff_seconds = min(2 ** message.retry_count, 300)  # Max 5 minutes

        # Update status - will stay in Pending/ for next cycle
        message.status = "pending"

        # Save updated message
        self.queue.save_message(message, "pending")

        self.stats["messages_retried"] += 1

        logger.info(
            f"Scheduled retry {message.retry_count}/{message.max_retries} "
            f"for message {message.message_id} "
            f"(backoff: {backoff_seconds}s)"
        )

    def _handle_expired_message(self, message: Message) -> None:
        """
        Handle an expired message.

        Args:
            message: Expired message
        """
        message.status = "expired"
        self.queue.move_message(message.message_id, "pending", "failed")

        logger.warning(f"Message {message.message_id} expired, moved to Failed/")

    def _handle_delivery_error(self, message: Message, error: str) -> None:
        """
        Handle a delivery error.

        Args:
            message: Message that failed to deliver
            error: Error message
        """
        message.error_message = error
        self._schedule_retry(message)

    def check_message_expiration(self) -> int:
        """
        Check all pending messages and move expired ones to Failed/.

        Returns:
            Number of messages expired
        """
        expired = 0

        for folder in ["pending", "processing"]:
            messages = self.queue.get_messages(folder)

            for message in messages:
                if message.is_expired():
                    self._handle_expired_message(message)
                    expired += 1

        return expired

    def cleanup_old_messages(self, days: int = 7) -> Dict[str, int]:
        """
        Clean up old completed messages.

        Args:
            days: Remove messages older than this many days

        Returns:
            Dict with counts of cleaned messages by folder
        """
        cleaned = {"completed": 0, "failed": 0, "dead_letter": 0}

        # Clean each folder
        for folder in ["completed", "failed", "dead_letter"]:
            messages = self.queue.get_messages(folder)
            cutoff = datetime.now() - timedelta(days=days)

            for message in messages:
                try:
                    msg_time = datetime.fromisoformat(message.timestamp.replace("Z", "+00:00"))
                    if msg_time < cutoff:
                        # Use a generic queue for deletion
                        generic_queue = MessageQueue(str(self.vault_path), "temp")
                        # Find the message file
                        for folder_path in [
                            self.signals_path / "Completed",
                            self.signals_path / "Failed",
                            self.signals_path / "Dead_Letter"
                        ]:
                            file_path = folder_path / f"{message.message_id}.md"
                            if file_path.exists():
                                file_path.unlink()
                                cleaned[folder.lower()] += 1
                                break
                except (ValueError, AttributeError):
                    continue

        self.stats["expired_cleaned"] += sum(cleaned.values())

        logger.info(f"Cleaned up old messages: {cleaned}")
        return cleaned

    def cleanup_stale_agents(self, max_age_hours: int = 24) -> int:
        """
        Remove stale agents from registry.

        Args:
            max_age_hours: Remove agents offline longer than this

        Returns:
            Number of agents removed
        """
        removed = self.registry.cleanup_stale_agents(max_age_hours)
        if removed > 0:
            logger.info(f"Cleaned up {removed} stale agents from registry")
        return removed

    def get_status(self) -> Dict[str, Any]:
        """
        Get broker status.

        Returns:
            Dict with broker status information
        """
        uptime_seconds = None
        if self.stats["started_at"]:
            uptime_seconds = (datetime.now() - self.stats["started_at"]).total_seconds()

        return {
            "broker_id": "a2a-message-broker",
            "running": self._running,
            "uptime_seconds": uptime_seconds,
            "statistics": self.stats.copy(),
            "registry": self.registry.get_status_summary(),
            "queue_sizes": {
                "pending": len(self.queue.get_messages("pending")),
                "processing": len(self.queue.get_messages("processing")),
                "completed": len(self.queue.get_messages("completed")),
                "failed": len(self.queue.get_messages("failed")),
                "dead_letter": len(self.queue.get_messages("dead_letter")),
            }
        }

    def _process_outbox(self) -> int:
        """
        Process messages in the Outbox/ folder.

        Moves them to Pending/ for routing.

        Returns:
            Number of messages processed
        """
        processed = 0
        outbox_path = self.signals_path / "Outbox"

        if not outbox_path.exists():
            return 0

        for file_path in outbox_path.glob("*.md"):
            try:
                # Read message
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                message = Message.from_markdown(content)

                # Move to Pending/
                filename = file_path.name
                dest_path = self.signals_path / "Pending" / filename

                file_path.rename(dest_path)
                processed += 1

                logger.debug(f"Moved {filename} from Outbox to Pending")

            except Exception as e:
                logger.error(f"Error processing outbox file {file_path}: {e}")

        return processed

    def run_once(self) -> Dict[str, int]:
        """
        Run a single broker cycle.

        Returns:
            Dict with cycle results
        """
        results = {
            "outbox_processed": 0,
            "messages_routed": 0,
            "messages_expired": 0,
            "messages_cleaned": 0,
            "agents_cleaned": 0,
        }

        try:
            # Process outbox
            results["outbox_processed"] = self._process_outbox()

            # Route messages
            results["messages_routed"] = self.route_messages()

            # Check expiration
            results["messages_expired"] = self.check_message_expiration()

            # Cleanup (run less frequently - every 10 cycles)
            # Could add a cycle counter here

        except Exception as e:
            logger.error(f"Error in broker cycle: {e}")

        return results

    def run(self) -> None:
        """
        Run the broker continuously.

        Monitors message queues and routes messages until shutdown.
        """
        self._running = True
        self.stats["started_at"] = datetime.now()
        self._register_broker()

        logger.info("A2A Message Broker started")
        logger.info(f"Check interval: {self.check_interval}s")

        cycle_count = 0

        try:
            while self._running and not self._shutdown_requested:
                cycle_count += 1

                # Run broker cycle
                results = self.run_once()

                # Log status every 10 cycles
                if cycle_count % 10 == 0:
                    logger.info(
                        f"Broker cycle {cycle_count}: "
                        f"outbox={results['outbox_processed']}, "
                        f"routed={results['messages_routed']}, "
                        f"expired={results['messages_expired']}"
                    )

                    # Periodic cleanup every 60 cycles (~5 minutes at 5s interval)
                    if cycle_count % 60 == 0:
                        cleaned = self.cleanup_old_messages(days=1)
                        agents_cleaned = self.cleanup_stale_agents(max_age_hours=6)
                        logger.info(f"Periodic cleanup: messages={sum(cleaned.values())}, agents={agents_cleaned}")

                # Wait for next cycle
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Broker interrupted by user")

        finally:
            self._unregister_broker()
            self._running = False
            logger.info("A2A Message Broker stopped")

    def shutdown(self) -> None:
        """Request broker shutdown."""
        logger.info("Shutdown requested")
        self._shutdown_requested = True


def main() -> int:
    """Main entry point for the message broker."""
    parser = argparse.ArgumentParser(
        description="A2A Message Broker - Routes messages between agents"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to AI_Employee_Vault folder"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Check interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single cycle and exit"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show broker status and exit"
    )

    args = parser.parse_args()

    # Validate vault path
    vault_path = Path(args.vault)
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        return 1

    # Create broker
    broker = A2AMessageBroker(
        vault_path=str(vault_path),
        check_interval_seconds=args.interval
    )

    # Handle status request
    if args.status:
        status = broker.get_status()
        print("\n=== A2A Message Broker Status ===")
        print(f"Running: {status['running']}")
        print(f"Uptime: {status['uptime_seconds']:.0f}s" if status['uptime_seconds'] else "Uptime: N/A")
        print(f"\nStatistics:")
        for key, value in status['statistics'].items():
            if key != 'started_at':
                print(f"  {key}: {value}")
        print(f"\nRegistry:")
        reg = status['registry']
        print(f"  Online agents: {reg['online_agents']}/{reg['total_agents']}")
        print(f"\nQueue Sizes:")
        for key, value in status['queue_sizes'].items():
            print(f"  {key}: {value}")
        print()
        return 0

    # Handle single run
    if args.once:
        results = broker.run_once()
        print(f"Broker cycle completed: {results}")
        return 0

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        broker.shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run broker
    broker.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
