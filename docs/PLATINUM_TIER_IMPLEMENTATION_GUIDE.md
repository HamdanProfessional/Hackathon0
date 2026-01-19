# Platinum Tier Implementation Guide

**Always-On Cloud + Local Executive (Production-ish AI Employee)**

## Overview

Platinum Tier implements a distributed AI Employee system with specialized work zones:

- **Cloud VM (24/7)**: Email triage, draft replies, social post drafts/scheduling (draft-only)
- **Local Machine**: Approvals, WhatsApp session, payments/banking, final "send/post" actions

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DIGITAL OCEAN CLOUD VM                      │
│  (Always-On: Email Triage + Drafting + Scheduling)                │
│                                                                     │
│  ✅ Gmail Watcher     → Detects emails                              │
│  ✅ Calendar Watcher  → Detects events                              │
│  ✅ Slack Watcher     → Detects messages                            │
│  ✅ Odoo Watcher      → Detects accounting events                  │
│                                                                     │
│  ✅ AI Auto-Approver  → Intelligent triage                         │
│                      → Safe: draft reply/approve                   │
│                      → Uncertain: mark for review                   │
│                      → Dangerous: reject                           │
│                                                                     │
│  ✅ Creates DRAFTS in:                                             │
│     - /Pending_Approval/EMAIL_*.md (draft replies)              │
│     - /Pending_Approval/LINKEDIN_POST_*.md (draft posts)         │
│     - /Pending_Approval/TWITTER_POST_*.md (draft tweets)          │
│     - /Pending_Approval/FACEBOOK_POST_*.md (draft posts)         │
│     - /Pending_Approval/INSTAGRAM_POST_*.md (draft posts)        │
│                                                                     │
│  ❌ NEVER runs:                                                    │
│     - WhatsApp Watcher (session required)                          │
│     - Email/Calendar/Slack/Instagram MCP senders (approval needed)│
│     - Payment/Banking actions (security)                           │
│                                                                     │
│  ✅ Git Sync: Pushes drafts/updates every 5 minutes               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Git Sync (markdown/state only)
                              │ (secrets never sync)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        LOCAL MACHINE                                 │
│  (Executive: Approvals + WhatsApp + Final Execution)              │
│                                                                     │
│  ✅ WhatsApp Watcher     → Monitors WhatsApp (local session)     │
│  ✅ Filesystem Watcher   → Monitors /Inbox for drop zone          │
│                                                                     │
│  ✅ User Approval        → Reviews /Pending_Approval/            │
│                          → Moves to /Approved/ or /Rejected/        │
│                                                                     │
│  ✅ Approval Monitors:  → Execute approved actions via MCP       │
│     - Email Monitor      → Sends draft replies via Gmail MCP      │
│     - Calendar Monitor   → Creates events via Calendar MCP       │
│     - LinkedIn Monitor   → Posts via Chrome CDP (port 9222)       │
│     - Twitter Monitor    → Posts via Chrome CDP                   │
│     - Facebook Monitor   → Posts via Chrome CDP                   │
│     - Instagram Monitor  → Posts via Chrome CDP                   │
│                                                                     │
│  ✅ Git Sync: Pulls drafts/updates, pushes approvals/changes      │
│  ✅ Dashboard Merger:  Merges /Updates/ into Dashboard.md         │
└─────────────────────────────────────────────────────────────────────┘
```

## Work-Zone Specialization

### Cloud Responsibilities (Draft-Only)

| Task | Cloud Action | Local Action |
|------|--------------|--------------|
| **Email arrives** | Triage, draft reply | Review, approve, send |
| **Social media** | Draft post content | Review, approve, post |
| **Calendar events** | Detect, draft if needed | Review, approve, create |
| **Slack messages** | Detect, categorize | Review, respond |
| **WhatsApp** | ❌ Never monitor | Monitor and respond |
| **Payments** | ❌ Never handle | Handle all payments |

### Security Rules

1. **Vault Sync (Git)**
   - ✅ Syncs: Markdown files, state files (`.*_state.json`)
   - ❌ Never syncs: `.env`, `*_token.json`, `whatsapp_session/`, banking credentials

2. **Cloud NEVER Has Access To:**
   - WhatsApp sessions (`whatsapp_session/`)
   - Payment/banking credentials
   - API tokens for sending (only has for reading)

3. **Claim-By-Move Rule**
   - First agent to move item from `/Needs_Action/` to `/In_Progress/<agent>/` owns it
   - Other agents must skip items in `/In_Progress/`

4. **Single-Writer Rule**
   - `Dashboard.md` = Local only (Cloud writes to `/Updates/`, Local merges)

## Directory Structure

```
AI_Employee_Vault/
├── Needs_Action/          # New items (Cloud writes here)
│   └── EMAIL_*.md
├── In_Progress/           # Claimed items (lock mechanism)
│   ├── cloud/            # Cloud working on these
│   └── local/            # Local working on these
├── Pending_Approval/      # Awaiting human review (AI marked uncertain)
│   ├── EMAIL_*.md        # Draft replies from Cloud
│   ├── LINKEDIN_POST_*.md
│   ├── TWITTER_POST_*.md
│   ├── FACEBOOK_POST_*.md
│   └── INSTAGRAM_POST_*.md
├── Approved/              # Ready for execution (Local only)
├── Rejected/              # Declined items
├── Done/                  # Completed items
├── Plans/                 # Execution plans
├── Updates/               # Cloud writes updates here (Local merges to Dashboard.md)
├── Signals/               # Real-time signals from Cloud
└── Dashboard.md           # Single-writer: Local only
```

## Implementation Steps

### Phase 1: Cloud VM Setup

1. **Deploy Cloud VM** (Already done: 143.244.143.143)
   - Ubuntu 22.04 LTS
   - Python 3.12 + venv
   - Node.js + PM2
   - Git repository

2. **Configure Cloud PM2** (Draft-Only processes)

```javascript
// process-manager/pm2.cloud.config.js

// Cloud RUNS these (draft-only):
module.exports = {
  apps: [
    // ===== WATCHERS (Detection Only) =====
    {
      name: 'gmail-watcher',
      script: 'watchers/gmail_watcher.py',
      args: '--vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json',
      interpreter: '/root/AI_EMPLOYEE_APP/venv/bin/python',
      autorestart: true
    },
    {
      name: 'calendar-watcher',
      script: 'watchers/calendar_watcher.py',
      args: '--vault AI_Employee_Vault',
      interpreter: '/root/AI_EMPLOYEE_APP/venv/bin/python',
      autorestart: true
    },
    {
      name: 'slack-watcher',
      script: 'watchers/slack_watcher.py',
      args: '--vault AI_Employee_Vault',
      interpreter: '/root/AI_EMPLOYEE_APP/venv/bin/python',
      autorestart: true
    },
    {
      name: 'odoo-watcher',
      script: 'watchers/odoo_watcher.py',
      args: '--vault AI_Employee_Vault',
      interpreter: '/root/AI_EMPLOYEE_APP/venv/bin/python',
      autorestart: true
    },

    // ===== AI AUTO-APPROVER (Triage + Draft) =====
    {
      name: 'auto-approver',
      script: '.claude/skills/approval-manager/scripts/auto_approver.py',
      args: '--vault AI_Employee_Vault --mode cloud-draft-only',
      env: {
        ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
        PYTHONPATH: '/root/AI_EMPLOYEE_APP'
      },
      interpreter: '/root/AI_EMPLOYEE_APP/venv/bin/python',
      autorestart: true
    },

    // ===== SOCIAL MEDIA SCHEDULER (Draft-Only) =====
    {
      name: 'social-media-scheduler',
      script: 'scripts/social_media_scheduler.py',
      args: '--vault AI_Employee_Vault --mode draft',
      interpreter: '/root/AI_EMPLOYEE_APP/venv/bin/python',
      autorestart: true,
      cron_restart: '0 */4 * * *'  // Every 4 hours
    },

    // ===== GIT SYNC (Push Drafts) =====
    {
      name: 'git-sync-push',
      script: 'scripts/git_sync_push.sh',
      cron_restart: '*/5 * * * *',  // Every 5 minutes
      autorestart: false
    }
  ]
};
```

### Phase 2: Local Machine Setup

```javascript
// process-manager/pm2.local.config.js

// Local RUNS these (approvals + execution):
module.exports = {
  apps: [
    // ===== LOCAL-ONLY WATCHERS =====
    {
      name: 'whatsapp-watcher',
      script: 'watchers/whatsapp_watcher_playwright.py',
      args: '--vault AI_Employee_Vault --session ./whatsapp_session',
      interpreter: 'python',
      autorestart: true
    },
    {
      name: 'filesystem-watcher',
      script: 'watchers/filesystem_watcher.py',
      args: '--vault AI_Employee_Vault --watch-folder AI_Employee_Vault/Inbox',
      interpreter: 'python',
      autorestart: true
    },

    // ===== APPROVAL MONITORS (Execute Approved Actions) =====
    {
      name: 'email-approval-monitor',
      script: '.claude/skills/email-manager/scripts/email_approval_monitor.py',
      args: '--vault AI_Employee_Vault',
      env: {
        EMAIL_DRY_RUN: 'false'  // LIVE MODE
      },
      interpreter: 'python',
      autorestart: true
    },
    {
      name: 'calendar-approval-monitor',
      script: '.claude/skills/calendar-manager/scripts/calendar_approval_monitor.py',
      args: '--vault AI_Employee_Vault',
      interpreter: 'python',
      autorestart: true
    },
    {
      name: 'slack-approval-monitor',
      script: '.claude/skills/slack-manager/scripts/slack_approval_monitor.py',
      args: '--vault AI_Employee_Vault',
      interpreter: 'python',
      autorestart: true
    },

    // ===== SOCIAL MEDIA POSTERS (Live Mode) =====
    {
      name: 'linkedin-approval-monitor',
      script: '.claude/skills/linkedin-manager/scripts/linkedin_approval_monitor.py',
      args: '--vault AI_Employee_Vault',
      env: {
        LINKEDIN_DRY_RUN: 'false'  // LIVE MODE
      },
      interpreter: 'python',
      autorestart: true
    },
    {
      name: 'twitter-approval-monitor',
      script: '.claude/skills/twitter-manager/scripts/twitter_approval_monitor.py',
      args: '--vault AI_Employee_Vault',
      env: {
        TWITTER_DRY_RUN: 'false'  // LIVE MODE
      },
      interpreter: 'python',
      autorestart: true
    },
    {
      name: 'facebook-approval-monitor',
      script: '.claude/skills/facebook-instagram-manager/scripts/facebook_approval_monitor.py',
      args: '--vault AI_Employee_Vault',
      env: {
        FACEBOOK_DRY_RUN: 'false'  // LIVE MODE
      },
      interpreter: 'python',
      autorestart: true
    },
    {
      name: 'instagram-approval-monitor',
      script: '.claude/skills/facebook-instagram-manager/scripts/instagram_approval_monitor.py',
      args: '--vault AI_Employee_Vault',
      env: {
        INSTAGRAM_DRY_RUN: 'false'  // LIVE MODE
      },
      interpreter: 'python',
      autorestart: true
    },

    // ===== DASHBOARD (Single-Writer: Local Only) =====
    {
      name: 'ai-employee-dashboard',
      script: './dashboard/server.js',
      env: {
        PORT: '3000',
        NODE_ENV: 'production'
      },
      autorestart: true
    },

    // ===== GIT SYNC (Pull Drafts, Push Approvals) =====
    {
      name: 'git-sync-pull',
      script: 'scripts/git_sync_pull.sh',
      cron_restart: '*/5 * * * *',  // Every 5 minutes
      autorestart: false
    },

    // ===== DASHBOARD MERGER =====
    {
      name: 'dashboard-merger',
      script: 'scripts/dashboard_merger.py',
      args: '--vault AI_Employee_Vault',
      interpreter: 'python',
      cron_restart: '*/2 * * * *',  // Every 2 minutes
      autorestart: true
    }
  ]
};
```

### Phase 3: Git Sync Setup

#### Cloud: Git Push Script

```bash
#!/bin/bash
# scripts/git_sync_push.sh (Cloud)

cd /root/AI_EMPLOYEE_APP

# Add all changes
git add -A

# Commit with timestamp
git commit -m "Cloud update $(date -u +'%Y-%m-%d %H:%M:%S UTC')" || echo "No changes to commit"

# Push to remote
git push origin main
```

#### Local: Git Pull Script

```bash
#!/bin/bash
# scripts/git_sync_pull.sh (Local)

cd "C:\Users\User\Desktop\AI_EMPLOYEE_APP"

# Pull from remote
git pull origin main

# Merge strategy: Local wins for conflicts
# (User will manually resolve if needed)
```

### Phase 4: Claim-By-Move System

Update watchers to use `/In_Progress/` lock:

```python
# watchers/base_watcher.py

class BaseWatcher:
    def check_for_updates(self):
        items = self._get_items()

        for item in items:
            # Skip if already claimed by another agent
            in_progress = self.vault_path / 'In_Progress'
            claimed = list(in_progress.glob('**/*'))
            if any(item['id'] in c.name for c in claimed):
                continue

            # Claim this item
            my_progress = in_progress / self.agent_name
            my_progress.mkdir(parents=True, exist_ok=True)
            shutil.move(item['path'], my_progress / item['filename'])

            try:
                # Process item
                self._process_item(item)
            finally:
                # Release claim
                pass  # Move to appropriate folder
```

### Phase 5: Dashboard Merger (Local Only)

```python
# scripts/dashboard_merger.py

def merge_updates_to_dashboard():
    """
    Merge /Updates/ and /Signals/ into Dashboard.md (Local only).
    Cloud writes to /Updates/, Local merges to Dashboard.md.
    """
    vault_path = Path('AI_Employee_Vault')
    updates_dir = vault_path / 'Updates'
    dashboard = vault_path / 'Dashboard.md'

    # Read current dashboard
    current_content = dashboard.read_text()

    # Read all updates
    updates = []
    for update_file in updates_dir.glob('*.md'):
        updates.append(update_file.read_text())
        update_file.unlink()  # Consume update

    if updates:
        # Merge updates into dashboard
        new_section = '\n\n## Cloud Updates\n\n' + '\n'.join(updates)
        dashboard.write_text(current_content + new_section)
```

## Platinum Tier Demo Workflow

**Scenario:** Email arrives while Local is offline → Cloud drafts reply + writes approval file → when Local returns, user approves → Local executes send via MCP → logs → moves task to /Done.

1. **Email Arrives** (Cloud Online, Local Offline)
   ```
   Cloud: Gmail Watcher detects email
   → Creates /Needs_Action/EMAIL_20260119_123456_invoice.md
   ```

2. **Cloud AI Triage** (Cloud Online, Local Offline)
   ```
   Cloud: Auto-Approver analyzes email
   → Determines: Safe but needs approval
   → Creates draft reply in /Pending_Approval/EMAIL_20260119_123456_invoice.md
   → Subject: Invoice Payment - Draft Reply Ready
   ```

3. **Git Sync** (Every 5 minutes)
   ```
   Cloud: Git push (includes draft reply)
   Local: Offline (no pull)
   ```

4. **Local Returns** (Local Comes Online)
   ```
   Local: Git pull (receives draft reply)
   → User sees draft in /Pending_Approval/
   → User reviews draft
   → User moves to /Approved/
   ```

5. **Local Execution** (Local Approval)
   ```
   Local: Email Approval Monitor detects approval
   → Sends reply via Gmail MCP
   → Moves to /Done/
   → Logs action
   ```

6. **Git Sync** (Next cycle)
   ```
   Local: Git push (includes /Done/ status)
   Cloud: Git pull (sees completed task)
   ```

## Configuration Files

### Cloud Environment (.env.cloud)

```bash
# Cloud VM Environment Variables
# SECRETS NEVER SYNC TO LOCAL

# Anthropic API for AI Auto-Approver (Cloud uses for triage)
ANTHROPIC_API_KEY=sk-ant-xxx

# Gmail Credentials (READ-ONLY for Cloud)
GMAIL_CREDENTIALS=mcp-servers/email-mcp/credentials.json

# Git Configuration
GIT_REPO_URL=https://github.com/HamdanProfessional/Hackathon0.git
GIT_BRANCH=main

# Timezone
TZ=UTC
```

### Local Environment (.env.local)

```bash
# Local Machine Environment Variables
# SECRETS NEVER SYNC TO CLOUD

# Gmail Credentials (READ-WRITE for Local - can send)
GMAIL_CREDENTIALS=mcp-servers/email-mcp/credentials.json

# Slack Bot Token (for sending)
SLACK_BOT_TOKEN=xoxb-xxx

# WhatsApp Session (Local only)
WHATSAPP_SESSION=whatsapp_session

# Social Media DRY_RUN (all false for live posting)
LINKEDIN_DRY_RUN=false
TWITTER_DRY_RUN=false
FACEBOOK_DRY_RUN=false
INSTAGRAM_DRY_RUN=false

# Payment/Banking (Local only)
STRIPE_API_KEY=sk_live_xxx
BANK_API_KEY=xxx
```

## Verification Checklist

- [ ] Cloud VM running with PM2 processes
- [ ] Cloud watchers: Gmail, Calendar, Slack, Odoo (detection only)
- [ ] Cloud auto-approver running (draft-only mode)
- [ ] Cloud Git push every 5 minutes
- [ ] Local PM2 processes running
- [ ] Local watchers: WhatsApp, Filesystem
- [ ] Local approval monitors: Email, Calendar, Slack, LinkedIn, Twitter, Facebook, Instagram
- [ ] Local Git pull every 5 minutes
- [ ] Dashboard merger running (Local only)
- [ ] Claim-by-move system active
- [ ] Test: Email arrives while Local offline → Cloud drafts → Local approves → Local sends

## Next Steps

1. ✅ Create this implementation guide
2. ⏳ Update PM2 configs (cloud vs local)
3. ⏳ Create Git sync scripts
4. ⏳ Implement claim-by-move system
5. ⏳ Create dashboard merger
6. ⏳ Test demo workflow
7. ⏳ Deploy and verify
