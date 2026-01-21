"""
Unit tests for Agent Registry module.

Tests the AgentInfo, AgentRegistry, and HeartbeatSender classes.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

from utils.agent_registry import (
    AgentInfo, AgentRegistry, HeartbeatSender,
    AgentRole, AgentStatus, discover_agents_by_capability,
    get_all_online_agents
)


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault directory."""
    vault_path = tmp_path / "AI_Employee_Vault"
    vault_path.mkdir()
    return str(vault_path)


@pytest.fixture
def sample_agent_info():
    """Create sample agent info for testing."""
    return AgentInfo(
        agent_id="gmail-watcher",
        status=AgentStatus.ONLINE,
        last_heartbeat=datetime.now().isoformat(),
        capabilities=["email_detection", "spam_classification"],
        message_queue="Signals/Inbox/gmail-watcher/",
        role=AgentRole.WATCHER,
        version="1.0.0"
    )


class TestAgentInfo:
    """Tests for AgentInfo class."""

    def test_agent_info_creation(self, sample_agent_info):
        """Test creating agent info."""
        assert sample_agent_info.agent_id == "gmail-watcher"
        assert sample_agent_info.status == AgentStatus.ONLINE
        assert "email_detection" in sample_agent_info.capabilities
        assert sample_agent_info.role == AgentRole.WATCHER

    def test_is_online_true(self, sample_agent_info):
        """Test online check for online agent."""
        assert sample_agent_info.is_online()

    def test_is_online_false(self):
        """Test online check for offline agent."""
        old_time = datetime.now() - timedelta(seconds=200)
        agent = AgentInfo(
            agent_id="test",
            status=AgentStatus.OFFLINE,
            last_heartbeat=old_time.isoformat(),
            capabilities=[]
        )
        assert not agent.is_online()

    def test_to_dict(self, sample_agent_info):
        """Test converting agent info to dictionary."""
        data = sample_agent_info.to_dict()

        assert data["agent_id"] == "gmail-watcher"
        assert data["status"] == "online"
        assert "email_detection" in data["capabilities"]
        assert data["role"] == "watcher"

    def test_from_dict(self):
        """Test creating agent info from dictionary."""
        data = {
            "agent_id": "auto-approver",
            "status": "online",
            "last_heartbeat": datetime.now().isoformat(),
            "capabilities": ["classification", "routing"],
            "message_queue": "Signals/Inbox/auto-approver/",
            "role": "processor",
            "version": "2.0.0"
        }

        agent = AgentInfo.from_dict(data)

        assert agent.agent_id == "auto-approver"
        assert agent.status == AgentStatus.ONLINE
        assert "classification" in agent.capabilities
        assert agent.role == AgentRole.PROCESSOR


class TestAgentRegistry:
    """Tests for AgentRegistry class."""

    @pytest.fixture
    def registry(self, temp_vault):
        """Create a registry instance."""
        return AgentRegistry(vault_path=temp_vault)

    def test_registry_initialization(self, registry, temp_vault):
        """Test registry creates necessary files."""
        registry_path = Path(temp_vault) / ".agent_registry.json"
        assert registry_path.exists()

        # Verify structure
        with open(registry_path) as f:
            data = json.load(f)

        assert "version" in data
        assert "agents" in data
        assert "last_updated" in data

    def test_register_agent(self, registry):
        """Test registering an agent."""
        registry.register(
            agent_id="test-watcher",
            capabilities=["watching"],
            role=AgentRole.WATCHER
        )

        agent = registry.get_agent("test-watcher")
        assert agent is not None
        assert agent.agent_id == "test-watcher"
        assert "watching" in agent.capabilities

    def test_register_with_all_params(self, registry):
        """Test registering with all parameters."""
        registry.register(
            agent_id="complex-agent",
            capabilities=["cap1", "cap2"],
            role=AgentRole.PROCESSOR,
            version="1.2.3",
            metadata={"location": "cloud"},
            message_queue="custom/path/"
        )

        agent = registry.get_agent("complex-agent")
        assert agent.version == "1.2.3"
        assert agent.metadata["location"] == "cloud"
        assert agent.message_queue == "custom/path/"

    def test_unregister_agent(self, registry):
        """Test unregistering an agent."""
        registry.register(
            agent_id="temp-agent",
            capabilities=["temp"],
            role=AgentRole.WATCHER
        )

        assert registry.get_agent("temp-agent") is not None

        registry.unregister("temp-agent")
        assert registry.get_agent("temp-agent") is None

    def test_send_heartbeat(self, registry):
        """Test sending heartbeat."""
        registry.register(
            agent_id="heartbeat-agent",
            capabilities=["test"],
            role=AgentRole.WATCHER
        )

        registry.send_heartbeat("heartbeat-agent")

        agent = registry.get_agent("heartbeat-agent")
        # Last heartbeat should be very recent
        last_beat = datetime.fromisoformat(agent.last_heartbeat.replace("Z", "+00:00"))
        assert (datetime.now(last_beat.tzinfo) - last_beat).total_seconds() < 5

    def test_send_heartbeat_with_status(self, registry):
        """Test sending heartbeat with custom status."""
        registry.register(
            agent_id="status-agent",
            capabilities=["test"],
            role=AgentRole.WATCHER
        )

        registry.send_heartbeat(
            "status-agent",
            status=AgentStatus.DEGRADED,
            metadata={"error": "high load"}
        )

        agent = registry.get_agent("status-agent")
        assert agent.status == AgentStatus.DEGRADED
        assert agent.metadata["error"] == "high load"

    def test_send_heartbeat_auto_registers(self, registry):
        """Test that heartbeat auto-registers unknown agents."""
        # Don't register, just send heartbeat
        registry.send_heartbeat("unknown-agent")

        agent = registry.get_agent("unknown-agent")
        assert agent is not None
        assert agent.agent_id == "unknown-agent"

    def test_update_status(self, registry):
        """Test updating agent status."""
        registry.register(
            agent_id="status-update-agent",
            capabilities=["test"],
            role=AgentRole.WATCHER
        )

        registry.update_status("status-update-agent", AgentStatus.MAINTENANCE)

        agent = registry.get_agent("status-update-agent")
        assert agent.status == AgentStatus.MAINTENANCE

    def test_get_all_agents(self, registry):
        """Test getting all agents."""
        registry.register("agent1", ["cap1"], AgentRole.WATCHER)
        registry.register("agent2", ["cap2"], AgentRole.PROCESSOR)
        registry.register("agent3", ["cap3"], AgentRole.MONITOR)

        agents = registry.get_all_agents()
        assert len(agents) == 3

        agent_ids = [a.agent_id for a in agents]
        assert "agent1" in agent_ids
        assert "agent2" in agent_ids
        assert "agent3" in agent_ids

    def test_is_agent_online(self, registry):
        """Test checking if agent is online."""
        registry.register(
            agent_id="online-agent",
            capabilities=["test"],
            role=AgentRole.WATCHER
        )

        assert registry.is_agent_online("online-agent")

        # Test with non-existent agent
        assert not registry.is_agent_online("nonexistent")

    def test_is_agent_offline_after_timeout(self, registry):
        """Test agent goes offline after heartbeat timeout."""
        registry.register(
            agent_id="timeout-agent",
            capabilities=["test"],
            role=AgentRole.WATCHER
        )

        # Manually set old heartbeat
        agent_data = registry._load_registry()
        old_time = (datetime.now() - timedelta(seconds=200)).isoformat()
        agent_data["agents"]["timeout-agent"]["last_heartbeat"] = old_time
        registry._save_registry(agent_data)

        assert not registry.is_agent_online("timeout-agent")

    def test_find_agents_by_capability(self, registry):
        """Test finding agents by capability."""
        registry.register("email-agent", ["email_detection"], AgentRole.WATCHER)
        registry.register("multi-agent", ["email_detection", "spam_filter"], AgentRole.PROCESSOR)
        registry.register("slack-agent", ["slack_detection"], AgentRole.WATCHER)

        agents = registry.find_agents_by_capability("email_detection")
        assert len(agents) == 2

        agent_ids = [a.agent_id for a in agents]
        assert "email-agent" in agent_ids
        assert "multi-agent" in agent_ids
        assert "slack-agent" not in agent_ids

    def test_find_agents_by_role(self, registry):
        """Test finding agents by role."""
        registry.register("watcher1", ["watch"], AgentRole.WATCHER)
        registry.register("watcher2", ["watch"], AgentRole.WATCHER)
        registry.register("processor1", ["process"], AgentRole.PROCESSOR)

        watchers = registry.find_agents_by_role(AgentRole.WATCHER)
        assert len(watchers) == 2

        processors = registry.find_agents_by_role(AgentRole.PROCESSOR)
        assert len(processors) == 1

    def test_get_online_count(self, registry):
        """Test getting online agent count."""
        registry.register("agent1", ["test"], AgentRole.WATCHER)
        registry.register("agent2", ["test"], AgentRole.PROCESSOR)
        registry.register("agent3", ["test"], AgentRole.MONITOR)

        assert registry.get_online_count() == 3

    def test_cleanup_stale_agents(self, registry):
        """Test cleanup of stale agents."""
        registry.register("fresh-agent", ["test"], AgentRole.WATCHER)

        # Create a stale agent
        registry.register("stale-agent", ["test"], AgentRole.WATCHER)
        agent_data = registry._load_registry()
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        agent_data["agents"]["stale-agent"]["last_heartbeat"] = old_time
        registry._save_registry(agent_data)

        # Cleanup
        removed = registry.cleanup_stale_agents(max_age_hours=24)

        assert removed == 1
        assert registry.get_agent("fresh-agent") is not None
        assert registry.get_agent("stale-agent") is None

    def test_get_status_summary(self, registry):
        """Test getting status summary."""
        registry.register("watcher1", ["email"], AgentRole.WATCHER)
        registry.register("watcher2", ["slack"], AgentRole.WATCHER)
        registry.register("processor1", ["approve"], AgentRole.PROCESSOR)

        summary = registry.get_status_summary()

        assert summary["total_agents"] == 3
        assert summary["online_agents"] == 3
        assert summary["offline_agents"] == 0
        assert summary["by_role"]["watcher"] == 2
        assert summary["by_role"]["processor"] == 1
        assert "email" in summary["capabilities"]
        assert "slack" in summary["capabilities"]

    def test_export_for_discovery(self, registry):
        """Test exporting registry for discovery."""
        registry.register(
            "discoverable-agent",
            ["discovery"],
            AgentRole.WATCHER,
            version="1.0"
        )

        export_json = registry.export_for_discovery()
        export = json.loads(export_json)

        assert export["version"] == "1.0"
        assert "timestamp" in export
        assert len(export["agents"]) == 1

        agent_export = export["agents"][0]
        assert agent_export["agent_id"] == "discoverable-agent"
        assert "discovery" in agent_export["capabilities"]
        # Should not include sensitive data like metadata


class TestHeartbeatSender:
    """Tests for HeartbeatSender class."""

    def test_heartbeat_sender_initialization(self, temp_vault):
        """Test heartbeat sender creation."""
        registry = AgentRegistry(vault_path=temp_vault)
        sender = HeartbeatSender(
            registry=registry,
            agent_id="test-agent",
            interval_seconds=1
        )

        assert sender.registry == registry
        assert sender.agent_id == "test-agent"
        assert sender.interval == 1

    def test_heartbeat_sender_start_stop(self, temp_vault):
        """Test starting and stopping heartbeat sender."""
        registry = AgentRegistry(vault_path=temp_vault)
        sender = HeartbeatSender(
            registry=registry,
            agent_id="test-agent",
            interval_seconds=1
        )

        sender.start()
        assert sender._running is True

        # Wait a bit for heartbeat
        time.sleep(2)

        sender.stop()
        assert sender._running is False

        # Verify heartbeat was sent
        agent = registry.get_agent("test-agent")
        assert agent is not None

    def test_heartbeat_sender_sends_periodic(self, temp_vault):
        """Test heartbeat sends at interval."""
        registry = AgentRegistry(vault_path=temp_vault)
        sender = HeartbeatSender(
            registry=registry,
            agent_id="periodic-agent",
            interval_seconds=1
        )

        sender.start()

        # Wait for multiple heartbeats
        time.sleep(3.5)

        sender.stop()

        # Check heartbeats were sent
        agent = registry.get_agent("periodic-agent")
        assert agent is not None


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_discover_agents_by_capability(self, temp_vault):
        """Test convenience function for discovering agents."""
        registry = AgentRegistry(vault_path=temp_vault)
        registry.register("email1", ["email_detection"], AgentRole.WATCHER)
        registry.register("email2", ["email_detection"], AgentRole.WATCHER)
        registry.register("slack1", ["slack_detection"], AgentRole.WATCHER)

        agent_ids = discover_agents_by_capability(temp_vault, "email_detection")

        assert len(agent_ids) == 2
        assert "email1" in agent_ids
        assert "email2" in agent_ids
        assert "slack1" not in agent_ids

    def test_get_all_online_agents(self, temp_vault):
        """Test convenience function for getting online agents."""
        registry = AgentRegistry(vault_path=temp_vault)
        registry.register("agent1", ["test"], AgentRole.WATCHER)
        registry.register("agent2", ["test"], AgentRole.WATCHER)

        agent_ids = get_all_online_agents(temp_vault)

        assert len(agent_ids) == 2
        assert "agent1" in agent_ids
        assert "agent2" in agent_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
