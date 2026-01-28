# Personal AI Employee Dashboard

**Last Updated:** 2026-01-20
**System Version:** v1.5.0 (Platinum Tier)
**System Status:** All Systems Operational - Platinum Tier Complete

---

## System Overview

**Platinum Tier Architecture:** Cloud + Local Hybrid
- **Cloud VM:** 143.244.143.143 (24/7 Detection + AI Triage + Draft Creation)
- **Local Machine:** Approvals + Final Execution
- **Total Processes:** 19 (8 Cloud + 11 Local)
- **Git Sync:** Every 5 minutes between Cloud and Local

### Core Architecture
```
Cloud (24/7) → Git Sync → Local (Executive)
  Detection                   Drafts                    Approvals
    +                         +                          +
  AI Triage                 Review                    Execution
```

---

## System Status

### Platinum Tier Complete ✅

| Component                 | Status                         | Location  |
| ------------------------- | ------------------------------ | --------- |
| **Cloud VM**              | 🟢 **Online** (24/7)            | Remote    |
| gmail-watcher (Cloud)     | 🟢 Online                      | Cloud     |
| calendar-watcher (Cloud)  | 🟢 Online                      | Cloud     |
| slack-watcher (Cloud)     | 🟢 Online                      | Cloud     |
| odoo-watcher (Cloud)      | 🟢 Online                      | Cloud     |
| auto-approver (Cloud)      | 🟢 **AI-Powered** (Claude 3)   | Cloud     |
| git-sync-push (Cloud)      | 🟢 Online                      | Cloud     |
| **Local Machine**          | 🟢 **Online** (when available)  | Local     |
| whatsapp-watcher (Local)   | 🟢 Online                      | Local     |
| filesystem-watcher (Local) | 🟢 Online                      | Local     |
| ai-employee-dashboard     | 🟢 Online (Port 3000)          | TBD   | TBD    | 0        |
| monday-ceo-briefing       | ⏸️ Scheduled (Mon 7AM)         | -     | -      | 0        |
| daily-review              | ⏸️ Scheduled (Weekdays 6AM)    | -     | -      | 0        |
| social-media-scheduler    | ⏸️ Scheduled (Mon/Wed/Fri 8AM) | -     | -      | 0        |
| audit-log-cleanup         | ⏸️ Scheduled (Sun 3AM)         | -     | -      | 0        |

---

## Active Integrations

### Communication Platforms
| Platform | Status | Capabilities |
|----------|--------|--------------|
| **Gmail** | ✅ Connected | Email monitoring, automatic processing |
| **Calendar** | ✅ Connected | Event monitoring, meeting prep files |
| **Slack** | ✅ Connected | Message monitoring, auto-replies |
| **WhatsApp** | ✅ Connected | Message monitoring, keyword alerts |

### Social Media Platforms
| Platform | Status | Capabilities |
|----------|--------|--------------|
| **LinkedIn** | ✅ Operational | Professional posting, fast copy-paste (100-200x faster) |
| **Twitter/X** | ✅ Operational | Tweet posting, fast copy-paste, 280 char limit |
| **Instagram** | ✅ Operational | Auto-generated images, 6 professional themes |
| **Facebook** | ✅ Operational | Direct content insertion, full formatting |

### Accounting & Finance
| Platform | Status | Capabilities |
|----------|--------|--------------|
| **Xero** | ✅ Connected | Transaction monitoring, invoice tracking, overdue alerts |
| **Odoo** | ✅ Connected (Local) | Invoicing, payments, accounting |
| **Tenant:** | AI EMPLOYEE (b154c8d6-0dbc-4891-9100-34af087c31f1) | |

---

## Today's Priority

### High Priority
- [ ] Review pending approvals in `/Pending_Approval/`
- [ ] Check urgent emails in `/Needs_Action/`
- [ ] Review Xero accounting alerts in `/Accounting/`

### Medium Priority
- [ ] Process inbox items
- [ ] Update business goals
- [ ] Prepare weekly briefing

### Social Media Queue
- [ ] Review pending posts in `/Pending_Approval/`
- [ ] Schedule upcoming content (Mon/Wed/Fri 8AM)

---

## Recent Activity

### Last 24 Hours
- **Xero Integration:** ✅ OAuth authentication completed, tenant connected
- **Monthly Accounting:** 📊 Created `Accounting/2026-01.md`
- **System Updates:** 🔄 All watchers restarted successfully
- **WhatsApp:** ✅ Intelligent spam warning thresholds implemented

### System Health
- ✅ All 19 processes configured
- ✅ 15 processes online (6 watchers + 6 monitors + 1 AI approver + 1 dashboard + 1 scheduler)
- ✅ 4 scheduled jobs ready
- ✅ 0 crashes (all systems stable)
- ✅ **NEW: AI-Powered Auto-Approval** using Claude 3 Haiku
- ✅ Platinum Tier Complete (AI + Human-in-the-Loop)

---

## Vault Structure

### Active Folders
| Folder | Purpose | Auto-Populated By |
|--------|---------|-------------------|
| `Inbox/` | Drop zone for new items | Manual |
| `Needs_Action/` | Items from watchers (pre-AI review) | All Watchers |
| `Pending_Approval/` | Awaiting human review (AI flagged) | AI Auto-Approver |
| `Approved/` | Ready for execution | AI Auto-Approver + Human |
| `Done/` | Completed items | Approval Monitors |
| `Rejected/` | Declined items (AI + Human) | AI Auto-Approver + Human |
| `Briefings/` | CEO summaries & reports | daily-briefing, weekly-briefing |
| `Plans/` | AI-generated plans | Claude Code |
| `Logs/` | Daily JSON logs (audit trail) | All Components |
| `Accounting/` | Monthly financial tracking | xero-watcher, odoo-watcher |
| `Templates/` | Reusable templates | Manual |

**AI Auto-Approver Workflow:**
```
Needs_Action/ → AI Analyzes → Approved/ (auto) → Executes
                           → Rejected/ (auto) → Blocked
                           → Pending_Approval/ (manual) → Human reviews
```

---

## Quick Actions

### Process Control
```bash
# Check all system status
pm2 status

# View logs
pm2 logs --lines 50

# Check AI auto-approver decisions
pm2 logs auto-approver --lines 50

# Restart all watchers
pm2 restart all

# Restart specific service
pm2 restart auto-approver
```

### Social Media Posting
1. Create post in `/Pending_Approval/` (e.g., `LINKEDIN_POST_YYYYMMDD_HHMMSS.md`)
2. Review content
3. Move to `/Approved/`
4. Automatic posting within seconds

### Xero Operations
- **Monthly Reports:** Auto-generated in `/Accounting/` (first of each month)
- **Overdue Alerts:** Created in `/Needs_Action/` when invoices are 7+ days overdue
- **Unusual Expenses:** Alerts for expenses over $500 threshold

---

## Quick Links

### Core Documentation
- **[[Company Handbook]]** - AI Employee rules of engagement
- **[[Business Goals]]** - Current objectives & targets
- **[[Dashboard]]** - This dashboard

### Action Folders
- **[[Needs Action]]** - Tasks requiring attention
- **[[Pending Approval]]** - Awaiting your review
- **[[Approved]]** - Ready for execution
- **[[Done]]** - Completed items

### Reports & Logs
- **[[Briefings]]** - CEO summaries & executive reports
- **[[Logs]]** - System activity logs (audit trail)
- **[[Accounting]]** - Monthly financial tracking

---

## Features

### ✅ Implemented
- **AI-Powered Auto-Approver** - Claude 3 Haiku makes intelligent approval decisions
- **Cross-Domain Coordination** - Personal vs Business domain classification and routing (NEW!)
- **Social Media Summary Generation** - All platforms generate post summaries (NEW!)
- **Ralph Wiggum Autonomous Task Execution** - Continuous loop for complex tasks
- **Monday Morning CEO Briefing** - Automated business performance audit
- **Social Media Posting** - LinkedIn, Twitter, Instagram, Facebook (all platforms)
- **Email Monitoring** - Gmail with automatic filtering and processing
- **Calendar Management** - Google Calendar with meeting preparation
- **Slack Integration** - Message monitoring and auto-replies
- **WhatsApp Monitoring** - Message scanning with intelligent spam filters
- **Xero Accounting** - Transaction monitoring, invoice tracking, overdue alerts
- **Odoo Accounting** - Local-first invoicing and payments
- **Filesystem Watcher** - Drop folder monitoring
- **Daily Review** - Weekdays at 6AM
- **Social Media Scheduler** - Mon/Wed/Fri at 8AM
- **Audit Log Cleanup** - Sundays at 3AM

### 🎯 Gold Tier Complete
All Gold Tier requirements fulfilled:
- ✅ Full cross-domain integration (Personal + Business)
- ✅ Facebook & Instagram posting with summaries
- ✅ Twitter/X posting with summaries
- ✅ Multiple MCP servers for different actions
- ✅ Weekly Business and Accounting Audit with CEO Briefing
- ✅ Error recovery and graceful degradation
- ✅ Comprehensive audit logging
- ✅ Ralph Wiggum loop for autonomous task completion

---

## Notes

This dashboard is automatically updated by your AI Employee. Edit manually to add personal notes or override system-generated content.

**System Version:** v1.4.0 (Gold Tier Complete)
**Last System Update:** 2026-01-20
**Gold Tier Documentation:** [docs/GOLD_TIER_COMPLETION.md](../docs/GOLD_TIER_COMPLETION.md)
**Next Daily Briefing:** Monday 7:00 AM

---

## Cross-Domain Insights

Generate unified insights across Personal and Business domains:
```bash
python scripts/cross_domain_insights.py --vault AI_Employee_Vault
```

### Domain Structure
- `/Needs_Action/Personal/` - Personal tasks (health, family, hobbies)
- `/Needs_Action/Business/` - Business tasks (clients, invoices, projects)
- `/Needs_Action/Shared/` - Shared items (urgent, scheduling, reminders)


---

## Cloud Updates

_Last update: 2026-01-21 18:48:30_

### System Health

- **Hostname:** hackathon0-1vcpu-1gb
- **Uptime:** 2 days, 22:51:47.739027
- **CPU:** 100.0%
- **Memory:** 85.1%
- **Disk:** 22.0%

### Cloud Processes

- ✅ **gmail-watcher**: online (CPU: 0.0%, Mem: 22.4MB)
- ✅ **calendar-watcher**: online (CPU: 0.0%, Mem: 23.3MB)
- ✅ **slack-watcher**: online (CPU: 0.0%, Mem: 25.4MB)
- ✅ **odoo-watcher**: online (CPU: 0.0%, Mem: 21.0MB)
- ❌ **git-sync-push**: stopped (CPU: 0.0%, Mem: 0.0MB)
- ✅ **cloud-health-monitor**: online (CPU: 0.1%, Mem: 15.8MB)
- ✅ **auto-approver**: online (CPU: 0.0%, Mem: 28.6MB)

### Alerts

- ⚠️ HIGH CPU: 100.0%
- ⚠️ HIGH MEMORY: 85.1%
- ⚠️ PROCESS STOPPED: git-sync-push
## Purpose

The **single-writer rule** states that only Local should update `Dashboard.md` directly. Cloud writes updates to this folder, and Local merges them.

## Why This Pattern?

**Problem:** If both Cloud and Local write to `Dashboard.md` simultaneously, you get git merge conflicts.

**Solution:** Cloud writes updates to `/Updates/`, Local merges them into `Dashboard.md`.

## Update Types

### Status Updates
```markdown
---
type: status_update
source: cloud
timestamp: 2026-01-20T12:00:00Z
---

## Cloud Status Summary

**Emails Processed:** 15
**Events Detected:** 3
**Drafts Created:** 8
**AI Decisions:** 12 (10 approved, 2 rejected)
```

### Alert Updates
```markdown
---
type: alert
source: cloud
timestamp: 2026-01-20T12:00:00Z
priority: high
---

## Alert: High Volume of Emails

Cloud detected 25+ emails in the last hour. Consider reviewing.
```

### Summary Updates
```markdown
---
type: summary
source: cloud
timestamp: 2026-01-20T12:00:00Z
period: 2026-01-20 11:00 - 12:00
---

## Hourly Summary

**New Items:** 12
**Processed:** 10
**Pending:** 2
**Errors:** 0
```

## Dashboard Merger Process

The `dashboard_merger.py` script runs every 2 minutes on Local:

1. Reads all files from `/Updates/`
2. Merges content into `Dashboard.md`
3. Deletes processed update files
4. Logs the merge operation

## Creating Update Files

### Cloud Agent

```python
from pathlib import Path
from datetime import datetime

updates_folder = Path("AI_Employee_Vault/Updates")

# Write update
update_file = updates_folder / f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
update_file.write_text(update_content)
```

### Local Agent (Automatic)

```bash
# Dashboard merger runs automatically via PM2 cron
# No manual action needed - it reads /Updates/ every 2 minutes
```

## File Naming Convention

- `update_YYYYMMDD_HHMMSS.md` - Timestamped updates
- `status_*.md` - Status updates
- `alert_*.md` - Alert notifications
- `summary_*.md` - Summary reports

## Cleanup

Processed update files are automatically deleted after merging. No manual cleanup needed.

---

*Last Updated: 2026-01-20*
*System Version: v1.5.0 (Platinum Tier)*
*Reference: scripts/dashboard_merger.py*


---

📡 **README.md**

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


---
