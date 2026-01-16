# User Guide - Day-to-Day Usage

**Learn how to work with your AI Employee effectively.**

---

## 🌅 Daily Workflow

### Morning Routine (5 minutes)

#### 1. Start Your Day
```
You: "What needs my attention today?"

Claude: (Shows summary from Briefings/ and Needs_Action/)
- 3 urgent emails
- 2 overdue invoices
- 1 meeting conflict
- 5 Slack messages flagged
```

#### 2. Check Dashboard
```
Visit http://localhost:3000
- Review system status
- Check pending approvals
- See recent activity
```

#### 3. Process Urgent Items
```
You: "Draft a response for the overdue invoice"
Claude: Creates draft in Pending_Approval/
You: (Review draft) → Move to Approved/
System: Sends email automatically
```

---

## 📧 Managing Email

### Check Emails
```
You: "Show me urgent emails from today"
You: "Find emails about invoices"
You: "What does sender@example.com want?"
```

### Process Email
```
1. Watcher detects email → Creates file in Needs_Action/
2. AI Auto-Approver analyzes:
   - Known contact? → Approved (auto-executes)
   - Unknown? → Pending_Approval/ (your review)
   - Scam? → Rejected/ (blocked)
3. You review (if needed)
4. Move to Approved/
5. System sends via Gmail MCP
```

### Manual Email Actions
```
You: "Send email to client@example.com about invoice INV-001"
Claude: Creates draft in Pending_Approval/
You: Review → Move to Approved/
System: Sends email
```

---

## 📅 Calendar Management

### Check Schedule
```
You: "What meetings do I have today?"
You: "Show me this week's schedule"
You: "When am I free tomorrow afternoon?"
```

### Meeting Preparation
```
System auto-creates meeting prep files in Needs_Action/:
- Agenda (if available)
- Attendees list
- Related documents
- Preparation tasks
```

### Create Event
```
You: "Schedule a team meeting for Friday 2pm"
Claude: Creates event → Pending_Approval/
You: Review → Move to Approved/
System: Adds to Calendar
```

---

## 💬 Slack & WhatsApp

### Monitor Messages
```
You: "What urgent Slack messages do I have?"
You: "Show me WhatsApp messages from today"
```

### Auto-Processed
- **Slack messages** → Auto-approved (just notifications)
- **WhatsApp** → Auto-approved if safe, manual if suspicious

### Send Messages
```
You: "Send message to #general: 'Starting the meeting now'"
Claude: Creates draft → Pending_Approval/
You: Approve → Approved/
System: Sends via MCP
```

---

## 💰 Accounting

### Xero (Online Accounting)
```
You: "Show me overdue invoices"
You: "What's my revenue this month?"
You: "List unpaid invoices over 30 days old"
```

### Odoo (Local Accounting)
```
You: "Create an invoice for Test Client for $1000"
Claude: Creates invoice in Odoo → Done/
System: Updates accounting file
```

### Monthly Reports
- **Auto-generated** on 1st of each month
- **Location:** `AI_Employee_Vault/Accounting/YYYY-MM.md`
- **Includes:** Revenue, invoices, expenses

---

## 📱 Social Media Posting

### Create LinkedIn Post
```
You: "Create a LinkedIn post about AI automation"
Claude: Generates content → Pending_Approval/

File: LINKEDIN_POST_20260117_123456.md
---
type: linkedin_post
platform: linkedin
content: |
  Excited to share our AI automation journey! 🤖
  We've built a system that...
#AI #Automation #Tech
---

You: Review content → Edit if needed → Move to Approved/
System: Posts to LinkedIn (100-200x faster than typing)
```

### Create Twitter Post
```
You: "Tweet about our new feature"
Claude: Creates tweet (280 chars max) → Pending_Approval/
You: Approve → Approved/
System: Posts to X.com
```

### Create Instagram Post
```
You: "Post to Instagram about our product launch"
Claude: Creates post + generates professional image → Pending_Approval/
You: Approve → Approved/
System: Posts image + caption to Instagram
```

### Create Facebook Post
```
You: "Post to Facebook about company news"
Claude: Creates post → Pending_Approval/
You: Approve → Approved/
System: Posts to Facebook
```

### Reply to Social Media
```
You: "Reply to @username: Thanks for the feedback!"
Claude: Creates reply → Pending_Approval/
You: Approve → Approved/
System: Posts reply
```

---

## 🤖 Understanding AI Auto-Approver

### What It Does
Runs every 2 minutes, scanning `Needs_Action/` and `Inbox/`:

**Auto-Approves** (safe actions):
- File operations in Inbox/
- Slack messages (notifications)
- WhatsApp messages
- Calendar events without attendees
- Emails from known contacts

**Auto-Rejects** (dangerous):
- Scams and phishing
- Payment requests
- "Urgent" financial solicitations

**Manual Review** (your decision):
- Social media posts (all platforms)
- Payment actions
- New contacts
- High-priority items

### Check AI Decisions
```bash
pm2 logs auto-approver --lines 50
```

### Override AI Decision
If AI auto-rejects something incorrectly:
```
1. Find item in Rejected/
2. Move back to Needs_Action/
3. AI will re-analyze (same result likely)
4. Move manually to Approved/ to force execution
```

---

## 📋 Using Claude Code Effectively

### Common Commands

**Email Management:**
```
"Check my urgent emails"
"Show me emails from sender@example.com"
"Draft response to invoice inquiry"
"Find emails about 'project deadline'"
```

**Calendar:**
```
"What meetings do I have today?"
"When am I free tomorrow?"
"Schedule meeting for Friday 2pm with team"
"Prepare for tomorrow's client meeting"
```

**Social Media:**
```
"Create LinkedIn post about AI"
"Generate 3 tweet ideas for our product"
"Draft Instagram caption for this photo"
```

**Accounting:**
```
"Show me overdue invoices"
"What's my revenue this month?"
"Create payment reminder for oldest invoice"
```

**General:**
```
"What's in my Needs_Action folder?"
"Create daily briefing"
"Show me system status"
"Help me prioritize these tasks"
```

---

## 🔧 Process Control

### Check System Status
```bash
# All processes
pm2 status

# Detailed info
pm2 show auto-approver

# View logs
pm2 logs --lines 50

# Specific service
pm2 logs gmail-watcher --lines 100
```

### Restart Services
```bash
# Restart everything
pm2 restart all

# Restart specific service
pm2 restart auto-approver
pm2 restart gmail-watcher

# Reset restart count
pm2 reset auto-approver
```

### Stop/Start
```bash
# Stop all
pm2 stop all

# Stop specific
pm2 stop gmail-watcher

# Start all
pm2 start process-manager/pm2.config.js

# Start specific
pm2 start gmail-watcher
```

---

## 📊 Monitor Your System

### Dashboard
Visit **http://localhost:3000** for:
- System status overview
- Process health
- Recent activity
- Quick actions

### Vault Folders
```bash
# What needs attention?
dir AI_Employee_Vault\Needs_Action

# Awaiting my review?
dir AI_Employee_Vault\Pending_Approval

# Ready to execute?
dir AI_Employee_Vault\Approved

# Completed?
dir AI_Employee_Vault\Done
```

### Audit Logs
```bash
# Today's log
cat AI_Employee_Vault\Logs\2026-01-17.json

# Format nicely
cat AI_Employee_Vault\Logs\2026-01-17.json | python -m json.tool
```

---

## 🎯 Best Practices

### Daily Review (5 min)
1. Check dashboard
2. Review `Pending_Approval/`
3. Check `Needs_Action/`
4. Review `Briefings/`
5. Approve/reject items

### Weekly Maintenance
1. Clean up `Done/` folder (archive old items)
2. Review `Company_Handbook.md` - update business rules
3. Check system logs for errors
4. Update business goals if needed

### Safety First
1. **Always review** before approving social media posts
2. **Check carefully** before approving payments
3. **Verify recipients** before sending emails
4. **Test with dry-run** for social media first

### Customize Your System
1. **Edit `Company_Handbook.md`** - Your business rules
2. **Add known contacts** to auto-approver whitelist
3. **Create custom skills** in `.claude/skills/`
4. **Adjust monitoring frequency** in PM2 config

---

## 🚀 Advanced Usage

### Create Custom Skills
```bash
# Create new skill
mkdir .claude/skills/my-skill
# Add SKILL.md with instructions
# Use in conversation
```

### Run Ralph (Autonomous Tasks)
```bash
# Start Ralph task loop
/start-ralph.sh

# Check progress
/check-ralph-status.sh
```

### Generate Reports
```
You: "Create Monday CEO briefing"
You: "Generate daily review"
You: "Prepare weekly summary"
```

---

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Check emails | `ls AI_Employee_Vault/Needs_Action/` |
| Check pending | `ls AI_Employee_Vault/Pending_Approval/` |
| Check status | `pm2 status` |
| View logs | `pm2 logs --lines 50` |
| Restart all | `pm2 restart all` |
| Open dashboard | `start http://localhost:3000` |

---

## 🆘 Getting Help

### Quick Troubleshooting
```bash
# 1. Check if services running
pm2 status

# 2. Check Chrome automation
netstat -ano | findstr :9222

# 3. Check logs
pm2 logs --err --lines 50

# 4. Restart problem service
pm2 restart <service-name>
```

### Common Issues
- **Services not starting** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Social media not posting** → Verify Chrome automation
- **No emails detected** → Check Gmail token
- **AI not making decisions** → Verify ANTHROPIC_API_KEY

---

## 🎓 Learn More

- **[START_HERE.md](START_HERE.md)** - Introduction
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix issues
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical details
- **[SOCIAL_MEDIA_GUIDE.md](SOCIAL_MEDIA_GUIDE.md)** - Social media posting

---

*Last Updated: 2026-01-17*
*System Version: v1.3.0*
