# A2A (Agent-to-Agent) Messaging System

## Overview

The A2A (Agent-to-Agent) messaging system enables direct communication between agents in the AI Employee system while maintaining the local-first architecture. Messages are stored as markdown files in the vault's `Signals/` folder, providing built-in audit trails via Git.

## Architecture

### Message Flow

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Sender Agent  │─────▶│ Message Broker  │─────▶│ Receiver Agent  │
│                 │      │   (Routes)      │      │   (Processes)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        │                         │
        ▼                        ▼                         ▼
   Signals/Outbox/         Signals/Pending/        Signals/Inbox/
```

### Message Protocol

Each message is a markdown file with YAML frontmatter:

```markdown
---
type: a2a_message
message_id: msg_20260122_143052_a1b2c3d4
timestamp: 2026-01-22T14:30:52Z
expires: 2026-01-22T15:30:52Z
priority: high
from_agent: gmail-watcher
to_agent: auto-approver
message_type: request
correlation_id: email_12345_processed
status: pending
retry_count: 0
max_retries: 3
---

# Subject: Email Processing Complete

## Payload
```json
{
  "email_id": "12345",
  "subject": "Invoice from Acme Corp"
}
```
```

### Message Types

| Type | Description |
|------|-------------|
| `request` | Asking for action/response (expects reply) |
| `response` | Reply to a request |
| `notification` | One-way informational message |
| `broadcast` | Send to all online agents |
| `command` | Direct instruction (elevated privileges) |

### Folder Structure

```
AI_Employee_Vault/
├── Signals/
│   ├── Inbox/                    # Per-agent incoming messages
│   │   ├── gmail-watcher/
│   │   ├── auto-approver/
│   │   └── email-approval-monitor/
│   ├── Outbox/                   # Outgoing messages (all agents)
│   ├── Pending/                  # Awaiting delivery by broker
│   ├── Processing/               # Currently being processed
│   ├── Completed/                # Successfully delivered
│   ├── Failed/                   # Delivery failed (will retry)
│   └── Dead_Letter/              # Max retries exceeded
└── .agent_registry.json          # Agent discovery
```

## Usage

### Sending Messages

```python
from utils.a2a_messenger import A2AMessenger

# Initialize messenger for your agent
messenger = A2AMessenger(
    vault_path="AI_Employee_Vault",
    agent_id="gmail-watcher"
)

# Send a message
msg_id = messenger.send_message(
    to_agent="auto-approver",
    message_type="request",
    subject="New email detected",
    payload={
        "email_id": "12345",
        "subject": "Invoice from Acme Corp",
        "sender": "billing@acmecorp.com"
    },
    priority="high",
    ttl_minutes=60
)

print(f"Sent message: {msg_id}")
# Output: Sent message: msg_20260122_143052_a1b2c3d4
```

### Receiving Messages

```python
# Get pending messages
messages = messenger.receive_messages()

for message in messages:
    print(f"From: {message.from_agent}")
    print(f"Subject: {message.subject}")
    print(f"Payload: {message.payload}")

    # Process the message...

    # Acknowledge when done
    messenger.acknowledge_message(
        message_id=message.message_id,
        result="success"
    )
```

### Request/Response Pattern

```python
# Sender: Send request and wait for response
from utils.a2a_messenger import send_request_and_wait

response = send_request_and_wait(
    messenger=messenger,
    to_agent="auto-approver",
    subject="Classify this email",
    payload={"subject": "URGENT: Payment Due"},
    timeout_seconds=30
)

if response:
    print(f"Classification: {response['category']}")
```

### Broadcast Messages

```python
from utils.a2a_messenger import create_broadcast_message

# Send to all online agents
msg_id = create_broadcast_message(
    messenger=messenger,
    subject="System Maintenance in 1 Hour",
    payload={
        "maintenance_type": "database_upgrade",
        "estimated_duration_minutes": 30
    },
    priority="high"
)
```

## Agent Integration

### Watcher Integration

All watchers inheriting from `BaseWatcher` automatically get A2A capabilities:

```python
from watchers.gmail_watcher import GmailWatcher

watcher = GmailWatcher(vault_path="AI_Employee_Vault")

# Send notification when email detected
watcher._send_a2a_message(
    to_agent="auto-approver",
    message_type="notification",
    subject="Email detected",
    payload={
        "email_id": email_id,
        "subject": subject
    }
)

# Check for incoming messages
messages = watcher._receive_a2a_messages()
```

### Custom Agent Implementation

```python
from utils.a2a_messenger import A2AMessenger
from utils.agent_registry import AgentRegistry, AgentRole, HeartbeatSender

class MyCustomAgent:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.agent_id = "my-custom-agent"

        # Initialize A2A components
        self.messenger = A2AMessenger(vault_path, self.agent_id)
        self.registry = AgentRegistry(vault_path)

        # Register this agent
        self.registry.register(
            agent_id=self.agent_id,
            capabilities=["my_capability", "data_processing"],
            role=AgentRole.PROCESSOR
        )

        # Start heartbeat
        self.heartbeat = HeartbeatSender(
            registry=self.registry,
            agent_id=self.agent_id,
            interval_seconds=60
        )
        self.heartbeat.start()

    def process_messages(self):
        """Process incoming messages."""
        messages = self.messenger.receive_messages()

        for msg in messages:
            # Handle message
            result = self.handle_message(msg)

            # Acknowledge
            self.messenger.acknowledge_message(
                msg.message_id,
                result="success" if result else "failure",
                response_payload={"result": result}
            )

    def shutdown(self):
        """Cleanup on shutdown."""
        self.heartbeat.stop()
        self.registry.unregister(self.agent_id)
```

## Message Broker

The A2A Message Broker routes messages between agents. It runs as a PM2 process:

```bash
# Start broker
pm2 start process-manager/pm2.config.js --only a2a-message-broker

# Check broker status
pm2 status a2a-message-broker

# View broker logs
pm2 logs a2a-message-broker

# Get broker status summary
python scripts/a2a_message_broker.py --vault AI_Employee_Vault --status
```

### Broker Operations

The broker continuously:

1. **Processes Outbox**: Moves messages from `Outbox/` to `Pending/`
2. **Routes Messages**: Delivers to recipient `Inbox/`
3. **Handles Retries**: Exponential backoff for failed deliveries
4. **Checks Expiration**: Moves expired messages to `Failed/`
5. **Cleans Up**: Removes old completed/dead-letter messages

### Broker Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BROKER_CHECK_INTERVAL` | 5 | Seconds between broker cycles |
| `PYTHONPATH` | Required | Project root path |

## Agent Registry

The agent registry tracks all online agents and their capabilities:

```python
from utils.agent_registry import AgentRegistry

registry = AgentRegistry("AI_Employee_Vault")

# Get all online agents
agents = registry.get_all_agents(include_offline=False)
for agent in agents:
    print(f"{agent.agent_id}: {agent.capabilities}")

# Find agents by capability
email_agents = registry.find_agents_by_capability("email_detection")

# Check if agent is online
if registry.is_agent_online("gmail-watcher"):
    print("Gmail Watcher is online")

# Get registry summary
summary = registry.get_status_summary()
print(f"Online agents: {summary['online_agents']}/{summary['total_agents']}")
```

## Security

### Message Signing

All messages are signed with HMAC-SHA256:

```python
# Messages are automatically signed when sent
msg_id = messenger.send_message(...)

# Signature verification is automatic on receive
messages = messenger.receive_messages()  # Only returns valid signatures
```

### Secret Management

The A2A secret is stored in `AI_Employee_Vault/.a2a_secret` (Git-ignored):

```bash
# Secret auto-generated on first use
# To rotate: delete the file and restart agents

# For production: use different secrets for cloud vs local
```

### Access Control

Agents have roles for access control:

| Role | Description |
|------|-------------|
| `watcher` | Monitors external services |
| `processor` | Processes data (auto-approver) |
| `monitor` | Monitors folders for actions |
| `admin` | Administrative functions |

## Testing

### Unit Tests

```bash
# Run all A2A tests
pytest tests/test_a2a_*.py -v

# Run specific test file
pytest tests/test_a2a_messenger.py -v

# Run with coverage
pytest tests/test_a2a_*.py --cov=utils/a2a_messenger --cov=utils/agent_registry
```

### Manual Testing

```python
# Test sending a message
python -c "
from utils.a2a_messenger import A2AMessenger
messenger = A2AMessenger('AI_Employee_Vault', 'test-sender')
msg_id = messenger.send_message(
    to_agent='test-recipient',
    message_type='notification',
    subject='Test Message',
    payload={'test': 'data'}
)
print(f'Sent: {msg_id}')
"

# Test broker
python scripts/a2a_message_broker.py --vault AI_Employee_Vault --once
```

### Integration Test

```python
# End-to-end test: Gmail Watcher -> Auto-Approver
from watchers.gmail_watcher import GmailWatcher

# Start watcher
watcher = GmailWatcher(vault_path="AI_Employee_Vault")

# Simulate email detection
watcher._send_a2a_message(
    to_agent="auto-approver",
    message_type="request",
    subject="Classify email",
    payload={"subject": "Invoice #1234"}
)

# Auto-approver receives and processes
# (via its message processing loop)
```

## Troubleshooting

### Messages Not Delivered

1. **Check broker status**:
   ```bash
   pm2 status a2a-message-broker
   pm2 logs a2a-message-broker --lines 50
   ```

2. **Check agent registry**:
   ```bash
   cat AI_Employee_Vault/.agent_registry.json
   ```

3. **Check message queues**:
   ```bash
   ls AI_Employee_Vault/Signals/Pending/
   ls AI_Employee_Vault/Signals/Inbox/<agent_id>/
   ```

### Agent Not Receiving Messages

1. **Verify agent is registered**:
   ```python
   from utils.agent_registry import AgentRegistry
   registry = AgentRegistry("AI_Employee_Vault")
   print(registry.is_agent_online("your-agent-id"))
   ```

2. **Check heartbeat is running**:
   ```bash
   # Look for heartbeat updates in registry
   grep "last_heartbeat" AI_Employee_Vault/.agent_registry.json
   ```

3. **Verify agent inbox exists**:
   ```bash
   ls AI_Employee_Vault/Signals/Inbox/your-agent-id/
   ```

### Signature Verification Failures

1. **Check secret is shared**:
   ```bash
   # All agents must use the same .a2a_secret
   cat AI_Employee_Vault/.a2a_secret
   ```

2. **Regenerate secret** (if corrupted):
   ```bash
   rm AI_Employee_Vault/.a2a_secret
   pm2 restart all
   ```

## Performance Considerations

### Message Throughput

- **Expected rate**: 100-500 messages/day per agent
- **Broker capacity**: ~1000 messages/minute
- **Latency**: < 5 seconds (target: < 1 second)

### Optimization Tips

1. **Batch messages**: Send multiple items in one payload
2. **Use appropriate priority**: Reserve "urgent" for critical messages
3. **Set reasonable TTL**: Default 60 minutes is usually sufficient
4. **Clean up old messages**: Run cleanup periodically

## Migration from File-Based

### Phase 1: Parallel Operation (Week 1-2)

A2A runs alongside existing file-based flows:

```python
# Old way (still works)
action_file = self.create_action_file(item)

# New way (A2A)
self._send_a2a_message(
    to_agent="auto-approver",
    message_type="notification",
    subject="Item detected",
    payload=item_data
)
```

### Phase 2: Gradual Migration (Week 3-4)

Migrate high-frequency flows:

```python
# Email processing now uses A2A
if self.enable_a2a:
    self._send_a2a_message(...)
else:
    # Fallback to file-based
    self.create_action_file(...)
```

### Phase 3: Full A2A (Week 5-6)

All communication via A2A, file-based for audit only:

```python
# All agents have A2A enabled
self._send_a2a_message(...)  # Primary method

# Keep file creation for audit trail
if self.create_audit_files:
    self.create_action_file(...)
```

## API Reference

### A2AMessenger

```python
class A2AMessenger:
    def __init__(self, vault_path: str, agent_id: str, secret_path: Optional[str] = None)
    def send_message(self, to_agent, message_type, subject, payload, priority="normal", ...) -> str
    def receive_messages(self, status=None, include_expired=False) -> List[Message]
    def acknowledge_message(self, message_id, result="success", ...) -> None
    def get_message(self, message_id) -> Optional[Message]
    def get_status(self) -> Dict[str, Any]
    def cleanup_old_messages(self, days=7) -> int
```

### AgentRegistry

```python
class AgentRegistry:
    def __init__(self, vault_path: str, heartbeat_interval_seconds=60, ...)
    def register(self, agent_id, capabilities, role=AgentRole.WATCHER, ...) -> None
    def unregister(self, agent_id: str) -> None
    def send_heartbeat(self, agent_id, status=AgentStatus.ONLINE, ...) -> None
    def get_agent(self, agent_id) -> Optional[AgentInfo]
    def get_all_agents(self, include_offline=False) -> List[AgentInfo]
    def is_agent_online(self, agent_id) -> bool
    def find_agents_by_capability(self, capability) -> List[AgentInfo]
    def find_agents_by_role(self, role) -> List[AgentInfo]
    def get_status_summary(self) -> Dict[str, Any]
```

### Message

```python
@dataclass
class Message:
    message_id: str
    timestamp: str
    expires: str
    priority: MessagePriority
    from_agent: str
    to_agent: str
    message_type: MessageType
    correlation_id: Optional[str]
    status: MessageStatus
    retry_count: int
    max_retries: int
    subject: str
    payload: Dict[str, Any]
    signature: Optional[str]
    reply_to: Optional[str]

    def to_markdown(self) -> str
    @classmethod
    def from_markdown(cls, markdown: str) -> "Message"
    def is_expired(self) -> bool
    def should_retry(self) -> bool
```

## See Also

- `CLAUDE.md` - Main project documentation
- `docs/ARCHITECTURE.md` - System architecture
- `utils/a2a_messenger.py` - Core messaging implementation
- `utils/agent_registry.py` - Agent registry implementation
- `scripts/a2a_message_broker.py` - Message broker implementation
