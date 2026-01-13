# AI Employee App - Comprehensive Test Plan

**Date:** 2026-01-13
**Status:** Social Media Verified ✅ | Other Components Ready for Testing

---

## ✅ Already Tested & Working

1. ✅ **LinkedIn Posting** - Full post with enhanced selectors
2. ✅ **Twitter/X Posting** - Short post with paste method
3. ✅ **Instagram Posting** - Image generation + Share button click
4. ✅ **All 16 PM2 Processes** - Running without crashes
5. ✅ **System Health Report** - Generated and saved

---

## 🧪 Ready for Testing - Other Components

### 1. **Email Operations (Gmail MCP)**
**What to Test:**
- Send test email via Gmail MCP
- Verify email appears in sent folder
- Test email drafting functionality
- Check Gmail watcher detects new emails

**How to Test:**
```bash
# Check Gmail watcher is detecting emails
pm2 logs gmail-watcher --lines 20

# Test Gmail MCP (requires Claude Code with Email MCP)
# Ask: "Send a test email to myself with subject 'AI Employee Test'"
```

---

### 2. **Calendar Operations (Calendar MCP)**
**What to Test:**
- Create test calendar event
- Verify event appears in calendar
- Check calendar watcher detects events
- Test event reminder functionality

**How to Test:**
```bash
# Check Calendar watcher status
pm2 logs calendar-watcher --lines 20

# Test Calendar MCP via Claude Code
# Ask: "Create a calendar event tomorrow at 2 PM called 'AI Employee Test'"
```

---

### 3. **Slack Operations (Slack MCP)**
**What to Test:**
- Send test Slack message
- Verify message appears in Slack channel
- Check Slack watcher detects messages
- Test Slack notifications

**How to Test:**
```bash
# Check Slack watcher logs
pm2 logs slack-watcher --lines 20

# Test Slack MCP via Claude Code
# Ask: "Send a message to #general channel: 'AI Employee test message'"
```

---

### 4. **Filesystem Watcher (Inbox Folder)**
**What to Test:**
- Drop test file in `AI_Employee_Vault/Inbox/`
- Verify watcher detects and processes file
- Check file gets moved to `Needs_Action/`
- Test different file types (md, txt, etc.)

**How to Test:**
```bash
# Create test file in Inbox
echo "# Test Task

This is a test task for the AI Employee.

## Task Details
- Priority: High
- Due: Tomorrow
- Assigned: AI Employee

## Actions Needed
- [ ] Action 1
- [ ] Action 2
" > AI_Employee_Vault/Inbox/test_task_$(date +%s).md

# Watch for it to be processed (should move to Needs_Action/)
ls -la AI_Employee_Vault/Needs_Action/
```

---

### 5. **Audit Logging System**
**What to Test:**
- Verify logs are being created daily
- Check log format is correct JSON
- Test log entries for different actions
- Verify 90-day retention is configured

**How to Test:**
```bash
# Check today's audit log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Verify audit log structure
python -c "import json; print(json.load(open('AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json')))"
```

---

### 6. **Approval Workflow (End-to-End)**
**What to Test:**
- Create approval request in `Pending_Approval/`
- Move to `Approved/`
- Verify monitor detects and executes
- Check file moves to `Done/` with summary

**How to Test:**
```bash
# Create test approval request
cat > AI_Employee_Vault/Pending_Approval/TEST_EMAIL_$(date +%s).md << EOF
---
type: email
service: gmail
priority: high
status: pending_approval
created: $(date -Iseconds)
---

## Test Email Approval

This is a test email to verify the approval workflow.

**To:** test@example.com
**Subject:** AI Employee Test Email

**Body:**
This is a test email sent by the AI Employee system to verify the approval workflow is working correctly.
EOF

# Approve it
mv AI_Employee_Vault/Pending_Approval/TEST_EMAIL_*.md AI_Employee_Vault/Approved/

# Watch for execution (should move to Done/)
ls -la AI_Employee_Vault/Done/ | tail -5
```

---

### 7. **WhatsApp Watcher**
**What to Test:**
- Verify WhatsApp session is maintained
- Check for connection errors
- Test message detection (if possible)
- Verify headless mode is working

**How to Test:**
```bash
# Check WhatsApp watcher logs
pm2 logs whatsapp-watcher --lines 30

# Look for authentication status
pm2 logs whatsapp-watcher --err | grep -i "login\|auth"
```

---

### 8. **Scheduled Tasks (Cron Jobs)**
**What to Test:**
- Verify all 5 cron jobs are configured
- Check schedules are correct:
  - daily-briefing: 7 AM daily
  - daily-review: 6 AM weekdays
  - social-media-scheduler: 8 AM Mon/Wed/Fri
  - invoice-review: 5 PM Mondays
  - audit-log-cleanup: 3 AM Sundays
- Test script execution manually

**How to Test:**
```bash
# Test daily briefing manually
python .claude/skills/weekly-briefing/scripts/generate_ceo_briefing.py --vault AI_Employee_Vault

# Test daily review manually
python .claude/skills/daily-review/scripts/generate_daily_plan.py --vault AI_Employee_Vault

# Test audit log cleanup manually
python scripts/cleanup_old_logs.py --vault AI_Employee_Vault --days 90 --dry-run

# Check generated files
ls -la AI_Employee_Vault/Briefings/
ls -la AI_Employee_Vault/Plans/
```

---

### 9. **MCP Servers**
**What to Test:**
- Verify all MCP servers can connect
- Test email-mcp operations
- Test calendar-mcp operations
- Test xero-mcp operations
- Test slack-mcp operations

**How to Test:**
```bash
# Check MCP server status via Claude Code
# Ask: "List all available MCP servers and their status"

# Test Email MCP
# Ask: "Send a test email to myself"

# Test Calendar MCP
# Ask: "List my calendar events for this week"

# Test Slack MCP
# Ask: "List my Slack channels"
```

---

### 10. **Ralph Autonomous Agent**
**What to Test:**
- Test Ralph skill initialization
- Test autonomous task execution loop
- Test task queue processing
- Verify Ralph can use other skills

**How to Test:**
```bash
# Run Ralph skill
/skill ralph

# Or check Ralph documentation
cat .claude/skills/ralph/SKILL.md

# Check Ralph README
cat .claude/skills/ralph/README.md
```

---

### 11. **Error Recovery System**
**What to Test:**
- Verify @with_retry decorator is working
- Test exponential backoff behavior
- Check error categories are handled
- Verify graceful degradation

**How to Test:**
```bash
# Check error recovery in action
pm2 logs gmail-watcher --err | grep -i "retry\|error\|timeout"

# Check retry handler module
python -c "from watchers.error_recovery import ErrorCategory; print('Error recovery OK')"
```

---

### 12. **System Health Dashboard**
**What to Test:**
- Verify Dashboard.md is up to date
- Check all status indicators are correct
- Test dashboard accuracy

**How to Test:**
```bash
# View dashboard
cat AI_Employee_Vault/Dashboard.md

# Compare with actual status
pm2 status
```

---

## 🎯 Priority Testing Order

### **High Priority (Core Functionality)**
1. ✅ Social Media Posting - **DONE**
2. Filesystem Watcher & Inbox Processing
3. Approval Workflow (End-to-End)
4. Email Operations (Gmail MCP)
5. Audit Logging Verification

### **Medium Priority (Important Features)**
6. Calendar Operations (Calendar MCP)
7. Slack Operations (Slack MCP)
8. Scheduled Tasks (Cron Jobs)
9. WhatsApp Watcher

### **Low Priority (Nice to Have)**
10. Ralph Autonomous Agent
11. Xero MCP Integration
12. Advanced Skills Testing

---

## 📋 Testing Checklist

Use this checklist to track testing progress:

- [ ] **Social Media** ✅ COMPLETE
  - [x] LinkedIn posting
  - [x] Twitter/X posting
  - [x] Instagram posting

- [ ] **Core Operations**
  - [ ] Gmail watcher + Email MCP
  - [ ] Calendar watcher + Calendar MCP
  - [ ] Slack watcher + Slack MCP
  - [ ] Filesystem watcher + Inbox drop

- [ ] **Approval Workflow**
  - [ ] Create approval request
  - [ ] Move to Approved/
  - [ ] Monitor executes action
  - [ ] File moves to Done/

- [ ] **Logging & Auditing**
  - [ ] Verify daily log creation
  - [ ] Check log format and content
  - [ ] Test 90-day retention

- [ ] **Scheduled Tasks**
  - [ ] Test daily briefing
  - [ ] Test daily review
  - [ ] Test invoice review
  - [ ] Test log cleanup

- [ ] **Additional Features**
  - [ ] WhatsApp session
  - [ ] Ralph autonomous agent
  - [ ] Xero integration
  - [ ] Error recovery verification

---

## 🚀 Quick Start Testing

### **Option 1: Quick Verification (5 minutes)**
```bash
# 1. Check all processes are running
pm2 status

# 2. Check recent logs
pm2 logs --lines 20 --nostream

# 3. Verify audit logs exist
ls -la AI_Employee_Vault/Logs/

# 4. Test filesystem watcher
echo "# Quick Test" > AI_Employee_Vault/Inbox/quick_test.md
sleep 5
ls -la AI_Employee_Vault/Needs_Action/
```

### **Option 2: Comprehensive Testing (30 minutes)**
Run through each test section above systematically.

### **Option 3: Claude Code Testing**
Use Claude Code to test MCP servers:
```bash
# Ask Claude:
"Test the Gmail MCP by sending a test email"
"Test the Calendar MCP by listing my events"
"Test the Slack MCP by listing channels"
```

---

## 📊 Test Results Template

After testing, document results:

```
Test Component: _____________
Status: [ ] Pass [ ] Fail [ ] Partial
Notes: _____________
Screenshot/File: _____________
Date: _____________
```

---

**Ready to begin testing! Which component would you like to test first?**
