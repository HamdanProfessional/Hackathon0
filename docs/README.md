# AI Employee

**Version:** 1.4.1
**Last Updated:** 2025-01-19

---

## Overview

AI Employee is a **production-ready autonomous AI system** that runs 24/7 to monitor external services, make intelligent decisions, and execute business actions with human oversight.

It transforms Claude from a general-purpose AI assistant into a specialized business employee that can:
- Monitor Gmail, Calendar, Slack, WhatsApp, and other services
- Generate and post content to LinkedIn, Twitter, Facebook, and Instagram
- Create CEO-level business briefings and daily plans
- Execute autonomous multi-step workflows
- Manage accounting via Odoo integration

**Key Innovation:** The **Monday Morning CEO Briefing** - AI autonomously audits business performance, reviews logs, analyzes transactions, compares progress to targets, and reports revenue and bottlenecks.

---

## Quick Start

### 1. Start the System

```bash
# Start all 19 PM2 processes
pm2 start process-manager/pm2.config.js

# Check status
pm2 status

# View logs
pm2 logs
```

### 2. Check the Dashboard

Open `AI_Employee_Vault/Dashboard.md` in Obsidian to see:
- Pending messages
- Active projects
- Bank balance
- System status

### 3. Review and Approve

Check `AI_Employee_Vault/Pending_Approval/` for items requiring human review.

Move to `AI_Employee_Vault/Approved/` to execute, or `AI_Employee_Vault/Rejected/` to decline.

---

## Architecture

### Three-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│                   PERCEPTION LAYER                          │
│  Monitors external services and creates action files          │
│                                                              │
│  Gmail • Calendar • Slack • WhatsApp • Filesystem          │
└───────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  REASONING LAYER                           │
│  AI Auto-Approver (Claude 3 Haiku) analyzes files and        │
│  makes intelligent decisions:                                │
│  • approve → Safe actions (file ops, known contacts)        │
│  • reject → Dangerous (scams, phishing, payments)           │
│  • manual → Needs human review (social media, new contacts) │
└───────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ACTION LAYER                             │
│  Approval monitors detect approved files and execute        │
│  actions via MCP servers using browser automation:         │
│                                                              │
│  LinkedIn • Twitter • Facebook • Instagram • Email         │
└─────────────────────────────────────────────────────────────┘
```

### Components

**16 PM2 Processes Running 24/7:**

| Type | Process | Purpose |
|------|---------|---------|
| **Watchers** (6) | gmail-watcher, calendar-watcher, slack-watcher, odoo-watcher, filesystem-watcher, whatsapp-watcher | Monitor external services |
| **Approval Monitors** (7) | email-approval-monitor, calendar-approval-monitor, slack-approval-monitor, linkedin-approval-monitor, twitter-approval-monitor, facebook-approval-monitor, instagram-approval-monitor | Execute approved actions |
| **Core** (3) | auto-approver, ai-employee-dashboard | AI decisions + web UI |

---

## Features

### 1. Email Management

**Gmail Watcher** monitors your inbox and:
- Detects new unread messages
- Identifies important emails (keywords, flags)
- Creates action files in `Needs_Action/`
- AI Auto-Approver triages automatically

**Email Approval Monitor**:
- Detects approved emails in `Approved/`
- Sends via Gmail MCP server
- Moves to `Done/` on success

### 2. Calendar Management

**Calendar Watcher** monitors Google Calendar:
- Detects upcoming events
- Identifies meetings requiring preparation
- Creates reminder files

**Calendar Approval Monitor**:
- Creates/updates calendar events via Calendar MCP
- Handles event conflicts and scheduling

### 3. Social Media Automation

All platforms support:
- **Create posts** via skill invocation or manual file creation
- **Auto-approval** workflow (AI flags for manual review)
- **Fast posting** via Chrome CDP automation

**LinkedIn:**
- Fast copy-paste method (100-200x faster than typing)
- No character limit
- Professional formatting

**Twitter/X:**
- 280 character limit (auto-truncates if longer)
- Fast copy-paste method

**Facebook:**
- Direct content insertion
- Supports emojis and formatting
- 63,206 character limit

**Instagram:**
- **Professional image generation** (1080x1080)
- 6 color themes (Midnight Purple, Ocean Blue, Sunset Orange, Forest Green, Royal Gold, Deep Navy)
- Auto-caption with hashtags
- Emojis removed from image, kept in caption

### 4. AI Auto-Approver

Powered by Claude 3 Haiku, makes intelligent decisions:

| Decision | Criteria |
|----------|----------|
| **approve** | File operations, known contacts, Slack/WhatsApp, internal tasks |
| **reject** | Scams, phishing, payment requests |
| **manual** | Social media, payments, new contacts |

**Cost:** ~$0.00025 per decision (~$5-10/month)

### 5. Monday Morning CEO Briefing

**The standout feature** that transforms AI from reactive to proactive.

**Generates comprehensive briefing with:**
- Executive summary
- Revenue analysis (weekly, MTD, vs target)
- Completed tasks
- Bottlenecks
- Proactive suggestions (cost optimization, process improvements)
- Action items

**Performance:** 10-15 minutes vs 30-60 manual (3-6x faster)

**Usage:**
```bash
# Via Python
python .claude/skills/weekly-briefing/invoke.py "Generate CEO briefing"

# Via Claude Code
/skill weekly-briefing "Generate business audit"
```

### 6. Ralph - Autonomous Task Execution

**Ralph Wiggum Loop** for autonomous multi-step task completion:

1. Load task list
2. Pick highest priority incomplete task
3. Plan execution
4. Execute using available skills
5. Create approval request for external actions
6. Wait for human approval
7. Verify execution
8. Continue to next task

**Usage:**
```bash
python .claude/skills/ralph/invoke.py "Complete client onboarding"
```

### 7. Daily Review

Generates daily task plans with:
- Priority tasks for the day
- Upcoming deadline alerts
- Inbox triage
- Schedule optimization

---

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # System status overview
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md          # Business targets
│
├── Needs_Action/              # Items detected by watchers
├── Pending_Approval/          # Awaiting human review
├── Approved/                  # Ready for execution
├── Rejected/                  # Declined items
├── Done/                      # Completed items
│
├── Plans/                     # Execution plans
├── Logs/                      # Daily JSON logs (YYYY-MM-DD.json)
├── Briefings/                  # CEO briefings
│
├── Accounting/                 # Financial records
└── Updates/                   # Cloud agent updates
```

---

## Skills

All AI functionality is organized as **Agent Skills** in `.claude/skills/`:

### Watcher Skills
- **email-manager** - Gmail API integration
- **calendar-manager** - Google Calendar events
- **slack-manager** - Slack Bot API
- **whatsapp-manager** - Playwright automation
- **filesystem-manager** - File system monitoring
- **xero-manager** - Xero accounting via MCP

### Social Media Skills
- **linkedin-manager** - LinkedIn posting
- **twitter-manager** - Twitter/X posting
- **facebook-instagram-manager** - Facebook & Instagram posting

### Core Skills
- **approval-manager** - Human-in-the-loop approval
- **ralph** - Autonomous task execution
- **weekly-briefing** - CEO business audit
- **daily-review** - Daily task planning

### Supporting Skills
- **content-generator** - Content creation
- **planning-agent** - Task breakdown
- **business-handover** - Executive continuity

---

## Usage Examples

### Create a LinkedIn Post

**Option 1: Via Skill Invocation**
```bash
python .claude/skills/linkedin-manager/invoke.py "Excited to share our AI automation progress #AI #Tech"
```

**Option 2: Manual File Creation**
```bash
cat > "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: linkedin_post
platform: linkedin
created: $(date -Iseconds)
status: pending_approval
---

Your post content here
#Hashtags
EOF

# Then approve
mv "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md" "AI_Employee_Vault/Approved/"
```

### Generate CEO Briefing

```bash
python .claude/skills/weekly-briefing/invoke.py "Generate CEO briefing"
```

Output saved to: `AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`

### Start Autonomous Task Execution

```bash
python .claude/skills/ralph/invoke.py "Complete client onboarding process"
```

Creates task file in `Plans/`, ready for Ralph to execute.

---

## PM2 Management

### Start All Processes

```bash
pm2 start process-manager/pm2.config.js
pm2 save
```

### Check Status

```bash
pm2 status
pm2 logs
pm2 logs gmail-watcher --lines 50
```

### Restart a Process

```bash
pm2 restart linkedin-approval-monitor
```

### Stop All

```bash
pm2 stop all
```

---

## Chrome Automation (Social Media)

### Start Chrome with CDP

```bash
# Windows
start_chrome.bat

# Or manually:
chrome.exe --user-data-dir="C:\Users\User\AppData\Local\Google\Chrome\User Data" --remote-debugging-port=9222
```

### Login to Platforms

1. Chrome window opens with CDP on port 9222
2. Navigate to each platform (linkedin.com, x.com, facebook.com, instagram.com)
3. Log in with your credentials
4. Keep Chrome window open

### Posting Flow

1. Create post in `Pending_Approval/`
2. Review and move to `Approved/`
3. Approval monitor detects and posts
4. Moves to `Done/` on success

---

## Configuration

### Environment Variables

```bash
# Social Media DRY_RUN mode (default: true for testing)
LINKEDIN_DRY_RUN=false
TWITTER_DRY_RUN=false
FACEBOOK_DRY_RUN=false
INSTAGRAM_DRY_RUN=false

# Anthropic API for AI Auto-Approver
ANTHROPIC_API_KEY=your-key-here
```

### PM2 Configuration

Main config: `process-manager/pm2.config.js`

All processes use:
- Vault path: `--vault AI_Employee_Vault`
- Python path: `PYTHONPATH=C:\Users\User\Desktop\AI_EMPLOYEE_APP`

---

## Troubleshooting

### Process Not Starting

```bash
# Check for errors
pm2 logs process-name --err

# Check if Python module exists
python -c "from watchers.gmail_watcher import GmailWatcher; print('OK')"

# Restart process
pm2 restart process-name
```

### Chrome Not Connecting

```bash
# Check if CDP port is open
curl http://localhost:9222/json/version

# Should return browser info
# If error, start Chrome CDP manually
```

### File Not Being Created

```bash
# Check vault exists
ls AI_Employee_Vault/

# Check folder permissions
ls -la AI_Employee_Vault/Pending_Approval/

# Check watcher logs
pm2 logs gmail-watcher
```

### Social Media Post Failing

```bash
# Check if Chrome CDP is running
curl http://localhost:9222/json/version

# Check if logged in (manually verify in Chrome)

# Check DRY_RUN mode
echo $LINKEDIN_DRY_RUN  # Should be "false" for live posting

# Check approval monitor logs
pm2 logs linkedin-approval-monitor --err
```

---

## Security

### Human-in-the-Loop

All sensitive actions require approval:
- Social media posts
- Email sending
- Calendar changes
- Payments
- New contacts

### No Secrets Sync

Vault sync excludes:
- `.env`
- `*_token.json`
- `*_credentials.json`
- WhatsApp sessions

### Audit Trail

All actions logged to: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

---

## Performance

| Metric | Value |
|--------|-------|
| **Processes Running** | 16/17 (94%) |
| **Skills Available** | 20+ |
| **Social Media Platforms** | 4 (LinkedIn, Twitter, Facebook, Instagram) |
| **Posting Speed** | 100-200x faster (fast copy-paste) |
| **CEO Briefing Speed** | 3-6x faster than manual |
| **Human Review Reduction** | 95%+ |
| **Cost/Month** | ~$5-10 (AI Auto-Approver) |

---

## Development

### Project Structure

```
AI_EMPLOYEE_APP/
├── .claude/
│   └── skills/              # All Agent Skills
│       ├── email-manager/
│       ├── linkedin-manager/
│       ├── weekly-briefing/
│       └── ... (20+ skills)
├── mcp-servers/               # MCP servers for external actions
│   ├── linkedin-mcp/
│   ├── twitter-mcp/
│   ├── facebook-mcp/
│   └── instagram-mcp/
├── watchers/                   # Watcher modules
│   ├── base_watcher.py
│   ├── gmail_watcher.py
│   └── ...
├── process-manager/
│   ├── pm2.config.js         # PM2 configuration
│   └── pm2.local.config.js    # Local PM2 config
├── AI_Employee_Vault/         # Obsidian vault (all data)
├── scripts/                    # Utility scripts
│   ├── chrome_cdp_helper.py
│   └── start_chrome.bat
└── docs/                       # Documentation (this file)
```

### Adding a New Skill

1. Create directory: `.claude/skills/your-skill/`
2. Create `SKILL.md` with YAML frontmatter
3. Add `scripts/` subdirectory if needed
4. Add to PM2 config if continuous process
5. Document in skills index

---

## Support

### Getting Help

- **README.md** - This file
- `docs/AGENT_SKILLS_REFERENCE.md` - Complete skill catalog
- `docs/TROUBLESHOOTING.md` - Common issues and solutions

### Logs

```bash
# All logs
pm2 logs

# Specific process
pm2 logs gmail-watcher --lines 100

# Error logs only
pm2 logs --err
```

### Dashboard

Web dashboard available at: http://localhost:3000

---

## License

Apache License 2.0

---

**AI Employee v1.4.1** - Your autonomous AI business assistant.

Built with Claude Code, Python, Node.js, Playwright, and Claude 3 Haiku.
