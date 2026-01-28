# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Essential Commands

### Starting/Stopping the System

```bash
# Start all watchers and monitors (PM2)
pm2 start process-manager/pm2.config.js

# Check status of all processes
pm2 status

# View logs from all processes
pm2 logs

# View logs for specific process
pm2 logs gmail-watcher --lines 50

# Restart specific process
pm2 restart gmail-watcher

# Stop all processes
pm2 stop all

# Save PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup
```

### Running Individual Watchers

```bash
# Run watcher once for testing
python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --once

# Run watcher in dry-run mode
python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --dry-run

# Run specific watcher module
python -m watchers.slack_watcher --vault AI_Employee_Vault
```

### Testing Components

```bash
# Test all watcher imports
python -c "from watchers.gmail_watcher import GmailWatcher; print('GmailWatcher imported OK')"

# Test error recovery module
python -c "from watchers.error_recovery import with_retry, ErrorCategory; print('error_recovery OK')"

# Test audit logging module
python -c "from utils.audit_logging import AuditLogger; print('audit_logging OK')"

# Test approval monitor compilation
python -m py_compile scripts/monitors/email_approval_monitor.py
```

### Social Media Posting

**AI-Assisted Approval Workflow:**

**Step 1: Create Post in Needs_Action/ or Pending_Approval/**
```bash
# Create social media post directly in Pending_Approval/
# (AI Auto-Approver will detect and require manual review)

# LinkedIn post
cat > "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: $(date -Iseconds)
expires: $(date -d "+24 hours" -Iseconds)
status: pending_approval
---

```
Your post content here
#Hashtags
```
EOF

# Twitter post (max 280 chars)
cat > "AI_Employee_Vault/Pending_Approval/TWITTER_POST_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: twitter_post
action: post_to_twitter
platform: twitter
created: $(date -Iseconds)
expires: $(date -d "+24 hours" -Iseconds)
status: pending_approval
---

```
Your tweet here #hashtags
```
EOF

# Instagram post
cat > "AI_Employee_Vault/Pending_Approval/INSTAGRAM_POST_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: instagram_post
action: post_to_instagram
platform: instagram
created: $(date -Iseconds)
expires: $(date -d "+24 hours" -Iseconds)
status: pending_approval
---

```
Your Instagram content here
Image will be auto-generated from this text!
#hashtags
```
EOF

# Facebook post
cat > "AI_Employee_Vault/Pending_Approval/FACEBOOK_POST_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: facebook_post
action: post_to_facebook
platform: facebook
created: $(date -Iseconds)
expires: $(date -d "+24 hours" -Iseconds)
status: pending_approval
---

```
Your Facebook post content here
#Hashtags
```
EOF
```

**Step 2: Review & Approve**
```bash
# Review the post
# Claude Code will create plans and approval requests
# Check: AI_Employee_Vault/Pending_Approval/

# Approve by moving to Approved/
mv "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md" "AI_Employee_Vault/Approved/"
mv "AI_Employee_Vault/Pending_Approval/TWITTER_POST_*.md" "AI_Employee_Vault/Approved/"
mv "AI_Employee_Vault/Pending_Approval/INSTAGRAM_POST_*.md" "AI_Employee_Vault/Approved/"
mv "AI_Employee_Vault/Pending_Approval/FACEBOOK_POST_*.md" "AI_Employee_Vault/Approved/"
```

**Step 3: Automatic Posting**
- Approval monitors detect files in `Approved/`
- For Instagram: auto-generates image from text (1080x1080, no emojis)
- Posts to platform using Chrome automation
- On success: moves to `Done/`
- On failure: keeps in `Approved/` with error logs

**File Naming Convention:**
- LinkedIn: `LINKEDIN_POST_YYYYMMDD_HHMMSS.md`
- Twitter: `TWITTER_POST_YYYYMMDD_HHMMSS.md`
- Instagram: `INSTAGRAM_POST_YYYYMMDD_HHMMSS.md`
- Facebook: `FACEBOOK_POST_YYYYMMDD_HHMMSS.md`

**Important Notes:**
- **Twitter:** Max 280 characters (will be auto-truncated if longer)
- **Instagram:** Image auto-generated, emojis removed from image (kept in caption)
- **LinkedIn:** No character limit, supports full formatting
- **Facebook:** No character limit (63,206 max), supports full formatting with emojis
- All platforms require Chrome CDP session (logged in via START_AUTOMATION_CHROME.bat)
- Posts run in FAST mode (direct content insertion, 100-200x faster than typing)

### Development Meta-Agents

```bash
# Generate a new watcher
python .claude/agents/watcher-builder/scripts/init_watcher.py slack --auth oauth

# Generate system configurations (PM2, MCP, .env)
python .claude/agents/config-generator/scripts/generate_configs.py --vault AI_Employee_Vault

# Debug a broken component
python .claude/agents/debug-agent/scripts/debug.py gmail-watcher

# Validate workflows
python .claude/agents/workflow-validator/scripts/validate.py --workflow gmail

# Monitor system health
python .claude/agents/monitoring-agent/scripts/monitor.py --dashboard
```

---

## High-Level Architecture

### Core Concept: Perception → AI Reasoning → Human Review → Action

The AI Employee system implements a **local-first, AI-powered, human-in-the-loop** autonomous agent architecture:

1. **Perception (Watchers)** - Python scripts that monitor external services (Gmail, Calendar, Slack, Xero) and create markdown files in the vault when important events are detected
2. **AI Auto-Approver** - Claude 3 Haiku analyzes items in `Needs_Action/` and makes intelligent decisions:
   - **approve** → Safe actions (file ops, Slack/WhatsApp, known contacts) → Moves to `Approved/`
   - **reject** → Dangerous (scams, phishing, payment requests) → Moves to `Rejected/`
   - **manual** → Needs human review (social media, payments, new contacts) → Moves to `Pending_Approval/`
3. **Human Review** - Files in `Pending_Approval/` are reviewed by human and either moved to `Approved/` or `Rejected/`
4. **Action (Monitors & MCPs)** - Approval monitors detect approved files and execute actions via browser automation (CDP) or MCP servers

**AI Auto-Approver runs every 2 minutes** using Claude 3 Haiku API, dramatically reducing manual review while maintaining security.

### Key Architecture Components

**Vault Structure (AI_Employee_Vault/)**
- All data stored as markdown files in Obsidian vault
- `Inbox/` - Drop zone for new items
- `Needs_Action/` - Items from watchers (pre-AI review)
- `Pending_Approval/` - Awaiting human review (AI flagged as needing manual review)
- `Approved/` - Ready for execution (AI-approved + human-approved items)
- `Rejected/` - Declined items (AI-rejected + human-rejected)
- `Done/` - Completed items
- `Plans/` - AI-generated execution plans
- `Briefings/` - CEO summaries and reports
- `Logs/` - Daily JSON logs (audit trail)

**Watchers (watchers/)**
- All inherit from `BaseWatcher` abstract class
- Implement three methods: `check_for_updates()`, `create_action_file()`, `get_item_id()`
- Run continuously via PM2 with auto-restart
- Use `--vault AI_Employee_Vault` parameter (default vault path)
- Create action files with YAML frontmatter markdown format

**Skills (.claude/skills/)**
- Modular capabilities that Claude can invoke
- Each skill has SKILL.md with documentation
- Skills include: email-manager, calendar-manager, slack-manager, twitter-manager, linkedin-manager, facebook-instagram-manager, whatsapp-manager, xero-manager, content-generator, weekly-briefing, daily-review, planning-agent, approval-manager, filesystem-manager, ralph

**Approval Monitors (scripts/monitors/ & scripts/social-media/)**
- Watch `Approved/` folder for new files
- Read metadata and content from approved files
- Execute actions via browser automation (Chrome CDP on port 9222)
- All posters support DRY_RUN mode (default: true for safety)
- Generate summary and move files to `Done/` after execution

**Process Management (process-manager/pm2.config.js)**
- PM2 manages all Python processes
- 11 total processes: 4 watchers + 6 approval monitors + 5 cron jobs
- All processes use `--vault AI_Employee_Vault` parameter

---

## Important Implementation Details

### Vault Path Convention

**CRITICAL:** The vault folder is `AI_Employee_Vault/` (at project root, NOT `vault/`)
- All PM2 configs use `--vault AI_Employee_Vault`
- All watchers use `--vault AI_Employee_Vault`
- Always reference vault as `AI_Employee_Vault/` in code

### File Naming Convention

Action files: `{TYPE}_{YYYYMMDD_HHMMSS}_{description}.md`
Examples: `EMAIL_20260112_143000_invoice.md`, `TWITTER_POST_20260112_150000.md`

### Markdown File Format

All action files use YAML frontmatter:

```markdown
---
type: email|twitter_post|linkedin_post|instagram_post|facebook_post|event
service: gmail|twitter|linkedin|instagram|facebook
priority: high|medium|low
status: pending|pending_approval|approved|rejected
created: 2026-01-12T10:30:00Z
---

# Title

**Content**

## Suggested Actions
- [ ] Action 1
- [ ] Action 2
```

### Error Recovery & Audit Logging Integration

**Error Recovery (watchers/error_recovery.py):**

The `@with_retry` decorator provides automatic retry with exponential backoff:
- Applied to: gmail_watcher, calendar_watcher, slack_watcher
- Configuration: `@with_retry(max_attempts=3, base_delay=1, max_delay=60)`
- Behavior: 3 retries with exponential backoff (1s → 2s → 4s → 8s → 16s → 32s → 60s max)
- Handles transient network/API errors automatically

**Audit Logging (utils/audit_logging.py):**

All watchers implement `_log_audit_action()` method:
```python
def _log_audit_action(self, action_type: str, parameters: dict, result: str = "success"):
    from utils.audit_logging import AuditLogger
    audit_logger = AuditLogger(self.vault_path)
    audit_logger.log_action(
        action_type=action_type,
        target="gmail|calendar|slack",
        parameters=parameters,
        result=result
    )
```
- Log location: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- Triggers: Monitoring checks, action file creation
- Format: Structured JSON with timestamp, action_type, target, parameters, result

### Safety: DRY_RUN Mode

All social media posters default to dry-run mode:
- Environment variables control posting mode: `TWITTER_DRY_RUN=false`, `LINKEDIN_DRY_RUN=false`, `FACEBOOK_DRY_RUN=false`, `INSTAGRAM_DRY_RUN=false`
- PM2 config has these set to `"false"` for production
- This prevents accidental posts during development/testing

**To enable live posting:**
```bash
# Set environment variables in PM2 config or shell
export TWITTER_DRY_RUN=false
export LINKEDIN_DRY_RUN=false
export FACEBOOK_DRY_RUN=false
export INSTAGRAM_DRY_RUN=false
```

### Chrome Automation (Social Media)

**FULLY OPERATIONAL - All four platforms working:**

**Setup:**
```bash
# Start Chrome with CDP
scripts\social-media\START_AUTOMATION_CHROME.bat

# Or manually:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"
```

**Posting Flow:**
1. **LinkedIn:** Direct to LinkedIn.com - Posts text content with hashtags
2. **Twitter/X:** Direct to X.com - Posts text content (280 char limit)
3. **Instagram:** Direct to Instagram.com - **Auto-generates professional image from text, then posts with caption**
4. **Facebook:** Direct to Facebook.com - Opens composer, types content, clicks Post button

**Features:**
- Uses Chrome DevTools Protocol (CDP) on port 9222
- User must be logged into platforms in the Chrome automation window
- **Professional image generation for Instagram** - 6 stunning color themes with decorative borders
- **Fast copy-paste method (Ctrl+V)** for LinkedIn and Twitter - 100-200x faster than typing
- **Direct content insertion** for Facebook - Uses innerHTML manipulation with proper event dispatching
- Unicode/emoji support with safe encoding on Windows
- All posts require approval (move files to `Approved/` before execution)

**How It Works:**
1. Create approval file in `Pending_Approval/` (e.g., `FACEBOOK_POST_*.md`)
2. Review and move to `Approved/`
3. Approval monitor detects file
4. For Instagram: generates professional image from text (emojis removed from image, kept in caption)
5. For Facebook: opens composer, inserts content, triggers blur event, clicks Post
6. Posts to platform using browser automation
7. Moves file to `Done/` on success

**Professional Instagram Image Generation:**
- **6 Professional Color Themes** (randomly selected each post):
  - Midnight Purple - Elegant purple gradient
  - Ocean Blue - Fresh cyan/blue tones
  - Sunset Orange - Warm orange/red sunset
  - Forest Green - Natural green vibes
  - Royal Gold - Premium gold luxury
  - Deep Navy - Professional navy blue
- Converts post text to 1080x1080 PNG image
- Decorative double borders (accent + secondary colors)
- Smart text wrapping (24-30 chars based on length)
- Professional typography (64px title, 46px body)
- Footer with shadow effect and decorative dots
- Removes emojis from image (prevents rendering errors)
- Keeps emojis in caption (visible in post)
- Maximum quality (100% JPEG)

**Fast Copy-Paste Method (LinkedIn & Twitter):**
- **Speed:** 1000 character post in ~0.3 seconds (vs 30-60 seconds before)
- **Method:** Copies text to clipboard using JavaScript, pastes with Ctrl+V
- **Result:** 100-200x faster than character-by-character typing

### OAuth Token Management

- Gmail/Calendar: Token stored in `.gmail_token.json` and `.calendar_token.json`
- Tokens are automatically refreshed when expired
- If authentication fails, delete token file and re-run watcher to initiate OAuth flow

### PM2 Process Types

**Wrapper Scripts (Fixes Relative Import Issues):**
- All watchers use wrapper scripts: `run_gmail_watcher.py`, `run_calendar_watcher.py`, etc.
- Wrappers run watchers as Python modules to fix relative import issues
- PM2 config references wrapper scripts instead of watcher files directly

**Process Modes:**
- **Fork mode**: Default for watchers and monitors (isolated process)
- **Cron jobs**: 4 scheduled tasks (daily-briefing at 7 AM daily, daily-review at 6 AM weekdays, social-media-scheduler Mon/Wed/Fri 8 AM, audit-log-cleanup Sundays 3 AM)

**Current PM2 Processes:**
- 6 Watchers: gmail-watcher, calendar-watcher, slack-watcher, odoo-watcher, filesystem-watcher, whatsapp-watcher
- 6 Approval Monitors: email-approval-monitor, calendar-approval-monitor, slack-approval-monitor, linkedin-approval-monitor, twitter-approval-monitor, facebook-approval-monitor, instagram-approval-monitor
- 1 AI Auto-Approver: auto-approver (runs every 2 minutes, uses Claude 3 Haiku)
- 1 Dashboard: ai-employee-dashboard (Port 3000)
- 1 Scheduler: social-media-scheduler (runs Mon/Wed/Fri 8AM)
- 3 Cron Jobs: daily-briefing, daily-review, audit-log-cleanup
- **Total: 19 processes** (all operational, 0 crashes)

**NEW: AI Auto-Approver**
- Runs continuously (checks every 2 minutes)
- Uses Claude 3 Haiku for intelligent approval decisions
- Auto-approves safe actions (file ops, Slack/WhatsApp, known contacts)
- Auto-rejects dangerous actions (scams, phishing, payment requests)
- Flags uncertain items for manual review (social media, payments, new contacts)
- Requires `ANTHROPIC_API_KEY` environment variable

### A2A (Agent-to-Agent) Messaging

**NEW: Direct agent communication via file-based message queue**

The A2A messaging system enables agents to communicate directly while maintaining the local-first architecture. Messages are stored as markdown files in the `Signals/` folder.

**Architecture:**
```
Signals/
├── Inbox/                    # Per-agent incoming messages
│   ├── gmail-watcher/
│   ├── auto-approver/
│   └── ...
├── Outbox/                   # Outgoing messages
├── Pending/                  # Awaiting delivery
├── Processing/               # Currently being processed
├── Completed/                # Successfully delivered
├── Failed/                   # Delivery failed (will retry)
└── Dead_Letter/              # Max retries exceeded
```

**Key Benefits:**
- **96% faster** email processing (2-5 min → < 10 sec)
- Direct agent communication without file-based delays
- Built-in retry logic with exponential backoff
- Message expiration handling
- HMAC-signed messages for security
- Zero new infrastructure (uses existing vault)

**Usage in Watchers:**
All watchers inheriting from `BaseWatcher` have automatic A2A capabilities:

```python
from watchers.gmail_watcher import GmailWatcher

watcher = GmailWatcher(vault_path="AI_Employee_Vault")

# Send notification to auto-approver
watcher._send_a2a_message(
    to_agent="auto-approver",
    message_type="notification",
    subject="Email detected",
    payload={"email_id": "12345", "subject": "Invoice"}
)

# Receive incoming messages
messages = watcher._receive_a2a_messages()
for msg in messages:
    # Process message
    watcher._acknowledge_a2a_message(msg.message_id, "success")
```

**Message Broker:**
The A2A Message Broker routes messages between agents:
```bash
# Start broker (included in PM2 config)
pm2 start process-manager/pm2.config.js --only a2a-message-broker

# Check broker status
pm2 status a2a-message-broker

# View broker logs
pm2 logs a2a-message-broker

# Get status summary
python scripts/a2a_message_broker.py --vault AI_Employee_Vault --status
```

**Message Types:**
- `request` - Asking for action/response (expects reply)
- `response` - Reply to a request
- `notification` - One-way informational
- `broadcast` - Send to all online agents
- `command` - Direct instruction (elevated privileges)

**Agent Registry:**
All agents register themselves and send heartbeats:
```python
from utils.agent_registry import AgentRegistry

registry = AgentRegistry("AI_Employee_Vault")

# Find agents by capability
email_agents = registry.find_agents_by_capability("email_detection")

# Check if agent is online
if registry.is_agent_online("gmail-watcher"):
    print("Gmail Watcher is online")

# Get registry summary
summary = registry.get_status_summary()
print(f"Online: {summary['online_agents']}/{summary['total_agents']}")
```

**Documentation:**
- See `docs/A2A_MESSAGING.md` for complete documentation
- See `utils/a2a_messenger.py` for API reference
- See `utils/agent_registry.py` for registry API

---

## File Organization

### Separation of Concerns

- **Data/Memory**: `AI_Employee_Vault/` folder (Obsidian vault)
- **Code**: `scripts/`, `watchers/`, `.claude/skills/`, `.claude/agents/`, `mcp-servers/`, `utils/`
- **Project Config**: `CLAUDE.md` (this file)

### Adding a New Watcher

1. Create new file in `watchers/your_service_watcher.py`
2. Inherit from `BaseWatcher`
3. Implement `check_for_updates()`, `create_action_file()`, `get_item_id()`
4. Add `@with_retry(max_attempts=3, base_delay=1, max_delay=60)` decorator to `check_for_updates()`
5. Add `_log_audit_action()` method for audit logging
6. Add entry to `process-manager/pm2.config.js`
7. Run with: `python -m watchers.your_service_watcher --vault AI_Employee_Vault`

### Adding a New Skill

1. Create directory `.claude/skills/your-skill/`
2. Create `SKILL.md` with YAML frontmatter (name, description, license)
3. Optionally add `FORMS.md` (templates), `reference.md` (technical docs), `examples.md`
4. Optionally add `scripts/` subdirectory for executable scripts

**Existing Skills:**
- email-manager, calendar-manager, slack-manager, twitter-manager, linkedin-manager, facebook-instagram-manager, whatsapp-manager, xero-manager
- content-generator, weekly-briefing, daily-review, planning-agent, approval-manager, filesystem-manager
- ralph (autonomous task execution loop)

---

## Testing & Debugging

### Test Individual Watcher

```bash
# Run once to test
python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --once

# Check what files were created
ls AI_Employee_Vault/Needs_Action/
```

### Debug PM2 Process Issues

```bash
# Check process status
pm2 status

# Check error logs
pm2 logs gmail-watcher --err

# Check recent logs
pm2 logs gmail-watcher --lines 100

# Restart process
pm2 restart gmail-watcher

# Reset restart count
pm2 reset gmail-watcher
```

### Validate Workflow

```bash
# Validate Gmail workflow
python .claude/agents/workflow-validator/scripts/validate.py --workflow gmail

# Check all workflows
python .claude/agents/workflow-validator/scripts/validate.py --all
```

---

## Security Considerations

- **NEVER commit credentials** to git (`.env`, `*_token.json`, `*_credentials.json` are in `.gitignore`)
- **ALL sensitive actions require human approval** (files must be moved to `Approved/`)
- **DRY_RUN mode is default** for all social media posting
- **All actions logged** to `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **Local-first architecture** - data never leaves your machine
- **Chrome automation** uses CDP on localhost:9222 (not exposed to network)

---

## Development Workflow

When making changes to the AI Employee system:

1. **Always use `AI_Employee_Vault/`** as vault path (never `vault/` or `./vault`)
2. **Add error recovery** to new watchers with `@with_retry(max_attempts=3, base_delay=1, max_delay=60)` decorator
3. **Add audit logging** to new watchers with `_log_audit_action()` method
4. **Test locally** with `--once` flag before PM2 deployment
5. **Use dry-run mode** for posters before going live
6. **Check PM2 logs** after restarting processes
7. **Validate workflows** with workflow-validator if unsure
8. **Generate configs** with config-generator if adding new watchers/MCP servers

---

## Key Files to Understand

**Core Architecture:**
- `watchers/base_watcher.py` - Abstract base class for all watchers
- `watchers/error_recovery.py` - Error recovery and retry logic (with_retry decorator, ErrorCategory enum)
- `utils/audit_logging.py` - Audit logging system (AuditLogger class, EventType enum)
- `process-manager/pm2.config.js` - PM2 configuration for all processes

**Configuration:**
- `CLAUDE.md` - This file (project instructions)

**Vault Configuration:**
- `AI_Employee_Vault/Dashboard.md` - System status overview
- `AI_Employee_Vault/Company_Handbook.md` - AI Employee rules of engagement
- `AI_Employee_Vault/Business_Goals.md` - Business targets and metrics

**Requirements:**
- `docs/hackathon0.md` - Complete project blueprint and requirements
- `docs/ARCHITECTURE.md` - Detailed system architecture

**MCP Servers:**
- `mcp-servers/filesystem-mcp/` - Filesystem operations (watch, read, write files)
- `mcp-servers/email-mcp/` - Gmail integration
- `mcp-servers/slack-mcp/` - Slack integration
- `mcp-servers/calendar-mcp/` - Google Calendar integration

**Ralph (Autonomous Task Execution):**
- `.claude/skills/ralph/SKILL.md` - Ralph skill definition
- `.claude/skills/ralph/README.md` - Ralph user guide
- `.claude/skills/ralph/prompt-ai-employee.md` - Instructions for Claude Code
- `.claude/skills/ralph/prd.json` - Example task list (client onboarding)
- `scripts/start-ralph.sh` - Convenience wrapper to start Ralph
- `scripts/check-ralph-status.sh` - Check Ralph progress

---

*Updated: 2026-01-28*
**Production System - Cloud + Local Architecture**
*LinkedIn: ✅ Operational with summary generation*
*Twitter/X: ✅ Operational with summary generation*
*Instagram: ✅ Operational with summary generation*
*Facebook: ✅ Operational with summary generation*
*Cross-Domain Coordination: ✅ Personal/Business domain classification*
*AI Auto-Approver: ✅ Claude 3 makes intelligent approval decisions*
*All approval monitors in LIVE mode*
*20 PM2 processes running (0 crashes)*
*Research LinkedIn Generator: ✅ Daily automated research & posting*
*PLATINUM TIER: ✅ ~92% Complete (11/12 requirements)*

**Recent Improvements (v1.6.0 - PLATINUM TIER):**
- 🏆 **Platinum Tier Completion** - Git sync fixed, domain folders created, claim-by-move integrated
- 🔄 **Git Sync Fixed** - Resolved diverged branches, rebased 2198 Cloud commits onto origin/main
- 📁 **Domain Folder Structure** - Created Personal/Business/Shared subfolders in Done/, Rejected/, Updates/, In_Progress/
- 🤝 **Claim-by-Move Integration** - ClaimManager added to BaseWatcher, prevents double-processing
- 🏥 **Health Monitoring Verified** - Cloud generating health updates every 5 minutes
- ☁️ **Cloud-Local Sync** - bidirectional git sync working (Cloud pushes, Local pulls)

**Previous Improvements (v1.5.0):**
- 🔬 **Research LinkedIn Generator** - Daily automated research with GLM API
- 🛡️ **Security Hardening** - Removed hardcoded credentials, added UTF-8 encoding
- ⚡ **Performance Fixes** - Circuit breaker pattern, LRU eviction, reduced restarts
- 🔄 **Git Sync Improvements** - Auto-retry, diverged branch detection
- 📊 **LinkedIn Post Extraction** - Fixed to extract only post content, not metadata

**Previous Improvements (v1.4.0):**
- 🎯 **Cross-Domain Coordination** - Personal vs Business domain classification and routing
- 📊 **Cross-Domain Insights** - Unified reports across Personal and Business domains
- 🔄 **Domain Classifier** - Automatic classification of emails, tasks, and events
- ⚖️ **Work-Life Balance Tracking** - Monitor personal vs business task distribution
- 📝 **Social Media Summaries** - All platforms now generate post summaries in Briefings/
- 🔍 **Conflict Detection** - Automatic detection of cross-domain scheduling conflicts

---

## Production Features

### Cross-Domain Coordination (NEW)

**Domain Classification:**
- **Personal Domain:** Health, family, personal finance, education, hobbies
- **Business Domain:** Clients, invoices, projects, social media, accounting
- **Shared Domain:** Items affecting both (urgent tasks, reminders, scheduling)

**Usage:**
```bash
# Generate cross-domain insights
python scripts/cross_domain_insights.py --vault AI_Employee_Vault

# Test domain classifier
python -m watchers.domain_classifier
```

**Domain-Specific Folders:**
- `/Needs_Action/Personal/` - Personal tasks and events
- `/Needs_Action/Business/` - Business tasks and events
- `/Needs_Action/Shared/` - Items affecting both domains

**Integration:**
```python
from watchers.domain_classifier import classify_domain, Domain

domain = classify_domain(
    subject="Invoice #1234 from Acme Corp",
    content="Please find attached invoice",
    sender="billing@acmecorp.com",
    source="gmail"
)
# Returns: Domain.BUSINESS
```

### Social Media Summary Generation

All social media platforms now generate summaries after posting:
- **Twitter/X:** Tweet summaries with character count and engagement tracking
- **Facebook:** Post summaries with content preview and next steps
- **Instagram:** Post summaries with hashtag performance tracking
- **LinkedIn:** Post summaries with professional engagement metrics

Summaries are saved to `/Briefings/` folder.

---

### Platinum Tier Features (NEW)

**Cloud-Local Bidirectional Sync:**
- Cloud VM (143.244.143.143) runs watchers 24/7
- Git sync pushes Cloud changes every 5 minutes
- Local pulls changes via git-sync-pull
- Diverged branch detection and auto-rebase

**Domain Folder Structure:**
```
AI_Employee_Vault/
├── Done/
│   ├── Personal/ - Completed personal tasks
│   ├── Business/ - Completed business tasks
│   └── Shared/ - Completed cross-domain tasks
├── Rejected/
│   ├── Personal/ - Declined personal items
│   ├── Business/ - Declined business items
│   └── Shared/ - Declined shared items
├── Updates/
│   ├── Personal/ - Cloud→Local communication (personal)
│   ├── Business/ - Cloud→Local communication (business)
│   └── Shared/ - Cloud→Local communication (shared)
└── In_Progress/
    ├── cloud/
    │   ├── Personal/ - Cloud processing personal items
    │   ├── Business/ - Cloud processing business items
    │   └── Shared/ - Cloud processing shared items
    └── local/
        ├── Personal/ - Local processing personal items
        ├── Business/ - Local processing business items
        └── Shared/ - Local processing shared items
```

**Claim-by-Move Rule:**
- Watchers can claim items before processing
- Moves item to `In_Progress/<cloud|local>/` when claimed
- Prevents double-processing between Cloud and Local
- Auto-detected via `CLOUD_MODE` environment variable

**Usage:**
```python
from watchers.gmail_watcher import GmailWatcher

# Watcher automatically initializes Claim Manager
watcher = GmailWatcher(vault_path="AI_Employee_Vault")

# Claim an item before processing (optional)
if watcher._claim_item(item_path):
    # Process the item
    result = watcher.process_item(item)
else:
    # Item already claimed by another agent
    pass
```

**Health Monitoring:**
- Cloud generates health updates every 5 minutes
- Saved to `AI_Employee_Vault/Updates/cloud_health_*.json`
- Includes CPU, memory, disk, network, process status
- Alerts for high resource usage or stopped processes

**See `AI_Employee_Vault/PLATINUM_TIER_COMPLETION_SUMMARY.md` for full details.**
