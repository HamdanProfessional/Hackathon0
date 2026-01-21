"""
Unit tests for A2A Messenger module.

Tests the Message, MessageQueue, and A2AMessenger classes.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json

from utils.a2a_messenger import (
    Message, MessageQueue, A2AMessenger,
    MessageType, MessageStatus, MessagePriority,
    MessageError, MessageValidationError,
    create_broadcast_message
)


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault directory."""
    vault_path = tmp_path / "AI_Employee_Vault"
    vault_path.mkdir()
    (vault_path / "Signals").mkdir()
    return str(vault_path)


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        message_id="msg_20260122_143052_a1b2c3d4",
        timestamp="2026-01-22T14:30:52Z",
        expires="2026-01-22T15:30:52Z",
        priority="high",
        from_agent="gmail-watcher",
        to_agent="auto-approver",
        message_type="request",
        correlation_id="email_12345_processed",
        subject="Test Email Detected",
        payload={"email_id": "12345", "subject": "Test Subject"}
    )


class TestMessage:
    """Tests for Message class."""

    def test_message_creation(self, sample_message):
        """Test creating a message."""
        assert sample_message.message_id == "msg_20260122_143052_a1b2c3d4"
        assert sample_message.from_agent == "gmail-watcher"
        assert sample_message.to_agent == "auto-approver"
        assert sample_message.message_type == "request"
        assert sample_message.priority == "high"

    def test_to_markdown(self, sample_message):
        """Test converting message to markdown format."""
        markdown = sample_message.to_markdown()

        assert "---" in markdown
        assert "type: a2a_message" in markdown
        assert "message_id: msg_20260122_143052_a1b2c3d4" in markdown
        assert "# Test Email Detected" in markdown
        assert "## Payload" in markdown
        assert '"email_id": "12345"' in markdown

    def test_from_markdown(self, sample_message):
        """Test parsing message from markdown format."""
        markdown = sample_message.to_markdown()
        parsed = Message.from_markdown(markdown)

        assert parsed.message_id == sample_message.message_id
        assert parsed.from_agent == sample_message.from_agent
        assert parsed.to_agent == sample_message.to_agent
        assert parsed.message_type == sample_message.message_type
        assert parsed.subject == sample_message.subject
        assert parsed.payload == sample_message.payload

    def test_is_expired_false(self, sample_message):
        """Test expiration check for non-expired message."""
        # Future expiration
        assert not sample_message.is_expired()

    def test_is_expired_true(self):
        """Test expiration check for expired message."""
        message = Message(
            message_id="msg_test",
            timestamp="2026-01-01T10:00:00Z",
            expires="2026-01-01T09:00:00Z",  # Expired
            priority="normal",
            from_agent="test",
            to_agent="test",
            message_type="notification"
        )
        assert message.is_expired()

    def test_should_retry(self):
        """Test retry logic."""
        message = Message(
            message_id="msg_test",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="test",
            to_agent="test",
            message_type="notification",
            retry_count=0,
            max_retries=3
        )

        assert message.should_retry()

        message.retry_count = 3
        assert not message.should_retry()


class TestMessageQueue:
    """Tests for MessageQueue class."""

    def test_queue_initialization(self, temp_vault):
        """Test queue creates necessary folders."""
        queue = MessageQueue(temp_vault, "test-agent")

        assert queue.inbox_path.exists()
        assert queue.outbox_path.exists()
        assert queue.pending_path.exists()
        assert queue.processing_path.exists()
        assert queue.completed_path.exists()
        assert queue.failed_path.exists()
        assert queue.dead_letter_path.exists()

    def test_save_and_get_message(self, temp_vault, sample_message):
        """Test saving and retrieving a message."""
        queue = MessageQueue(temp_vault, "test-agent")

        # Save message
        file_path = queue.save_message(sample_message, "outbox")
        assert file_path.exists()
        assert file_path.name == f"{sample_message.message_id}.md"

        # Get messages
        messages = queue.get_messages("outbox")
        assert len(messages) == 1
        assert messages[0].message_id == sample_message.message_id

    def test_move_message(self, temp_vault, sample_message):
        """Test moving message between folders."""
        queue = MessageQueue(temp_vault, "test-agent")

        # Save to outbox
        queue.save_message(sample_message, "outbox")

        # Create a new queue with a different agent to simulate recipient
        recipient_queue = MessageQueue(temp_vault, "recipient")
        recipient_queue.inbox_path.mkdir(parents=True, exist_ok=True)

        # Copy message to pending first
        pending_path = queue.pending_path / f"{sample_message.message_id}.md"
        shutil.copy(
            queue.outbox_path / f"{sample_message.message_id}.md",
            pending_path
        )

        # Move to processing
        result = queue.move_message(sample_message.message_id, "pending", "processing")
        assert result.exists()
        assert not pending_path.exists()

        # Verify in processing
        messages = queue.get_messages("processing")
        assert len(messages) == 1
        assert messages[0].status == "processing"

    def test_delete_message(self, temp_vault, sample_message):
        """Test deleting a message."""
        queue = MessageQueue(temp_vault, "test-agent")

        # Save message
        queue.save_message(sample_message, "completed")

        # Delete message
        queue.delete_message(sample_message.message_id, "completed")

        # Verify deleted
        messages = queue.get_messages("completed")
        assert len(messages) == 0

    def test_get_messages_by_status(self, temp_vault):
        """Test filtering messages by status."""
        queue = MessageQueue(temp_vault, "test-agent")

        # Create messages with different statuses
        msg1 = Message(
            message_id="msg_1",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="test",
            to_agent="test",
            message_type="notification",
            status="pending"
        )

        msg2 = Message(
            message_id="msg_2",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="test",
            to_agent="test",
            message_type="notification",
            status="completed"
        )

        queue.save_message(msg1, "processing")
        queue.save_message(msg2, "completed")

        # Get all messages
        all_messages = queue.get_messages("processing")
        assert len(all_messages) == 1

        # Get by status (simulated - would need to implement filter)
        completed = queue.get_messages("completed", "completed")
        assert len(completed) == 1


class TestA2AMessenger:
    """Tests for A2AMessenger class."""

    @pytest.fixture
    def messenger(self, temp_vault):
        """Create a messenger instance."""
        return A2AMessenger(vault_path=temp_vault, agent_id="test-agent")

    def test_messenger_initialization(self, messenger):
        """Test messenger creates necessary components."""
        assert messenger.agent_id == "test-agent"
        assert messenger.queue is not None
        assert messenger._secret is not None

    def test_send_message(self, messenger):
        """Test sending a message."""
        msg_id = messenger.send_message(
            to_agent="recipient",
            message_type="request",
            subject="Test Request",
            payload={"test": "data"}
        )

        assert msg_id.startswith("msg_")
        assert len(msg_id) > 10

        # Verify message in outbox
        messages = messenger.queue.get_messages("outbox")
        assert len(messages) == 1
        assert messages[0].message_id == msg_id
        assert messages[0].to_agent == "recipient"
        assert messages[0].subject == "Test Request"

    def test_send_broadcast_message(self, messenger):
        """Test sending a broadcast message."""
        msg_id = messenger.send_message(
            to_agent="",  # Empty for broadcast
            message_type="broadcast",
            subject="Broadcast Test",
            payload={"announcement": "test"}
        )

        messages = messenger.queue.get_messages("outbox")
        assert len(messages) == 1
        assert messages[0].message_type == "broadcast"

    def test_receive_messages_empty(self, messenger):
        """Test receiving messages when inbox is empty."""
        messages = messenger.receive_messages()
        assert len(messages) == 0

    def test_send_and_receive(self, temp_vault):
        """Test sending a message between two agents."""
        # Create two messengers
        sender = A2AMessenger(vault_path=temp_vault, agent_id="sender")
        recipient = A2AMessenger(vault_path=temp_vault, agent_id="recipient")

        # Send message
        msg_id = sender.send_message(
            to_agent="recipient",
            message_type="request",
            subject="Hello",
            payload={"greeting": "hi"}
        )

        # Manually move to recipient inbox (simulating broker)
        recipient_queue = MessageQueue(temp_vault, "recipient")
        recipient_queue.inbox_path.mkdir(parents=True, exist_ok=True)
        msg_file = sender.queue.outbox_path / f"{msg_id}.md"
        dest_file = recipient_queue.inbox_path / f"{msg_id}.md"
        shutil.copy(msg_file, dest_file)

        # Receive message
        messages = recipient.receive_messages()
        assert len(messages) == 1
        assert messages[0].subject == "Hello"

    def test_acknowledge_message(self, temp_vault):
        """Test acknowledging a message."""
        messenger = A2AMessenger(vault_path=temp_vault, agent_id="test-agent")

        # Create a message in processing
        msg = Message(
            message_id="msg_test_ack",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="sender",
            to_agent="test-agent",
            message_type="request",
            status="processing"
        )

        messenger.queue.save_message(msg, "processing")

        # Acknowledge
        messenger.acknowledge_message("msg_test_ack", "success")

        # Verify moved to completed
        messages = messenger.queue.get_messages("completed")
        assert len(messages) == 1
        assert messages[0].status == "completed"

    def test_acknowledge_with_failure(self, temp_vault):
        """Test acknowledging with failure result."""
        messenger = A2AMessenger(vault_path=temp_vault, agent_id="test-agent")

        # Create a message in processing
        msg = Message(
            message_id="msg_test_fail",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="sender",
            to_agent="test-agent",
            message_type="request",
            status="processing"
        )

        messenger.queue.save_message(msg, "processing")

        # Acknowledge with failure
        messenger.acknowledge_message("msg_test_fail", "failure", "Test error")

        # Verify moved to failed
        messages = messenger.queue.get_messages("failed")
        assert len(messages) == 1
        assert messages[0].error_message == "Test error"

    def test_get_status(self, messenger):
        """Test getting messenger status."""
        status = messenger.get_status()

        assert "agent_id" in status
        assert status["agent_id"] == "test-agent"
        assert "inbox_pending" in status
        assert "processing" in status

    def test_send_message_validation_error(self, messenger):
        """Test validation when sending message."""
        # Missing to_agent
        with pytest.raises(MessageValidationError):
            messenger.send_message(
                to_agent="",
                message_type="request",
                subject="Test",
                payload={}
            )

        # Missing subject
        with pytest.raises(MessageValidationError):
            messenger.send_message(
                to_agent="recipient",
                message_type="request",
                subject="",
                payload={}
            )

    def test_message_signing(self, messenger):
        """Test message signing and verification."""
        msg = Message(
            message_id="msg_sign_test",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="test-agent",
            to_agent="recipient",
            message_type="request"
        )

        # Sign message
        signature = messenger._sign_message(msg)
        msg.signature = signature

        # Verify signature
        assert messenger._verify_signature(msg)

        # Tamper with message
        msg.to_agent = "attacker"
        assert not messenger._verify_signature(msg)

    def test_cleanup_old_messages(self, messenger):
        """Test cleanup of old messages."""
        # Create an old completed message
        old_time = datetime.now() - timedelta(days=10)
        old_msg = Message(
            message_id="msg_old",
            timestamp=old_time.isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="test",
            to_agent="test",
            message_type="notification",
            status="completed",
            processed_at=datetime.now().isoformat()
        )

        messenger.queue.save_message(old_msg, "completed")

        # Cleanup
        cleaned = messenger.cleanup_old_messages(days=7)
        assert cleaned >= 1


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_broadcast_message(self, temp_vault):
        """Test creating broadcast message helper."""
        messenger = A2AMessenger(vault_path=temp_vault, agent_id="test-agent")

        msg_id = create_broadcast_message(
            messenger=messenger,
            subject="System Announcement",
            payload={"message": "Hello all"},
            priority="high"
        )

        messages = messenger.queue.get_messages("outbox")
        assert len(messages) == 1
        assert messages[0].message_type == "broadcast"
        assert messages[0].priority == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
