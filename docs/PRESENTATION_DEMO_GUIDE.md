# AI Employee App - Presentation Demo Guide

**Version:** 1.1.0
**Date:** January 14, 2026
**Purpose:** Step-by-step guide for live demonstration

---

## 🎯 Presentation Overview

This guide provides **step-by-step instructions** for demonstrating the AI Employee App during your presentation. Follow these commands in order to showcase the system's capabilities.

**Total Demo Time:** 15-20 minutes
**Key Features to Demo:**
1. System status and architecture
2. Watchers monitoring live data
3. Ralph Wiggum autonomous execution (standout feature)
4. Social media posting (fast copy-paste method)
5. Human-in-the-loop approval workflow

---

## 📋 Pre-Demo Checklist (Before Presentation)

### ✅ System Verification

```bash
# 1. Check PM2 processes are running
pm2 status

# Expected output: 16 processes online (or at least 5-6 core watchers)
# If stopped: pm2 start process-manager/pm2.config.js

# 2. Check vault exists
ls AI_Employee_Vault/

# Expected: Dashboard.md, Company_Handbook.md, etc.

# 3. Check watchers are creating files
ls -la AI_Employee_Vault/Needs_Action/ | head -20

# Expected: Some EMAIL_*.md or WHATSAPP_*.md files

# 4. Check logs are being written
ls AI_Employee_Vault/Logs/ | tail -5

# Expected: YYYY-MM-DD.json files
```

### ✅ Chrome Automation Setup (For Social Media Demo)

```bash
# Start Chrome with remote debugging (if not already running)
# Windows:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\User\Desktop\AI_EMPLOYEE_APP\ChromeAutomationProfile"

# Log in to platforms in the Chrome window:
# - LinkedIn (linkedin.com)
# - Twitter/X (x.com)
# - Facebook (facebook.com)
# - Instagram (instagram.com)
```

---

## 🚀 Demo Script (Step-by-Step)

### Part 1: Introduction & Architecture (2 minutes)

#### Slide: Architecture Overview

**Say:** "Let me show you how the AI Employee system works."

**Action:**
```bash
# Show system status
pm2 status
```

**Explain:**
- "I have 16 processes running 24/7 via PM2"
- "5 Watchers monitor Gmail, Calendar, Slack, Filesystem, WhatsApp"
- "6 Approval Monitors handle human-in-the-loop workflows"
- "5 Cron jobs handle scheduled tasks like CEO Briefings"

**Show:**
```bash
# Show the vault structure
ls AI_Employee_Vault/

# Show the skills
ls .claude/skills/

# Show documentation
ls docs/
```

**Explain:**
- "All data stored locally in Obsidian vault"
- "20 Agent Skills provide modular capabilities"
- "Complete documentation for every component"

---

### Part 2: Live Watcher Demo (3 minutes)

#### Slide: The Watchers (Perception Layer)

**Say:** "The Watchers are the AI Employee's senses. Let me show them detecting real events."

**Action 1: Check recent watcher activity**
```bash
# Show recent action files from watchers
ls -lt AI_Employee_Vault/Needs_Action/ | head -10
```

**Explain:** "These are action files created by watchers when they detect important events."

**Action 2: Read a sample action file**
```bash
# Pick the most recent file
cat "$(ls -t AI_Employee_Vault/Needs_Action/*.md | head -1)"
```

**Explain:**
- "Each action file has YAML frontmatter with metadata"
- "Contains the detected content (email, message, event)"
- "Includes suggested actions for me to review"

**Action 3: Show WhatsApp watcher working (if active)**
```bash
# Check WhatsApp watcher logs
pm2 logs whatsapp-watcher --lines 20 --nostream
```

**Explain:**
- "WhatsApp watcher scans for keywords: urgent, asap, invoice, payment, help"
- "Uses Playwright to read chat list without clicking (privacy-focused)"
- "Found X messages with keywords just now"

---

### Part 3: Ralph Wiggum Autonomous Execution (5 minutes)

#### Slide: Ralph Wiggum (Standout Feature)

**Say:** "This is the standout feature - Ralph Wiggum autonomous task execution. Let me show it running the Monday Morning CEO Briefing."

**Action 1: Check Ralph status**
```bash
# Check if Ralph is already running
./scripts/check-ralph-status.sh
```

**If not running, start it:**

**Action 2: Show the task list**
```bash
# Show the CEO Briefing task list
cat .claude/skills/ralph/prd_monday_ceo_briefing.json | head -50
```

**Explain:**
- "7 tasks for the Monday CEO Briefing"
- "Check Gmail for urgent messages"
- "Review calendar for upcoming events"
- "Analyze business performance from logs"
- "Compare progress to targets"
- "Generate proactive suggestions"
- "Create professional briefing document"

**Action 3: Start Ralph (if not running)**
```bash
# Start Ralph with 10 max iterations
./scripts/start-ralph.sh 10
```

**Explain:**
- "Ralph will now autonomously execute all 7 tasks"
- "Each iteration, it picks the highest priority incomplete task"
- "Plans, executes, requests approval if needed"
- "Continues until all tasks complete or max iterations reached"

**Action 4: Watch Ralph work**
```bash
# In a separate terminal, watch Ralph progress
watch -n 5 './scripts/check-ralph-status.sh'
```

**Let it run for 2-3 minutes, then:**

**Action 5: Check if approval needed**
```bash
# Check for pending approvals
ls AI_Employee_Vault/Pending_Approval/
```

**If file exists:**
```bash
# Read the approval request
cat "$(ls -t AI_Employee_Vault/Pending_Approval/*.md | head -1)"
```

**Say:** "Ralph needs my approval for an action. Let me review and approve it."

**Action 6: Approve the action**
```bash
# Move to Approved folder
mv "$(ls -t AI_Employee_Vault/Pending_Approval/*.md | head -1)" AI_Employee_Vault/Approved/
```

**Explain:** "I've approved the action. Ralph will now continue to the next task."

**Action 7: Check Ralph progress after 2-3 minutes**
```bash
./scripts/check-ralph-status.sh
```

**Explain:**
- "Ralph has completed X of 7 tasks"
- "Takes 10-15 minutes total vs 30-60 minutes manually"
- "3-6x faster with consistent quality"

**Action 8: Show the generated briefing (if complete)**
```bash
# Check if briefing was created
ls -lt AI_Employee_Vault/Briefings/ | head -5

# If Monday_Briefing exists, show it
cat "$(ls -t AI_Employee_Vault/Briefings/*Monday_Briefing*.md 2>/dev/null | head -1)" | head -100
```

---

### Part 4: Social Media Posting Demo (4 minutes)

#### Slide: Social Media Automation

**Say:** "Now let me show you the social media automation with fast copy-paste method."

**Action 1: Create a test LinkedIn post**
```bash
# Create approval request for LinkedIn post
cat > "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_demo_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: $(date -Iseconds)
expires: $(date -d "+24 hours" -Iseconds)
status: pending_approval
---

# The Future of Autonomous AI Agents

Excited to share my Personal AI Employee project - a local-first AI system that works 24/7 as my digital FTE.

## Key Features:
✅ Local-first (all data on my machine)
✅ Human-in-the-loop approval
✅ Autonomous task execution
✅ 85-90% cost savings vs human FTE
✅ Works 168 hours/week vs 40 hours

## Standout Feature:
Monday Morning CEO Briefing - autonomously audits business, analyzes performance, and generates actionable insights.

#AI #Automation #AutonomousAgents #FutureOfWork
EOF
```

**Explain:**
- "I create a markdown file with post content"
- "YAML frontmatter specifies platform and metadata"
- "Human-in-the-loop: I must approve before posting"

**Action 2: Review and approve**
```bash
# Show the file
cat "$(ls -t AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md | head -1)"

# Approve by moving to Approved/
mv "$(ls -t AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md | head -1)" AI_Employee_Vault/Approved/
```

**Action 3: Watch the approval monitor post it**
```bash
# In a separate terminal, watch the monitor logs
pm2 logs linkedin-approval-monitor --lines 0
```

**Explain:**
- "The approval monitor detects the file in Approved/"
- "Reads the post content"
- "Opens LinkedIn via Chrome DevTools Protocol"
- "Uses fast copy-paste method: 0.3 seconds vs 30-60 seconds"
- "100-200x faster than typing character-by-character"

**Action 4: Verify the post was created**
```bash
# Check for summary file
ls -lt AI_Employee_Vault/Briefings/ | head -5

# Check the file moved to Done
ls AI_Employee_Vault/Done/ | grep LINKEDIN_POST
```

**Explain:**
- "Post summary created in Briefings/"
- "File moved to Done/ to confirm completion"
- "Audit trail in Logs/YYYY-MM-DD.json"

---

### Part 5: System Health & Monitoring (2 minutes)

#### Slide: System Architecture

**Action 1: Show PM2 dashboard**
```bash
# Show all processes
pm2 status

# Show resource usage
pm2 monit
```

**Explain:**
- "16 processes running: 5 watchers, 6 approval monitors, 5 cron jobs"
- "0 crashes - system is stable"
- "Resource usage: minimal overhead"

**Action 2: Show audit logs**
```bash
# Show today's audit log
cat "AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json" | head -50
```

**Explain:**
- "Every action logged with timestamp"
- "Tracks action_type, actor, target, parameters, approval_status, result"
- "Complete audit trail for compliance"

**Action 3: Show Dashboard**
```bash
# Show the dashboard
cat AI_Employee_Vault/Dashboard.md | head -100
```

**Explain:**
- "Dashboard shows system status at a glance"
- "Recent activity, pending items, business metrics"
- "Updated automatically by watchers and Ralph"

---

### Part 6: Conclusion (1 minute)

#### Slide: Summary & Results

**Summary Script:**

"In conclusion, the AI Employee App demonstrates:

✅ **Local-First Architecture** - All data on my machine
✅ **Human-in-the-Loop** - Approval required for sensitive actions
✅ **Autonomous Execution** - Ralph completes 7-task briefing in 10-15 minutes
✅ **Fast Social Posting** - 100-200x faster with copy-paste method
✅ **85-90% Cost Savings** - $0.50/task vs $5.00/task for human
✅ **168 Hours/Week** - 4.5x more availability than human FTE

**Gold Tier Requirements: 100% Complete**
- 20 Agent Skills documented and operational
- Cross-domain integration (Personal + Business)
- Xero accounting integration
- Full social media automation
- Ralph Wiggum autonomous execution
- Complete documentation

The code is open source on GitHub: github.com/HamdanProfessional/Hackathon0

Thank you! Questions?"

---

## 🔧 Troubleshooting During Demo

### Issue: PM2 processes not running

**Solution:**
```bash
# Start all processes
pm2 start process-manager/pm2.config.js

# Save configuration
pm2 save
```

### Issue: Chrome automation not working

**Solution:**
```bash
# Start Chrome with debugging
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\User\Desktop\AI_EMPLOYEE_APP\ChromeAutomationProfile"

# Log in to platforms in the Chrome window
```

### Issue: Ralph not completing tasks

**Solution:**
```bash
# Check Ralph status
./scripts/check-ralph-status.sh

# Check progress file
cat .claude/ralph-loop.local.md

# If stuck, cancel and restart
/cancel-ralph
./scripts/start-ralph.sh 10
```

### Issue: Approval not executing

**Solution:**
```bash
# Check approval monitor logs
pm2 logs linkedin-approval-monitor --lines 50

# Check file format
cat AI_Employee_Vault/Approved/FILENAME.md

# Verify YAML frontmatter is valid
```

---

## 📊 Quick Reference Commands

### System Status
```bash
pm2 status                    # Show all processes
pm2 logs [process-name]       # Show logs for specific process
./scripts/check-ralph-status.sh # Check Ralph progress
```

### Testing Watchers
```bash
# Run watcher once for testing
python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --once

# Run in dry-run mode
python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --dry-run
```

### Testing Ralph
```bash
# Start Ralph
./scripts/start-ralph.sh 10

# Check status
./scripts/check-ralph-status.sh

# Cancel Ralph
/cancel-ralph
```

### Testing Social Media
```bash
# Create approval request (use templates from AI_Employee_Vault/Templates/)

# Approve
mv "Pending_Approval/FILE.md" "Approved/"

# Check logs
pm2 logs linkedin-approval-monitor --lines 50
```

### Monitoring
```bash
# Watch real-time logs
pm2 logs --lines 0

# Monitor specific process
pm2 monit

# Check audit log
cat "AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json" | jq
```

---

## 🎯 Demo Tips

1. **Practice First:** Run through the demo at least once before presentation
2. **Have Backups:** Keep terminal tabs pre-loaded with commands
3. **Stay Calm:** If something fails, explain the error and move to next demo
4. **Focus on Value:** Emphasize business value (85-90% cost savings, 168 hrs/week)
5. **Show Don't Tell:** Let the system speak for itself with live demos
6. **Time Management:** Keep each section to allocated time
7. **Have Fun:** This is an impressive system - enjoy showing it off!

---

## 📱 Demo File Locations

### Configuration Files
- `process-manager/pm2.config.js` - PM2 configuration
- `.env` - Credentials (XERO_CLIENT_ID, SLACK_BOT_TOKEN, etc.)
- `.claude/settings.local.json` - Claude Code settings

### Vault Files
- `AI_Employee_Vault/Dashboard.md` - System dashboard
- `AI_Employee_Vault/Company_Handbook.md` - AI Employee rules
- `AI_Employee_Vault/Business_Goals.md` - Business targets
- `AI_Employee_Vault/Needs_Action/` - Action files from watchers
- `AI_Employee_Vault/Pending_Approval/` - Awaiting approval
- `AI_Employee_Vault/Approved/` - Ready to execute
- `AI_Employee_Vault/Done/` - Completed actions
- `AI_Employee_Vault/Briefings/` - Generated reports
- `AI_Employee_Vault/Logs/` - Audit logs

### Ralph Files
- `.claude/skills/ralph/prd_monday_ceo_briefing.json` - CEO Briefing task list
- `.claude/ralph-loop.local.md` - Ralph state (created when running)
- `scripts/start-ralph.sh` - Start Ralph script
- `scripts/check-ralph-status.sh` - Check Ralph progress

### Skills Documentation
- `.claude/skills/INDEX.md` - Central skills index
- `.claude/skills/[skill-name]/SKILL.md` - Individual skill docs

---

**Good luck with your presentation! 🚀**

*Demo Guide v1.1.0 - Last Updated: 2026-01-14*
*AI Employee App - Gold Tier 100% Complete*
