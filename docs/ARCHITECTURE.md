# System Architecture

**AI Employee v1.4.1**

---

## Overview

The AI Employee uses a **three-layer architecture**:

```
┌─────────────────────────────────────────────────────┐
│              PERCEPTION LAYER                     │
│                                                      │
│  Watchers run 24/7 monitoring external services:    │
│  • Gmail API                                         │
│  • Calendar API                                      │
│  • Slack Bot API                                     │
│  • Playwright (WhatsApp)                            │
│  • File system watchers                             │
│                                                      │
│  Creates action files in Needs_Action/               │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│             REASONING LAYER                      │
│                                                      │
│  AI Auto-Approver (Claude 3 Haiku):              │
│  • Scans Needs_Action/ every 2 minutes           │
│  • Analyzes each item                             │
│  • Makes decisions:                                 │
│    - approve (safe) → Approved/                 │
│    - reject (dangerous) → Rejected/             │
│    - manual (uncertain) → Pending_Approval/     │
│                                                      │
│  Human reviews items in Pending_Approval/         │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              ACTION LAYER                         │
│                                                      │
│  Approval Monitors watch Approved/ for files:      │
│  • Email → Gmail MCP server                       │
│  • Calendar → Calendar MCP server                  │
│  • Slack → Slack API                               │
│  • LinkedIn → LinkedIn MCP server                  │
│  • Twitter → Twitter MCP server                   │
│  • Facebook → Facebook MCP server                 │
│  │
│  MCP Servers use Playwright + Chrome CDP:         │
│  • Connects to localhost:9222                     │
│  • Automates browser actions                      │
│  • Posts content / executes actions                 │
│                                                      │
│  Results moved to Done/                            │
└─────────────────────────────────────────────────────┘
```

---

## Data Flow

### Email Processing Flow

```
1. Gmail Watcher detects new email
   ↓
2. Creates: Needs_Action/EMAIL_*.md
   ↓
3. AI Auto-Approver analyzes
   ↓
   → approve → Approved/ (safe, known sender)
   → manual → Pending_Approval/ (needs review)
   ↓
4. Human reviews Pending_Approval/
   ↓
5. Move to Approved/
   ↓
6. Email Approval Monitor detects
   ↓
7. Sends via Gmail MCP server
   ↓
8. Move to Done/
```

### Social Media Posting Flow

```
1. User/Claude creates post
   ↓
2. Creates: Pending_Approval/PLATFORM_POST_*.md
   ↓
3. AI Auto-Approver analyzes
   ↓
   → manual (social media always requires human review)
   ↓
4. Human reviews post
   ↓
5. Move to Approved/
   ↓
6. Platform Approval Monitor detects
   ↓
7. Ensures Chrome CDP running
   ↓
8. Calls platform MCP wrapper
   ↓
9. MCP server uses Playwright + Chrome CDP:
   - Navigate to platform
   - Paste content / Click buttons
   - Confirm post
   ↓
10. Move to Done/
```

### CEO Briefing Flow

```
1. Cron triggers (Mondays 7 AM) or manual invocation
   ↓
2. Weekly Briefing script runs
   ↓
3. Aggregates data from:
   - Logs/ (audit trail)
   - Plans/ (execution history)
   - Business_Goals.md (targets)
   - Done/ (completed tasks)
   ↓
4. Analyzes performance:
   - Revenue (weekly, MTD, vs target)
   - Bottlenecks
   - Completed tasks
   ↓
5. Generates briefing with:
   - Executive summary
   - Revenue analysis
   - Proactive suggestions
   - Action items
   ↓
6. Saves to: Briefings/YYYY-MM-DD_Monday_Briefing.md
```

---

## Technology Stack

### Backend (Python)

- **Watchers**: Python scripts with BaseWatcher class
- **Error Recovery**: @with_retry decorator with exponential backoff
- **Audit Logging**: Structured JSON logs
- **PM2**: Process manager for 24/7 operation

### Frontend (Browser Automation)

- **Playwright**: Browser automation
- **Chrome CDP**: Chrome DevTools Protocol on port 9222
- **MCP Servers**: Node.js servers for external actions

### AI

- **Claude 3 Haiku**: AI Auto-Approver decision making
- **Claude Code**: Skills invocation, reasoning, planning

### Data

- **Obsidian Vault**: Markdown-based storage
- **YAML Frontmatter**: Metadata in markdown files
- **JSON Logs**: Structured audit trail

---

## Integration Points

### External Services

| Service | Integration Method |
|---------|-------------------|
| Gmail | Gmail API + OAuth2 |
| Calendar | Calendar API + OAuth2 |
| Slack | Slack Bot API |
| WhatsApp | Playwright automation |
| LinkedIn | MCP + Playwright + CDP |
| Twitter/X | MCP + Playwright + CDP |
| Facebook | MCP + Playwright + CDP |
| Instagram | MCP + Playwright + CDP + image generation |
| Odoo | XML-RPC API |

### Internal Components

| Component | Integration |
|-----------|------------|
| Watchers | BaseWatcher class, error_recovery.py |
| Approval Monitors | Read from Approved/, write via MCP |
| AI Auto-Approver | Reads Needs_Action/, moves to folders |
| Ralph | Reads Plans/, creates approval requests |
| CEO Briefing | Aggregates from vault folders |

---

## File System Organization

```
AI_EMPLOYEE_APP/
├── .claude/
│   └── skills/              # Agent Skills (20+ skills)
│       ├── email-manager/
│       │   ├── SKILL.md
│       │   └── scripts/
│       ├── linkedin-manager/
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   └── invoke.py
│       └── ...
├── mcp-servers/           # MCP servers
│   ├── linkedin-mcp/
│   ├── twitter-mcp/
│   ├── facebook-mcp/
│   └── instagram-mcp/
├── watchers/              # Watcher modules
├── process-manager/       # PM2 configuration
│   ├── pm2.config.js
│   └── pm2.local.config.js
├── scripts/               # Utility scripts
│   ├── chrome_cdp_helper.py
│   └── start_chrome.bat
└── AI_Employee_Vault/    # Obsidian vault
    ├── Dashboard.md
    ├── Company_Handbook.md
    ├── Business_Goals.md
    ├── Needs_Action/
    ├── Pending_Approval/
    ├── Approved/
    ├── Rejected/
    ├── Done/
    ├── Plans/
    ├── Logs/
    └── Briefings/
```

---

## Security Model

### Human-in-the-Loop

1. **All sensitive actions require approval**
   - No command-line override
   - No environment variable bypass
   - File movement is required

2. **AI Auto-Approver is conservative**
   - Uncertain → manual review
   - External actions → manual review
   - Payments → manual review
   - Social media → manual review

3. **Audit trail**
   - All actions logged to `Logs/YYYY-MM-DD.json`
   - Timestamp, action, parameters, result
   - Retained for 90 days minimum

### Credential Management

- **Never synced to cloud**: `.env`, `*_token.json`
- **OAuth tokens**: Local storage, auto-refresh
- **WhatsApp sessions**: Never synced
- **Banking credentials**: Local storage only

---

## Performance

### System Capacity

| Component | Capacity |
|-----------|----------|
| Watchers | 6 running 24/7 |
| Approval Monitors | 7 running 24/7 |
| PM2 Processes | 16-17 total |
| Skills Available | 20+ |
| Social Platforms | 4 (LinkedIn, Twitter, Facebook, Instagram) |

### Speed Optimizations

| Task | Manual Time | AI Time | Speedup |
|------|-------------|----------|--------|
| LinkedIn post (1000 chars) | 30-60s | 0.3s | **100-200x** |
| Twitter post | 5-10s | 0.3s | **16-33x** |
| CEO Briefing | 30-60 min | 10-15 min | **3-6x** |
| Daily Review | 15-30 min | 2-5 min | **3-6x** |

### Error Recovery

- **@with_retry decorator**: 3 retries with exponential backoff
- **Graceful degradation**: Watchers continue if one service down
- **Automatic restart**: PM2 auto-restarts crashed processes
- **Fallback**: Simple plans if generators unavailable

---

## Scalability

### Horizontal Scaling

- Add more watchers for additional services
- Add more approval monitors for parallel processing
- Add more MCP servers for more platforms

### Vertical Scaling

- Increase PM2 `max_memory_restart` limits
- Upgrade VM resources
- Optimize database queries

---

## Monitoring

### Health Checks

- **PM2 status**: `pm2 status`
- **Dashboard**: http://localhost:3000
- **Logs**: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **PM2 logs**: `pm2 logs`

### Metrics Tracked

- Email triage rate
- Approval decisions (auto/manual/reject)
- Social media posting success rate
- Error rates by component
- Process uptime
- Resource usage (CPU, memory)

---

## Summary

The AI Employee architecture is designed for:

1. **Reliability** - 24/7 operation with error recovery
2. **Security** - Human-in-the-loop for sensitive actions
3. **Transparency** - Complete audit trail
4. **Performance** - Optimized for speed and efficiency
5. **Scalability** - Modular, can add more services/skills
6. **Maintainability** - Well-documented, clean code

The three-layer architecture (Perception → Reasoning → Action) provides clear separation of concerns and makes the system easy to understand and extend.
