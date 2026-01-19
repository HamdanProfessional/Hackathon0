# Troubleshooting Guide

**AI Employee v1.4.1**

---

## Table of Contents

- [System Issues](#system-issues)
- [Watchers](#watchers)
- [Approval Monitors](#approval-monitors)
- [Social Media](#social-media)
- [Chrome Automation](#chrome-automation)
- [PM2](#pm2)
- [Common Errors](#common-errors)

---

## System Issues

### PM2 shows 0 processes running

**Symptom:**
```
pm2 status
┌────┬───────────┬─────────┬──────────┐
│ id │ name      │ status │ ...     │
└────┴───────────┴─────────┴──────────┘
(empty table)
```

**Solution:**

```bash
# Start PM2 processes
pm2 start process-manager/pm2.config.js

# Wait and check status
pm2 status

# If errors, check logs
pm2 logs --err
```

### All processes showing "errored"

**Symptom:**
```
│ id │ name      │ status │ ...     │
│ 18 │ dashboard│ errored │ ...     │
```

**Solution:**

```bash
# Check error logs
pm2 logs dashboard --err

# Common issue: Dashboard port 3000 already in use
# Kill process on port 3000 or change port in config

# Restart specific process
pm2 restart ai-employee-dashboard
```

### Processes keep restarting

**Symptom:**
```
│ id │ name      │ ↺  │
│  5 │ watcher   │ 10+ │ (high restart count)
```

**Solution:**

```bash
# Check error logs
pm2 logs name --err --lines 50

# Common fixes:
# 1. Fix Python path issues
# 2. Fix import errors
# 3. Reset restart count
pm2 reset name
```

---

## Watchers

### Gmail Watcher not creating files

**Symptom:** No new files in `Needs_Action/`

**Debug:**

```bash
# Check if watcher is running
pm2 logs gmail-watcher --lines 20

# Test manually
python -m watchers.gmail_watcher --vault AI_Employee_Vault --once
```

**Common Fixes:**

1. **Check OAuth token**
   - Delete `.gmail_token.json`
   - Re-run watcher to initiate OAuth flow

2. **Check credentials**
   ```bash
   ls mcp-servers/email-mcp/credentials.json
   ```

3. **Check API quota**
   - Wait and try again

### Calendar Watcher not working

**Symptom:** No calendar files created

**Debug:**

```bash
pm2 logs calendar-watcher --lines 20
python -m watchers.calendar_watcher --vault AI_Employee_Vault --once
```

**Fix:** Delete `.calendar_token.json` and re-authenticate

### Slack Watcher not monitoring

**Symptom:** Slack messages not detected

**Debug:**

```bash
pm2 logs slack-watcher --lines 20
```

**Fix:** Check bot token:
```bash
echo $SLACK_BOT_TOKEN
```

---

## Approval Monitors

### Files stuck in Approved/ folder

**Symptom:** Files in `Approved/` not being processed

**Debug:**

```bash
# Check monitor logs
pm2 logs linkedin-approval-monitor --lines 50
```

**Common Fixes:**

1. **Chrome CDP not running**
   ```bash
   curl http://localhost:9222/json/version
   # If error, start: start_chrome.bat
   ```

2. **Not logged in**
   - Open Chrome automation window
   - Navigate to platform
   - Log in manually

3. **Monitor crashed**
   ```bash
   pm2 restart linkedin-approval-monitor
   ```

### Auto-approver making wrong decisions

**Symptom:** Items auto-approved when should be manual

**Debug:**

```bash
pm2 logs auto-approver --lines 50
```

**Fix:** Adjust criteria in auto_approver.py or move to manual-only mode

---

## Social Media

### LinkedIn post not appearing

**Symptom:** Post approved but not showing on LinkedIn

**Checklist:**

1. **Chrome CDP running?**
   ```bash
   curl http://localhost:9222/json/version
   ```

2. **Logged into LinkedIn?**
   - Check Chrome automation window
   - Navigate to linkedin.com
   - Verify logged in state

3. **Dry-run mode off?**
   ```bash
   echo $LINKEDIN_DRY_RUN  # Should be "false"
   ```

4. **Monitor status:**
   ```bash
   pm2 logs linkedin-approval-monitor --lines 50
   ```

### Instagram post failing

**Symptom:** Error when posting to Instagram

**Fixes:**

1. **Image generation failed**
   - Check permissions
   - Verify PIL/Pillow installed

2. **Caption too long**
   - Instagram limit: 2,200 characters

3. **Not logged in**
   - Open Chrome automation
   - Log into instagram.com

### Twitter post truncated

**Symptom:** Post cut off at 280 characters

**This is expected behavior.** Twitter limit is 280 characters.

---

## Chrome Automation

### Chrome CDP port 9222 not available

**Symptom:**
```
curl http://localhost:9222/json/version
curl: (7) Failed to connect
```

**Fix:**

```bash
# Kill all Chrome processes
taskkill /F /IM chrome.exe /T

# Start Chrome CDP
start_chrome.bat

# Verify
curl http://localhost:9222/json/version
```

### Chrome opens wrong profile

**Symptom:** Chrome opens to a different user profile

**Fix:** Check path in `start_chrome.bat`:
```batch
chrome.exe "--user-data-dir=C:\Users\User\AppData\Local\Google\Chrome\User Data" --remote-debugging-port=9222
```

**Note:** Quote the ENTIRE parameter including flag name, not just path.

### Chrome not logging in

**Symptom:** Need to log in every time Chrome restarts

**Fix:** Save Chrome user data after logging in once. Chrome should preserve session.

---

## PM2

### Module not found errors

**Symptom:**
```
ModuleNotFoundError: No module named 'watchers'
```

**Fixes:**

1. **Check PYTHONPATH in PM2 config**
   ```javascript
   env: {
     PYTHONPATH: path.join(PROJECT_ROOT)
   }
   ```

2. **Restart process**
   ```bash
   pm2 restart process-name
   ```

### Process exit code 1

**Symptom:** Process exits immediately

**Debug:**

```bash
pm2 logs process-name --err
```

**Common Fixes:**

1. **Script not found** - Check file path in PM2 config
2. **Import error** - Fix Python imports
3. **Permission denied** - Check file permissions

### PM2 daemon not running

**Symptom:**
```
PM2 Error: PM2 not running
```

**Fix:**

```bash
# Kill existing PM2 daemon
taskkill /F /IM pm2.exe /T

# Start fresh
pm2 start process-manager/pm2.config.js
pm2 save
```

---

## Common Errors

### `KeyError: 'ANTHROPIC_API_KEY'`

**Cause:** Environment variable not set

**Fix:**

```bash
# Set in current session
export ANTHROPIC_API_KEY=your-key-here

# Add to PM2 config for persistence
# Add to env section in pm2.config.js:
# "ANTHROPIC_AUTH_TOKEN": "your-key-here"
```

### `PermissionError: [Errno 13] Permission denied`

**Cause:** Vault folder not writable

**Fix:**

```bash
# Check permissions
ls -la AI_Employee_Vault/

# Fix permissions
chmod -R u+rw AI_Employee_Vault/
```

### `ModuleNotFoundError: No module named 'skills'`

**Cause:** Wrong Python path calculation

**Fix:** Scripts in `.claude/skills/skill-name/scripts/` need to go up 5 levels to project root

### `OSError: [Errno 2] No such file or directory`

**Cause:** Vault folder doesn't exist

**Fix:**

```bash
# Create vault folder
mkdir -p AI_Employee_Vault
mkdir -p AI_Employee_Vault/{Needs_Action,Pending_Approval,Approved,Rejected,Done,Plans,Logs,Briefings}
```

---

## Getting Help

### Check Logs First

Always check logs before debugging:

```bash
# System logs
pm2 logs

# Specific process
pm2 logs process-name

# Error logs only
pm2 logs --err
```

### Documentation

- `README.md` - Main documentation
- `ARCHITECTURE.md` - System architecture
- `QUICKSTART.md` - Quick start guide

### Support

1. Check this guide
2. Check system logs
3. Check main README
4. Review architecture docs

---

## Still Stuck?

### Reset Everything

```bash
# Stop all
pm2 delete all

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Start fresh
pm2 start process-manager/pm2.config.js
pm2 save
```

### Get System Status

```bash
# PM2 status
pm2 status

# Vault contents
ls AI_Employee_Vault/

# Recent logs
tail -50 AI_Employee_Vault/Logs/*.json
```

---

**Last Updated:** 2025-01-19
