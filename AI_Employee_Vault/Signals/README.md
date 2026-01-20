# Signals - Agent-to-Agent (A2A) Messaging

This folder is reserved for future **Phase 2: Direct A2A Communication**.

## Current Status (Phase 1)

**NOT YET IMPLEMENTED** - Currently, agents communicate by writing files to the vault.

**Phase 1 Communication (Current):**
- Cloud creates files in `/Needs_Action/`, `/Pending_Approval/`, `/Updates/`
- Local reads files and processes them
- Communication is asynchronous via file system

## Future: Phase 2 A2A Messaging

**Planned Communication (Phase 2):**
- Direct agent-to-agent messages
- Real-time communication
- Reduced file overhead
- Faster coordination

## Planned Signal Types

### Request Signals
```yaml
type: request
from: local
to: cloud
action: generate_draft
target: EMAIL_123.md
context: Urgent client inquiry
```

### Response Signals
```yaml
type: response
from: cloud
to: local
action: draft_ready
target: EMAIL_123_DRAFT.md
status: success
```

### Notification Signals
```yaml
type: notification
from: cloud
to: local
event: new_email
data:
  id: EMAIL_456
  priority: high
  subject: Urgent: Server down
```

### Command Signals
```yaml
type: command
from: local
to: cloud
action: sync_now
priority: immediate
```

## Signal Processing

**Future Implementation:**

```python
class SignalProcessor:
    """Process A2A signals for Phase 2"""

    def send_signal(self, signal: dict):
        """Send signal to another agent"""
        signal_file = self.signals_folder / f"signal_{uuid.uuid4()}.json"
        signal_file.write_text(json.dumps(signal))

    def receive_signals(self) -> list:
        """Read pending signals"""
        signals = []
        for signal_file in self.signals_folder.glob("signal_*.json"):
            signal = json.loads(signal_file.read_text())
            signals.append(signal)
            signal_file.unlink()  # Remove after reading
        return signals
```

## When to Use Signals vs Files

### Use File-Based Communication (Phase 1)
- Creating action files
- Drafting replies/posts
- Approval workflows
- Audit logs
- Long-term storage

### Use A2A Signals (Phase 2)
- Real-time coordination
- Request-response patterns
- Immediate notifications
- Agent handoffs
- Status queries

## Migration Path

**Phase 1 → Phase 2 Migration:**

1. Add signal processing to existing agents
2. Implement signal router
3. Convert file-based flows to signals where beneficial
4. Keep vault as audit record
5. Gradual rollout, testing each flow

## Current Use

**For now, this folder remains empty** and is reserved for future Phase 2 implementation.

---

*Last Updated: 2026-01-20*
*System Version: v1.5.0 (Platinum Tier)*
*Phase 2 Status: PLANNED - NOT IMPLEMENTED*
