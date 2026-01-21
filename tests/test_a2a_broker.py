"""
Unit tests for A2A Message Broker module.

Tests the A2AMessageBroker class.
"""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.a2a_message_broker import A2AMessageBroker
from utils.agent_registry import AgentRole


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault directory."""
    vault_path = tmp_path / "AI_Employee_Vault"
    vault_path.mkdir()
    (vault_path / "Signals").mkdir()
    return str(vault_path)


@pytest.fixture
def broker(temp_vault):
    """Create a broker instance."""
    return A2AMessageBroker(
        vault_path=temp_vault,
        check_interval_seconds=1
    )


class TestA2AMessageBroker:
    """Tests for A2AMessageBroker class."""

    def test_broker_initialization(self, broker, temp_vault):
        """Test broker initialization."""
        assert broker.vault_path == Path(temp_vault)
        assert broker.check_interval == 1
        assert broker._running is False
        assert broker.stats["messages_routed"] == 0

    def test_register_broker(self, broker):
        """Test broker registers itself in registry."""
        broker._register_broker()

        agent = broker.registry.get_agent("a2a-message-broker")
        assert agent is not None
        assert agent.agent_id == "a2a-message-broker"
        assert "message_routing" in agent.capabilities

        broker._unregister_broker()

    def test_unregister_broker(self, broker):
        """Test broker unregisters itself."""
        broker._register_broker()
        broker._unregister_broker()

        agent = broker.registry.get_agent("a2a-message-broker")
        assert agent is None

    def test_process_outbox(self, temp_vault):
        """Test processing messages from outbox."""
        from utils.a2a_messenger import A2AMessenger, Message

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Create a message in outbox
        messenger = A2AMessenger(vault_path=temp_vault, agent_id="sender")
        messenger.send_message(
            to_agent="recipient",
            message_type="request",
            subject="Test",
            payload={"test": "data"}
        )

        # Process outbox
        processed = broker._process_outbox()

        assert processed == 1

        # Verify moved to pending
        messages = broker.queue.get_messages("pending")
        assert len(messages) == 1

    def test_deliver_message(self, temp_vault):
        """Test delivering a message to recipient."""
        from utils.a2a_messenger import Message, MessagePriority

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Register recipient
        broker.registry.register(
            agent_id="recipient",
            capabilities=["receive"],
            role=AgentRole.WATCHER
        )

        # Create message
        msg = Message(
            message_id="msg_test_delivery",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority=MessagePriority.NORMAL,
            from_agent="sender",
            to_agent="recipient",
            message_type="request",
            subject="Test Delivery"
        )

        # Save to pending
        broker.queue.save_message(msg, "pending")

        # Route messages
        routed = broker.route_messages()

        assert routed == 1
        assert broker.stats["messages_routed"] == 1

        # Verify in recipient inbox
        recipient_queue = broker.queue.__class__(temp_vault, "recipient")
        messages = recipient_queue.get_messages("inbox")
        assert len(messages) == 1

    def test_deliver_to_offline_agent(self, temp_vault):
        """Test behavior when recipient is offline."""
        from utils.a2a_messenger import Message, MessagePriority

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Don't register recipient (so it's offline)

        # Create message
        msg = Message(
            message_id="msg_offline_test",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority=MessagePriority.NORMAL,
            from_agent="sender",
            to_agent="offline-recipient",
            message_type="request",
            subject="Test Offline",
            retry_count=0,
            max_retries=3
        )

        broker.queue.save_message(msg, "pending")

        # Route messages
        broker.route_messages()

        # Message should stay in pending (will retry)
        messages = broker.queue.get_messages("pending")
        assert len(messages) == 1
        assert messages[0].retry_count == 1

    def test_handle_broadcast(self, temp_vault):
        """Test handling broadcast messages."""
        from utils.a2a_messenger import Message, MessagePriority

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Register multiple agents
        broker.registry.register("agent1", ["cap1"], AgentRole.WATCHER)
        broker.registry.register("agent2", ["cap2"], AgentRole.WATCHER)
        broker.registry.register("agent3", ["cap3"], AgentRole.WATCHER)

        # Create broadcast message
        msg = Message(
            message_id="msg_broadcast_test",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority=MessagePriority.NORMAL,
            from_agent="sender",
            to_agent="",  # Empty for broadcast
            message_type="broadcast",
            subject="Broadcast Test",
            payload={"announcement": "hello"}
        )

        broker.queue.save_message(msg, "pending")

        # Route
        broker.route_messages()

        # Original should be in completed
        messages = broker.queue.get_messages("completed")
        assert len(messages) == 1

        # Each recipient should have received a copy
        for agent_id in ["agent1", "agent2", "agent3"]:
            agent_queue = broker.queue.__class__(temp_vault, agent_id)
            agent_messages = agent_queue.get_messages("inbox")
            assert len(agent_messages) == 1
            assert agent_messages[0].subject == "[Broadcast] Broadcast Test"

    def test_check_message_expiration(self, temp_vault):
        """Test checking for expired messages."""
        from utils.a2a_messenger import Message

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Create expired message
        expired_msg = Message(
            message_id="msg_expired",
            timestamp="2026-01-01T10:00:00Z",
            expires="2026-01-01T09:00:00Z",  # Already expired
            priority="normal",
            from_agent="test",
            to_agent="test",
            message_type="notification"
        )

        broker.queue.save_message(expired_msg, "pending")

        # Check expiration
        expired_count = broker.check_message_expiration()

        assert expired_count == 1

        # Should be in failed
        messages = broker.queue.get_messages("failed")
        assert len(messages) == 1

    def test_cleanup_old_messages(self, temp_vault):
        """Test cleanup of old messages."""
        from utils.a2a_messenger import Message

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Create old message
        old_time = datetime.now() - timedelta(days=10)
        old_msg = Message(
            message_id="msg_old",
            timestamp=old_time.isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority="normal",
            from_agent="test",
            to_agent="test",
            message_type="notification",
            status="completed"
        )

        broker.queue.save_message(old_msg, "completed")

        # Cleanup
        cleaned = broker.cleanup_old_messages(days=7)

        assert sum(cleaned.values()) >= 1

    def test_cleanup_stale_agents(self, temp_vault):
        """Test cleanup of stale agents."""
        broker = A2AMessageBroker(vault_path=temp_vault)

        # Register fresh agent
        broker.registry.register("fresh", ["test"], AgentRole.WATCHER)

        # Register stale agent
        broker.registry.register("stale", ["test"], AgentRole.WATCHER)
        agent_data = broker.registry._load_registry()
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        agent_data["agents"]["stale"]["last_heartbeat"] = old_time
        broker.registry._save_registry(agent_data)

        # Cleanup
        removed = broker.cleanup_stale_agents(max_age_hours=24)

        assert removed == 1

    def test_get_status(self, broker):
        """Test getting broker status."""
        status = broker.get_status()

        assert "broker_id" in status
        assert status["broker_id"] == "a2a-message-broker"
        assert "running" in status
        assert "statistics" in status
        assert "registry" in status
        assert "queue_sizes" in status

    def test_run_once(self, temp_vault):
        """Test running a single broker cycle."""
        from utils.a2a_messenger import A2AMessenger

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Register recipient
        broker.registry.register("recipient", ["receive"], AgentRole.WATCHER)

        # Create message
        messenger = A2AMessenger(vault_path=temp_vault, agent_id="sender")
        messenger.send_message(
            to_agent="recipient",
            message_type="request",
            subject="Test",
            payload={"test": "data"}
        )

        # Run one cycle
        results = broker.run_once()

        assert "outbox_processed" in results
        assert "messages_routed" in results
        assert results["outbox_processed"] == 1

    def test_max_retries_exceeded(self, temp_vault):
        """Test message moved to dead letter after max retries."""
        from utils.a2a_messenger import Message, MessagePriority

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Don't register recipient

        # Create message with max retries
        msg = Message(
            message_id="msg_retry_test",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority=MessagePriority.NORMAL,
            from_agent="sender",
            to_agent="offline-recipient",
            message_type="request",
            subject="Retry Test",
            retry_count=3,  # Already at max
            max_retries=3
        )

        broker.queue.save_message(msg, "pending")

        # Route
        broker.route_messages()

        # Should be in dead letter
        messages = broker.queue.get_messages("dead_letter")
        assert len(messages) == 1

    def test_broadcast_excludes_sender(self, temp_vault):
        """Test broadcast excludes the sender from recipients."""
        from utils.a2a_messenger import Message, MessagePriority

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Register agents including the sender
        broker.registry.register("sender", ["send"], AgentRole.WATCHER)
        broker.registry.register("recipient1", ["receive"], AgentRole.WATCHER)
        broker.registry.register("recipient2", ["receive"], AgentRole.WATCHER)

        # Create broadcast from sender
        msg = Message(
            message_id="msg_broadcast_exclude",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority=MessagePriority.NORMAL,
            from_agent="sender",
            to_agent="",
            message_type="broadcast",
            subject="Test",
            payload={"test": "data"}
        )

        broker.queue.save_message(msg, "pending")

        # Route
        broker.route_messages()

        # Sender should not receive their own broadcast
        sender_queue = broker.queue.__class__(temp_vault, "sender")
        sender_messages = sender_queue.get_messages("inbox")
        assert len(sender_messages) == 0

        # Recipients should receive
        for agent_id in ["recipient1", "recipient2"]:
            agent_queue = broker.queue.__class__(temp_vault, agent_id)
            agent_messages = agent_queue.get_messages("inbox")
            assert len(agent_messages) == 1


class TestBrokerLifecycle:
    """Tests for broker lifecycle management."""

    def test_broker_run_and_shutdown(self, temp_vault):
        """Test broker run loop and shutdown."""
        broker = A2AMessageBroker(
            vault_path=temp_vault,
            check_interval_seconds=1
        )

        # Start broker in background
        import threading
        broker_thread = threading.Thread(target=broker.run)
        broker_thread.start()

        # Wait a bit
        time.sleep(2)

        # Request shutdown
        broker.shutdown()

        # Wait for thread to finish
        broker_thread.join(timeout=5)

        assert broker._running is False

    def test_shutdown_signal_handling(self, temp_vault):
        """Test broker handles shutdown signals."""
        broker = A2AMessageBroker(vault_path=temp_vault)

        # Request shutdown
        broker.shutdown()

        assert broker._shutdown_requested is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
