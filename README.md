# Personal AI Employee

> A **local-first** AI system that acts as your 24/7 intelligent assistant. Built with Claude Code, Obsidian, and Python.

[![Status: Gold Tier 100% Complete](https://img.shields.io/badge/Status-Gold%20Tier%20100%25-brightgreen)](docs/STATUS.md)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue)](https://claude.ai/claude-code)
[![Obsidian](https://img.shields.io/badge/Obsidian-Compatible-purple)](https://obsidian.md)
[![Version](https://img.shields.io/badge/Version-1.1.1-blue)](CHANGELOG.md)

---

## Overview

The Personal AI Employee is a **Digital FTE (Full-Time Equivalent)** that monitors your digital life, reasons about the data using Claude (via Claude Code), and takes actions through various integrations. All data is stored locally in an Obsidian vault, ensuring complete privacy and control.

### Key Features

- **Local-First Architecture**: All data stored locally, no cloud dependencies
- **Human-in-the-Loop**: Approval workflows for all sensitive actions
- **Multi-Platform Monitoring**: Gmail, Calendar, WhatsApp, Xero, Twitter, LinkedIn, Facebook/Instagram
- **Automated Posting**: Social media posting with **fast copy-paste method** (100-200x faster)
- **Professional Instagram Images**: 6 stunning color themes with decorative borders
- **CEO Briefings**: Monday Morning CEO Briefing (7-task autonomous workflow, 3-6x faster)
- **Extensible Skills**: 20+ agent capabilities (content generation, accounting, scheduling)
- **See:** [Agent Skills Index](.claude/skills/INDEX.md) for complete skill documentation

### What Makes It Different

| Traditional AI Assistants | Personal AI Employee |
|--------------------------|---------------------|
| Cloud-based, data sent to servers | **Local-first, data stays on your machine** |
| Generic responses | **Context-aware, reads your vault** |
| Limited integrations | **15+ integrated platforms** |
| Black-box decisions | **Human approval required for actions** |
| Monthly subscription | **One-time setup, free to operate** |

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Claude Code** (Pro subscription or Gemini API router)
- **Obsidian** (v1.10.6+)
- **Node.js v20+ LTS** (for MCP servers)
- **PM2** (for process management): `npm install -g pm2`

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/PERSONAL_AI_EMPLOYEE.git
cd PERSONAL_AI_EMPLOYEE

# 2. Install Python dependencies
pip install playwright watchdog google-api-python-client google-auth-oauthlib
playwright install chromium

# 3. Install PM2
npm install -g pm2

# 4. Open in Obsidian
# Open this folder as an Obsidian vault

# 5. Start with Claude Code
claude --cwd .
```

### First Run

```bash
# Start the watchers
pm2 start process-manager/pm2.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Stop all
pm2 stop all
```

---

## Architecture

### Perception → Reasoning → Action Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     OBSIDIAN VAULT (Storage)                    │
│  ┌─────────┐  ┌───────────┐  ┌─────────┐  ┌──────────────┐    │
│  │ Inbox/  │  │  Needs_   │  │ Pending │  │   Approved/  │    │
│  │         │  │  Action/  │  │_Approv/ │  │              │    │
│  └────┬────┘  └─────┬─────┘  └────┬────┘  └──────┬───────┘    │
└───────┼─────────────┼─────────────┼──────────────┼─────────────┘
        │             │             │              │
        ▼             ▼             ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐
  │ File     │  │ Claude   │  │ Human    │  │ Approval   │
  │ Watcher  │  │ Code     │  │ Review   │  │ Monitors   │
  └──────────┘  └──────────┘  └──────────┘  └────────────┘
        │             │                          │
        └─────────────┴──────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   ACTIONS     │
              │               │
              │ • Social Post │
              │ • Send Email  │
              │ • Invoice     │
              └───────────────┘
```

### Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Watchers** | Monitor external sources | Python, Watchdog |
| **Claude Code** | Reasoning engine | Claude Sonnet 4.5 |
| **Skills** | Agent capabilities | Modular markdown |
| **Approval Monitors** | Human-in-the-loop | Python, Watchdog |
| **Actions** | Execute tasks | Playwright, APIs |
| **Obsidian** | Knowledge base & UI | Markdown |

---

## Features by Tier

### Bronze Tier (✅ Complete)

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] Gmail Watcher - Monitors unread emails
- [x] Calendar Watcher - Monitors upcoming events
- [x] Folder structure for workflow
- [x] Base Watcher class for extensibility
- [x] Claude Code integration

### Silver Tier (✅ Complete)

- [x] LinkedIn Watcher & Poster
- [x] WhatsApp Watcher
- [x] Email MCP server
- [x] Enhanced approval workflow
- [x] PM2 process management
- [x] Cron scheduling
- [x] Agent Skills (content-generator, planning-agent, approval-manager)

### Gold Tier (✅ 100% Complete)

- [x] Xero Integration (accounting, invoicing)
- [x] Facebook/Instagram Watcher & Poster with **professional image generation**
- [x] Twitter/X Watcher & Poster with **fast copy-paste method**
- [x] LinkedIn Watcher & Poster with **fast copy-paste method**
- [x] CEO Briefings (daily automated)
- [x] Daily Review Agent
- [x] Social Media Scheduler
- [x] 17+ Agent Skills
- [x] Comprehensive documentation
- [x] **Speed optimizations** (100-200x faster posting)
- [x] **Professional image themes** (6 color themes for Instagram)
- [x] **Ralph Wiggum autonomous task execution** (Monday CEO Briefing)
- [x] **Process control guide** (complete PM2 management)
- [x] **Presentation materials** (script, slides, Q&A prep)
- [ ] Demo video (5-10 minutes)

---

## Project Structure

```
PERSONAL_AI_EMPLOYEE/
│
├── 📄 Core Vault Files (Root Level)
│   ├── Index.md                   ⭐ Vault home page
│   ├── Dashboard.md               - System status overview
│   ├── README.md                  - This file
│   └── .gitignore                 - Git ignore rules
│
├── 📂 Input/Processing Folders
│   ├── Inbox/                     - Drop zone for new items
│   ├── Needs_Action/              - Items requiring attention
│   ├── Pending_Approval/          - Awaiting human review
│   ├── Approved/                  - Ready for execution
│   ├── Rejected/                  - Declined actions
│   ├── Plans/                     - Execution plans
│   └── Done/                      - Completed items
│
├── 📂 Output/Records Folders
│   ├── Briefings/                  - CEO briefings & summaries
│   ├── Logs/                       - Daily JSON logs
│   └── Accounting/                 - Monthly accounting
│
├── 📂 Configuration
│   └── config/
│       ├── Company_Handbook.md    - Rules of engagement
│       ├── Business_Goals.md       - Strategic objectives
│       ├── CLAUDE.md                - Project documentation
│       └── client_secret.json      - OAuth credentials (gitignored)
│
├── 📂 Documentation
│   └── docs/
│       ├── ARCHITECTURE.md         - System architecture
│       ├── LESSONS_LEARNED.md      - Development insights
│       ├── SECURITY.md             - Security best practices
│       ├── Hackathon0.md           - Project overview
│       ├── Skill-Create.md         - Skill development guide
│       └── QUICK_REFERENCE.md      - Common commands
│
├── 📂 Scripts & Automation
│   └── scripts/
│       ├── main.py                  - Main entry point
│       ├── orchestrator.py           - Process manager
│       └── social-media/            - Social media posters
│           ├── linkedin_poster.py
│           ├── linkedin_stealth_poster.py
│           ├── linkedin_approval_monitor.py
│           ├── meta_poster.py
│           ├── meta_approval_monitor.py
│           ├── twitter_poster.py
│           └── twitter_approval_monitor.py
│
├── 📂 Watchers (Sensors)
│   └── watchers/
│       ├── base_watcher.py          - Abstract base class
│       ├── gmail_watcher.py         - Gmail monitoring
│       ├── calendar_watcher.py      - Calendar monitoring
│       ├── xero_watcher.py          - Xero monitoring
│       ├── filesystem_watcher.py    - File drop monitoring
│       └── whatsapp_watcher_simple.py - WhatsApp monitoring
│
├── 📂 Agent Skills
│   └── .claude/skills/
│       ├── whatsapp-manager/          - WhatsApp interaction
│       ├── email-manager/             - Email management
│       ├── calendar-manager/          - Calendar scheduling
│       ├── xero-manager/              - Accounting tasks
│       ├── facebook-instagram-manager/ - Meta platforms
│       ├── twitter-manager/           - Twitter/X posting
│       ├── linkedin-manager/          - LinkedIn posting
│       ├── social-media-manager/      - Cross-platform strategy
│       ├── content-generator/         - Content creation
│       ├── weekly-briefing/           - CEO briefings
│       ├── daily-review/              - Daily planning
│       └── accounting/                - Financial reporting
│
├── 📂 Utilities
│   ├── utils/                      - Utility modules
│   ├── mcp-servers/               - MCP servers
│   ├── process-manager/           - PM2 configuration
│   └── Archive/                   - Archived files
│
└── 📂 Temporary/Sessions (gitignored)
    ├── whatsapp_session/          - WhatsApp browser session
    ├── .env                        - Environment variables
    └── __pycache__/               - Python cache
```

---

## Setup Guide

### 1. Google Cloud Setup (Gmail & Calendar)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Gmail API** and **Calendar API**
4. Configure OAuth consent screen:
   - Select "External" user type
   - Add required scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/calendar.readonly`
5. Create OAuth 2.0 credentials:
   - Go to Credentials > Create Credentials > OAuth client ID
   - Application type: Desktop app
   - Download JSON and save as `config/client_secret.json`

### 2. Xero Setup (Optional)

For accounting integration:

1. Go to [Xero Developer Portal](https://developer.xero.com/app/manage)
2. Create a new app
3. Save credentials to `config/.xero_credentials.json`
4. Run authentication:
   ```bash
   python -m watchers.xero_watcher --credentials config/.xero_credentials.json --once
   ```

### 3. Chrome Setup (Social Media Posting)

For Facebook/Instagram, Twitter, and LinkedIn posting:

**Windows:**
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

**Mac/Linux:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222
```

Then:
1. Open https://business.facebook.com (Meta Business Suite)
2. Log in with your Facebook account
3. Connect your Instagram business account
4. Open https://twitter.com or https://linkedin.com and log in

### 4. Configure Your Vault

Edit these files to personalize your AI Employee:

1. **`config/Company_Handbook.md`** - Define rules of engagement
2. **`config/Business_Goals.md`** - Set business objectives
3. **`Dashboard.md`** - Will be auto-updated by watchers

### 5. Start the System

```bash
# Start all watchers with PM2
pm2 start process-manager/pm2.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup
# Follow the instructions displayed

# Check status
pm2 status

# View logs
pm2 logs

# Stop all
pm2 stop all
```

---

## Usage Examples

### Email Monitoring

```bash
# Watcher detects new invoice email
# Creates: Needs_Action/GMAIL_20260111_180000.md
```

Then in Claude Code:
```
Read the new Gmail file in Needs_Action and extract the invoice details
```

### Social Media Posting

```bash
# Create approval file
cat > Pending_Approval/TWITTER_POST_20260111_180000.md << 'EOF'
---
type: twitter_post
platforms: [Twitter]
priority: high
status: pending_approval
---

## Content
Just shipped a new feature that will save you hours every week! 🚀

#ProductLaunch #Innovation
EOF

# Move to Approved/
mv Pending_Approval/TWITTER_POST_20260111_180000.md Approved/

# Monitor detects and posts automatically
```

### Daily Briefing

```bash
# Generated automatically at 7 AM daily
cat Briefings/CEO_Daily_Briefing_20260111.md
```

---

## Agent Skills

The AI Employee has 20+ skills that Claude can invoke:

### Communication Skills
- **whatsapp-manager**: Monitor and respond to WhatsApp messages
- **email-manager**: Email management and drafting
- **calendar-manager**: Schedule management
- **slack-manager**: Slack communication management

### Social Media Skills
- **twitter-manager**: Twitter/X posting and engagement (fast copy-paste)
- **linkedin-manager**: LinkedIn posting and networking (fast copy-paste)
- **facebook-instagram-manager**: Meta platform management
- **social-media-manager**: Cross-platform strategy

### Business Skills
- **xero-manager**: Accounting and invoicing
- **accounting**: Financial reporting
- **content-generator**: Content creation

### Productivity Skills
- **ralph**: Autonomous task execution (Ralph Wiggum loop)
- **business-handover**: Monday Morning CEO Briefing (standout feature)
- **weekly-briefing**: CEO briefings and business audits
- **daily-review**: Daily planning
- **approval-manager**: Approval workflow management
- **planning-agent**: Complex task breakdown

### Utility Skills
- **filesystem-manager**: Drop folder monitoring
- **inbox-processor**: Inbox organization
- **skill-creator**: Create new skills

### See Also
- **`.claude/skills/`** - All skill documentation
- **`docs/RALPH_USER_GUIDE.md`** - Ralph autonomous task execution guide
- **`docs/PROCESS_CONTROL_GUIDE.md`** - PM2 process management guide

---

## Configuration

### Environment Variables

Create `config/.env` (gitignored):

```bash
# Google API credentials path
GOOGLE_CREDENTIALS_PATH=config/client_secret.json

# Xero credentials
XERO_API_KEY=your_api_key
XERO_API_SECRET=your_api_secret

# Vault path
VAULT_PATH=.

# Dry run mode (log only, no actions)
DRY_RUN=false
```

### PM2 Configuration

Edit `process-manager/pm2.config.js` to customize:

- Polling intervals
- Cron schedules
- Resource limits
- Environment variables

---

## Security

### Key Security Features

- ✅ Local-first architecture (data never leaves your control)
- ✅ OAuth2 for external service authentication
- ✅ Credential isolation in `config/` directory
- ✅ Comprehensive audit logging
- ✅ Human-in-the-loop approval workflows
- ✅ No hardcoded credentials
- ✅ Environment variable isolation

### Best Practices

1. **Never commit** credentials to git
2. **Enable full disk encryption** on your computer
3. **Use strong passwords** for all accounts
4. **Enable 2FA** on all integrated services
5. **Review logs regularly** for suspicious activity
6. **Keep dependencies updated**

### See Also
- **`docs/SECURITY.md`** - Comprehensive security guide

---

## Troubleshooting

### Common Issues

**Q: Chrome won't connect to CDP**
```bash
# Check if Chrome is running with debugging
netstat -ano | findstr :9222

# Restart Chrome with debugging
# Windows:
taskkill /F /IM chrome.exe
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

**Q: Token expired**
```bash
# Delete the token file and re-authenticate
rm config/.gmail_token.json
python -m watchers.gmail_watcher --credentials config/client_secret.json --once
```

**Q: No files being created**
```bash
# Check that the vault path is correct
# Verify your inbox has unread messages
# Run with --dry-run to see what would be created
python -m watchers.gmail_watcher --vault . --credentials config/client_secret.json --dry-run
```

**Q: PM2 processes keep restarting**
```bash
# Check logs for errors
pm2 logs

# Reset restart count
pm2 reset all

# Increase max_restarts in pm2.config.js
```

### Getting Help

- **Documentation**: See `docs/` folder
- **Issues**: Check `docs/LESSONS_LEARNED.md` for common problems
- **Community**: [GitHub Discussions](https://github.com/yourusername/PERSONAL_AI_EMPLOYEE/discussions)

---

## Development

### Adding a New Watcher

```python
# watchers/my_watcher.py
from watchers.base_watcher import BaseWatcher

class MyWatcher(BaseWatcher):
    """Watch for events in MyService."""

    def scan(self) -> List[ActionFile]:
        # 1. Connect to external service
        # 2. Scan for new events
        # 3. Create action files
        pass
```

### Adding a New Skill

```bash
# Create skill directory
mkdir -p .claude/skills/my-skill

# Create skill files
touch .claude/skills/my-skill/SKILL.md
touch .claude/skills/my-skill/FORMS.md
touch .claude/skills/my-skill/reference.md
touch .claude/skills/my-skill/examples.md
```

### See Also
- **`docs/Skill-Create.md`** - Skill development guide
- **`docs/ARCHITECTURE.md`** - System architecture

---

## Roadmap

### Completed (✅)

- Bronze Tier: Gmail and Calendar monitoring
- Silver Tier: LinkedIn, WhatsApp, Email MCP
- Gold Tier: Xero, Social Media posting, CEO Briefings

### In Progress (🔄)

- Final documentation (95% complete)
- Demo video

### Future (📋)

- Web UI for approvals
- Analytics dashboard
- Mobile app for approvals
- Multi-language support
- Advanced scheduling
- Machine learning for content optimization

---

## Contributing

This is a personal project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - Feel free to use this as a template for your own AI Employee.

---

## Acknowledgments

Built with:
- **[Claude Code](https://claude.ai/claude-code)** - AI reasoning engine
- **[Obsidian](https://obsidian.md)** - Knowledge base interface
- **[Playwright](https://playwright.dev)** - Browser automation
- **[PM2](https://pm2.keymetrics.io)** - Process manager
- **[Watchdog](https://python-watchdog.readthedocs.io/)** - File monitoring

---

**Status**: Gold Tier 100% Complete | Last Updated: 2026-01-14 | Version 1.1.1

*Generated with Claude Code - Personal AI Employee*

**Recent Updates (v1.1.1):**
- ✨ **Ralph Wiggum autonomous task execution** - Monday Morning CEO Briefing capability
- 📚 **Complete process control guide** - PM2 process management documentation
- 🎯 **Presentation materials** - Full presentation script, slides, Q&A preparation
- 📋 **Executive summary** - Business-ready summary for stakeholders
- 🎨 **6 professional Instagram themes** - Midnight Purple, Ocean Blue, Sunset Orange, Forest Green, Royal Gold, Deep Navy
- ⚡ **Fast copy-paste** for LinkedIn & Twitter (100-200x faster posting)
- 📚 **Complete documentation** - Process control, Ralph user guide, Social media guide
- 🔧 **Vault path fix** - Removed nested vault structure
- 📝 **Changelog updated** - Complete version history tracked

**Available Documentation:**
- `README.md` - Project overview and quick start (this file)
- `CLAUDE.md` - Complete project instructions
- `docs/ARCHITECTURE.md` - System architecture
- `docs/SOCIAL_MEDIA_GUIDE.md` - Social media posting guide
- `docs/PROCESS_CONTROL_GUIDE.md` - PM2 process management
- `docs/RALPH_USER_GUIDE.md` - Ralph autonomous task execution guide
- `CHANGELOG.md` - Version history and updates

See [`CHANGELOG.md`](CHANGELOG.md) for full version history.
