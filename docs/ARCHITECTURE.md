# AI Employee Architecture Documentation

**Updated:** 2026-01-12
**Version:** 1.0 Production Ready

---

## 🏗️ System Architecture

The AI Employee system implements a **three-tier architecture** following the Perception → Reasoning → Action pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Employee System                          │
│                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ PERCEPTION   │ -> │  REASONING   │ -> │   ACTION      │    │
│  │              │    │              │    │              │    │
│  │  Watchers    │    │ Claude Code  │    │  MCPs +      │    │
│  │  (Python)    │    │   + You      │    │  Posters     │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 Layer 1: Perception (Watchers)

### Purpose
Continuously monitor external services and create action files for important items.

### Architecture

```
External APIs                Watcher                    Vault
     │                         │                         │
     ├─ Gmail API ──────────> │ gmail_watcher.py ────> │ Needs_Action/
     │                         │                         │
     ├─ Calendar API ───────> │ calendar_watcher.py ─> │ Needs_Action/
     │                         │                         │
     ├─ Xero API ────────────> │ xero_watcher.py ────> │ Needs_Action/
     │                         │                         │
     ├─ Slack API ───────────> │ slack_watcher.py ───> │ Needs_Action/
     │                         │                         │
     ├─ WhatsApp ────────────> │ whatsapp_watcher.py ─> │ Needs_Action/
     │                         │                         │
     └─ Filesystem ──────────> │ filesystem_watcher.py > │ Needs_Action/
```

### Implementation Details

**Base Class:** `BaseWatcher` (`watchers/base_watcher.py`)

**All Watchers Inherit:**
- `check_for_updates()` - Scan external service
- `create_action_file()` - Create markdown file in vault
- `get_item_id()` - Get unique identifier
- `run()` - Main loop (runs continuously)

**PM2 Process Management:**
- All watchers run as separate PM2 processes
- Auto-restart on failure
- Configurable check intervals
- Resource limits (max 500MB per watcher)

**File Creation Pattern:**
```markdown
---
type: email|event|xero|slack|whatsapp
service: gmail|calendar|xero|slack|whatsapp
priority: high|medium|low
status: pending
created: 2026-01-12T10:30:00Z
---

# Title

**Content**

## Suggested Actions
- [ ] Action 1
- [ ] Action 2
```

### Active Watchers

| Watcher | Class | Interval | Status | API Used |
|---------|-------|----------|--------|----------|
| Gmail | `GmailWatcher` | 60s | ✅ Active | Gmail API |
| Calendar | `CalendarWatcher` | 60s | ✅ Active | Calendar API |
| Xero | `XeroWatcher` | 3600s | ⚠️ Needs pip | Xero API |
| Slack | `SlackWatcher` | 60s | ✅ Active | Slack API |
| Filesystem | `FilesystemWatcher` | Real-time | ✅ Active | inotify/OS |

---

## 🧠 Layer 2: Reasoning (Claude Code + You)

### Purpose
Analyze action files, consult rules, generate proposals, await human approval.

### Workflow

```
Needs_Action/                  Pending_Approval/
     │                              │
     ├─ EMAIL_001.md              │
     ├─ EVENT_001.md              │
     └─ XERO_001.md              │
           │                       ^
           │                       │
           v                       │
     ┌─────────────┐              │
     │  Claude Code │              │
     └─────────────┘              │
           │                       │
           v                       │
     ┌─────────────┐              │
     │ Analyze     │              │
     │ Prioritize  │              │
     │ Consult     │              │
     │ Handbook    │              │
     └─────────────┘              │
           │                       │
           v                       │
     ┌─────────────┐              │
     │ Create      │──────────────┘
     │ Proposals   │
     └─────────────┘
```

### Claude's Capabilities

**1. Read Vault**
```python
# Claude reads all markdown files
vault.read("Needs_Action/*.md")

# Parse YAML frontmatter
type = file.frontmatter['type']
priority = file.frontmatter['priority']
```

**2. Consult Rules**
```markdown
# Company_Handbook.md contains rules like:
- Email priority: urgent > invoice > deadline
- Response times: urgent (1hr), normal (24hr)
- Approval required for: payments, contracts, public posts
```

**3. Generate Proposals**
```markdown
# Example Proposal in Pending_Approval/

---
type: email_reply
priority: high
status: pending_approval
original_file: Needs_Action/EMAIL_001.md
---

# Payment Reminder Email

**To:** client@company.com
**Subject:** FOLLOW-UP: Invoice #1234

Dear [Client Name],

Our records show Invoice #1234 is 30 days overdue...
```

**4. Human Approval Loop**
```
You review → Edit if needed → Move to Approved/
                ↓
         Or reject → Delete or move to Rejected/
```

### Available Skills

Claude has access to modular skills via `.claude/skills/`:

- `email-manager` - Handle Gmail operations
- `calendar-manager` - Manage calendar events
- `xero-manager` - Accounting & invoices
- `slack-manager` - Slack communications
- `twitter-manager` - X.com posting
- `linkedin-manager` - LinkedIn posting
- `whatsapp-manager` - WhatsApp messaging
- `content-generator` - Generate content
- `weekly-briefing` - CEO summaries
- `daily-review` - Daily workflow review

---

## ⚡ Layer 3: Action (MCPs + Posters)

### Purpose
Execute approved actions using MCP servers (API-based) or browser automation (CDP-based).

### Architecture

```
Approved/                        External Services
     │                                │
     ├─ EMAIL_REPLY_001.md           ├─ Gmail API
     ├─ LINKEDIN_POST_001.md         ├─ LinkedIn (CDP)
     ├─ INSTAGRAM_POST_001.md        ├─ Instagram (CDP)
     └─ TWEET_001.md                 ├─ X.com (CDP)
           │                                │
           v
     ┌─────────────┐
     │  Monitors   │
     │  (Scripts)  │
     └─────────────┘
           │
           └────────────────────────────────┘
                    │
                    v
         ┌──────────────────┐
         │   Execution      │
         │                  │
         │  MCP Servers     │
         │  - Gmail         │
         │  - Calendar      │
         │  - Xero          │
         │  - Slack         │
         │                  │
         │  Browser CDP     │
         │  - LinkedIn      │
         │  - Instagram     │
         │  - X.com         │
         └──────────────────┘
                    │
                    v
         ┌──────────────────┐
         │    Done/         │
         │  with Summary    │
         └──────────────────┘
```

### MCP Servers (API-based)

**How They Work:**
```
Claude Code → MCP Client (stdio) → MCP Server → External API
     ↑                                              ↓
     └──────────────────── Response ──────────────────┘
```

**Server Implementations:**

| MCP | Technology | Token Location | Port |
|-----|------------|----------------|------|
| Email | Node.js + googleapis | `.gmail_mcp_token.json` | stdio |
| Calendar | Node.js + googleapis | `.calendar_mcp_token.json` | stdio |
| Xero | Node.js + xero-node | `.xero_mcp_token.json` | stdio |
| Slack | Node.js + slack-sdk | Environment var | stdio |

**MCP Tool Flow:**
```javascript
// Claude calls tool
{
  "name": "list_emails",
  "arguments": { "max_results": 10 }
}

// MCP server receives
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const result = await gmail.users.messages.list({...});
  return { content: [{ type: "text", text: result }] };
});

// Claude receives response
"Here are your recent emails:..."
```

### Browser Automation (CDP-based)

**Chrome DevTools Protocol Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    Chrome Browser                         │
│                   (Port 9222 - CDP)                      │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Session 1 (Automation Profile)                 │   │
│  │                                                   │   │
│  │  Tab 1: LinkedIn (logged in)                    │   │
│  │  Tab 2: Instagram (logged in)                   │   │
│  │  Tab 3: X.com (logged in)                       │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  CDP Endpoint: http://localhost:9222                     │
└─────────────────────────────────────────────────────────┘
                            ↑
                            │
         ┌──────────────────┴──────────────────┐
         │                                       │
    ┌────┴─────┐                          ┌────┴─────┐
    │ Playwright│                          │  PyCDP   │
    │  (Node.js)│                          │ (Python) │
    └───────────┘                          └──────────┘
         │                                       │
         └──────────────────┬──────────────────┘
                            │
                    ┌───────┴────────┐
                    │  Poster Script │
                    └────────────────┘
```

**Human-Like Automation:**

```python
# NOT instant (detectable as bot)
page.fill("textarea", "Post content")  # ❌ Bad

# Human-like (undetectable)
for char in "Post content":
    page.type(char)
    time.sleep(random.uniform(0.05, 0.18))  # ✅ Good
```

**Poster Implementations:**

| Poster | Technology | Profile | Status |
|--------|------------|---------|--------|
| LinkedIn | PyCDP | ChromeAutomationProfile | ✅ Active |
| Instagram | Playwright | ChromeAutomationProfile | ✅ Active |
| X.com | PyCDP | ChromeAutomationProfile | ✅ Active |

---

## 🗂️ Vault Structure

```
AI_Employee_Vault/
│
├── 📥 Inbox/                    # Manual drop zone
│   └── [User files]
│
├── ⚠️  Needs_Action/            # Watcher output
│   ├── EMAIL_20260112_143000.md
│   ├── EVENT_20260112_150000.md
│   ├── XERO_20260112_160000.md
│   └── SLACK_20260112_170000.md
│
├── 🤔 Pending_Approval/         # Claude proposals
│   ├── EMAIL_REPLY_001.md
│   └── CALENDAR_EVENT_001.md
│
├── ✅ Approved/                 # Ready to execute
│   ├── LINKEDIN_POST_001.md
│   └── INSTAGRAM_POST_001.md
│
├── ✅ Done/                     # Completed items
│   ├── EMAIL_REPLY_001.md
│   │   └── [Summary appended]
│   └── LINKEDIN_POST_001.md
│       └── [Screenshot + confirmation]
│
├── 📋 Plans/                    # Execution plans
│   └── DAILY_PLAN_2026-01-12.md
│
├── 📊 Briefings/                # CEO summaries
│   └── DAILY_BRIEFING_2026-01-12.md
│
├── 📝 Logs/                     # Audit trail
│   └── 2026-01-12.json
│       └── [{timestamp, action, result}]
│
├── 📖 Company_Handbook.md       # Rules for Claude
├── 🎯 Business_Goals.md         # Objectives
└── 📊 Dashboard.md              # System status
```

---

## 🔒 Security Architecture

### Local-First Design

```
┌─────────────────────────────────────────────────────────┐
│                  Your Machine                            │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │   Vault    │  │   Claude   │  │   Chrome   │       │
│  │ (Markdown) │  │   Code     │  │  (CDP)      │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│         │                 │                │             │
│         └─────────────────┴────────────────┘             │
│                      │                                   │
│                      v                                   │
│            ┌──────────────────────┐                      │
│            │                      │                      │
│            │   External APIs      │<──┐                  │
│            │  (Gmail, Slack, etc)  │   │                  │
│            └──────────────────────┘   │                  │
│                                          │                  │
└──────────────────────────────────────────┼──────────────────┘
                                           │
                                           │
                         ┌─────────────────┴─────────┐
                         │  Internet (Optional)    │
                         │  - For API calls only   │
                         │  - You control everything│
                         └──────────────────────────┘
```

**Key Security Features:**

1. **Data Ownership**
   - All data stored locally as markdown
   - No cloud dependencies
   - You control everything

2. **Human-in-the-Loop**
   - Nothing executes without approval
   - You review every action
   - Can reject or modify anything

3. **DRY_RUN Mode**
   - All posters default to preview mode
   - Must explicitly use `--live` flag
   - Screenshots saved for review

4. **Audit Trail**
   - All actions logged to `Logs/YYYY-MM-DD.json`
   - Timestamps, results, errors
   - Complete accountability

---

## 🚀 Deployment Architecture

### PM2 Process Management

```
pm2.config.js
    │
    ├──> Gmail Watcher (Fork)
    ├──> Calendar Watcher (Fork)
    ├──> Xero Watcher (Fork)
    ├──> Slack Watcher (Fork)
    └──> Filesystem Watcher (Fork)
```

**Process Configuration:**
```javascript
{
  name: "gmail-watcher",
  script: "watchers/gmail_watcher.py",
  args: "--vault AI_Employee_Vault --credentials path/to/credentials.json",
  interpreter: "python",
  exec_mode: "fork",
  autorestart: true,
  max_restarts: 10,
  max_memory_restart: "500M",
  env: {
    "PYTHONUNBUFFERED": "1"
  }
}
```

**Startup:**
```bash
pm2 start process-manager/pm2.config.js
pm2 save
pm2 startup  # Run on system boot
```

---

## 📊 Technology Stack

### Watchers (Python)
- **Gmail:** google-api-python-client, OAuth2
- **Calendar:** google-api-python-client, OAuth2
- **Xero:** xero (Python SDK)
- **Slack:** slack-sdk
- **WhatsApp:** playwright

### MCP Servers (Node.js/TypeScript)
- **Gmail:** @googleapis/gmail, google-auth-library
- **Calendar:** @googleapis/calendar, google-auth-library
- **Xero:** xero-node
- **Slack:** @slack/web-api
- **Framework:** @modelcontextprotocol/sdk

### Posters (Python + Browser)
- **LinkedIn:** pycdp + fast copy-paste (Ctrl+V) - 100-200x faster than typing
- **Instagram:** playwright + professional image generation (6 color themes, decorative borders)
- **X.com:** pycdp + fast copy-paste (Ctrl+V) - 100-200x faster than typing

### Process Management
- **PM2:** Node.js process manager
- **Python 3:** 3.10+
- **Node.js:** 18+

**Total Processes:** 16
- **Continuous:** 11 (Watchers + Approval Monitors)
- **Scheduled:** 5 (Cron jobs)

---

## 🎯 Design Principles

1. **Modularity** - Each watcher/MCP/poster is independent
2. **Extensibility** - Easy to add new services
3. **Local-First** - All data stays on your machine
4. **Human-Centric** - You're always in control
5. **Transparent** - Everything logged and visible
6. **Undetectable** - Browser automation looks human

---

## 📈 Performance Characteristics

| Metric | Value |
|--------|-------|
| Watcher Check Interval | 60 seconds (configurable) |
| Vault Read/Write | < 100ms (local file I/O) |
| MCP Response Time | 200-500ms (API dependent) |
| Browser Automation (LinkedIn/Twitter) | < 1 second (fast copy-paste) |
| Browser Automation (Instagram) | 1-3 seconds (includes image generation) |
| Memory per Watcher | < 500MB |
| Total Memory (all watchers) | < 2GB |
| CPU Usage (idle) | < 5% |
| CPU Usage (posting) | < 20% |

**Speed Improvements (2026-01-14):**
- LinkedIn/Twitter posting: **100-200x faster** (0.3s vs 30-60s before)
- Instagram image generation: **6 professional color themes** with decorative borders
- All platforms: **Fast copy-paste method** replaces character-by-character typing
- Ralph Wiggum: **3-6x faster** for Monday CEO Briefing (10-15 min vs 30-60 min manual)
- Vault structure: **Fixed nested vault bug** (removed `AI_Employee_Vault/AI_Employee_Vault/`)

**Documentation Improvements (v1.1.1):**
- Added process control guide for PM2 management
- Added Ralph user guide for autonomous task execution
- Added presentation materials for stakeholder communication
- Complete documentation suite now available

---

*Architecture documentation v1.1.1 - Last updated 2026-01-14*
