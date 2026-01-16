# AI Employee System - Start Here

**Welcome to your AI Employee!** This guide will help you get started quickly.

---

## 🎯 What Is This?

The AI Employee is an **autonomous assistant** that:
- 📧 **Reads your email** (Gmail) and flags important items
- 📅 **Manages your calendar** (Google Calendar) with meeting prep
- 💬 **Monitors Slack/WhatsApp** for important messages
- 📊 **Tracks accounting** (Xero & Odoo) - invoices, payments, revenue
- 📱 **Posts to social media** (LinkedIn, Twitter, Instagram, Facebook)
- 🧠 **Uses AI (Claude)** to make smart decisions about what needs attention

**Key Feature:** AI Auto-Approver using Claude 3 Haiku intelligently filters out safe actions from items needing your review, dramatically reducing noise while keeping you in control.

---

## ⚡ Quick Start (5 Minutes)

### 1. Start Chrome Automation Browser
```bash
# Run this batch file to start Chrome for social media automation
scripts\social-media\START_AUTOMATION_CHROME.bat
```
**Keep this Chrome window open** - log into LinkedIn, Twitter, Instagram, Facebook in it.

### 2. Start All Services
```bash
# Start everything
pm2 start process-manager/pm2.config.js

# Check status (all should be "online")
pm2 status

# Save configuration
pm2 save
```

### 3. Check System Status
```bash
# Open dashboard in browser
start http://localhost:3000

# Or check via command line
pm2 list
```

**That's it!** Your AI Employee is now running.

---

## 📚 What To Read Next?

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - First-time setup guide (5 min)
2. **[USER_GUIDE.md](USER_GUIDE.md)** - How to use your AI Employee (10 min)
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues

---

## 🏗️ System Overview

```
External Services
     ↓
   Watchers (6 total)
-Gmail, Calendar, Slack, WhatsApp, Xero, Odoo
     ↓
Creates Files in Vault → Needs_Action/
     ↓
┌─────────────────────────────────────┐
│   AI Auto-Approver (Claude 3 Haiku)   │
│   - Runs every 2 minutes              │
│   - Reads Company_Handbook.md         │
│   - Makes smart decisions:             │
│     ✓ approve → Safe actions          │
│     ✗ reject → Scams/phishing        │
│     ? manual → Needs your review     │
└─────────────────────────────────────┘
     ↓              ↓              ↓
Approved/     Rejected/     Pending_Approval/
     ↓              ↓              ↓
Executes      Blocked       You review
     ↓                           ↓
   Done/                      Approved/
```

---

## 📁 Vault Structure (Where Everything Lives)

```
AI_Employee_Vault/
├── 📥 Inbox/              # Drop files here manually
├── ⚠️  Needs_Action/      # Watchers put items here first
├── 🤔 Pending_Approval/   # AI flagged for your review
├── ✅ Approved/           # Ready to execute (AI or human)
├── ❌ Rejected/           # Declined items
├── ✅ Done/               # Completed items
├── 📊 Briefings/          # CEO summaries & reports
├── 📋 Plans/              # Execution plans
├── 📝 Logs/               # All actions logged here (JSON)
└── 🧠 Company_Handbook.md # Your business rules
```

---

## 🎛️ Control Panel

### Check What's Happening
```bash
# View all processes
pm2 status

# View live logs
pm2 logs

# Check AI approval decisions
pm2 logs auto-approver --lines 50
```

### View Your Dashboard
Open in browser: **http://localhost:3000**

---

## 🎯 What Can It Do?

### Daily Tasks
- ✅ Check for urgent emails
- ✅ Monitor for overdue invoices
- ✅ Prepare for upcoming meetings
- � Flag important Slack/WhatsApp messages
- ✅ Generate daily briefings
- ✅ Post to social media (with your approval)

### Social Media (All 4 Platforms)
- ✅ **LinkedIn** - Professional posts (100-200x faster than typing)
- ✅ **Twitter/X** - Tweets and replies
- ✅ **Instagram** - Posts with auto-generated images
- ✅ **Facebook** - Posts with full formatting

### Accounting
- ✅ Track invoices (Xero)
- ✅ Monitor payments (Odoo)
- ✅ Revenue reports
- ✅ Overdue alerts

### AI Auto-Approver (NEW!)
- ✅ Auto-approves: File operations, Slack/WhatsApp, safe calendar events
- ✅ Auto-rejects: Scams, phishing, payment requests
- ❓ Manual review: Social media, payments, new contacts

---

## 🚀 Next Steps

**Read these in order:**

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup everything from scratch
2. **[USER_GUIDE.md](USER_GUIDE.md)** - Learn to use your AI Employee
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues

---

## 🆘 Need Help?

### Quick Checks
```bash
# 1. Are services running?
pm2 status

# 2. Is Chrome automation open?
# (Look for Chrome window with automation profile)

# 3. Check logs
pm2 logs --lines 50
```

### Common Issues
- **Services won't start** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Social media not posting** → Verify Chrome automation is running
- **Not detecting emails** → Check Gmail token authentication

---

## 📊 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Total Processes** | 19 | 15 continuous + 4 scheduled |
| **Watchers** | 6 | Gmail, Calendar, Slack, WhatsApp, Xero, Odoo |
| **AI Auto-Approver** | ✅ Online | Uses Claude 3 Haiku |
| **Social Media** | ✅ Ready | LinkedIn, Twitter, Instagram, Facebook |
| **Dashboard** | ✅ Running | http://localhost:3000 |
| **System Version** | v1.3.0 | Platinum Tier (AI + Human-in-the-Loop) |

---

*Last Updated: 2026-01-17*
*System Status: All Operational ✅*
