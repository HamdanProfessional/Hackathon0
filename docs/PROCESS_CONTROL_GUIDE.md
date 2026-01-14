# AI Employee App - Process Control Guide

**Complete guide to managing 16 PM2 processes for the AI Employee App**

---

## 📚 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Starting the System](#starting-the-system)
3. [Checking Status](#checking-status)
4. [Viewing Logs](#viewing-logs)
5. [Restarting Processes](#restarting-processes)
6. [Stopping Processes](#stopping-processes)
7. [Saving Configuration](#saving-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Process Reference](#process-reference)
10. [Common Workflows](#common-workflows)

---

## Quick Reference

**Essential Commands:**
```bash
# Start all processes
pm2 start process-manager/pm2.config.js && pm2 save

# Check status
pm2 status

# View all logs
pm2 logs

# Restart all
pm2 restart all

# Stop all
pm2 stop all

# Save configuration
pm2 save
```

---

## Starting the System

### Start All Processes (16 total)

```bash
cd "C:\Users\User\Desktop\AI_EMPLOYEE_APP"
pm2 start process-manager/pm2.config.js
pm2 save
```

**Output:** 16 processes launched
- 11 continuous processes (running 24/7)
- 5 scheduled processes (triggered by cron)

### Start Individual Process

```bash
# Watchers (5 processes)
pm2 start gmail-watcher
pm2 start calendar-watcher
pm2 start slack-watcher
pm2 start filesystem-watcher
pm2 start whatsapp-watcher

# Approval Monitors (6 processes)
pm2 start email-approval-monitor
pm2 start calendar-approval-monitor
pm2 start slack-approval-monitor
pm2 start linkedin-approval-monitor
pm2 start twitter-approval-monitor
pm2 start meta-approval-monitor

# Cron Jobs (5 processes)
pm2 start daily-briefing
pm2 start daily-review
pm2 start social-media-scheduler
pm2 start invoice-review
pm2 start audit-log-cleanup
```

### Start from Configuration File

```bash
pm2 start process-manager/pm2.config.js
```

**What it does:** Reads `process-manager/pm2.config.js` and starts all 16 processes defined in the file.

---

## Checking Status

### Show All Processes

```bash
pm2 status
```

**Shows:** Process name, PID, uptime, restart count, status, CPU%, memory

**Example Output:**
```
┌────┬───────────┬─────────┬─────────┬──────────┬──────┬───────────┐
│ id │ name      │ status  │ memory  │ restarts │ cpu  │ status    │
├────┼───────────┼─────────┼─────────┼──────────┼──────┼───────────┤
│ 0  │ gmail-watcher     │ online  │ 34.7mb  │ 0    │ 0%   │ ✓         │
│ 10 │ meta-appr         │ online  │ 20.9mb  │ 0    │ 0%   │ ✓         │
└────┴───────────┴─────────┴─────────┴──────────┴──────┴───────────┘
```

### Show Simple List

```bash
pm2 list
```

**Shows:** Clean table format without extra formatting

### Check Specific Process

```bash
pm2 status gmail-watcher
pm2 status meta-approval-monitor
pm2 status linkedin-approval-monitor
pm2 status twitter-approval-monitor
```

### Show Process Details

```bash
pm2 show gmail-watcher
pm2 show meta-approval-monitor
```

**Shows:** Full process details including configuration, environment variables, script path

---

## Viewing Logs

### All Logs (Real-time Tail)

```bash
pm2 logs
```

**Follows all process logs in real-time**

### Specific Process Logs

```bash
# Watcher logs
pm2 logs gmail-watcher
pm2 logs calendar-watcher
pm2 logs slack-watcher
pm2 logs filesystem-watcher
pm2 logs whatsapp-watcher

# Approval monitor logs
pm2 logs email-approval-monitor
pm2 logs calendar-approval-monitor
pm2 logs slack-approval-monitor
pm2 logs linkedin-approval-monitor
pm2 logs twitter-approval-monitor
pm2 logs meta-approval-monitor
```

### Error Logs Only

```bash
pm2 logs gmail-watcher --err
pm2 logs meta-approval-monitor --err
pm2 logs linkedin-approval-monitor --err
```

### View Last N Lines

```bash
pm2 logs meta-approval-monitor --lines 50
pm2 logs linkedin-approval-monitor --lines 20
pm2 logs gmail-watcher --lines 100
```

### View Logs Without Tail (Don't Follow)

```bash
pm2 logs meta-approval-monitor --nostream
```

**Use case:** Check recent logs without following new output

### Clear Logs

```bash
pm2 flush
```

**What it does:** Clears all log files

---

## Restarting Processes

### Restart All Processes

```bash
pm2 restart all
```

### Restart Individual Process

```bash
pm2 restart gmail-watcher
pm2 restart meta-approval-monitor
pm2 restart linkedin-approval-monitor
pm2 restart twitter-approval-monitor
```

### Reload (Zero Downtime Restart)

```bash
pm2 reload all
pm2 reload meta-approval-monitor
```

**What it does:** Restarts process without dropping connections

### Reload with Graceful Shutdown

```bash
pm2 reload all ---graceful
```

---

## Stopping Processes

### Stop All Processes

```bash
pm2 stop all
```

**What it does:** Stops all 16 processes but keeps them in PM2's list

### Stop Individual Process

```bash
pm2 stop gmail-watcher
pm2 stop meta-approval-monitor
pm2 stop linkedin-approval-monitor
```

### Stop and Delete Process

```bash
pm2 delete gmail-watcher
pm2 delete meta-approval-monitor
```

**What it does:** Stops and removes process from PM2's list

### Delete All Processes

```bash
pm2 delete all
```

**Warning:** This removes all processes from PM2's list. You'll need to restart them from the config file.

---

## Saving Configuration

### Save Current Process List

```bash
pm2 save
```

**What it does:** Saves current process list to `C:\Users\User\.pm2\dump.pm2`

**Why:** Ensures processes restart on system reboot

### Save After Every Change

```bash
pm2 stop gmail-watcher
pm2 start gmail-watcher
pm2 save  # Don't forget this!
```

---

## Troubleshooting

### Process Not Starting

**Problem:** Process won't start or immediately stops

```bash
# Check PM2 logs
pm2 logs --err

# Check process-specific logs
pm2 logs gmail-watcher --err

# Check if port is in use
netstat -ano | grep :9222

# Try starting with more verbose output
pm2 start process-manager/pm2.config.js --no-daemon
```

### Process Crashing

**Problem:** Process keeps restarting

```bash
# Check restart count
pm2 status

# Check error logs
pm2 logs <process-name> --err

# Check memory usage
pm2 monit

# Increase max memory limit
pm2 start <process-name> --max-memory-restart 1G
```

### High Memory Usage

**Problem:** Process using too much memory

```bash
# Check memory usage
pm2 status

# Monitor in real-time
pm2 monit

# Restart process
pm2 restart <process-name>
```

### Process Won't Stop

**Problem:** `pm2 stop` not working

```bash
# Force kill
pm2 delete <process-name>

# Or kill by PID
pm2 kill <pid>
```

---

## Process Reference

### Watchers (Continuous - 5 total)

| Process | Purpose | Script | Memory |
|---------|---------|--------|--------|
| `gmail-watcher` | Monitors Gmail for important emails | `run_gmail_watcher.py` | 500MB |
| `calendar-watcher` | Monitors Calendar for upcoming events | `run_calendar_watcher.py` | 500MB |
| `slack-watcher` | Monitors Slack for important messages | `run_slack_watcher.py` | 500MB |
| `filesystem-watcher` | Watches Inbox/ folder for new files | `run_filesystem_watcher.py` | 500MB |
| `whatsapp-watcher` | Monitors WhatsApp for keywords | `run_whatsapp_watcher.py` | 500MB |

**Status:** All run continuously (24/7) with auto-restart

---

### Approval Monitors (Continuous - 6 total)

| Process | Purpose | Script | Memory |
|---------|---------|--------|--------|
| `email-approval-monitor` | Sends approved emails via Gmail MCP | `email_approval_monitor.py` | 300MB |
| `calendar-approval-monitor` | Creates calendar events via Calendar MCP | `calendar_approval_monitor.py` | 300MB |
| `slack-approval-monitor` | Sends Slack messages via Slack MCP | `slack_approval_monitor.py` | 300MB |
| `linkedin-approval-monitor` | Posts to LinkedIn (0.3s per post) | `linkedin_approval_monitor.py` | 300MB |
| `twitter-approval-monitor` | Posts to Twitter/X (0.3s per post) | `twitter_approval_monitor.py` | 300MB |
| `meta-approval-monitor` | Posts to Instagram/Facebook with professional images | `meta_approval_monitor.py` | 300MB |

**Status:** All run continuously (24/7) with auto-restart
**Monitoring:** Watch `AI_Employee_Vault/Approved/` folder

---

### Scheduled Tasks (Cron Jobs - 5 total)

| Process | Schedule | Purpose | Script |
|---------|----------|---------|--------|
| `daily-briefing` | 7 AM daily | Generate daily CEO briefing | weekly-briefing skill |
| `daily-review` | 6 AM Mon-Fri | Generate daily review | daily-review skill |
| `social-media-scheduler` | 8 AM Mon/Wed/Fri | Generate social media content | social-media-manager skill |
| `invoice-review` | 5 PM Mondays | Check overdue invoices | xero-manager skill |
| `audit-log-cleanup` | 3 AM Sundays | Clean logs older than 90 days | cleanup script |

**Status:** Run on schedule (not continuous)
**Note:** These show as "stopped" in `pm2 status` - this is normal

---

## Common Workflows

### 1. Daily Startup

```bash
# Start all processes
pm2 start process-manager/pm2.config.js

# Save configuration (persists after reboot)
pm2 save

# Check status
pm2 status
```

**Expected Output:** 11 processes "online", 5 processes "stopped" (scheduled - normal)

---

### 2. System Health Check

```bash
# Check all processes
pm2 status

# View recent logs
pm2 logs --lines 10

# Monitor resources
pm2 monit
```

**What to Look For:**
- Restart count: 0 is good, high count indicates problems
- Memory usage: Should be under 500MB for most processes
- CPU usage: Should be under 20% normally
- Status: "online" is good, "errored" is bad

---

### 3. Restart Social Media Monitors

```bash
# Restart all social media monitors
pm2 restart linkedin-approval-monitor
pm2 restart twitter-approval-monitor
pm2 restart meta-approval-monitor
```

**When to Use:** After posting issues, after code changes, after configuration updates

---

### 4. View Social Media Logs

```bash
# LinkedIn logs
pm2 logs linkedin-approval-monitor --lines 20

# Twitter logs
pm2 logs twitter-approval-monitor --lines 20

# Instagram/Facebook logs
pm2 logs meta-approval-monitor --lines 20
```

**When to Use:** Troubleshooting posting issues, verifying posts

---

### 5. Stop All for Maintenance

```bash
# Stop all processes
pm2 stop all

# Save state
pm2 save
```

**When to Use:** System maintenance, code updates, configuration changes

---

### 6. Start After Maintenance

```bash
# Start all from config
pm2 start process-manager/pm2.config.js

# Save configuration
pm2 save

# Verify status
pm2 status
```

---

### 7. Restart Everything

```bash
# Restart all processes
pm2 restart all

# Flush logs
pm2 flush
```

**When to Use:** After system changes, to clear memory issues

---

### 8. Monitor Approval Workflow

```bash
# Terminal 1: Watch for approved files
pm2 logs meta-approval-monitor

# Terminal 2: Watch LinkedIn posting
pm2 logs linkedin-approval-monitor

# Terminal 3: Watch Twitter posting
pm2 logs twitter-approval-monitor
```

**When to Use:** Testing approval workflow, debugging posting

---

### 9. Troubleshoot Posting Issues

```bash
# 1. Check monitor status
pm2 status | grep -E "linkedin|twitter|meta"

# 2. Check monitor logs
pm2 logs linkedin-approval-monitor --lines 20
pm2 logs twitter-approval-monitor --lines 20
pm2 logs meta-approval-monitor --lines 20

# 3. Restart monitors
pm2 restart linkedin-approval-monitor
pm2 restart twitter-approval-monitor
pm2 restart meta-approval-monitor

# 4. Check Chrome automation
# Verify Chrome is running with CDP on port 9222
# Verify you're logged into platforms in Chrome window
```

---

## Understanding the Output

### pm2 status Fields

| Field | Description | Good Value |
|-------|-------------|------------|
| **id** | Process ID number | Any |
| **name** | Process name | Unique |
| **status** | Process state | `online` ✓ |
| **memory** | RAM usage | < 500MB |
| **restarts** | Restart count | 0 (low) |
| **cpu** | CPU usage | < 20% |
| **uptime** | Time since last restart | Any |

### Status Values

- **online** ✓ - Process running normally
- **stopped** - Process intentionally stopped (normal for scheduled tasks)
- **errored** - Process crashed (check logs)
- **stopping** - Process shutting down
- **launching** - Process starting up

---

## Advanced Commands

### Monitor Resources in Real-Time

```bash
pm2 monit
```

**Shows:** Real-time CPU and memory usage for all processes

---

### Reset Restart Count

```bash
pm2 reset meta-approval-monitor
```

**When to Use:** After fixing a crash, to clear high restart count

---

### Generate Startup Script

```bash
pm2 startup
```

**What it does:** Creates a startup script for auto-start on system boot

**Platform Support:**
- Linux: systemd, upstart, rc.d
- Windows: Startup folder
- macOS: launchd

---

### Dump Process List

```bash
pm2 dump
```

**What it does:** Saves current process list to `C:\Users\User\.pm2\dump.pm2`

**Same as:** `pm2 save`

---

### Resurrect from Dump

```bash
pm2 resurrect
```

**What it does:** Restores processes from saved dump file

**When to Use:** After system reboot, after `pm2 delete all`

---

## Process Memory Management

### Memory Limits by Process Type

**Watchers:** 500MB max memory
- Gmail Watcher: 500MB
- Calendar Watcher: 500MB
- Slack Watcher: 500MB
- Filesystem Watcher: 500MB
- WhatsApp Watcher: 500MB

**Approval Monitors:** 300MB max memory
- Email Approval Monitor: 300MB
- Calendar Approval Monitor: 300MB
- Slack Approval Monitor: 300MB
- LinkedIn Approval Monitor: 300MB
- Twitter Approval Monitor: 300MB
- Meta Approval Monitor: 300MB

### Change Memory Limit

```bash
# Stop process
pm2 stop gmail-watcher

# Start with new memory limit
pm2 start process-manager/pm2.config.js
# (Edit config to change max_memory_restart)

# Or start specific process with limit
pm2 start gmail-watcher --max-memory-restart 1G
```

---

## Environment Variables

### View Environment Variables

```bash
pm2 show gmail-watcher
```

**Shows:** All environment variables for the process

### Key Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PYTHONUNBUFFERED` | Disable Python output buffering | `1` |
| `META_DRY_RUN` | Enable/disable Instagram posting | `false` |
| `LINKEDIN_DRY_RUN` | Enable/disable LinkedIn posting | `false` |
| `TWITTER_DRY_RUN` | Enable/disable Twitter posting | `false` |
| `SLACK_BOT_TOKEN` | Slack bot token | (in config) |

---

## Auto-Start on Boot

### Enable Auto-Start

```bash
# 1. Save current configuration
pm2 save

# 2. Generate startup script
pm2 startup

# 3. Follow the prompts for your platform:
#    - Windows: Startup folder
#    - macOS: launchd
#    - Linux: systemd, upstart, or rc.d
```

### Windows Startup

1. PM2 generates a startup script
2. Run: `pm2-startup.bat` (or add to Windows Startup folder)
3. Processes start automatically on boot

### Linux Systemd

```bash
pm2 startup
# Choose "systemd"
# PM2 creates systemd service
# Enable with: sudo systemctl enable pm2-root
```

---

## Quick Diagnostic Commands

### Health Check

```bash
# Count online processes
pm2 status | grep -c "online"

# Should show: 11 (11 continuous processes)
# Scheduled processes show as "stopped" (normal)

# Check for errors
pm2 status | grep -v "online\|stopped"

# Check restart counts
pm2 status | awk '{if ($9 > 0) print $2, "restarted", $9, "times"}'

# Check memory usage
pm2 status | awk '{print $2, $5}'
```

### Full System Diagnostic

```bash
echo "=== AI Employee System Diagnostic ==="
echo ""
echo "Process Status:"
pm2 status | grep -E "online|stopped|errored"
echo ""
echo "Recent Errors:"
pm2 logs --err --lines 10 --nostream
echo ""
echo "Memory Usage:"
pm2 status | awk '{print $2, ":", $5}'
echo ""
echo "Restart Counts:"
pm2 status | awk '{print $2, ":", $9}'
```

---

## Best Practices

### 1. Save After Every Change

```bash
pm2 stop gmail-watcher
pm2 start gmail-watcher
pm2 save  # Always save!
```

### 2. Monitor Regularly

```bash
# Daily health check
pm2 status

# Weekly log review
pm2 logs --lines 100
```

### 3. Flush Logs Periodically

```bash
# Clear old logs
pm2 flush

# Automatically cleanup (scheduled task runs Sundays at 3 AM)
```

### 4. Use Process Groups

```bash
# Restart all watchers
pm2 restart gmail-watcher calendar-watcher slack-watcher

# Restart all approval monitors
pm2 restart email-approval-monitor calendar-approval-monitor slack-approval-monitor linkedin-approval-monitor twitter-approval-monitor meta-approval-monitor
```

### 5. Check Before Changes

```bash
# Always check status before making changes
pm2 status

# View logs before stopping
pm2 logs <process-name> --lines 20
```

---

## Common Issues and Solutions

### Issue: Process Won't Start

**Solution:**
```bash
# Check if port 9222 is in use (Chrome CDP)
netstat -ano | grep :9222

# Start Chrome CDP if needed
scripts/social-media/START_AUTOMATION_CHROME.bat

# Check PM2 logs
pm2 logs --err --lines 50

# Try starting without daemon
pm2 start process-manager/pm2.config.js --no-daemon
```

---

### Issue: Process Keeps Restarting

**Solution:**
```bash
# Check error logs
pm2 logs <process-name> --err

# Check memory usage
pm2 monit

# Increase memory limit
pm2 stop <process-name>
# Edit pm2.config.js to increase max_memory_restart
pm2 start process-manager/pm2.config.js
```

---

### Issue: Social Media Not Posting

**Solution:**
```bash
# 1. Check monitor is running
pm2 status | grep -E "linkedin|twitter|meta"

# 2. Check logs for errors
pm2 logs linkedin-approval-monitor --err --lines 20

# 3. Verify Chrome CDP is running
netstat -ano | grep :9222

# 4. Restart monitors
pm2 restart linkedin-approval-monitor
pm2 restart twitter-approval-monitor
pm2 restart meta-approval-monitor

# 5. Verify you're logged in Chrome automation window
```

---

### Issue: High CPU Usage

**Solution:**
```bash
# Check which process
pm2 monit

# Restart the process
pm2 restart <process-name>

# If still high, consider:
# - Reducing check frequency
# - Increasing delays between checks
# - Upgrading hardware
```

---

## Summary

**Key Commands:**

| Task | Command |
|------|---------|
| Start all | `pm2 start process-manager/pm2.config.js && pm2 save` |
| Check status | `pm2 status` |
| View logs | `pm2 logs` |
| Restart all | `pm2 restart all` |
| Stop all | `pm2 stop all` |
| Save config | `pm2 save` |
| Monitor | `pm2 monit` |

**Process Count:** 16 total
- 11 continuous (running 24/7)
- 5 scheduled (cron jobs)

**Total Memory:** ~3-4GB when all running

**Status:** All systems operational ✅

---

*Last Updated: 2026-01-14*
*AI Employee App v1.1.0 - Gold Tier 100% Complete*
