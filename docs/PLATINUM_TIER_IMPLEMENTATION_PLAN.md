# Platinum Tier Implementation Plan
## AI Employee v1.4.1 - Cloud + Local Executive Architecture

**Status:** Complete Implementation Blueprint
**Created:** 2025-01-19
**Target:** Oracle Cloud Free Tier (AMP) + Local Windows Machine

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Infrastructure Setup](#2-infrastructure-setup)
3. [Cloud VM Configuration](#3-cloud-vm-configuration)
4. [Local Machine Configuration](#4-local-machine-configuration)
5. [Vault Synchronization](#5-vault-synchronization)
6. [Work-Zone Specialization](#6-work-zone-specialization)
7. [Security & Secrets Management](#7-security--secrets-management)
8. [Odoo Cloud Deployment](#8-odoo-cloud-deployment)
9. [Health Monitoring](#9-health-monitoring)
10. [Demo Scenarios](#10-demo-scenarios)
11. [Verification Checklist](#11-verification-checklist)

---

## 1. Architecture Overview

### 1.1 System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD VM (Oracle Free Tier)                 │
│                    ──────────────────────────────                │
│  ✅ RUNS 24/7                                                      │
│  ✅ Public IP                                                      │
│  ✅ No secrets stored                                             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Git Push/Pull (markdown only)
                            │
┌─────────────────────────────────────────────────────────────────┐
│               SHARED OBSIDIAN VAULT (Git Repository)            │
│                    ─────────────────────────────                │
│  ✅ Markdown files only                                            │
│  ✅ State files                                                   │
│  ❌ NEVER: .env, tokens, sessions, credentials                    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Git Push/Pull (markdown only)
                            │
┌─────────────────────────────────────────────────────────────────┐
│                   LOCAL MACHINE (Your PC)                      │
│                    ─────────────────────────────                │
│  ✅ Runs on-demand                                               │
│  ✅ Stores ALL secrets                                           │
│  ✅ Final approval & execution                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Work-Zone Responsibilities

| Operation | Cloud VM | Local Machine | Why? |
|-----------|----------|---------------|-----|
| **Gmail Watcher** | ✅ Runs 24/7 | ❌ | Detect emails anytime |
| **Calendar Watcher** | ✅ Runs 24/7 | ❌ | Monitor events anytime |
| **Slack Watcher** | ✅ Runs 24/7 | ❌ | Watch messages anytime |
| **Email Drafting** | ✅ Creates drafts | ❌ | Prepare responses |
| **Social Media Drafting** | ✅ Creates drafts | ❌ | Prepare posts |
| **Odoo Integration** | ✅ Draft invoices | ❌ | Cloud has Odoo access |
| **Approval Monitor** | ❌ | ✅ | Human approval local |
| **Email Send** | ❌ | ✅ | Final send local |
| **Social Media Post** | ❌ | ✅ | Final post local (via CDP) |
| **WhatsApp** | ❌ | ✅ | Session lives locally |
| **Payments** | ❌ | ✅ | Banking creds local |
| **Chrome CDP** | ❌ | ✅ | Browser automation local |

### 1.3 File Flow: Email Example

```
CLOUD: Email arrives → Gmail Watcher detects
       → Creates EMAIL_*.md in Needs_Action/Email/
       → AI Auto-Approver analyzes
       → Moves to Pending_Approval/Email/
       → Generates draft reply in file

VOLUME SYNC: Git push → Local pulls

LOCAL: Human reviews draft
      → Moves to Approved/Email/
      → Email Approval Monitor detects
      → Sends via Gmail MCP (Local API tokens)
      → Moves to Done/
      → Git push → Cloud pulls
```

### 1.4 Claim-by-Move Rule

To prevent double-work between Cloud and Local agents:

```
1. Cloud agent finds task in /Needs_Action/Email/
2. Cloud agent creates /In_Progress/cloud-agent/TASK_*.md
3. Other agents see /In_Progress/cloud-agent/ and ignore
4. When complete, move to /Pending_Approval/ or /Done/
```

---

## 2. Infrastructure Setup

### 2.1 Cloud VM Options

The Platinum Tier requires **any cloud VM** that runs 24/7. Options include:

#### Oracle Cloud Free Tier ⭐ **Recommended for Hackathon**
- **Cost:** FREE (truly free, no credit card required in some regions)
- **Specs:** 2 AMD CPUs, 1 GB RAM, 10 GB boot, 50 GB block storage
- **OR:** Ampere A1: 4 ARM CPUs, 24 GB RAM
- **Public IP:** Included
- **Link:** https://www.oracle.com/cloud/free/

#### AWS Free Tier
- **Cost:** FREE for 12 months, then ~$8-15/month
- **Specs:** EC2 t2.micro (1 vCPU, 1 GB RAM)
- **Public IP:** ~$3.50/month extra
- **Link:** https://aws.amazon.com/free/

#### Google Cloud Free Tier
- **Cost:** $300 credit for 12 months, then ~$4-6/month
- **Specs:** e2-micro (2 vCPU, 1 GB RAM)
- **Link:** https://cloud.google.com/free

#### Azure Free Tier
- **Cost:** $200 credit for 12 months, then ~$6-10/month
- **Specs:** B1s burstable (1 vCPU, 1 GB RAM)
- **Link:** https://azure.microsoft.com/free/

#### DigitalOcean (Not Free)
- **Cost:** $6/month
- **Specs:** 1 vCPU, 512 MB RAM, 10 GB SSD
- **Link:** https://www.digitalocean.com/

#### Linode (Not Free)
- **Cost:** $5/month
- **Specs:** 1 vCPU, 1 GB RAM, 25 GB SSD
- **Link:** https://www.linode.com/

---

**Why Oracle Cloud Free Tier for Hackathon?**
- ✅ **Truly FREE** (can keep running after hackathon)
- ✅ Meets all Platinum requirements
- ✅ No ongoing cost commitment
- ✅ Judges won't deduct points for "expensive solution"

**Setup Steps:**

```bash
# 1. Create Oracle Cloud Account
# Go to: https://www.oracle.com/cloud/free/
# Create account (requires credit card for verification, but no charges)

# 2. Create AMP Instance
# Console → Compute → Instances → Create Instance
# - Name: ai-employee-cloud
# - Shape: VM.Standard.E2.1.Micro (Always Free)
# - Image: Oracle Linux 9 or Ubuntu 22.04
# - SSH Key: Upload your public key
# - Network: Create with public IP

# 3. Connect to VM
ssh -i ~/.ssh/your_key ubuntu@<public-ip>

# 4. Initial Setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3.13 python3.13-venv python3-pip nodejs npm

# 5. Clone Repository
git clone https://github.com/YOUR_USERNAME/AI_EMPLOYEE_APP.git
cd AI_EMPLOYEE_APP

# 6. Install Python Dependencies
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 7. Install PM2
npm install -g pm2

# 8. Create cloud-specific config
cp process-manager/pm2.cloud.config.js ecosystem.config.js
```

### 2.2 Local Machine: Your Development PC

**Requirements:**
- Windows 10/11 or macOS/Linux
- Python 3.13+
- Node.js 24+
- Git
- Chrome browser (for CDP)
- Obsidian (optional, for viewing vault)

**Setup Steps:**

```bash
# Already done if you're reading this!

# Verify installation
python --version  # Should be 3.13+
node --version     # Should be v24+
pm2 list           # Should show processes running

# Clone/set up repo (if not already)
git clone https://github.com/YOUR_USERNAME/AI_EMPLOYEE_APP.git
cd AI_EMPLOYEE_APP
```

---

## 3. Cloud VM Configuration

### 3.1 Cloud PM2 Configuration

Create `process-manager/ecosystem.config.js` for cloud:

```javascript
/**
 * CLOUD VM PM2 Configuration
 *
 * RUNS ON CLOUD VM ONLY
 * - Watchers: Gmail, Calendar, Slack, Odoo, Filesystem
 * - Auto-Approver: AI triage (Claude 3 Haiku)
 * - Daily tasks: Briefing, Review
 *
 * NEVER RUNS ON CLOUD:
 * - Approval monitors (human approval is local)
 * - WhatsApp (session lives locally)
 * - Social media posters (CDP is local)
 * - Payment processing (banking creds local)
 */

const path = require('path');

// Project root directory - dynamically resolved
const PROJECT_ROOT = process.cwd();
const VAULT_PATH = path.join(PROJECT_ROOT, 'AI_Employee_Vault');

module.exports = {
  apps: [
    // ==================== WATCHERS (Cloud Only) ====================

    {
      name: "gmail-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/email-manager/scripts", "run_gmail_watcher.py"),
      args: "--vault " + VAULT_PATH + " --credentials " + path.join(PROJECT_ROOT, "mcp-servers", "email-mcp", "credentials.json"),
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": PROJECT_ROOT
      }
    },

    {
      name: "calendar-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/calendar-manager/scripts", "run_calendar_watcher.py"),
      args: "--vault " + VAULT_PATH + " --credentials " + path.join(PROJECT_ROOT, "mcp-servers", "calendar-mcp", "credentials.json"),
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "slack-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/slack-manager/scripts", "run_slack_watcher.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "SLACK_BOT_TOKEN": process.env.SLACK_BOT_TOKEN || ""
      }
    },

    {
      name: "odoo-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/odoo-manager/scripts", "run_odoo_watcher.py"),
      args: "--vault " + VAULT_PATH + " --interval 300",
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "ODOO_URL": process.env.ODOO_URL || "http://localhost:8069",
        "ODOO_DB": process.env.ODOO_DB || "odoo",
        "ODOO_USERNAME": process.env.ODOO_USERNAME || "admin",
        "ODOO_PASSWORD": process.env.ODOO_PASSWORD || "admin"
      }
    },

    {
      name: "filesystem-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/filesystem-manager/scripts", "run_filesystem_watcher.py"),
      args: "--vault " + VAULT_PATH + " --watch-folder Inbox",
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "200M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    // ==================== AUTO-APPROVER (Cloud Only) ====================

    {
      name: "auto-approver",
      script: path.join(PROJECT_ROOT, ".claude/skills/approval-manager/scripts", "auto_approver.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "ANTHROPIC_API_KEY": process.env.ANTHROPIC_API_KEY || ""
      }
    },

    // ==================== CRON JOBS (Cloud Only) ====================

    {
      name: "daily-review",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "daily-review", "scripts", "generate_daily_plan.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 6 * * 1-5",  // 6 AM weekdays (Cloud time)
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "social-media-scheduler",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "social-media-manager", "scripts", "generate_linkedin_ai.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 8 * * 1,3,5",  // 8 AM Mon/Wed/Fri (Cloud time)
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "audit-log-cleanup",
      script: path.join(PROJECT_ROOT, "scripts", "cleanup_old_logs.py"),
      args: "--vault " + VAULT_PATH + " --days 90",
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 3 * * 0",  // 3 AM Sundays (Cloud time)
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    // ==================== HEALTH MONITOR (Cloud Only) ====================

    {
      name: "cloud-health-monitor",
      script: path.join(PROJECT_ROOT, "scripts", "cloud_health_monitor.py"),
      interpreter: "python3",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "200M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "CHECK_INTERVAL": "300"  // Check every 5 minutes
      }
    },

    // ==================== GITHUB SYNC (Cloud Auto-Push) ====================

    {
      name: "git-auto-push",
      script: path.join(PROJECT_ROOT, "scripts", "git_sync_push.sh"),
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "*/5 * * * *",  // Every 5 minutes
      env: {
        "GIT_SSH_COMMAND": "ssh -i ~/.ssh/id_rsa"
      }
    }
  ]
};
```

### 3.2 Cloud Environment Variables

Create `/home/ubuntu/AI_EMPLOYEE_APP/.env.cloud` (NEVER COMMIT):

```bash
# AI Employee Cloud Environment Variables

# Anthropic API for Auto-Approver (Claude 3 Haiku)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxx

# Slack Bot Token (for Slack Watcher)
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxxxxxx

# Odoo Credentials (Cloud-hosted Odoo)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=admin
ODOO_PASSWORD=CHANGE_THIS_PASSWORD

# Git Configuration
GIT_REPO_URL=git@github.com:YOUR_USERNAME/AI_EMPLOYEE_APP.git
GIT_BRANCH=main

# Timezone
TZ=UTC
```

### 3.3 Cloud Startup Script

Create `scripts/cloud_startup.sh`:

```bash
#!/bin/bash
# Cloud VM Startup Script
# Runs on VM boot via cron or systemd

set -e

echo "[AI Employee Cloud] Starting up..."

cd /home/ubuntu/AI_EMPLOYEE_APP

# Pull latest vault changes
echo "[AI Employee Cloud] Pulling latest vault..."
git pull origin main

# Start PM2 processes
echo "[AI Employee Cloud] Starting PM2..."
pm2 resurrect
pm2 save

echo "[AI Employee Cloud] Startup complete!"
pm2 list
```

### 3.4 Cloud Git Setup

```bash
# On Cloud VM

# Generate SSH key for GitHub
ssh-keygen -t rsa -b 4096 -C "ai-employee-cloud" -f ~/.ssh/id_rsa -N ""

# Display public key (add to GitHub SSH keys)
cat ~/.ssh/id_rsa.pub

# Configure Git
git config --global user.email "ai-employee@cloud-vm"
git config --global user.name "AI Employee Cloud"

# Test SSH connection to GitHub
ssh -T git@github.com
```

---

## 4. Local Machine Configuration

### 4.1 Local PM2 Configuration

Update `process-manager/pm2.local.config.js` for local-only operations:

```javascript
/**
 * LOCAL MACHINE PM2 Configuration
 *
 * RUNS ON LOCAL MACHINE ONLY
 * - Approval monitors: Email, Calendar, Slack, LinkedIn, Twitter, Facebook, Instagram
 * - WhatsApp Watcher (session lives locally)
 * - Dashboard (single writer rule)
 *
 * NEVER RUNS LOCALLY (to avoid conflicts):
 * - Gmail, Calendar, Slack, Odoo, Filesystem Watchers (Cloud handles these)
 * - Auto-Approver (Cloud handles this)
 * - Daily tasks (Cloud handles these)
 */

const path = require('path');

const PROJECT_ROOT = process.cwd();
const VAULT_PATH = path.join(PROJECT_ROOT, 'AI_Employee_Vault');

module.exports = {
  apps: [
    // ==================== LOCAL-ONLY WATCHERS ====================

    {
      name: 'whatsapp-watcher',
      script: 'python',
      interpreter: 'none',
      args: '-m watchers.whatsapp_watcher_playwright --vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1',
        "PYTHONPATH": PROJECT_ROOT
      },
      error_file: './logs/whatsapp-watcher-error.log',
      out_file: './logs/whatsapp-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ==================== LOCAL APPROVAL MONITORS ====================

    {
      name: 'email-approval-monitor',
      script: path.join(PROJECT_ROOT, ".claude", "skills", "email-manager", "scripts", "email_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "EMAIL_DRY_RUN": "false",  // LIVE MODE on local
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": PROJECT_ROOT
      },
      error_file: './logs/email-approval-monitor-error.log',
      out_file: './logs/email-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'calendar-approval-monitor',
      script: path.join(PROJECT_ROOT, ".claude", "skills", "calendar-manager", "scripts", "calendar_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1"
      },
      error_file: './logs/calendar-approval-monitor-error.log',
      out_file: './logs/calendar-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'slack-approval-monitor',
      script: path.join(PROJECT_ROOT, ".claude", "skills", "slack-manager", "scripts", "slack_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "SLACK_BOT_TOKEN": process.env.SLACK_BOT_TOKEN || ""
      },
      error_file: './logs/slack-approval-monitor-error.log',
      out_file: './logs/slack-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ==================== SOCIAL MEDIA APPROVAL MONITORS (LIVE MODE) ====================

    {
      name: 'linkedin-approval-monitor',
      script: './.claude/skills/linkedin-manager/scripts/linkedin_approval_monitor.py',
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        LINKEDIN_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/linkedin-approval-monitor-error.log',
      out_file: './logs/linkedin-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'twitter-approval-monitor',
      script: './.claude/skills/twitter-manager/scripts/twitter_approval_monitor.py',
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        TWITTER_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/twitter-approval-monitor-error.log',
      out_file: './logs/twitter-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'facebook-approval-monitor',
      script: './.claude/skills/facebook-instagram-manager/scripts/facebook-approval-monitor.py',
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        FACEBOOK_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/facebook-approval-monitor-error.log',
      out_file: './logs/facebook-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'instagram-approval-monitor',
      script: './.claude/skills/facebook-instagram-manager/scripts/instagram-approval-monitor.py',
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        INSTAGRAM_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/instagram-approval-monitor-error.log',
      out_file: './logs/instagram-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ==================== LOCAL DASHBOARD (Single Writer Rule) ====================

    {
      name: 'ai-employee-dashboard',
      script: './dashboard/server.js',
      interpreter: 'node',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PORT: '3000',
        NODE_ENV: 'production'
      },
      error_file: './logs/dashboard-error.log',
      out_file: './logs/dashboard-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ==================== GIT SYNC (Local Auto-Pull) ====================

    {
      name: 'git-auto-pull',
      script: path.join(PROJECT_ROOT, "scripts", "git_sync_pull.sh"),
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "*/5 * * * *",  // Every 5 minutes
      env: {
        "GIT_SSH_COMMAND": "ssh -i ~/.ssh/id_rsa"
      }
    }
  ]
};
```

### 4.2 Local Environment Variables

Update `.env` (LOCAL ONLY - NEVER COMMIT):

```bash
# AI Employee Local Environment Variables

# === LOCAL SECRETS (NEVER SYNC TO CLOUD) ===

# Gmail API Credentials (Local tokens for sending)
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# Calendar API Credentials (Local tokens)
CALENDAR_CLIENT_ID=your_client_id.apps.googleusercontent.com
CALENDAR_CLIENT_SECRET=your_client_secret
CALENDAR_REFRESH_TOKEN=your_refresh_token

# Slack Bot Token
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxxxxxx

# Social Media (NOT stored on cloud)
LINKEDIN_DRY_RUN=false
TWITTER_DRY_RUN=false
FACEBOOK_DRY_RUN=false
INSTAGRAM_DRY_RUN=false

# Banking Credentials (NEVER sync)
BANK_API_TOKEN=your_bank_token
PAYMENT_API_KEY=your_payment_key

# === SECRETS THAT ARE SAFE TO SHARE ===

# Anthropic API (same on cloud and local)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxx

# === LOCAL SETTINGS ===

# Git Configuration
GIT_REPO_URL=git@github.com:YOUR_USERNAME/AI_EMPLOYEE_APP.git
GIT_BRANCH=main
```

---

## 5. Vault Synchronization

### 5.1 Git Repository Structure

```
AI_EMPLOYEE_APP/                    # Git Root
├── .git/                           # Git repository
├── .gitignore                      # Excludes secrets!
├── AI_Employee_Vault/              # SHARED via Git
│   ├── Dashboard.md
│   ├── Needs_Action/               # Domain-specific folders
│   │   ├── Email/
│   │   ├── Calendar/
│   │   ├── Slack/
│   │   ├── Social_Media/
│   │   └── Odoo/
│   ├── Pending_Approval/           # Domain-specific folders
│   │   ├── Email/
│   │   ├── Calendar/
│   │   ├── Slack/
│   │   ├── Social_Media/
│   │   └── Odoo/
│   ├── Approved/                   # Domain-specific folders
│   │   ├── Email/
│   │   ├── Calendar/
│   │   ├── Slack/
│   │   ├── Social_Media/
│   │   └── Odoo/
│   ├── Rejected/                   # Domain-specific folders
│   ├── Done/                       # All completed tasks
│   ├── Plans/                      # Execution plans
│   ├── Briefings/                  # CEO briefings
│   ├── Logs/                       # Audit logs (json)
│   ├── Accounting/                 # Financial data
│   ├── Updates/                    # Cloud signals for Local
│   ├── In_Progress/                # Claim-by-move rule
│   │   ├── cloud-agent/
│   │   └── local-agent/
│   └── *.md                        # All markdown files
├── .env                            # EXCLUDED (local secrets)
├── .env.cloud                      # EXCLUDED (cloud secrets)
├── *_token.json                    # EXCLUDED (OAuth tokens)
├── *_credentials.json              # EXCLUDED (API creds)
├── whatsapp_session/               # EXCLUDED (WhatsApp session)
└── .claude/config.json             # EXCLUDED (Claude config)
```

### 5.2 .gitignore Configuration

Ensure `.gitignore` properly excludes ALL secrets:

```gitignore
# === SENSITIVE CREDENTIALS - NEVER COMMIT ===
.env
.env.local
.env.cloud
.env.*.local

# OAuth Tokens
*_token.json
token_*.json
.gmail_token.json
.calendar_token.json
.xero_token.json
.xero_credentials.json
.slack_token.json

# API Credentials
credentials.json
client_secret.json
client_secret*.json
mcp_tokens.json

# Browser Sessions
whatsapp_session/
chrome_debug/
ChromeDebug/
*.crsession
*.session

# Watcher State Files
.*_state.json
.whatsapp_state.json
.gmail_state.json
.calendar_state.json
.slack_state.json
.filesystem_state.json
.xero_state.json
.odoo_watcher_state.json

# === LOG FILES ===
Logs/
*.log
logs/
pm2_*.log

# === PYTHON CACHE ===
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# === NODE MODULES ===
node_modules/
package-lock.json

# === VENDOR ===
vendor/
.venv/
venv/
ENV/

# === OS FILES ===
.DS_Store
Thumbs.db
Desktop.ini

# === TEMPORARY FILES ===
*.tmp
*.temp
*.cache
*.bak
*.swp
*~

# === TEST FILES ===
test_*.py
*_test.py
*_test.md
```

### 5.3 Cloud Git Sync Scripts

#### Auto-Push Script (Cloud)

Create `scripts/git_sync_push.sh`:

```bash
#!/bin/bash
# Cloud Git Auto-Push Script
# Pushes vault changes to GitHub every 5 minutes

set -e

REPO_DIR="/home/ubuntu/AI_EMPLOYEE_APP"
cd "$REPO_DIR"

echo "[Git Sync] Checking for changes..."

# Check if there are changes to push
if git diff --quiet && git diff --cached --quiet; then
    echo "[Git Sync] No changes to push"
    exit 0
fi

# Add only markdown and state files (exclude secrets)
git add AI_Employee_Vault/ || true
git add ./*.md || true

# Commit changes
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
git commit -m "Cloud update: $TIMESTAMP" || true

# Push to GitHub
git push origin main

echo "[Git Sync] Changes pushed successfully"
```

Make it executable:

```bash
chmod +x scripts/git_sync_push.sh
```

#### Auto-Pull Script (Local)

Create `scripts/git_sync_pull.sh`:

```bash
#!/bin/bash
# Local Git Auto-Pull Script
# Pulls vault changes from GitHub every 5 minutes

set -e

REPO_DIR="C:/Users/User/Desktop/AI_EMPLOYEE_APP"
cd "$REPO_DIR"

echo "[Git Sync] Pulling changes from GitHub..."

# Pull changes
git pull origin main

echo "[Git Sync] Changes pulled successfully"
```

On Windows, create `scripts/git_sync_pull.bat`:

```batch
@echo off
REM Local Git Auto-Pull Script (Windows)

cd /d C:\Users\User\Desktop\AI_EMPLOYEE_APP

echo [Git Sync] Pulling changes from GitHub...

git pull origin main

echo [Git Sync] Changes pulled successfully
```

---

## 6. Work-Zone Specialization

### 6.1 Domain-Specific Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── Email/              # Cloud writes here (email detected)
│   ├── Calendar/           # Cloud writes here (event detected)
│   ├── Slack/              # Cloud writes here (message detected)
│   ├── Social_Media/       # Cloud writes here (scheduled post due)
│   └── Odoo/               # Cloud writes here (invoice created)
│
├── In_Progress/
│   ├── cloud-agent/        # Cloud claims tasks here
│   │   ├── EMAIL_*.md
│   │   ├── CALENDAR_*.md
│   │   └── PLAN_*.md
│   └── local-agent/        # Local claims tasks here
│       ├── SOCIAL_POST_*.md
│       └── PAYMENT_*.md
│
├── Pending_Approval/
│   ├── Email/              # Cloud moves drafts here
│   ├── Calendar/           # Cloud moves drafts here
│   ├── Slack/              # Cloud moves drafts here
│   ├── Social_Media/       # Cloud moves drafts here
│   └── Odoo/               # Cloud moves draft invoices here
│
├── Approved/
│   ├── Email/              # Local moves approved emails here
│   ├── Calendar/           # Local moves approved events here
│   ├── Slack/              # Local moves approved messages here
│   ├── Social_Media/       # Local moves approved posts here
│   └── Odoo/               # Local moves approved invoices here
│
├── Rejected/
│   ├── Email/
│   ├── Calendar/
│   ├── Slack/
│   ├── Social_Media/
│   └── Odoo/
│
├── Done/                    # All agents move completed tasks here
│
├── Updates/                 # Cloud writes signals for Local
│   └── signals/            # "New email drafted", "Odoo invoice ready"
│
└── Dashboard.md            # Single writer: Local only
```

### 6.2 Cloud Agent Workflow

```
CLOUD: Gmail Watcher detects new email
       ↓
       Creates: Needs_Action/Email/EMAIL_*.md
       ↓
       Creates: In_Progress/cloud-agent/EMAIL_*.md (claim)
       ↓
       AI Auto-Approver analyzes
       ↓
       If safe → Moves to Approved/Email/
       If needs review → Moves to Pending_Approval/Email/
       ↓
       If needs draft → Generates draft reply in file
       ↓
       Moves to Done/ or Pending_Approval/
       ↓
       Git push → GitHub
```

### 6.3 Local Agent Workflow

```
LOCAL: Git pull from GitHub
       ↓
       Human reviews: Pending_Approval/Email/EMAIL_*.md
       ↓
       Human approves → Moves to Approved/Email/
       ↓
       Email Approval Monitor detects
       ↓
       Sends via Gmail MCP (Local API tokens)
       ↓
       Moves to Done/Email/
       ↓
       Git push → GitHub
```

---

## 7. Security & Secrets Management

### 7.1 Secrets Distribution Matrix

| Secret | Cloud VM | Local Machine | Sync via Git |
|--------|----------|---------------|-------------|
| `.env` | ❌ | ✅ | ❌ |
| `.env.cloud` | ✅ | ❌ | ❌ |
| `*_token.json` | ❌ | ✅ | ❌ |
| `whatsapp_session/` | ❌ | ✅ | ❌ |
| `AI_Employee_Vault/*.md` | ✅ | ✅ | ✅ |
| `AI_Employee_Vault/Logs/*.json` | ✅ | ✅ | ✅ |
| `.*_state.json` | ✅ | ✅ | ✅ |

### 7.2 Secure Cloud Setup

```bash
# ON CLOUD VM

# 1. Create .env.cloud file
cat > .env.cloud << 'EOF'
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxx
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=admin
ODOO_PASSWORD=$(openssl rand -base64 16)
EOF

# 2. Set permissions
chmod 600 .env.cloud

# 3. Source in PM2 config
echo "source .env.cloud" >> ~/.bashrc
```

### 7.3 Secure Local Setup

```bash
# ON LOCAL MACHINE

# 1. Keep .env local (already in .gitignore)
# Already done!

# 2. Ensure tokens are in correct location
ls -la *_token.json
ls -la whatsapp_session/

# 3. Test local approval monitors
pm2 start process-manager/pm2.local.config.js
pm2 logs email-approval-monitor
```

### 7.4 Security Rules

**RULE #1: Cloud NEVER has secrets**
- No OAuth tokens stored on cloud
- No banking credentials on cloud
- No WhatsApp session on cloud
- No payment API keys on cloud

**RULE #2: Local has ALL secrets**
- OAuth tokens for email/calendar
- Slack bot token
- Banking credentials
- Payment API keys
- WhatsApp session

**RULE #3: Git sync excludes secrets**
- `.gitignore` must be comprehensive
- Verify with `git status` before committing
- Never commit secrets accidentally

**RULE #4: Human approval for sensitive actions**
- All payments require approval
- All social media posts require approval
- All emails to new contacts require approval
- Cloud drafts, Local approves

---

## 8. Odoo Cloud Deployment

### 8.1 Odoo Docker Setup (Cloud)

Create `docker/odoo/docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: ai-employee-db
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${ODOO_DB_PASSWORD:-changeme}
      POSTGRES_DB: postgres
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - odoo-network
    restart: unless-stopped

  odoo:
    image: odoo:19
    container_name: ai-employee-odoo
    depends_on:
      - db
    ports:
      - "127.0.0.1:8069:8069"  # Bind to localhost only
    environment:
      HOST: db
      USER: odoo
      PASSWORD: ${ODOO_DB_PASSWORD:-changeme}
    volumes:
      - odoo-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    networks:
      - odoo-network
    restart: unless-stopped

volumes:
  db-data:
  odoo-data:

networks:
  odoo-network:
    driver: bridge
```

### 8.2 Odoo Setup Script (Cloud)

Create `scripts/setup_odoo_cloud.sh`:

```bash
#!/bin/bash
# Odoo Cloud Setup Script

set -e

echo "[Odoo Setup] Installing Docker..."

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "[Odoo Setup] Starting Odoo containers..."

cd /home/ubuntu/AI_EMPLOYEE_APP/docker/odoo

# Generate secure password
ODOO_PASSWORD=$(openssl rand -base64 16)

# Create .env file
cat > .env << EOF
ODOO_DB_PASSWORD=$ODOO_PASSWORD
EOF

# Start containers
docker-compose up -d

echo "[Odoo Setup] Waiting for Odoo to start..."
sleep 30

# Check if Odoo is running
if curl -f http://localhost:8069; then
    echo "[Odoo Setup] Odoo is running at http://localhost:8069"
    echo "[Odoo Setup] Database password: $ODOO_PASSWORD"
    echo "[Odoo Setup] Save this to .env.cloud!"
else
    echo "[Odoo Setup] ERROR: Odoo failed to start"
    exit 1
fi
```

### 8.3 Odoo Backup Script (Cloud)

Create `scripts/backup_odoo.sh`:

```bash
#!/bin/bash
# Odoo Backup Script (Daily cron)

BACKUP_DIR="/home/ubuntu/AI_EMPLOYEE_APP/backups/odoo"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "[Odoo Backup] Starting backup..."

# Backup PostgreSQL
docker exec ai-employee-db pg_dump -U odoo postgres > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Backup Odoo data
docker exec ai-employee-odoo pg_dump -U odoo -d postgres > "$BACKUP_DIR/odoo_backup_$TIMESTAMP.sql"

# Compress
gzip "$BACKUP_DIR"/*.sql

echo "[Odoo Backup] Backup complete: $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
```

---

## 9. Health Monitoring

### 9.1 Cloud Health Monitor

Create `scripts/cloud_health_monitor.py`:

```python
#!/usr/bin/env python3
"""
Cloud Health Monitor
Monitors all PM2 processes and reports status to Updates/signals/
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def check_pm2_status():
    """Check PM2 process status."""
    try:
        result = subprocess.run(
            ['pm2', 'jlist'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"[ERROR] Failed to check PM2 status: {e}")
        return []

def write_health_status(status_data):
    """Write health status to vault."""
    vault_path = Path("AI_Employee_Vault")
    updates_dir = vault_path / "Updates" / "signals"
    updates_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    status_file = updates_dir / f"cloud_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    status_data['timestamp'] = timestamp
    status_data['hostname'] = os.uname().nodename

    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)

    print(f"[Health Monitor] Status written to {status_file}")

def main():
    print("[Health Monitor] Checking cloud health...")

    processes = check_pm2_status()

    online_count = sum(1 for p in processes if p.get('pm2_env', {}).get('status') == 'online')
    total_count = len(processes)

    status_data = {
        'total_processes': total_count,
        'online_processes': online_count,
        'offline_processes': total_count - online_count,
        'processes': []
    }

    for p in processes:
        name = p.get('name', 'unknown')
        status = p.get('pm2_env', {}).get('status', 'unknown')
        cpu = p.get('monit', {}).get('cpu', 0)
        memory = p.get('monit', {}).get('memory', 0)

        status_data['processes'].append({
            'name': name,
            'status': status,
            'cpu': cpu,
            'memory': memory
        })

        if status != 'online':
            print(f"[WARNING] Process {name} is {status}")

    print(f"[Health Monitor] {online_count}/{total_count} processes online")

    write_health_status(status_data)

if __name__ == "__main__":
    main()
```

### 9.2 Local Health Dashboard

Create `scripts/local_health_check.sh`:

```bash
#!/bin/bash
# Local Health Check Script

echo "=== AI Employee Local Health Check ==="

# Check PM2 processes
echo ""
echo "PM2 Processes:"
pm2 list

# Check Git sync status
echo ""
echo "Git Status:"
cd C:/Users/User/Desktop/AI_EMPLOYEE_APP
git status --short | head -10

# Check Chrome CDP
echo ""
echo "Chrome CDP:"
curl -s http://localhost:9222/json/version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Chrome CDP is running"
else
    echo "❌ Chrome CDP is NOT running (start with start_chrome.bat)"
fi

# Check Vault
echo ""
echo "Vault Folders:"
ls AI_Employee_Vault/ | head -20
```

---

## 10. Demo Scenarios

### 10.1 Platinum Demo Gate (Minimum Passing)

**Scenario:** Email arrives while Local is offline → Cloud drafts reply → Local approves → Local sends

```
STEP 1: CLOUD (Local is offline)
├─ Gmail Watcher detects new email
├─ Creates: Needs_Action/Email/EMAIL_client_invoice_*.md
├─ Moves to: In_Progress/cloud-agent/EMAIL_client_invoice_*.md (claim)
├─ AI Auto-Approver analyzes
├─ Generates draft reply in file
├─ Moves to: Pending_Approval/Email/EMAIL_client_invoice_*.md
└─ Git push → GitHub

STEP 2: LOCAL (User returns)
├─ Git pull from GitHub
├─ User reviews: Pending_Approval/Email/EMAIL_client_invoice_*.md
├─ User approves → Moves to: Approved/Email/EMAIL_client_invoice_*.md
├─ Email Approval Monitor detects
├─ Sends via Gmail MCP (Local tokens)
└─ Moves to: Done/Email/EMAIL_client_invoice_*.md

STEP 3: SYNC
└─ Git push → GitHub → Cloud pulls
```

### 10.2 Demo Video Script

Record a 5-10 minute demo video showing:

1. **Introduction (1 min)**
   - Explain Platinum Tier architecture
   - Show Cloud VM console
   - Show Local machine

2. **Cloud Operations (2 min)**
   - Show PM2 processes on cloud
   - Show Gmail Watcher detecting email
   - Show AI Auto-Approver working
   - Show Git push to GitHub

3. **Local Operations (2 min)**
   - Show Git pull from GitHub
   - Show pending approval files
   - Show user approving email
   - Show Email Approval Monitor sending
   - Show Chrome CDP browser automation (for social media)

4. **Social Media Demo (2 min)**
   - Cloud generates LinkedIn post draft
   - Git sync to local
   - User approves
   - Local posts via LinkedIn MCP
   - Show result in browser

5. **Odoo Demo (1 min)**
   - Cloud creates draft invoice in Odoo
   - Show Odoo web interface
   - Local approves invoice
   - Show result

6. **Conclusion (1 min)**
   - Summary of Platinum Tier features
   - Cost savings analysis
   - Next steps

---

## 11. Verification Checklist

### 11.1 Pre-Deployment Checklist

- [ ] **Cloud VM Setup**
  - [ ] Oracle Cloud account created
  - [ ] AMP instance provisioned
  - [ ] SSH key configured
  - [ ] Can connect via SSH
  - [ ] Python 3.13 installed
  - [ ] Node.js 24 installed
  - [ ] PM2 installed globally
  - [ ] Repository cloned

- [ ] **Local Machine Setup**
  - [ ] Python 3.13 installed
  - [ ] Node.js 24 installed
  - [ ] PM2 installed locally
  - [ ] Git configured
  - [ ] Chrome browser installed
  - [ ] All MCP servers installed

- [ ] **Vault Setup**
  - [ ] Repository initialized with Git
  - [ ] .gitignore configured (excludes secrets)
  - [ ] Folder structure created (domain-specific)
  - [ ] Dashboard.md created
  - [ ] Company_Handbook.md created
  - [ ] Business_Goals.md created

### 11.2 Cloud Deployment Checklist

- [ ] **Secrets Setup**
  - [ ] .env.cloud created on cloud
  - [ ] ANTHROPIC_API_KEY set
  - [ ] SLACK_BOT_TOKEN set
  - [ ] ODOO credentials generated
  - [ ] NO OAuth tokens on cloud
  - [ ] NO banking credentials on cloud

- [ ] **Watchers Running**
  - [ ] gmail-watcher online
  - [ ] calendar-watcher online
  - [ ] slack-watcher online
  - [ ] odoo-watcher online
  - [ ] filesystem-watcher online

- [ ] **Auto-Approver Running**
  - [ ] auto-approver online
  - [ ] Processing Needs_Action/
  - [ ] Creating approval files

- [ ] **Cron Jobs Scheduled**
  - [ ] daily-review scheduled
  - [ ] social-media-scheduler scheduled
  - [ ] audit-log-cleanup scheduled

- [ ] **Git Sync Working**
  - [ ] git-auto-push cron active
  - [ ] Pushing every 5 minutes
  - [ ] Can see commits on GitHub

- [ ] **Odoo Running**
  - [ ] PostgreSQL container running
  - [ ] Odoo container running
  - [ ] Accessible at http://localhost:8069
  - [ ] Backup script scheduled

### 11.3 Local Deployment Checklist

- [ ] **Secrets Setup**
  - [ ] .env created locally
  - [ ] Gmail OAuth tokens working
  - [ ] Calendar OAuth tokens working
  - [ ] Slack bot token set
  - [ ] Banking credentials set (if using)
  - [ ] All tokens excluded from Git

- [ ] **Approval Monitors Running**
  - [ ] email-approval-monitor online
  - [ ] calendar-approval-monitor online
  - [ ] slack-approval-monitor online
  - [ ] linkedin-approval-monitor online
  - [ ] twitter-approval-monitor online
  - [ ] facebook-approval-monitor online
  - [ ] instagram-approval-monitor online

- [ ] **WhatsApp Running**
  - [ ] whatsapp-watcher online
  - [ ] WhatsApp session active

- [ ] **Dashboard Running**
  - [ ] ai-employee-dashboard online
  - [ ] Accessible at http://localhost:3000
  - [ ] Single writer rule enforced

- [ ] **Chrome CDP Ready**
  - [ ] Chrome running with CDP on port 9222
  - [ ] Logged into LinkedIn
  - [ ] Logged into Twitter/X
  - [ ] Logged into Facebook
  - [ ] Logged into Instagram

- [ ] **Git Sync Working**
  - [ ] git-auto-pull cron active
  - [ ] Pulling every 5 minutes
  - [ ] Can see cloud changes locally

### 11.3 Integration Testing Checklist

- [ ] **Email Flow**
  - [ ] Cloud detects email → Creates file in Needs_Action/Email/
  - [ ] AI Auto-Approver triages → Moves to Pending_Approval/Email/
  - [ ] Git sync → File appears on local
  - [ ] User reviews → Approves
  - [ ] Email Approval Monitor detects → Sends via Gmail MCP
  - [ ] File moves to Done/
  - [ ] Git sync → Cloud sees completion

- [ ] **Social Media Flow**
  - [ ] Cloud generates post draft → Pending_Approval/Social_Media/
  - [ ] Git sync → File appears on local
  - [ ] User reviews → Approves
  - [ ] Approval Monitor detects → Posts via CDP
  - [ ] Post appears on platform
  - [ ] File moves to Done/

- [ ] **Odoo Flow**
  - [ ] Cloud detects invoice → Creates in Odoo
  - [ ] Cloud creates approval file
  - [ ] Git sync → File appears on local
  - [ ] User reviews → Approves
  - [ ] Invoice posted/emailed
  - [ ] File moves to Done/

### 11.4 Demo Verification Checklist

- [ ] **Platinum Gate Demo**
  - [ ] Send test email while local is offline
  - [ ] Verify Cloud detects and drafts reply
  - [ ] Turn on local machine
  - [ ] Verify Git pull brings file
  - [ ] Approve email locally
  - [ ] Verify Email Approval Monitor sends
  - [ ] Verify email received
  - [ ] Verify file moves to Done/

- [ ] **Social Media Demo**
  - [ ] Cloud generates LinkedIn post draft
  - [ ] Git sync to local
  - [ ] Approve locally
  - [ ] Verify post appears on LinkedIn
  - [ ] Verify using CDP, not cloud

- [ ] **Health Monitoring**
  - [ ] Cloud health monitor running
  - [ ] Status files written to Updates/signals/
  - [ ] Local can see cloud status
  - [ ] Email alerts on failures

- [ ] **Failover Testing**
  - [ ] Stop Cloud VM
  - [ ] Verify Local continues working
  - [ ] Restart Cloud VM
  - [ ] Verify Cloud resumes watching
  - [ ] Verify Git sync resumes

---

## 12. Troubleshooting Guide

### 12.1 Cloud VM Issues

**Issue: Cloud VM won't start**

```bash
# Check Oracle Cloud Console
# Verify instance is in "Running" state
# Check public IP is assigned
# Try SSH connection:
ssh -i ~/.ssh/your_key ubuntu@<public-ip>
```

**Issue: PM2 processes not starting**

```bash
# Check PM2 logs
pm2 logs --err

# Check Python version
python3 --version  # Should be 3.13+

# Check PYTHONPATH
echo $PYTHONPATH

# Restart PM2
pm2 delete all
pm2 start ecosystem.config.js
pm2 save
```

**Issue: Git sync not working**

```bash
# Check GitHub SSH key
ssh -T git@github.com

# Check git remote
git remote -v

# Test push
git push origin main --dry-run
```

### 12.2 Local Machine Issues

**Issue: Approval monitors not detecting files**

```bash
# Check if files are synced
ls AI_Employee_Vault/Approved/

# Check PM2 logs
pm2 logs email-approval-monitor

# Restart monitor
pm2 restart email-approval-monitor
```

**Issue: Chrome CDP not available**

```bash
# Test CDP port
curl http://localhost:9222/json/version

# If error, start Chrome
start_chrome.bat

# Verify logged in
# Open http://localhost:9222/json in Chrome
```

**Issue: Social media post not appearing**

```bash
# Check if in LIVE MODE
echo $LINKEDIN_DRY_RUN  # Should be "false"
echo $TWITTER_DRY_RUN   # Should be "false"

# Check approval monitor logs
pm2 logs linkedin-approval-monitor

# Check CDP connection
curl http://localhost:9222/json/version
```

### 12.3 Sync Issues

**Issue: Changes not appearing**

```bash
# Check git status
git status

# Check last pull
git log -1 --oneline

# Manual sync
git pull origin main
```

**Issue: Secrets accidentally committed**

```bash
# Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" HEAD

# Force push
git push origin main --force
```

---

## 13. Success Criteria

### 13.1 Platinum Tier Requirements Met

✅ **All Gold requirements**
- Full cross-domain integration
- Odoo accounting system
- Facebook and Instagram integration
- Twitter integration
- Multiple MCP servers
- Weekly Business Audit with CEO Briefing
- Error recovery and graceful degradation
- Comprehensive audit logging
- Ralph Wiggum loop for autonomous tasks

✅ **Platinum requirements**
- Cloud VM running 24/7 (Oracle AMP)
- Work-Zone specialization (Cloud drafts, Local approves)
- Delegation via Synced Vault (Git)
- Claim-by-move rule implemented
- Single-writer rule for Dashboard
- Security rules enforced (secrets never sync)
- Odoo deployed on Cloud VM
- Platinum demo gate passed

### 13.2 Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| **Uptime** | 99%+ | ___ |
| **Cost/Month** | $0 (free tier) | $0 |
| **Watchers Online** | 5/5 (cloud) | ___ |
| **Approval Monitors Online** | 7/7 (local) | ___ |
| **Git Sync Frequency** | Every 5 min | ___ |
| **Email Triage Time** | < 5 min | ___ |
| **Social Media Draft Time** | < 10 min | ___ |

---

**End of Platinum Tier Implementation Plan**

**Next Steps:**
1. Set up Oracle Cloud Free Tier VM
2. Configure Git repository with proper .gitignore
3. Deploy watchers to cloud
4. Deploy approval monitors locally
5. Configure Git auto-sync
6. Deploy Odoo to cloud
7. Test end-to-end flows
8. Record demo video
9. Submit to hackathon
