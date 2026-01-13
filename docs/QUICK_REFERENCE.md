# AI Employee System - Quick Reference Guide

**Updated:** 2026-01-12
**Status:** Production Ready ✅

---

## 🚀 Quick Start

### Start All Services
```bash
# Start Chrome with CDP (for social media)
START_AUTOMATION_CHROME.bat

# Start all watchers
pm2 start process-manager/pm2.config.js

# Check status
pm2 status

# Save configuration
pm2 save
```

### Stop All Services
```bash
# Stop all watchers
pm2 stop all

# Close Chrome (optional)
# Chrome window with automation profile can stay open
```

---

## 📧 Gmail

### Check Emails via Claude Code
```
You: "Check my urgent emails"
You: "List recent emails from sender@example.com"
You: "Find emails about invoices"
```

### Watcher Commands
```bash
# Run once (test mode)
python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --once --dry-run

# Run continuously (PM2)
pm2 start gmail-watcher

# View logs
pm2 logs gmail-watcher --lines 50
```

### MCP Test
```bash
cd mcp-servers/email-mcp
node test-email.js
```

---

## 📅 Calendar

### Check Calendar via Claude Code
```
You: "What meetings do I have today?"
You: "Show me upcoming events this week"
You: "Create a meeting for tomorrow at 2 PM"
```

### Watcher Commands
```bash
# Run once
python -m watchers.calendar_watcher --vault AI_Employee_Vault --credentials mcp-servers/calendar-mcp/credentials.json --once --dry-run

# Run continuously
pm2 start calendar-watcher

# View logs
pm2 logs calendar-watcher --lines 50
```

### MCP Test
```bash
cd mcp-servers/calendar-mcp
node test-calendar.js
```

---

## 💰 Xero

### Query Xero via Claude Code
```
You: "Show me overdue invoices"
You: "What's my total revenue this month?"
You: "List unpaid invoices over 30 days old"
```

### Watcher Commands
```bash
# Run once
python -m watchers.xero_watcher --vault AI_Employee_Vault --once --dry-run

# Run continuously
pm2 start xero-watcher

# View logs
pm2 logs xero-watcher --lines 50
```

### MCP Test
```bash
cd mcp-servers/xero-mcp
node test-xero.js
```

---

## 💬 Slack

### Use Slack via Claude Code
```
You: "Send a message to #general"
You: "What urgent messages do I have in Slack?"
You: "List all channels"
```

### Watcher Commands
```bash
# Run once
python -m watchers.slack_watcher --vault AI_Employee_Vault --token xoxb-***REMOVED*** --once --dry-run

# Run continuously
pm2 start slack-watcher

# View logs
pm2 logs slack-watcher --lines 50
```

### MCP Test
```bash
cd mcp-servers/slack-mcp
node test-slack.js
```

---

## 📸 Instagram (via Meta Business Suite)

### Post to Instagram
```bash
cd scripts/social-media

# Dry run (preview)
python meta_poster.py "Your Instagram post caption #hashtags" --dry-run

# Live post
python meta_poster.py "Your Instagram post caption #hashtags" --live
```

### Requirements
- Chrome running with CDP on port 9222
- Logged into Meta Business Suite
- Instagram account connected

---

## 💼 LinkedIn

### Post to LinkedIn
```bash
cd scripts/social-media

# Dry run (preview)
python linkedin_poster.py "Your LinkedIn post content" --dry-run

# Live post
python linkedin_poster.py "Your LinkedIn post content" --live

# From file
python linkedin_poster.py --file post_content.md --live
```

### Requirements
- Chrome running with CDP on port 9222
- Logged into LinkedIn
- Profile: hamdan-mohammad-922486374

---

## 🐦 X.com (Twitter)

### Post to X.com
```bash
cd scripts/social-media

# Dry run (preview)
python twitter_poster.py "Your tweet content #hashtags" --dry-run

# Live post
python twitter_poster.py "Your tweet content #hashtags" --live

# Reply to tweet
python twitter_poster.py "Reply content" --reply-to @username --live
```

### Requirements
- Chrome running with CDP on port 9222
- Logged into X.com

---

## 📁 Filesystem Watcher

### Monitor Inbox Folder
```bash
# Start monitoring
python -m watchers.filesystem_watcher --vault AI_Employee_Vault --watch-folder AI_Employee_Vault/Inbox

# Files dropped in Inbox/ will be auto-processed to Needs_Action/
```

---

## 🧠 Using Claude Code

### Daily Workflow
```
1. You: "Check what needs attention today"
   Claude: "3 urgent emails, 2 overdue invoices, 1 meeting conflict"

2. You: "Create payment reminder for the oldest invoice"
   Claude: [Creates draft in Pending_Approval/]

3. You: [Review draft] → Move to Approved/

4. Claude: [Sends email via Gmail MCP, updates Xero]
```

### Common Commands
```
"Show me all pending emails"
"Create a LinkedIn post about AI automation"
"Schedule a meeting for tomorrow 2 PM"
"Send a Slack message to #general"
"What's in my Needs_Action folder?"
"Create a daily briefing"
```

---

## 📊 Monitoring & Logs

### Check PM2 Status
```bash
# Status of all processes
pm2 status

# Detailed info
pm2 show gmail-watcher

# Real-time logs
pm2 logs

# Logs for specific process
pm2 logs gmail-watcher --lines 100

# Restart process
pm2 restart gmail-watcher

# Reset restart count
pm2 reset gmail-watcher
```

### Vault Monitoring
```bash
# Check action files
ls AI_Employee_Vault/Needs_Action/

# Check pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Check completed items
ls AI_Employee_Vault/Done/

# Count files
find AI_Employee_Vault/Needs_Action/ -type f | wc -l
```

---

## 🔧 Troubleshooting

### Chrome CDP Not Working
```bash
# Check if Chrome is listening on port 9222
netstat -ano | findstr :9222

# If not found, start Chrome
START_AUTOMATION_CHROME.bat

# Or manually:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"
```

### Watcher Not Creating Files
```bash
# Check logs
pm2 logs <watcher-name>

# Check token files exist
ls .gmail_token.json .calendar_token.json

# Check credentials
ls mcp-servers/email-mcp/credentials.json

# Run manually to see error
python -m watchers.gmail_watcher --vault AI_Employee_Vault --once
```

### MCP Not Responding
```bash
# Check token is valid
cat mcp-servers/email-mcp/.gmail_mcp_token.json

# Test MCP directly
cd mcp-servers/email-mcp
node test-email.js

# Re-authenticate if needed
cd mcp-servers/email-mcp
npm run authenticate
```

### Social Media Poster Failing
```bash
# Verify Chrome is running with CDP
netstat -ano | findstr :9222

# Check you're logged in
# (Open Chrome window and verify)

# Test in dry-run mode first
python linkedin_poster.py "Test" --dry-run

# Check for screenshots
ls error_debug.png dry_run_preview.png
```

---

## 🔐 Authentication Status

| Service | Status | Token Location | Auth Command |
|---------|--------|----------------|---------------|
| Gmail | ✅ Valid | `.gmail_mcp_token.json` | `cd mcp-servers/email-mcp && npm run authenticate` |
| Calendar | ✅ Valid | `.calendar_mcp_token.json` | `cd mcp-servers/calendar-mcp && npm run authenticate` |
| Xero | ✅ Valid | `.xero_mcp_token.json` | `cd mcp-servers/xero-mcp && npm run authenticate` |
| Slack | ✅ Valid | Environment variable | See slack-mcp setup |

---

## 📝 Vault Structure Reference

```
AI_Employee_Vault/
├── 📥 Inbox/              # Drop zone for manual items
├── ⚠️  Needs_Action/      # Auto-created by watchers
├── 🤔 Pending_Approval/   # Claude's proposals
├── ✅ Approved/           # Ready for execution
├── ✅ Done/               # Completed items
├── 📋 Plans/              # Execution plans
├── 📊 Briefings/          # CEO summaries
└── 📝 Logs/               # Audit trail (JSON)
```

---

## 🎯 Common Tasks

### Process Urgent Email
```
1. Watcher detects urgent email → Creates file in Needs_Action/
2. You ask: "What needs attention?"
3. Claude shows urgent email
4. You: "Draft a response"
5. Claude creates draft in Pending_Approval/
6. You review and move to Approved/
7. Monitor sends email via Gmail MCP
8. File moved to Done/ with summary
```

### Post to Social Media
```
1. You: "Create a LinkedIn post about AI"
2. Claude generates content → Pending_Approval/
3. You review and edit → Move to Approved/
4. Run: python linkedin_poster.py "content" --live
5. Script posts via Chrome CDP
6. Confirmation saved to Done/
```

### Handle Overdue Invoice
```
1. Xero watcher detects overdue invoice → Needs_Action/
2. You: "Show me overdue invoices"
3. You: "Create payment reminder"
4. Claude drafts reminder → Pending_Approval/
5. You approve → Approved/
6. Monitor sends email → Updates Xero
7. Done/ with summary
```

---

## 📚 Documentation Files

- `CLAUDE.md` - Project instructions
- `SYSTEM_OVERVIEW.md` - Complete system guide
- `docs/STATUS.md` - Current completion status
- `docs/ARCHITECTURE.md` - Detailed architecture
- `docs/SECURITY.md` - Security model
- `docs/PROCESS_MANAGEMENT.md` - PM2 guide
- `ERROR_FIXES.md` - Fixed issues list

---

## 💡 Tips & Tricks

1. **Always test with --dry-run first** for social media posts
2. **Check PM2 logs** if something isn't working
3. **Use Claude Code interactively** - ask questions
4. **Review Pending_Approval/** daily
5. **Keep Chrome open** with automation profile
6. **Monitor vault size** - archive old Done/ files periodically
7. **Customize Company_Handbook.md** for your business
8. **Create custom skills** in `.claude/skills/`

---

## 🆘 Getting Help

### Check Status First
```bash
# PM2 status
pm2 status

# Chrome CDP
netstat -ano | findstr :9222

# Token files
ls -la .*_token.json

# Vault contents
ls AI_Employee_Vault/
```

### Common Issues
- **Chrome not posting**: Ensure Chrome is running with CDP and you're logged in
- **Watcher not working**: Check PM2 logs, verify tokens exist
- **MCP not responding**: Test MCP directly, re-authenticate if needed
- **File not created**: Check watcher logs, verify credentials

---

*Quick Reference v1.0 - Last updated 2026-01-12*
