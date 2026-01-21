"""
A2A (Agent-to-Agent) Messaging System

This module provides the core messaging infrastructure for agent-to-agent
communication within the AI Employee system. Messages are stored as markdown
files in the vault's Signals/ folder, maintaining the local-first architecture.

Architecture:
    - Messages are markdown files with YAML frontmatter
    - File-based queue system in Signals/ folder
    - Built-in retry logic with exponential backoff
    - Message expiration handling
    - HMAC-based authentication for security

Message Flow:
    1. Sender creates message in Signals/Outbox/
    2. Message Broker moves to Signals/Pending/
    3. Broker routes to Signals/Inbox/<recipient_agent>/
    4. Recipient processes and moves to Signals/Completed/
    5. On failure: moves to Signals/Failed/ or Signals/Dead_Letter/
"""

import os
import json
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# Message types
MessageType = Literal["request", "response", "notification", "broadcast", "command"]
MessageStatus = Literal["pending", "processing", "completed", "failed", "expired"]
MessagePriority = Literal["low", "normal", "high", "urgent"]


class MessageError(Exception):
    """Base exception for message-related errors."""
    pass


class MessageValidationError(MessageError):
    """Raised when message validation fails."""
    pass


class MessageDeliveryError(MessageError):
    """Raised when message delivery fails."""
    pass


class MessageExpiredError(MessageError):
    """Raised when attempting to process an expired message."""
    pass


@dataclass
class Message:
    """
    Represents an A2A message between agents.

    Messages are stored as markdown files with YAML frontmatter.
    The actual message data is stored in the YAML frontmatter for easy parsing.

    Attributes:
        message_id: Unique message identifier (msg_<timestamp>_<random>)
        timestamp: When the message was created (ISO 8601)
        expires: When the message expires (ISO 8601)
        priority: Message priority level
        from_agent: Sender agent ID
        to_agent: Recipient agent ID (empty for broadcasts)
        message_type: Type of message
        correlation_id: For request/response correlation
        status: Current message status
        retry_count: Number of delivery attempts
        max_retries: Maximum retry attempts before dead letter
        subject: Human-readable subject line
        payload: JSON-serializable message data
        signature: HMAC signature for authentication
        reply_to: Message ID this is a reply to
    """
    message_id: str
    timestamp: str
    expires: str
    priority: MessagePriority
    from_agent: str
    to_agent: str
    message_type: MessageType
    correlation_id: Optional[str] = None
    status: MessageStatus = "pending"
    retry_count: int = 0
    max_retries: int = 3
    subject: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None
    reply_to: Optional[str] = None
    error_message: Optional[str] = None
    delivered_at: Optional[str] = None
    processed_at: Optional[str] = None

    def to_markdown(self) -> str:
        """Convert message to markdown format with YAML frontmatter."""
        frontmatter = {
            "type": "a2a_message",
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "expires": self.expires,
            "priority": self.priority,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "reply_to": self.reply_to,
            "signature": self.signature,
            "error_message": self.error_message,
            "delivered_at": self.delivered_at,
            "processed_at": self.processed_at,
        }

        # Remove None values
        frontmatter = {k: v for k, v in frontmatter.items() if v is not None}

        frontmatter_yaml = "---\n"
        for key, value in frontmatter.items():
            if isinstance(value, str):
                frontmatter_yaml += f"{key}: {value}\n"
            elif isinstance(value, (list, dict)):
                frontmatter_yaml += f"{key}: {json.dumps(value)}\n"
            else:
                frontmatter_yaml += f"{key}: {value}\n"
        frontmatter_yaml += "---\n\n"

        # Add subject and payload as content
        content = f"# {self.subject}\n\n"
        if self.payload:
            content += "## Payload\n\n```json\n"
            content += json.dumps(self.payload, indent=2)
            content += "\n```\n"

        return frontmatter_yaml + content

    @classmethod
    def from_markdown(cls, markdown: str) -> "Message":
        """Parse message from markdown format."""
        lines = markdown.split("\n")

        # Parse frontmatter
        frontmatter = {}
        in_frontmatter = False
        payload_started = False

        for i, line in enumerate(lines):
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    # End of frontmatter
                    break

            if in_frontmatter:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Try to parse as JSON for complex values
                    try:
                        frontmatter[key] = json.loads(value)
                    except json.JSONDecodeError:
                        frontmatter[key] = value

        # Extract payload from JSON code block
        payload = {}
        subject = ""
        for i, line in enumerate(lines):
            if line.startswith("# ") and not subject:
                subject = line[2:].strip()
            elif line.startswith("```json"):
                # Start of payload
                payload_lines = []
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("```"):
                        break
                    payload_lines.append(lines[j])
                payload_json = "\n".join(payload_lines)
                try:
                    payload = json.loads(payload_json)
                except json.JSONDecodeError:
                    payload = {}

        return cls(
            message_id=frontmatter.get("message_id", ""),
            timestamp=frontmatter.get("timestamp", ""),
            expires=frontmatter.get("expires", ""),
            priority=frontmatter.get("priority", "normal"),
            from_agent=frontmatter.get("from_agent", ""),
            to_agent=frontmatter.get("to_agent", ""),
            message_type=frontmatter.get("message_type", "notification"),
            correlation_id=frontmatter.get("correlation_id"),
            status=frontmatter.get("status", "pending"),
            retry_count=frontmatter.get("retry_count", 0),
            max_retries=frontmatter.get("max_retries", 3),
            subject=subject or frontmatter.get("subject", ""),
            payload=payload,
            signature=frontmatter.get("signature"),
            reply_to=frontmatter.get("reply_to"),
            error_message=frontmatter.get("error_message"),
            delivered_at=frontmatter.get("delivered_at"),
            processed_at=frontmatter.get("processed_at"),
        )

    def is_expired(self) -> bool:
        """Check if message has expired."""
        try:
            expires_dt = datetime.fromisoformat(self.expires.replace("Z", "+00:00"))
            return datetime.now(expires_dt.tzinfo) > expires_dt
        except (ValueError, AttributeError):
            return False

    def should_retry(self) -> bool:
        """Check if message should be retried."""
        return self.retry_count < self.max_retries


class MessageQueue:
    """
    Manages the message queue for a specific agent.

    Handles reading, writing, and organizing messages in the Signals/ folder.
    """

    def __init__(self, vault_path: str, agent_id: str):
        """
        Initialize message queue for an agent.

        Args:
            vault_path: Path to the AI_Employee_Vault
            agent_id: Agent ID for this queue
        """
        self.vault_path = Path(vault_path)
        self.agent_id = agent_id
        self.signals_path = self.vault_path / "Signals"

        # Ensure Signals folder exists
        self.signals_path.mkdir(parents=True, exist_ok=True)

        # Queue folders
        self.inbox_path = self.signals_path / "Inbox" / agent_id
        self.outbox_path = self.signals_path / "Outbox"
        self.pending_path = self.signals_path / "Pending"
        self.processing_path = self.signals_path / "Processing"
        self.completed_path = self.signals_path / "Completed"
        self.failed_path = self.signals_path / "Failed"
        self.dead_letter_path = self.signals_path / "Dead_Letter"

        # Create folders
        for path in [
            self.inbox_path, self.outbox_path, self.pending_path,
            self.processing_path, self.completed_path, self.failed_path,
            self.dead_letter_path
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def get_messages(self, folder: str, status: Optional[MessageStatus] = None) -> List[Message]:
        """
        Get all messages from a folder.

        Args:
            folder: One of 'inbox', 'outbox', 'pending', 'processing',
                    'completed', 'failed', 'dead_letter'
            status: Optional filter by message status

        Returns:
            List of Message objects
        """
        folder_map = {
            "inbox": self.inbox_path,
            "outbox": self.outbox_path,
            "pending": self.pending_path,
            "processing": self.processing_path,
            "completed": self.completed_path,
            "failed": self.failed_path,
            "dead_letter": self.dead_letter_path,
        }

        if folder not in folder_map:
            raise ValueError(f"Invalid folder: {folder}")

        folder_path = folder_map[folder]
        messages = []

        for file_path in folder_path.glob("*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                message = Message.from_markdown(content)

                # Filter by status if specified
                if status is None or message.status == status:
                    messages.append(message)
            except Exception as e:
                logger.error(f"Error reading message file {file_path}: {e}")

        # Sort by timestamp (newest first)
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        return messages

    def save_message(self, message: Message, folder: str) -> Path:
        """
        Save a message to a folder.

        Args:
            message: Message to save
            folder: One of 'outbox', 'pending', 'processing', 'completed',
                    'failed', 'dead_letter'

        Returns:
            Path to saved message file
        """
        folder_map = {
            "outbox": self.outbox_path,
            "pending": self.pending_path,
            "processing": self.processing_path,
            "completed": self.completed_path,
            "failed": self.failed_path,
            "dead_letter": self.dead_letter_path,
        }

        if folder not in folder_map:
            raise ValueError(f"Invalid folder: {folder}")

        folder_path = folder_map[folder]
        filename = f"{message.message_id}.md"
        file_path = folder_path / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(message.to_markdown())

        logger.debug(f"Saved message {message.message_id} to {folder}")
        return file_path

    def move_message(self, message_id: str, from_folder: str, to_folder: str) -> Path:
        """
        Move a message between folders.

        Args:
            message_id: Message ID to move
            from_folder: Source folder
            to_folder: Destination folder

        Returns:
            Path to new message file
        """
        folder_map = {
            "inbox": self.inbox_path,
            "outbox": self.outbox_path,
            "pending": self.pending_path,
            "processing": self.processing_path,
            "completed": self.completed_path,
            "failed": self.failed_path,
            "dead_letter": self.dead_letter_path,
        }

        if from_folder not in folder_map or to_folder not in folder_map:
            raise ValueError(f"Invalid folder: {from_folder} -> {to_folder}")

        from_path = folder_map[from_folder] / f"{message_id}.md"
        to_path = folder_map[to_folder] / f"{message_id}.md"

        if not from_path.exists():
            raise FileNotFoundError(f"Message not found: {from_path}")

        # Read message to update status
        with open(from_path, "r", encoding="utf-8") as f:
            content = f.read()

        message = Message.from_markdown(content)

        # Update status based on destination
        status_map = {
            "pending": "pending",
            "processing": "processing",
            "completed": "completed",
            "failed": "failed",
            "dead_letter": "failed",
        }
        message.status = status_map.get(to_folder, message.status)

        # Write to destination
        with open(to_path, "w", encoding="utf-8") as f:
            f.write(message.to_markdown())

        # Remove from source
        from_path.unlink()

        logger.debug(f"Moved message {message_id} from {from_folder} to {to_folder}")
        return to_path

    def delete_message(self, message_id: str, folder: str) -> None:
        """Delete a message from a folder."""
        folder_map = {
            "inbox": self.inbox_path,
            "outbox": self.outbox_path,
            "pending": self.pending_path,
            "processing": self.processing_path,
            "completed": self.completed_path,
            "failed": self.failed_path,
            "dead_letter": self.dead_letter_path,
        }

        if folder not in folder_map:
            raise ValueError(f"Invalid folder: {folder}")

        file_path = folder_map[folder] / f"{message_id}.md"

        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted message {message_id} from {folder}")


class A2AMessenger:
    """
    Main messenger class for agent-to-agent communication.

    Provides high-level send/receive operations with built-in retry logic,
    message signing, and error handling.

    Usage:
        messenger = A2AMessenger(vault_path="AI_Employee_Vault", agent_id="gmail-watcher")

        # Send a message
        msg_id = messenger.send_message(
            to_agent="auto-approver",
            message_type="request",
            subject="New email detected",
            payload={"email_id": "12345"}
        )

        # Receive messages
        messages = messenger.receive_messages()

        # Acknowledge processing
        messenger.acknowledge_message(msg_id, result="success")
    """

    def __init__(
        self,
        vault_path: str,
        agent_id: str,
        secret_path: Optional[str] = None
    ):
        """
        Initialize A2A Messenger.

        Args:
            vault_path: Path to the AI_Employee_Vault
            agent_id: This agent's ID
            secret_path: Optional path to .a2a_secret file (defaults to vault/.a2a_secret)
        """
        self.vault_path = Path(vault_path)
        self.agent_id = agent_id
        self.queue = MessageQueue(vault_path, agent_id)

        # Secret for message signing
        if secret_path is None:
            secret_path = self.vault_path / ".a2a_secret"
        else:
            secret_path = Path(secret_path)

        self.secret_path = secret_path
        self._secret = self._load_or_create_secret()

        logger.info(f"A2A Messenger initialized for agent: {agent_id}")

    def _load_or_create_secret(self) -> str:
        """Load existing secret or create a new one."""
        if self.secret_path.exists():
            with open(self.secret_path, "r", encoding="utf-8") as f:
                return f.read().strip()

        # Create new secret
        secret = secrets.token_hex(32)
        self.secret_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.secret_path, "w", encoding="utf-8") as f:
            f.write(secret)

        logger.info(f"Created new A2A secret at {self.secret_path}")
        return secret

    def _sign_message(self, message: Message) -> str:
        """Generate HMAC signature for message."""
        # Create a canonical representation
        canonical = (
            f"{message.message_id}|{message.timestamp}|{message.from_agent}|"
            f"{message.to_agent}|{message.message_type}|{json.dumps(message.payload, sort_keys=True)}"
        )

        signature = hmac.new(
            self._secret.encode(),
            canonical.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _verify_signature(self, message: Message) -> bool:
        """Verify message signature."""
        if message.signature is None:
            return False

        expected_signature = self._sign_message(message)
        return hmac.compare_digest(message.signature, expected_signature)

    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = secrets.token_hex(4)
        return f"msg_{timestamp}_{random_suffix}"

    def send_message(
        self,
        to_agent: str,
        message_type: MessageType,
        subject: str,
        payload: Dict[str, Any],
        priority: MessagePriority = "normal",
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        ttl_minutes: int = 60,
        max_retries: int = 3
    ) -> str:
        """
        Send a message to another agent.

        Args:
            to_agent: Recipient agent ID
            message_type: Type of message (request, response, notification, etc.)
            subject: Human-readable subject line
            payload: Message data (must be JSON-serializable)
            priority: Message priority level
            correlation_id: For request/response correlation
            reply_to: Message ID this is a reply to
            ttl_minutes: Time-to-live in minutes
            max_retries: Maximum retry attempts

        Returns:
            Message ID of sent message

        Raises:
            MessageValidationError: If message validation fails
        """
        # Validate inputs
        if not subject:
            raise MessageValidationError("subject is required")

        # Broadcasts have empty to_agent
        if message_type == "broadcast":
            to_agent = ""
        elif not to_agent:
            raise MessageValidationError("to_agent is required")

        # Create message
        now = datetime.now()
        expires = now + timedelta(minutes=ttl_minutes)

        message = Message(
            message_id=self._generate_message_id(),
            timestamp=now.isoformat(),
            expires=expires.isoformat(),
            priority=priority,
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            correlation_id=correlation_id,
            subject=subject,
            payload=payload,
            reply_to=reply_to,
            max_retries=max_retries,
        )

        # Sign message
        message.signature = self._sign_message(message)

        # Save to outbox
        self.queue.save_message(message, "outbox")

        logger.info(
            f"Sent {message_type} message {message.message_id} "
            f"from {self.agent_id} to {to_agent or 'broadcast'}"
        )

        return message.message_id

    def receive_messages(
        self,
        status: Optional[MessageStatus] = None,
        include_expired: bool = False
    ) -> List[Message]:
        """
        Receive pending messages for this agent.

        Args:
            status: Optional filter by status
            include_expired: Whether to include expired messages

        Returns:
            List of pending messages
        """
        messages = self.queue.get_messages("inbox", status)

        # Filter expired messages unless requested
        if not include_expired:
            messages = [m for m in messages if not m.is_expired()]

        # Verify signatures
        valid_messages = []
        for message in messages:
            if self._verify_signature(message):
                valid_messages.append(message)
            else:
                logger.warning(f"Message {message.message_id} has invalid signature")

        return valid_messages

    def acknowledge_message(
        self,
        message_id: str,
        result: Literal["success", "failure"] = "success",
        error_message: Optional[str] = None,
        response_payload: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Acknowledge processing of a message.

        Args:
            message_id: Message ID being acknowledged
            result: Processing result
            error_message: Optional error message on failure
            response_payload: Optional response data

        Raises:
            MessageDeliveryError: If message not found
        """
        messages = self.queue.get_messages("processing")
        message = None

        for msg in messages:
            if msg.message_id == message_id:
                message = msg
                break

        if message is None:
            raise MessageDeliveryError(f"Message not found in processing: {message_id}")

        # Update message
        message.processed_at = datetime.now().isoformat()
        message.error_message = error_message

        if result == "success":
            message.status = "completed"
            # Save updated message to destination
            self.queue.save_message(message, "completed")
            # Remove from processing
            from_path = self.queue.processing_path / f"{message_id}.md"
            if from_path.exists():
                from_path.unlink()
            logger.info(f"Message {message_id} processed successfully")
        else:
            message.status = "failed"
            # Save updated message to destination
            self.queue.save_message(message, "failed")
            # Remove from processing
            from_path = self.queue.processing_path / f"{message_id}.md"
            if from_path.exists():
                from_path.unlink()
            logger.warning(f"Message {message_id} processing failed: {error_message}")

        # Send response if this was a request
        if message.message_type == "request" and result == "success" and response_payload:
            self.send_message(
                to_agent=message.from_agent,
                message_type="response",
                subject=f"Re: {message.subject}",
                payload=response_payload,
                correlation_id=message.message_id,
                reply_to=message.message_id
            )

    def get_message(self, message_id: str) -> Optional[Message]:
        """
        Get a message by ID from any folder.

        Args:
            message_id: Message ID to retrieve

        Returns:
            Message if found, None otherwise
        """
        for folder in ["inbox", "processing", "completed", "failed", "dead_letter"]:
            messages = self.queue.get_messages(folder)
            for msg in messages:
                if msg.message_id == message_id:
                    return msg
        return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get current messenger status.

        Returns:
            Dict with message counts by status
        """
        return {
            "agent_id": self.agent_id,
            "inbox_pending": len(self.queue.get_messages("inbox", "pending")),
            "processing": len(self.queue.get_messages("processing")),
            "completed": len(self.queue.get_messages("completed")),
            "failed": len(self.queue.get_messages("failed")),
            "dead_letter": len(self.queue.get_messages("dead_letter")),
        }

    def cleanup_old_messages(self, days: int = 7) -> int:
        """
        Clean up old completed messages.

        Args:
            days: Remove messages older than this many days

        Returns:
            Number of messages cleaned up
        """
        cutoff = datetime.now() - timedelta(days=days)
        cleaned = 0

        messages = self.queue.get_messages("completed")
        for message in messages:
            try:
                msg_time = datetime.fromisoformat(message.timestamp.replace("Z", "+00:00"))
                if msg_time < cutoff:
                    self.queue.delete_message(message.message_id, "completed")
                    cleaned += 1
            except (ValueError, AttributeError):
                continue

        logger.info(f"Cleaned up {cleaned} old messages")
        return cleaned


def create_broadcast_message(
    messenger: A2AMessenger,
    subject: str,
    payload: Dict[str, Any],
    priority: MessagePriority = "normal"
) -> str:
    """
    Convenience function to create a broadcast message.

    Broadcast messages are sent to all agents and typically contain
    system-wide announcements or notifications.

    Args:
        messenger: A2A Messenger instance
        subject: Subject line
        payload: Message data
        priority: Message priority

    Returns:
        Message ID
    """
    return messenger.send_message(
        to_agent="",  # Empty for broadcast
        message_type="broadcast",
        subject=subject,
        payload=payload,
        priority=priority
    )


def send_request_and_wait(
    messenger: A2AMessenger,
    to_agent: str,
    subject: str,
    payload: Dict[str, Any],
    timeout_seconds: int = 30,
    poll_interval: float = 0.5
) -> Optional[Dict[str, Any]]:
    """
    Send a request and wait for response.

    This is a blocking call that waits for a response message.

    Args:
        messenger: A2A Messenger instance
        to_agent: Recipient agent
        subject: Request subject
        payload: Request data
        timeout_seconds: Maximum time to wait
        poll_interval: How often to check for responses

    Returns:
        Response payload if received, None on timeout
    """
    msg_id = messenger.send_message(
        to_agent=to_agent,
        message_type="request",
        subject=subject,
        payload=payload
    )

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        # Check for response
        messages = messenger.receive_messages()
        for msg in messages:
            if msg.reply_to == msg_id and msg.message_type == "response":
                messenger.acknowledge_message(msg.message_id, "success")
                return msg.payload

        time.sleep(poll_interval)

    logger.warning(f"Request {msg_id} timed out waiting for response")
    return None
