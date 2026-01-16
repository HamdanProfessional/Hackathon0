# Troubleshooting Guide

**Having issues?** This guide covers the most common problems and solutions.

---

## 🔍 Quick Diagnosis

### Step 1: Check System Status
```bash
pm2 status
```

**What to look for:**
- All processes should show "online" status
- "errored" or "stopped" means problems
- High restart counts (↺ column) indicates crashes

### Step 2: Check Recent Logs
```bash
pm2 logs --lines 50 --err
```

### Step 3: Verify Chrome Automation
```bash
netstat -ano | findstr :9222
```
**Should show:** `LISTENING` with a PID

---

## 🚨 Common Issues & Solutions

### Issue 1: Services Won't Start

**Symptoms:**
- `pm2 start` fails
- Processes show "errored"
- High restart counts

**Solutions:**

#### A. PM2 Daemon Issue
```bash
# Kill PM2 daemon
pm2 kill

# Start fresh
pm2 start process-manager/pm2.config.js
```

#### B. Missing Dependencies
```bash
# Install Python packages
pip install anthropic pyyaml playwright

# Install PM2 globally
npm install -g pm2
```

#### C. Port Already in Use
```bash
# Check what's using port 3000
netstat -ano | findstr :3000

# Kill the process or use different port
# Edit dashboard/server.js to change PORT variable
```

---

### Issue 2: Chrome Automation Not Working

**Symptoms:**
- Social media posts fail
- Error: "Chrome CDP not available"
- Posts not executing

**Solutions:**

#### A. Chrome Not Running with CDP
```bash
# Close all Chrome windows

# Restart with batch file
scripts\social-media\START_AUTOMATION_CHROME.bat

# Or manually:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"
```

#### B. Wrong Chrome Profile
```bash
# Close Chrome, delete old profile
rmdir /s "C:\Users\User\ChromeAutomationProfile"

# Restart with batch file
scripts\social-media\START_AUTOMATION_CHROME.bat

# Log into platforms again
```

#### C. Port 9222 Blocked
```bash
# Check what's using port 9222
netstat -ano | findstr :9222

# Kill the process or use different port
# Edit social-media posters to use different port
```

---

### Issue 3: Not Detecting Emails/Calendar

**Symptoms:**
- Watcher running but no files created
- No new items in Needs_Action/
- MCP not responding

**Solutions:**

#### A. Token Expired
```bash
# Delete old token
rm mcp-servers/email-mcp/.gmail_mcp_token.json

# Re-authenticate
cd mcp-servers/email-mcp
npm run authenticate
```

#### B. Wrong Credentials Path
```bash
# Check PM2 config uses correct path
pm2 show gmail-watcher

# Should show:
# args: --vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json
```

#### C. Gmail API Not Enabled
```bash
# Enable Gmail API
# Visit: https://console.cloud.google.com/apis/api/gmail.googleapis.com/overview

# Check MCP config
cat mcp-servers/email-mcp/package.json
# Look for "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
```

#### D. Test MCP Directly
```bash
cd mcp-servers/email-mcp
node test-email.js
```

---

### Issue 4: Social Media Posts Failing

**Symptoms:**
- Posts created but not executing
- Error: "Element not found"
- Posts stuck in Approved/

**Solutions:**

#### A. Not Logged In
```bash
# Open Chrome automation window
# Check if logged into platform
# Log in if needed
```

#### B. Wrong Content Extraction
```bash
# Check post file
cat AI_Employee_Vault/Approved/LINKEDIN_POST_*.md

# Should have content between ``` marks
# If metadata included, see docs/SOCIAL_MEDIA_GUIDE.md
```

#### C. Platform Changed UI
```bash
# Check platform for UI changes
# May need to update selectors in scripts/social-media/*_poster.py
# Look for elements: .global-nav__me, [aria-label="Post"], etc.
```

#### D. Network Timeout
```bash
# Check internet connection
# Increase timeout in poster script
# Edit: timeout=180000 (3 minutes)
```

---

### Issue 5: AI Auto-Approver Not Working

**Symptoms:**
- Items stay in Needs_Action/
- No AI decisions being made
- Error: "ANTHROPIC_API_KEY not set"

**Solutions:**

#### A. API Key Not Set
```bash
# Check if API key is set
pm2 show auto-approver

# Set API key
setx ANTHROPIC_API_KEY "your-api-key-here"

# Restart with new env variable
pm2 restart auto-approver --update-env
```

#### B. API Key Invalid
```bash
# Verify API key works
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

#### C. Using Fallback Mode
```bash
# Check logs
pm2 logs auto-approver

# Look for: "AI decision failed: ... using fallback"
# Without API key, uses rule-based decisions (less smart)
```

#### D. Anthropic Account Issues
```bash
# Check API key at: https://console.anthropic.com/settings/keys
# Verify:
# - Key is active
# - Has credits available
# - Correct permissions enabled
```

---

### Issue 6: Vault Folder Problems

**Symptoms:**
- Files not being created
- Wrong folder paths
- Permission errors

**Solutions:**

#### A. Wrong Vault Path
```bash
# Check PM2 config
grep "vault" process-manager/pm2.config.js

# Should be: --vault AI_Employee_Vault
# NOT: --vault vault or --vault ./vault
```

#### B. Folder Not Created
```bash
# Create folders manually
mkdir AI_Employee_Vault\Inbox
mkdir AI_Employee_Vault\Needs_Action
mkdir AI_Employee_Vault\Pending_Approval
mkdir AI_Employee_Vault\Approved
mkdir AI_Employee_Vault\Rejected
mkdir AI_Employee_Vault\Done
mkdir AI_Employee_Vault\Briefings
mkdir AI_Employee_Vault\Plans
mkdir AI_Employee_Vault\Logs
mkdir AI_Employee_Vault\Templates
mkdir AI_Employee_Vault\Accounting
```

#### C. Windows Path Issues
```bash
# Use forward slashes in Python scripts
# Wrong: C:\Users\...
# Correct: C:/Users/... or use raw strings: r"C:\Users\..."

# In PM2 config, double backslashes are OK
# args: "--vault C:\\Users\\User\\Desktop\\AI_EMPLOYEE_APP\\AI_Employee_Vault"
```

---

### Issue 7: Dashboard Not Accessible

**Symptoms:**
- Can't access http://localhost:3000
- Dashboard shows errors
- Data not loading

**Solutions:**

#### A. Dashboard Not Running
```bash
pm2 status | grep dashboard

# If stopped/errored:
pm2 restart ai-employee-dashboard
```

#### B. Port 3000 Blocked
```bash
# Check what's using port 3000
netstat -ano | findstr :3000

# Kill the process or change port
# Edit dashboard/server.js: const PORT = process.env.PORT || 3001
```

#### C. CORS Errors
```bash
# Check dashboard is served from correct origin
# Should be http://localhost:3000
# Not file:// protocol
```

---

### Issue 8: High Memory Usage

**Symptoms:**
- Processes consuming lots of RAM
- System running slowly
- PM2 shows high memory usage

**Solutions:**

#### A. Restart Heavy Processes
```bash
pm2 restart gmail-watcher
pm2 restart odoo-watcher
pm2 restart ai-employee-dashboard
```

#### B. Configure Memory Limits
```bash
# Edit PM2 config
# Add: max_memory_restart: "500M"

# Apply changes
pm2 restart all
```

#### C. Clean Up Logs
```bash
# Run log cleanup
pm2 start audit-log-cleanup
# Or manually:
rm AI_Employee_Vault/Logs/2025-*.json
```

---

### Issue 9: Files Stuck in Approved/

**Symptoms:**
- Files in Approved/ not executing
- Approval monitors not detecting files
- No errors in logs

**Solutions:**

#### A. Monitor Not Running
```bash
pm2 status | grep approval-monitor

# Should show: linkedin-approval-monitor, twitter-approval-monitor, etc.
```

#### B. File Format Wrong
```bash
# Check file has correct frontmatter
head -20 AI_Employee_Vault/Approved/LINKEDIN_POST_*.md

# Should have:
# ---
# type: linkedin_post
# platform: linkedin
# ---
```

#### C. Already Processed
```bash
# Check if file was already processed
ls AI_Employee_Vault/Done/LINKEDIN_POST_*.md

# If in Done/, already processed
```

#### D. Force Re-processing
```bash
# Move from Approved/ back to Needs_Action/
mv AI_Employee_Vault/Approved/LINKEDIN_POST_*.md AI_Employee_Vault/Needs_Action/

# AI will re-analyze and move to correct folder
```

---

### Issue 10: Duplicate Entries

**Symptoms:**
- Same email creating multiple files
- Duplicate calendar entries
- Multiple monitors processing same file

**Solutions:**

#### A. Check processed_files Tracking
```bash
# Monitor logs for "Already processed" messages
pm2 logs gmail-watcher | grep "Already processed"
```

#### B. Clear processed_files Set
```bash
# Restart watcher
pm2 restart gmail-watcher
# Clears in-memory tracking
```

#### C. Check Multiple Watchers Running
```bash
pm2 status | grep watcher
# Should only have one of each type
```

---

## 🔧 Advanced Troubleshooting

### Enable Debug Logging

#### For Watchers
```bash
# Run manually with verbose output
python -m watchers.gmail_watcher --vault AI_Employee_Vault --once --debug
```

#### For AI Auto-Approver
```bash
# Run manually to see AI decisions
python scripts/auto_approver.py --vault AI_Employee_Vault --once
```

### Check System Resources

#### CPU/Memory
```bash
# Task Manager (Windows)
# Look for python.exe processes
# Check for high CPU/memory usage
```

#### Disk Space
```bash
# Check vault size
du -sh AI_Employee_Vault

# Check logs size
du -sh AI_Employee_Vault/Logs
```

### Reset Everything

#### Nuclear Option (Use as Last Resort)
```bash
# Stop everything
pm2 kill

# Clear PM2 state
pm2 flush

# Delete PM2 ecosystem
pm2 delete all

# Start fresh
pm2 start process-manager/pm2.config.js
```

---

## 📞 Getting More Help

### Check Logs First
```bash
# All logs
pm2 logs

# Error logs only
pm2 logs --err

# Specific service
pm2 logs gmail-watcher --lines 100

# Recent logs
pm2 logs --lines 50
```

### Collect Diagnostic Info
```bash
# System status
pm2 status > status.txt

# Recent errors
pm2 logs --err --lines 100 > errors.txt

# Vault contents
ls -R AI_Employee_Vault/ > vault_contents.txt

# Chrome CDP
netstat -ano | findstr :9222 > chrome_cdp.txt

# Token files
ls -la mcp-servers/*_mcp/*.json > tokens.txt

# Send all these when asking for help
```

### Common Error Messages

#### "Chrome CDP not available"
→ Chrome not running with --remote-debugging-port=9222
→ See Issue 2 above

#### "Gmail API error"
→ Token expired or API not enabled
→ See Issue 3 above

#### "Module not found"
→ Missing Python dependency
→ Run: pip install anthropic pyyaml

#### "ENOENT: no such file or directory"
→ Wrong vault path
→ Check PM2 config vault path

#### "Permission denied"
→ Windows folder permissions
→ Run as Administrator or fix folder permissions

---

## 📚 Additional Resources

- **[START_HERE.md](START_HERE.md)** - New user guide
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup instructions
- **[USER_GUIDE.md](USER_GUIDE.md)** - Daily usage
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical details
- **[SECURITY.md](SECURITY.md)** - Security model

---

## 🎯 Prevention Tips

### Regular Maintenance
1. **Weekly:** Check logs for errors
2. **Monthly:** Clean up old Done/ files
3. **Quarterly:** Review and update Company_Handbook.md
4. **As needed:** Update API keys and tokens

### Best Practices
1. **Always test** with --dry-run first for social media
2. **Review changes** before updating PM2 config
3. **Backup vault** before major changes
4. **Keep Chrome automation** logged in to platforms
5. **Monitor costs** (API usage, system resources)

### Stay Updated
- Check `CLAUDE.md` for latest system info
- Review `CHANGELOG.md` for recent changes
- Update documentation when making changes

---

*Last Updated: 2026-01-17*
*System Version: v1.3.0*
