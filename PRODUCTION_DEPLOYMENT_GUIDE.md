# Production Deployment Guide - AI Employee System

**Date:** 2026-01-13
**Status:** Ready for Production
**System Version:** v1.2

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Starting the System](#starting-the-system)
4. [Monitoring & Management](#monitoring--management)
5. [Production Checklist](#production-checklist)
6. [Troubleshooting](#troubleshooting)
7. [Stopping the System](#stopping-the-system)

---

## Prerequisites

### Required Software

```bash
# Check Python (3.13+)
python --version

# Check Node.js (v24+ LTS)
node --version

# Check PM2 (should be installed)
npm list -g pm2
```

### Install PM2 (if not installed)

```bash
# Install PM2 globally
npm install -g pm2

# Verify installation
pm2 --version
```

### Install Python Dependencies

```bash
# Install required Python packages
pip install playwright
pip install watchdog
pip install google-api-python-client
pip install google-auth-oauthlib
pip install slack-sdk

# Install Playwright browsers (for WhatsApp/Social Media)
playwright install chromium
```

---

## Initial Setup

### Step 1: Configure Environment Variables

```bash
# Navigate to project root
cd C:\Users\User\Desktop\AI_Employee_Vault

# Check if .env exists (should be in .gitignore)
ls .env

# If not exists, create from example (if you have one)
# cp .env.example .env
```

### Step 2: Verify Authentication Tokens

```bash
# Check Gmail token (should exist and be valid)
ls -la .gmail_token.json

# Check Calendar token (should exist and be valid)
ls -la .calendar_token.json

# Check Slack token
ls -la mcp-servers/slack-mcp/.slack_mcp_token.json

# Check Xero token
ls -la mcp-servers/xero-mcp/.xero_mcp_token.json
```

**Expected Status:**
- ✅ `.gmail_token.json` - Present, valid until 2026-01-12 20:22:27 UTC
- ✅ `.calendar_token.json` - Present, valid until 2026-01-12 20:30:08 UTC
- ✅ `mcp-servers/slack-mcp/.slack_mcp_token.json` - Present
- ✅ `mcp-servers/xero-mcp/.xero_mcp_token.json` - Present

### Step 3: Verify MCP Servers are Built

```bash
# Check all MCP servers have dist/ folders
ls mcp-servers/email-mcp/dist/
ls mcp-servers/calendar-mcp/dist/
ls mcp-servers/slack-mcp/dist/
ls mcp-servers/xero-mcp/dist/
```

**Expected:** All 4 MCP servers should have `dist/index.js` files.

### Step 4: Update PM2 Configuration (Optional)

Review `process-manager/pm2.config.js` and adjust if needed:

```javascript
// Edit configuration
nano process-manager/pm2.config.js

// Key settings to review:
// - Vault paths (should be AI_Employee_Vault)
// - Token file paths
// - Check intervals
// - Cron schedules
```

### Step 5: (Optional) Remove Dry-Run Flags for Production

**⚠️ WARNING:** Only do this after thorough testing!

Edit approval monitors in `process-manager/pm2.config.js`:

```javascript
// Find lines like:
args: "--vault AI_Employee_Vault --dry-run",

// Change to:
args: "--vault AI_Employee_Vault",

// ⚠️ Do this for each monitor you want to make live:
// - email-approval-monitor (line 107)
// - calendar-approval-monitor (line 122)
// - slack-approval-monitor (line 137)
// - linkedin-approval-monitor (line 153)
// - twitter-approval-monitor (line 168)
// - meta-approval-monitor (line 183)
```

**Environment Variable Alternative:**
```bash
# Set environment variables for live posting
export TWITTER_DRY_RUN=false
export META_DRY_RUN=false
export LINKEDIN_DRY_RUN=false
```

---

## Starting the System

### Option 1: Start All Processes (Recommended)

```bash
# Navigate to project root
cd C:\Users\User\Desktop\AI_Employee_Vault

# Start all processes (watchers + monitors + cron jobs)
pm2 start process-manager/pm2.config.js

# Check status
pm2 status

# Expected output:
# ┌────┬─────────────────────────────┬─────────┬─────┬─────────┬──────────┬──────────┐
# │ ID │ Name                        │ Status  │ CPU │ Memory │ Restarts │ Uptime   │
# ├────┼─────────────────────────────┼─────────┼─────┼─────────┼──────────┼──────────┤
# │ 0  │ gmail-watcher               │ online  │ 0%  │ 150MB   │ 0        │ 0:00:05  │
# │ 1  │ calendar-watcher            │ online  │ 0%  │ 145MB   │ 0        │ 0:00:05  │
# │ 2  │ slack-watcher               │ online  │ 0%  │ 140MB   │ 0        │ 0:00:05  │
# │ 3  │ filesystem-watcher          │ online  │ 0%  │ 120MB   │ 0        │ 0:00:05  │
# │ 4  │ email-approval-monitor      │ online  │ 0%  │ 130MB   │ 0        │ 0:00:05  │
# │ 5  │ calendar-approval-monitor   │ online  │ 0%  │ 125MB   │ 0        │ 0:00:05  │
# │ 6  │ slack-approval-monitor      │ online  │ 0%  │ 125MB   │ 0        │ 0:00:05  │
# │ 7  │ linkedin-approval-monitor   │ online  │ 0%  │ 130MB   │ 0        │ 0:00:05  │
# │ 8  │ twitter-approval-monitor    │ online  │ 0%  │ 125MB   │ 0        │ 0:00:05  │
# │ 9  │ meta-approval-monitor       │ online  │ 0%  │ 125MB   │ 0        │ 0:00:05  │
# │ 10 │ whatsapp-watcher            │ stopped │ 0%  │ 0MB     │ 0        │ 0:00:00  │
# └────┴─────────────────────────────┴─────────┴─────┴─────────┴──────────┴──────────┘
```

**Note:** WhatsApp watcher is configured but commented out by default (requires Playwright setup and manual login).

### Option 2: Start Watchers Only (Manual Approval)

```bash
# Start only the 4 main watchers
pm2 start process-manager/pm2.config.js --only gmail-watcher,calendar-watcher,slack-watcher,filesystem-watcher

# Start approval monitors manually when ready
pm2 start process-manager/pm2.config.js --only email-approval-monitor
pm2 start process-manager/pm2.config.js --only calendar-approval-monitor
pm2 start process-manager/pm2.config.js --only slack-approval-monitor
```

### Option 3: Start Specific Process

```bash
# Start just Gmail watcher
pm2 start process-manager/pm2.config.js --only gmail-watcher

# Start just email approval monitor
pm2 start process-manager/pm2.config.js --only email-approval-monitor
```

### Save PM2 Configuration

```bash
# Save current process list
pm2 save

# Set up PM2 to start on system boot
pm2 startup

# Follow the instructions (copy-paste the command it gives you)
# Example: sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u yourusername --hp /home/yourusername
```

---

## Monitoring & Management

### Check System Status

```bash
# Show all processes
pm2 status

# Show detailed information
pm2 show gmail-watcher

# Show monitoring dashboard
pm2 monit
```

### View Logs

```bash
# View all logs in real-time
pm2 logs

# View logs for specific process
pm2 logs gmail-watcher

# View last 100 lines
pm2 logs gmail-watcher --lines 100

# View only errors
pm2 logs --err

# View logs by date
pm2 logs --timestamp
```

### Log Files Location

```bash
# PM2 logs are stored here:
~/.pm2/logs/

# Specific log files:
~/.pm2/logs/gmail-watcher-out.log
~/.pm2/logs/gmail-watcher-error.log
~/.pm2/logs/email-approval-monitor-out.log
~/.pm2/logs/email-approval-monitor-error.log

# Your audit logs are here:
AI_Employee_Vault/Logs/2026-01-13.json
```

### Restart Processes

```bash
# Restart specific process
pm2 restart gmail-watcher

# Restart all processes
pm2 restart all

# Reset restart count (good for monitoring)
pm2 reset gmail-watcher
```

### Stop Processes

```bash
# Stop specific process
pm2 stop gmail-watcher

# Stop all processes
pm2 stop all

# Delete process from PM2 list
pm2 delete gmail-watcher

# Delete all processes
pm2 delete all
```

---

## Production Checklist

### Before Going Live

- [ ] **Test all watchers in dry-run mode**
  ```bash
  python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --once
  python -m watchers.slack_watcher --vault AI_Employee_Vault --once
  ```

- [ ] **Verify MCP authentication**
  ```bash
  cat .gmail_token.json
  cat .calendar_token.json
  cat mcp-servers/slack-mcp/.slack_mcp_token.json
  ```

- [ ] **Test approval workflow**
  - Create test file in `AI_Employee_Vault/Pending_Approval/`
  - Move to `AI_Employee_Vault/Approved/`
  - Verify it executes and moves to `AI_Employee_Vault/Done/`

- [ ] **Remove --dry-run flags** (if ready for live posting)
  - Edit `process-manager/pm2.config.js`
  - OR set environment variables

- [ ] **Configure PM2 startup**
  ```bash
  pm2 save
  pm2 startup
  ```

- [ ] **Set up log rotation** (optional but recommended)
  ```bash
  pm2 install pm2-logrotate
  ```

- [ ] **Monitor initial startup**
  ```bash
  pm2 logs
  # Watch for errors in first 5 minutes
  ```

### Daily Operations

- [ ] **Check dashboard daily**
  - Open `AI_Employee_Vault/Dashboard.md` in Obsidian
  - Review pending items

- [ ] **Review approval queue**
  - Check `AI_Employee_Vault/Pending_Approval/`
  - Approve or reject items

- [ ] **Check PM2 status**
  ```bash
  pm2 status
  # Look for processes with high restart counts
  ```

- [ ] **Review error logs**
  ```bash
  pm2 logs --err --lines 50
  ```

- [ ] **Backup vault** (automatic if using GitHub/sync)
  ```bash
  cd AI_Employee_Vault
  git add .
  git commit -m "Daily backup"
  git push
  ```

### Weekly Maintenance

- [ ] **Review audit logs**
  ```bash
  # Review this week's activity
  cat AI_Employee_Vault/Logs/2026-01-*.json
  ```

- [ ] **Check Briefings folder**
  - Review CEO briefings in `AI_Employee_Vault/Briefings/`

- [ ] **Clean up Done folder**
  - Archive old completed items
  - Keep recent items for reference

- [ ] **Update Business_Goals.md**
  - Adjust targets based on performance
  - Update metrics

---

## Troubleshooting

### Issue: Watcher Not Starting

**Symptom:** Process shows "errored" status

**Solution:**
```bash
# Check error logs
pm2 logs gmail-watcher --err

# Common issues:
# 1. Token expired -> Delete token file, re-authenticate
# 2. Missing dependency -> pip install <package>
# 3. Wrong vault path -> Update pm2.config.js
```

### Issue: Process Keeps Restarting

**Symptom:** High restart count in `pm2 status`

**Solution:**
```bash
# Check logs for crash reason
pm2 logs <process-name> --lines 100

# Reset restart count
pm2 reset <process-name>

# If crashing continues, stop the process
pm2 stop <process-name>
```

### Issue: Gmail/Calendar Token Expired

**Symptom:** Authentication errors in logs

**Solution:**
```bash
# Delete old token
rm .gmail_token.json
# OR
rm .calendar_token.json

# Restart watcher - will trigger OAuth flow
pm2 restart gmail-watcher
```

### Issue: Watcher Runs But No Files Created

**Symptom:** Process online but nothing in Needs_Action/

**Solution:**
```bash
# Run watcher manually with --once flag to see output
python -m watchers.gmail_watcher --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json --once

# Check for:
# - No new messages (normal)
# - API errors (check logs)
# - Filter too restrictive (check keywords)
```

### Issue: Social Media Posting Fails

**Symptom:** Approval file moves to Done but nothing posted

**Solution:**
```bash
# Check poster script logs
pm2 logs linkedin-approval-monitor --err

# Common issues:
# 1. Chrome not running with CDP -> Start Chrome with --remote-debugging-port=9222
# 2. Not logged in -> Manually log in to platform
# 3. DRY_RUN still enabled -> Check pm2.config.js args
```

### Issue: PM2 Won't Start on Boot

**Symptom:** Processes don't start after reboot

**Solution:**
```bash
# Re-run startup command
pm2 startup

# Save configuration
pm2 save

# Verify startup script is enabled
systemctl status pm2-root  # Linux
# OR check launchctl list | grep pm2  # macOS
```

---

## Stopping the System

### Graceful Shutdown

```bash
# Stop all processes
pm2 stop all

# Wait for processes to finish current tasks
sleep 10

# Save final state
pm2 save
```

### Emergency Stop

```bash
# Stop everything immediately
pm2 delete all

# Verify nothing is running
pm2 status
# Should show "No processes found"
```

### Disable PM2 Startup

```bash
# Remove PM2 from system startup
pm2 unstartup

# Verify
systemctl disable pm2-root  # Linux
# OR remove from launchctl  # macOS
```

---

## Performance Tuning

### Memory Optimization

```javascript
// Edit process-manager/pm2.config.js
{
  name: "gmail-watcher",
  max_memory_restart: "300M",  // Reduce from 500M
  node_args: "--max-old-space-size=256"  // Limit memory
}
```

### CPU Optimization

```bash
# Set process priority (Linux/macOS)
pm2 start process-manager/pm2.config.js --watch-delay 1000

# Reduce check frequency (if system is too responsive)
# Edit individual watcher configs in pm2.config.js
```

### Log Rotation

```bash
# Install pm2-logrotate
pm2 install pm2-logrotate

# Configure rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

---

## Security Best Practices

### Credential Management

```bash
# NEVER commit these files:
.env
.gmail_token.json
.calendar_token.json
mcp-servers/slack-mcp/.slack_mcp_token.json
mcp-servers/xero-mcp/.xero_mcp_token.json

# Verify .gitignore
cat .gitignore | grep token
```

### Firewall Rules

```bash
# Only allow outbound HTTPS (if using firewall)
# Block inbound connections except SSH
# PM2 runs on localhost, no external access needed
```

### Regular Updates

```bash
# Update PM2 monthly
npm update -g pm2

# Update Python dependencies monthly
pip install --upgrade playwright watchdog google-api-python-client
```

---

## Quick Reference Commands

```bash
# Start system
pm2 start process-manager/pm2.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Restart process
pm2 restart <name>

# Stop system
pm2 stop all

# Save configuration
pm2 save

# System startup
pm2 startup

# Monitor dashboard
pm2 monit

# Flush logs
pm2 flush

# Reset restarts
pm2 reset all
```

---

## Support & Resources

### Log Locations

- **PM2 Logs:** `~/.pm2/logs/`
- **Audit Logs:** `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **System Logs:** Check individual process logs in PM2

### Configuration Files

- **PM2 Config:** `process-manager/pm2.config.js`
- **Vault:** `AI_Employee_Vault/`
- **Skills:** `.claude/skills/`
- **Watchers:** `watchers/`
- **MCP Servers:** `mcp-servers/`

### Documentation

- **Project Instructions:** `CLAUDE.md`
- **Requirements:** `docs/hackathon0.md`
- **Test Reports:** `*_TEST_REPORT.md`
- **Status Reports:** `*_SYSTEM_CHECK.md`, `*_REQUIREMENTS_STATUS.md`

---

## Conclusion

Your AI Employee system is **production-ready** and can be deployed immediately using PM2. The system is designed for:

- ✅ **24/7 Operation** - All watchers run continuously
- ✅ **Auto-Recovery** - PM2 restarts crashed processes
- ✅ **Graceful Degradation** - Error recovery on all API watchers
- ✅ **Audit Trail** - All actions logged
- ✅ **Human Oversight** - Approval workflow for sensitive actions
- ✅ **Scheduled Tasks** - Cron jobs for periodic operations

**Recommended First Step:**

```bash
# 1. Start with dry-run mode enabled
pm2 start process-manager/pm2.config.js

# 2. Monitor for 24 hours
pm2 logs
pm2 monit

# 3. Review actions in vault
# Open AI_Employee_Vault/ in Obsidian

# 4. If satisfied, remove --dry-run flags for live posting
# Edit process-manager/pm2.config.js

# 5. Save and monitor
pm2 save
pm2 startup
```

---

*Production Deployment Guide - 2026-01-13*
*AI Employee System v1.2*
*100% Gold Tier Complete*
*Ready for Production*
