# Personal AI Employee Vault Index

Welcome to your **Personal AI Employee** vault. This is your central command center - your digital brain, memory, and workflow manager.

---

## 🚀 Quick Start

### For New Users
1. **Open in Obsidian** - Open this folder as an Obsidian vault
2. **Read [[Dashboard]]** - Your real-time status overview
3. **Review [[Company Handbook]]** - Rules for your AI Employee
4. **Set [[Business Goals]]** - Define your objectives

### Daily Usage
- Check **[[Dashboard]]** for pending tasks
- Review **[[Needs Action]]** for items requiring attention
- Approve items in **[[Pending Approval]]**
- Read summaries in **[[Briefings]]**

---

## 📁 Vault Structure

### 🎯 Core Files
- **[[Dashboard]]** - Real-time system status and priorities
- **[[Company Handbook]]** - AI Employee rules and behaviors
- **[[Business Goals]]** - Objectives, KPIs, and targets

### 📥 Action Folders
- **[[Needs Action]]** - Tasks detected by watchers (Gmail, WhatsApp, etc.)
- **[[Pending Approval]]** - Awaiting your review
- **[[Approved]]** - Approved actions (executed by AI)
- **[[Rejected]]** - Declined actions
- **[[Done]]** - Completed tasks

### 📊 Monitoring
- **[[Briefings]]** - Weekly CEO summaries and reports
- **[[Logs]]** - Detailed system activity logs
- **[[Accounting]]** - Financial transactions and invoices
- **[[Plans]]** - AI-generated action plans

### 📥 Inputs
- **[[Inbox]]** - File drop zone for manual processing

---

## 🤖 How It Works

### 1. **Perception** (Watchers)
Background scripts monitor:
- 📧 **Gmail** - Important emails
- 💬 **WhatsApp** - Urgent messages
- 💰 **Banking** - Transactions and payments
- 📁 **File System** - Dropped files

### 2. **Reasoning** (Claude Code)
- Reads items in **[[Needs Action]]**
- Consults **[[Company Handbook]]** for rules
- Creates action plans in **[[Plans]]**
- Generates approval requests in **[[Pending Approval]]**

### 3. **Action** (MCP Servers)
- Waits for your approval in **[[Approved]]**
- Executes actions (send email, post to social media, etc.)
- Logs results to **[[Logs]]**
- Moves completed items to **[[Done]]**

---

## 📋 Typical Workflows

### 🔄 Invoice Request Flow
```
Client emails request
    ↓
Gmail Watcher detects
    ↓
Creates [[Needs Action]]/INVOICE_client.md
    ↓
Claude generates invoice
    ↓
Creates [[Pending Approval]]/EMAIL_invoice.md
    ↓
You review and move to [[Approved]]
    ↓
AI sends invoice via Email MCP
    ↓
Logs to [[Accounting]] and [[Done]]
```

### 📱 Social Media Flow
```
AI generates content ideas
    ↓
Creates [[Pending Approval]]/SOCIAL_post.md
    ↓
You review/edit in Obsidian
    ↓
Move to [[Approved]]
    ↓
AI posts via LinkedIn/Twitter/Meta MCP
    ↓
Creates summary in [[Briefings]]
    ↓
Moves to [[Done]]
```

### 📊 Weekly CEO Briefing
```
Every Sunday at 10 PM
    ↓
AI reads [[Business Goals]]
    ↓
Reviews [[Done]] tasks
    ↓
Analyzes [[Accounting]] data
    ↓
Generates [[Briefings]]/YYYY-MM-DD_Weekly_Summary.md
    ↓
Updates [[Dashboard]]
```

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root (not in vault):

```bash
# Gmail
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json

# Xero (Accounting)
XERO_API_KEY=your_api_key
XERO_API_SECRET=your_api_secret

# Social Media - Safety
LINKEDIN_DRY_RUN=true
META_DRY_RUN=true
TWITTER_DRY_RUN=true

# Paths
VAULT_PATH=/path/to/vault
```

### Watcher Processes
```bash
# Start all watchers
pm2 start process-manager/ecosystem.config.js

# Check status
pm2 list

# View logs
pm2 logs

# Stop all
pm2 stop all
```

---

## 🔒 Security

### Credential Safety
- ✅ All credentials in `.env` file (gitignored)
- ✅ Never store passwords in vault
- ✅ Use OAuth tokens when possible
- ✅ Rotate credentials every 90 days

### Human-in-the-Loop
- ✅ All sensitive actions require approval
- ✅ Payments always need human review
- ✅ Social media posts never auto-post
- ✅ Emails to new contacts require approval

### Audit Trail
- ✅ All actions logged to `[[Logs]]/`
- ✅ Logs retained for 90 days
- ✅ Complete traceability

---

## 📈 Gold Tier Progress

This vault is part of a **Gold Tier** Personal AI Employee implementation.

### Completed Features ✅
- [x] All Silver Tier features
- [x] Cross-domain integration (Personal + Business)
- [x] Xero accounting integration
- [x] Facebook + Instagram posting
- [x] Twitter/X posting
- [x] Multiple MCP servers (3+)
- [x] Weekly CEO Briefing generation
- [x] Error recovery & graceful degradation
- [x] Comprehensive audit logging
- [x] Agent Skills implementation

### Documentation
- [x] `ARCHITECTURE.md` - Complete system documentation
- [x] `LESSONS_LEARNED.md` - Development insights
- [x] `SECURITY.md` - Security practices
- [x] Status summaries for each integration

---

## 🆘 Troubleshooting

### "No items appearing in Needs_Action"
- Check if watchers are running: `pm2 list`
- Review watcher logs: `pm2 logs gmail-watcher`
- Verify API credentials in `.env`

### "Items stuck in Pending_Approval"
- Open vault in Obsidian
- Review items in `/Pending_Approval/`
- Move to `/Approved/` (to execute) or `/Rejected/` (to cancel)

### "AI not posting to social media"
- Check `DRY_RUN` setting in `.env`
- Ensure Chrome is running with CDP enabled
- Review approval monitor logs: `pm2 logs`

### "Weekly briefing not generating"
- Check cron schedule: `pm2 crontab`
- Verify `Business_Goals.md` exists
- Review logs for errors

---

## 📚 Additional Resources

### Project Documentation
- `README.md` - Project overview (outside vault)
- `ARCHITECTURE.md` - Technical architecture (outside vault)
- `SECURITY.md` - Security documentation (outside vault)
- `status/` - Integration summaries (outside vault)

### Skills
- `.claude/skills/` - Agent capabilities (outside vault)
- Each skill has a `SKILL.md` file

### Scripts
- `scripts/` - Automation scripts (outside vault)
- `watchers/` - Monitoring scripts (outside vault)
- `mcp-servers/` - MCP integrations (outside vault)

---

## 🎓 Next Steps

1. **Customize [[Company Handbook]]** - Add your business rules
2. **Set [[Business Goals]]** - Define your targets
3. **Configure `.env`** - Add your API credentials
4. **Start watchers** - Run `pm2 start process-manager/ecosystem.config.js`
5. **Monitor [[Dashboard]]** - Check for items needing action

---

## 💡 Tips

- **Daily**: Check [[Dashboard]] (2 minutes)
- **Weekly**: Review [[Logs]] for errors (15 minutes)
- **Monthly**: Rotate credentials, audit permissions (1 hour)
- **Quarterly**: Full security review, update goals

---

**Vault Created:** 2026-01-11
**Version:** 1.0 (Gold Tier)
**Status:** Ready for use 🚀

---

*Remember: Your AI Employee is a tool, not a replacement for your judgment. Always review important actions and maintain regular oversight.*
