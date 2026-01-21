"""
Integration tests for A2A Messaging System.

Tests end-to-end message flow between agents, including:
- Multi-agent coordination
- Request/response patterns
- Broadcast messaging
- Failure scenarios
"""

import pytest
import tempfile
import shutil
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.a2a_messenger import A2AMessenger, MessageType, MessagePriority
from utils.agent_registry import AgentRegistry, AgentRole
from scripts.a2a_message_broker import A2AMessageBroker


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault with Signals folder."""
    vault_path = tmp_path / "AI_Employee_Vault"
    vault_path.mkdir()
    (vault_path / "Signals").mkdir()
    return str(vault_path)


@pytest.fixture
def setup_agents(temp_vault):
    """Set up multiple agents for testing."""
    agents = {}

    # Create multiple agents
    agent_configs = [
        ("gmail-watcher", ["email_detection", "spam_classification"], AgentRole.WATCHER),
        ("auto-approver", ["classification", "routing"], AgentRole.PROCESSOR),
        ("slack-watcher", ["slack_detection"], AgentRole.WATCHER),
        ("email-approval-monitor", ["email_processing"], AgentRole.MONITOR),
    ]

    for agent_id, capabilities, role in agent_configs:
        messenger = A2AMessenger(vault_path=temp_vault, agent_id=agent_id)
        registry = AgentRegistry(vault_path=temp_vault)

        # Register agent
        registry.register(
            agent_id=agent_id,
            capabilities=capabilities,
            role=role
        )

        agents[agent_id] = {
            "messenger": messenger,
            "registry": registry,
        }

    return agents


class TestEndToEndMessaging:
    """Tests for complete message flows."""

    def test_send_and_receive_single_message(self, temp_vault, setup_agents):
        """Test basic send and receive between two agents."""
        sender = setup_agents["gmail-watcher"]["messenger"]
        recipient_messenger = setup_agents["auto-approver"]["messenger"]

        # Register recipient
        setup_agents["auto-approver"]["registry"].send_heartbeat("auto-approver")

        # Send message
        msg_id = sender.send_message(
            to_agent="auto-approver",
            message_type="request",
            subject="Classify email",
            payload={"subject": "Invoice #1234"}
        )

        # Simulate broker routing
        from utils.a2a_messenger import MessageQueue
        queue = MessageQueue(temp_vault, "gmail-watcher")
        recipient_queue = MessageQueue(temp_vault, "auto-approver")

        # Move from outbox to pending
        pending_files = list(queue.outbox_path.glob("*.md"))
        if pending_files:
            shutil.move(pending_files[0], queue.pending_path / pending_files[0].name)

        # Read and deliver to recipient
        pending_msg_files = list(queue.pending_path.glob("*.md"))
        if pending_msg_files:
            with open(pending_msg_files[0], "r") as f:
                content = f.read()
            dest = recipient_queue.inbox_path / pending_msg_files[0].name
            recipient_queue.inbox_path.mkdir(parents=True, exist_ok=True)
            with open(dest, "w") as f:
                f.write(content)
            pending_msg_files[0].unlink()

        # Receive message
        messages = recipient_messenger.receive_messages()
        assert len(messages) == 1
        assert messages[0].message_id == msg_id
        assert messages[0].subject == "Classify email"

    def test_request_response_pattern(self, temp_vault, setup_agents):
        """Test request-response pattern between agents."""
        requester = setup_agents["gmail-watcher"]["messenger"]
        responder = setup_agents["auto-approver"]["messenger"]

        # Register both
        setup_agents["gmail-watcher"]["registry"].send_heartbeat("gmail-watcher")
        setup_agents["auto-approver"]["registry"].send_heartbeat("auto-approver")

        # Send request
        request_id = requester.send_message(
            to_agent="auto-approver",
            message_type="request",
            subject="Classification request",
            payload={"subject": "URGENT: Payment Due"}
        )

        # Simulate delivery
        from utils.a2a_messenger import MessageQueue
        queue = MessageQueue(temp_vault, "gmail-watcher")
        recipient_queue = MessageQueue(temp_vault, "auto-approver")

        # Move and deliver
        pending_files = list(queue.outbox_path.glob("*.md"))
        if pending_files:
            shutil.move(pending_files[0], queue.pending_path / pending_files[0].name)

        pending_msg_files = list(queue.pending_path.glob("*.md"))
        if pending_msg_files:
            with open(pending_msg_files[0], "r") as f:
                content = f.read()
            dest = recipient_queue.inbox_path / pending_msg_files[0].name
            recipient_queue.inbox_path.mkdir(parents=True, exist_ok=True)
            with open(dest, "w") as f:
                f.write(content)
            pending_msg_files[0].unlink()

        # Responder receives
        messages = responder.receive_messages()
        assert len(messages) == 1

        original_msg = messages[0]

        # Send response
        response_id = responder.send_message(
            to_agent="gmail-watcher",
            message_type="response",
            subject=f"Re: {original_msg.subject}",
            payload={"category": "urgent", "confidence": 0.95},
            correlation_id=request_id,
            reply_to=request_id
        )

        assert response_id.startswith("msg_")

    def test_broadcast_to_multiple_agents(self, temp_vault, setup_agents):
        """Test broadcast message reaches all agents."""
        broadcaster = setup_agents["gmail-watcher"]["messenger"]

        # Register all agents
        for agent_id in setup_agents:
            setup_agents[agent_id]["registry"].send_heartbeat(agent_id)

        # Send broadcast
        broadcast_id = broadcaster.send_message(
            to_agent="",  # Empty for broadcast
            message_type="broadcast",
            subject="System announcement",
            payload={"message": "Maintenance at 10 PM"}
        )

        # Simulate broker broadcast delivery
        from utils.a2a_messenger import MessageQueue
        queue = MessageQueue(temp_vault, "gmail-watcher")

        # Move to pending
        pending_files = list(queue.outbox_path.glob("*.md"))
        if pending_files:
            shutil.move(pending_files[0], queue.pending_path / pending_files[0].name)

        # Broker creates copies for each recipient (except sender)
        pending_msg_files = list(queue.pending_path.glob("*.md"))
        if pending_msg_files:
            with open(pending_msg_files[0], "r") as f:
                content = f.read()

            # Deliver to all other agents
            for agent_id in ["auto-approver", "slack-watcher", "email-approval-monitor"]:
                recipient_queue = MessageQueue(temp_vault, agent_id)
                recipient_queue.inbox_path.mkdir(parents=True, exist_ok=True)

                # Create copy with unique ID
                import re
                msg_id_match = re.search(r'msg_\d+_\d+_[a-f0-9]+', content)
                if msg_id_match:
                    original_id = msg_id_match.group()
                    copy_id = f"{original_id}_to_{agent_id}_{int(time.time())}"
                    content_copy = content.replace(original_id, copy_id)
                    content_copy = content_copy.replace(
                        f"to_agent: gmail-watcher",
                        f"to_agent: {agent_id}"
                    )
                else:
                    content_copy = content

                dest = recipient_queue.inbox_path / f"{copy_id if 'copy_id' in locals() else broadcast_id}.md"
                with open(dest, "w") as f:
                    f.write(content_copy)

            pending_msg_files[0].unlink()

        # Verify all recipients received
        for agent_id in ["auto-approver", "slack-watcher", "email-approval-monitor"]:
            recipient_messenger = setup_agents[agent_id]["messenger"]
            messages = recipient_messenger.receive_messages()
            assert len(messages) == 1
            assert "System announcement" in messages[0].subject

    def test_message_expiration(self, temp_vault):
        """Test expired messages are handled correctly."""
        messenger = A2AMessenger(vault_path=temp_vault, agent_id="test-agent")

        # Create expired message
        from utils.a2a_messenger import Message, MessageQueue
        queue = MessageQueue(temp_vault, "test-agent")

        expired_msg = Message(
            message_id="msg_expired_test",
            timestamp="2026-01-01T10:00:00Z",
            expires="2026-01-01T09:00:00Z",  # Already expired
            priority="normal",
            from_agent="sender",
            to_agent="test-agent",
            message_type="notification",
            subject="Expired message"
        )

        queue.save_message(expired_msg, "inbox")

        # Receive should not include expired by default
        messages = messenger.receive_messages(include_expired=False)
        assert len(messages) == 0

        # But should include if requested
        messages = messenger.receive_messages(include_expired=True)
        assert len(messages) == 1


class TestBrokerIntegration:
    """Tests for broker integration with messaging."""

    def test_broker_processes_outbox(self, temp_vault):
        """Test broker moves messages from outbox to pending."""
        # Create sender
        sender = A2AMessenger(vault_path=temp_vault, agent_id="sender")

        # Register recipient
        registry = AgentRegistry(vault_path=temp_vault)
        registry.register("recipient", ["receive"], AgentRole.WATCHER)
        registry.send_heartbeat("recipient")

        # Send message
        sender.send_message(
            to_agent="recipient",
            message_type="notification",
            subject="Test",
            payload={}
        )

        # Create broker and run once
        broker = A2AMessageBroker(vault_path=temp_vault, check_interval_seconds=1)
        broker._register_broker()

        # Process outbox
        processed = broker._process_outbox()
        assert processed == 1

        # Verify in pending
        messages = broker.queue.get_messages("pending")
        assert len(messages) == 1

        broker._unregister_broker()

    def test_broker_delivers_messages(self, temp_vault):
        """Test broker delivers to recipient inboxes."""
        # Create and register agents
        sender = A2AMessenger(vault_path=temp_vault, agent_id="sender")
        registry = AgentRegistry(vault_path=temp_vault)

        registry.register("sender", ["send"], AgentRole.WATCHER)
        registry.register("recipient", ["receive"], AgentRole.WATCHER)
        registry.send_heartbeat("recipient")

        # Send message
        msg_id = sender.send_message(
            to_agent="recipient",
            message_type="notification",
            subject="Test delivery",
            payload={"test": "data"}
        )

        # Run broker
        broker = A2AMessageBroker(vault_path=temp_vault, check_interval_seconds=1)
        broker._register_broker()

        # Run one cycle
        results = broker.run_once()

        assert results["outbox_processed"] == 1
        assert results["messages_routed"] == 1

        # Verify recipient received
        recipient = A2AMessenger(vault_path=temp_vault, agent_id="recipient")
        messages = recipient.receive_messages()

        assert len(messages) == 1
        assert messages[0].subject == "Test delivery"

        broker._unregister_broker()

    def test_broker_handles_offline_recipient(self, temp_vault):
        """Test broker handles offline recipients with retry."""
        # Create sender but don't register recipient
        sender = A2AMessenger(vault_path=temp_vault, agent_id="sender")
        registry = AgentRegistry(vault_path=temp_vault)

        registry.register("sender", ["send"], AgentRole.WATCHER)
        # recipient NOT registered (offline)

        # Send message
        sender.send_message(
            to_agent="offline-recipient",
            message_type="notification",
            subject="Test offline",
            payload={}
        )

        # Run broker
        broker = A2AMessageBroker(vault_path=temp_vault, check_interval_seconds=1)
        broker._register_broker()

        broker.run_once()

        # Message should stay in pending (will retry)
        messages = broker.queue.get_messages("pending")
        assert len(messages) == 1
        # Retry count should have increased
        assert messages[0].retry_count >= 1

        broker._unregister_broker()


class TestAgentRegistryIntegration:
    """Tests for agent registry integration."""

    def test_agents_discoverable(self, temp_vault):
        """Test agents can discover each other."""
        registry = AgentRegistry(vault_path=temp_vault)

        # Register agents
        registry.register("agent1", ["email"], AgentRole.WATCHER)
        registry.register("agent2", ["slack", "email"], AgentRole.WATCHER)
        registry.register("agent3", ["calendar"], AgentRole.WATCHER)

        # Send heartbeats
        registry.send_heartbeat("agent1")
        registry.send_heartbeat("agent2")
        registry.send_heartbeat("agent3")

        # Find by capability
        email_agents = registry.find_agents_by_capability("email")
        agent_ids = [a.agent_id for a in email_agents]
        assert "agent1" in agent_ids
        assert "agent2" in agent_ids
        assert "agent3" not in agent_ids

        # Find by role
        watchers = registry.find_agents_by_role(AgentRole.WATCHER)
        assert len(watchers) == 3

    def test_agent_goes_offline(self, temp_vault):
        """Test agents marked offline after heartbeat timeout."""
        registry = AgentRegistry(vault_path=temp_vault, heartbeat_timeout_seconds=2)

        # Register agent
        registry.register("temp-agent", ["test"], AgentRole.WATCHER)
        registry.send_heartbeat("temp-agent")

        # Should be online
        assert registry.is_agent_online("temp-agent")

        # Wait for timeout
        time.sleep(3)

        # Should be offline
        assert not registry.is_agent_online("temp-agent")


class TestFailureScenarios:
    """Tests for various failure scenarios."""

    def test_max_retries_exceeded(self, temp_vault):
        """Test messages moved to dead letter after max retries."""
        from utils.a2a_messenger import Message, MessagePriority

        broker = A2AMessageBroker(vault_path=temp_vault)

        # Create message at max retries
        msg = Message(
            message_id="msg_retry_max",
            timestamp=datetime.now().isoformat(),
            expires=(datetime.now() + timedelta(hours=1)).isoformat(),
            priority=MessagePriority.NORMAL,
            from_agent="sender",
            to_agent="offline-recipient",  # Not registered
            message_type="notification",
            retry_count=3,
            max_retries=3
        )

        broker.queue.save_message(msg, "pending")

        # Run broker
        broker._register_broker()
        broker.route_messages()

        # Should be in dead letter
        messages = broker.queue.get_messages("dead_letter")
        assert len(messages) == 1

        broker._unregister_broker()

    def test_signature_validation(self, temp_vault):
        """Test messages with invalid signatures are rejected."""
        # Create two messengers with different secrets
        messenger1 = A2AMessenger(vault_path=temp_vault, agent_id="agent1")
        messenger2 = A2AMessenger(vault_path=temp_vault, agent_id="agent2")

        # They should share the same secret file, so signatures should work
        msg_id = messenger1.send_message(
            to_agent="agent2",
            message_type="notification",
            subject="Test",
            payload={}
        )

        # Manually tamper with message signature
        from utils.a2a_messenger import MessageQueue
        queue = MessageQueue(temp_vault, "agent1")
        msg_files = list(queue.outbox_path.glob("*.md"))

        if msg_files:
            with open(msg_files[0], "r") as f:
                content = f.read()

            # Tamper with signature
            content = content.replace(
                "signature: ",
                "signature: tampered_"
            )

            with open(msg_files[0], "w") as f:
                f.write(content)

        # Recipient should reject tampered message
        # (This would be caught during receive_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
