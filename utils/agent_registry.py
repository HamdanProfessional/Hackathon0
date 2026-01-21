"""
Agent Registry for A2A Messaging System

This module provides agent discovery, heartbeat monitoring, and capability
matching for the AI Employee system. All agents register themselves and
send periodic heartbeats to indicate they are online and healthy.

The registry is stored as a JSON file in the vault for persistence and
can be shared between cloud and local instances via Git sync.

Architecture:
    - Registry stored as .agent_registry.json in vault
    - Agents register on startup
    - Heartbeats sent every 60 seconds
    - Agents marked offline after 3 missed heartbeats (180 seconds)
    - Capability matching for discovering agents by functionality
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles for access control."""
    WATCHER = "watcher"          # Monitors external services
    PROCESSOR = "processor"      # Processes data (e.g., auto-approver)
    MONITOR = "monitor"          # Monitors folders for actions
    ADMIN = "admin"              # Administrative functions


class AgentStatus(Enum):
    """Agent status in the registry."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"        # Running but with issues
    MAINTENANCE = "maintenance"  # Under maintenance


@dataclass
class AgentInfo:
    """
    Information about a registered agent.

    Attributes:
        agent_id: Unique agent identifier (e.g., "gmail-watcher")
        status: Current agent status
        last_heartbeat: ISO timestamp of last heartbeat
        capabilities: List of capabilities (e.g., ["email_detection"])
        message_queue: Path to message queue (e.g., "Signals/Inbox/gmail-watcher/")
        role: Agent role for access control
        version: Agent version (optional)
        metadata: Additional agent-specific data
        pid: Process ID (if applicable)
        host: Hostname where agent is running
        started_at: When the agent was started
    """
    agent_id: str
    status: AgentStatus
    last_heartbeat: str
    capabilities: List[str] = field(default_factory=list)
    message_queue: str = ""
    role: AgentRole = AgentRole.WATCHER
    version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    pid: Optional[int] = None
    host: str = "localhost"
    started_at: Optional[str] = None

    def is_online(self, heartbeat_timeout_seconds: int = 180) -> bool:
        """Check if agent is considered online based on heartbeat."""
        try:
            last_beat = datetime.fromisoformat(self.last_heartbeat.replace("Z", "+00:00"))
            cutoff = datetime.now(last_beat.tzinfo) - timedelta(seconds=heartbeat_timeout_seconds)
            return last_beat > cutoff and self.status != AgentStatus.OFFLINE
        except (ValueError, AttributeError):
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat,
            "capabilities": self.capabilities,
            "message_queue": self.message_queue,
            "role": self.role.value,
            "version": self.version,
            "metadata": self.metadata,
            "pid": self.pid,
            "host": self.host,
            "started_at": self.started_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInfo":
        """Create AgentInfo from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            status=AgentStatus(data.get("status", "offline")),
            last_heartbeat=data["last_heartbeat"],
            capabilities=data.get("capabilities", []),
            message_queue=data.get("message_queue", ""),
            role=AgentRole(data.get("role", "watcher")),
            version=data.get("version"),
            metadata=data.get("metadata", {}),
            pid=data.get("pid"),
            host=data.get("host", "localhost"),
            started_at=data.get("started_at"),
        )


class AgentRegistry:
    """
    Registry for tracking all agents in the system.

    Provides agent discovery, heartbeat monitoring, and capability matching.
    Registry is persisted to JSON file in the vault.

    Usage:
        # Agent registers itself
        registry = AgentRegistry(vault_path="AI_Employee_Vault")
        registry.register(
            agent_id="gmail-watcher",
            capabilities=["email_detection", "spam_classification"],
            role=AgentRole.WATCHER
        )

        # Send heartbeat
        registry.send_heartbeat("gmail-watcher")

        # Discover agents
        agents = registry.find_agents_by_capability("email_detection")

        # Check if agent is online
        if registry.is_agent_online("gmail-watcher"):
            print("Agent is online")
    """

    def __init__(
        self,
        vault_path: str,
        heartbeat_interval_seconds: int = 60,
        heartbeat_timeout_seconds: int = 180
    ):
        """
        Initialize Agent Registry.

        Args:
            vault_path: Path to the AI_Employee_Vault
            heartbeat_interval_seconds: How often agents should send heartbeats
            heartbeat_timeout_seconds: How long before agent is considered offline
        """
        self.vault_path = Path(vault_path)
        self.registry_file = self.vault_path / ".agent_registry.json"
        self.heartbeat_interval = heartbeat_interval_seconds
        self.heartbeat_timeout = heartbeat_timeout_seconds
        self._lock = threading.Lock()

        # Ensure registry file exists
        self._ensure_registry()

        logger.info(f"Agent Registry initialized at {self.registry_file}")

    def _ensure_registry(self) -> None:
        """Ensure registry file exists with valid structure."""
        if not self.registry_file.exists():
            self._save_registry({
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "agents": {}
            })
            logger.info(f"Created new registry at {self.registry_file}")

    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from file."""
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid registry file: {e}")
            return {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "agents": {}
            }
        except FileNotFoundError:
            self._ensure_registry()
            return self._load_registry()

    def _save_registry(self, data: Dict[str, Any]) -> None:
        """Save registry to file."""
        data["last_updated"] = datetime.now().isoformat()

        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register(
        self,
        agent_id: str,
        capabilities: List[str],
        role: AgentRole = AgentRole.WATCHER,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        message_queue: Optional[str] = None
    ) -> None:
        """
        Register an agent in the registry.

        Should be called when an agent starts up.

        Args:
            agent_id: Unique agent identifier
            capabilities: List of agent capabilities
            role: Agent role for access control
            version: Optional agent version
            metadata: Optional additional metadata
            message_queue: Optional path to message queue
        """
        with self._lock:
            registry = self._load_registry()

            # Determine message queue path
            if message_queue is None:
                message_queue = f"Signals/Inbox/{agent_id}/"

            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent_id,
                status=AgentStatus.ONLINE,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=capabilities,
                message_queue=message_queue,
                role=role,
                version=version,
                metadata=metadata or {},
                started_at=datetime.now().isoformat()
            )

            registry["agents"][agent_id] = agent_info.to_dict()
            self._save_registry(registry)

            logger.info(f"Registered agent: {agent_id} with capabilities: {capabilities}")

    def unregister(self, agent_id: str) -> None:
        """
        Unregister an agent from the registry.

        Should be called when an agent shuts down gracefully.

        Args:
            agent_id: Agent ID to unregister
        """
        with self._lock:
            registry = self._load_registry()

            if agent_id in registry["agents"]:
                del registry["agents"][agent_id]
                self._save_registry(registry)
                logger.info(f"Unregistered agent: {agent_id}")

    def send_heartbeat(
        self,
        agent_id: str,
        status: AgentStatus = AgentStatus.ONLINE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Send heartbeat for an agent.

        Should be called periodically (every 60 seconds recommended).

        Args:
            agent_id: Agent ID sending heartbeat
            status: Current agent status
            metadata: Optional metadata update
        """
        with self._lock:
            registry = self._load_registry()

            if agent_id not in registry["agents"]:
                # Agent not registered, auto-register
                logger.warning(f"Heartbeat from unregistered agent: {agent_id}, auto-registering")
                self.register(agent_id, capabilities=[], role=AgentRole.WATCHER)
                registry = self._load_registry()

            # Update heartbeat
            agent_data = registry["agents"][agent_id]
            agent_data["last_heartbeat"] = datetime.now().isoformat()
            agent_data["status"] = status.value

            if metadata:
                agent_data["metadata"].update(metadata)

            self._save_registry(registry)

    def update_status(
        self,
        agent_id: str,
        status: AgentStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update agent status.

        Args:
            agent_id: Agent ID to update
            status: New status
            metadata: Optional metadata update
        """
        with self._lock:
            registry = self._load_registry()

            if agent_id in registry["agents"]:
                agent_data = registry["agents"][agent_id]
                agent_data["status"] = status.value

                if metadata:
                    agent_data["metadata"].update(metadata)

                self._save_registry(registry)
                logger.info(f"Updated agent {agent_id} status to {status.value}")

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """
        Get information about a specific agent.

        Args:
            agent_id: Agent ID to look up

        Returns:
            AgentInfo if found, None otherwise
        """
        registry = self._load_registry()

        if agent_id in registry["agents"]:
            return AgentInfo.from_dict(registry["agents"][agent_id])

        return None

    def get_all_agents(self, include_offline: bool = False) -> List[AgentInfo]:
        """
        Get all registered agents.

        Args:
            include_offline: Whether to include offline agents

        Returns:
            List of AgentInfo objects
        """
        registry = self._load_registry()
        agents = []

        for agent_data in registry["agents"].values():
            agent = AgentInfo.from_dict(agent_data)

            if include_offline or agent.is_online(self.heartbeat_timeout):
                agents.append(agent)

        return agents

    def is_agent_online(self, agent_id: str) -> bool:
        """
        Check if an agent is currently online.

        Args:
            agent_id: Agent ID to check

        Returns:
            True if agent is online, False otherwise
        """
        agent = self.get_agent(agent_id)
        return agent is not None and agent.is_online(self.heartbeat_timeout)

    def find_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """
        Find agents that have a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of agents with the capability
        """
        agents = self.get_all_agents(include_offline=False)
        return [a for a in agents if capability in a.capabilities]

    def find_agents_by_role(self, role: AgentRole) -> List[AgentInfo]:
        """
        Find agents with a specific role.

        Args:
            role: Role to search for

        Returns:
            List of agents with the role
        """
        agents = self.get_all_agents(include_offline=False)
        return [a for a in agents if a.role == role]

    def get_online_count(self) -> int:
        """Get count of currently online agents."""
        return len(self.get_all_agents(include_offline=False))

    def cleanup_stale_agents(self, max_age_hours: int = 24) -> int:
        """
        Remove agents that have been offline for too long.

        Args:
            max_age_hours: Remove agents offline longer than this

        Returns:
            Number of agents removed
        """
        with self._lock:
            registry = self._load_registry()
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            removed = 0

            agents_to_remove = []
            for agent_id, agent_data in registry["agents"].items():
                try:
                    last_beat = datetime.fromisoformat(agent_data["last_heartbeat"].replace("Z", "+00:00"))
                    if last_beat < cutoff:
                        agents_to_remove.append(agent_id)
                except (ValueError, KeyError):
                    # Invalid data, mark for removal
                    agents_to_remove.append(agent_id)

            for agent_id in agents_to_remove:
                del registry["agents"][agent_id]
                removed += 1
                logger.info(f"Removed stale agent: {agent_id}")

            if removed > 0:
                self._save_registry(registry)

            return removed

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of registry status.

        Returns:
            Dict with registry statistics
        """
        all_agents = self.get_all_agents(include_offline=True)
        online_agents = [a for a in all_agents if a.is_online(self.heartbeat_timeout)]

        # Count by role
        role_counts = {}
        for agent in all_agents:
            role = agent.role.value
            role_counts[role] = role_counts.get(role, 0) + 1

        # Collect all capabilities
        all_capabilities = set()
        for agent in all_agents:
            all_capabilities.update(agent.capabilities)

        return {
            "total_agents": len(all_agents),
            "online_agents": len(online_agents),
            "offline_agents": len(all_agents) - len(online_agents),
            "by_role": role_counts,
            "capabilities": sorted(list(all_capabilities)),
            "last_updated": self._load_registry()["last_updated"],
        }

    def export_for_discovery(self) -> str:
        """
        Export registry for agent discovery.

        Returns:
            JSON string of agent information (excluding sensitive data)
        """
        agents = self.get_all_agents(include_offline=False)

        export_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "capabilities": a.capabilities,
                    "role": a.role.value,
                    "message_queue": a.message_queue,
                    "status": a.status.value,
                }
                for a in agents
            ]
        }

        return json.dumps(export_data, indent=2)


class HeartbeatSender:
    """
    Helper class to automatically send heartbeats at regular intervals.

    Usage:
        heartbeat = HeartbeatSender(
            registry=registry,
            agent_id="gmail-watcher"
        )
        heartbeat.start()  # Runs in background thread

        # When shutting down
        heartbeat.stop()
    """

    def __init__(
        self,
        registry: AgentRegistry,
        agent_id: str,
        interval_seconds: int = 60
    ):
        """
        Initialize heartbeat sender.

        Args:
            registry: AgentRegistry instance
            agent_id: This agent's ID
            interval_seconds: Heartbeat interval
        """
        self.registry = registry
        self.agent_id = agent_id
        self.interval = interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _heartbeat_loop(self) -> None:
        """Background thread that sends heartbeats."""
        while self._running:
            try:
                self.registry.send_heartbeat(self.agent_id)
            except Exception as e:
                logger.error(f"Heartbeat error for {self.agent_id}: {e}")

            # Wait for next interval or until stopped
            for _ in range(self.interval):
                if not self._running:
                    break
                time.sleep(1)

    def start(self) -> None:
        """Start sending heartbeats in background."""
        if self._running:
            logger.warning(f"Heartbeat sender already running for {self.agent_id}")
            return

        self._running = True
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()
        logger.info(f"Started heartbeat sender for {self.agent_id}")

    def stop(self) -> None:
        """Stop sending heartbeats."""
        if not self._running:
            return

        self._running = False

        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

        logger.info(f"Stopped heartbeat sender for {self.agent_id}")


def discover_agents_by_capability(
    vault_path: str,
    capability: str
) -> List[str]:
    """
    Convenience function to discover agents with a capability.

    Args:
        vault_path: Path to the vault
        capability: Capability to search for

    Returns:
        List of agent IDs with the capability
    """
    registry = AgentRegistry(vault_path)
    agents = registry.find_agents_by_capability(capability)
    return [a.agent_id for a in agents]


def get_all_online_agents(vault_path: str) -> List[str]:
    """
    Convenience function to get all online agent IDs.

    Args:
        vault_path: Path to the vault

    Returns:
        List of online agent IDs
    """
    registry = AgentRegistry(vault_path)
    agents = registry.get_all_agents(include_offline=False)
    return [a.agent_id for a in agents]
