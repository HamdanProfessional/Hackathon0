# Quick Start Guide - AI Employee

**Get your AI Employee running in 5 minutes**

---

## Prerequisites

- Python 3.13+
- Node.js 24+
- PM2 installed globally
- Chrome browser
- Obsidian (optional, for vault viewing)

---

## Step 1: Start the System

```bash
# Navigate to project directory
cd AI_EMPLOYEE_APP

# Start all PM2 processes
pm2 start process-manager/pm2.config.js

# Save PM2 configuration
pm2 save

# Check all processes are running
pm2 status
```

**Expected:** 16-17 processes showing "online" status

---

## Step 2: Verify Your Vault

Open `AI_Employee_Vault/Dashboard.md` in your text editor or Obsidian.

You should see:
- System status
- Pending messages
- Active projects
- Bank balance
- Recent activity

---

## Step 3: Test the System

### Test Email Monitoring

1. Send yourself an email with keyword "urgent"
2. Wait 10 minutes (or check immediately)
3. Look for file in `AI_Employee_Vault/Needs_Action/`

### Test Social Media (Optional)

1. Start Chrome automation:
   ```bash
   start_chrome.bat
   ```

2. Log in to each platform in the Chrome window:
   - linkedin.com
   - x.com (Twitter)
   - facebook.com
   - instagram.com

3. Create a test post:
   ```bash
   python .claude/skills/linkedin-manager/invoke.py "Test post from AI Employee system"
   ```

4. Review the created file in `AI_Employee_Vault/Pending_Approval/`

5. Move to approved:
   ```bash
   mv "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md" "AI_Employee_Vault/Approved/"
   ```

6. Watch it post automatically (LinkedIn monitor will execute within 30 seconds)

---

## Step 4: Generate CEO Briefing

```bash
python .claude/skills/weekly-briefing/invoke.py "Generate CEO briefing"
```

Open the generated file at: `AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`

---

## Common Commands

### Check System Status

```bash
# PM2 status
pm2 status

# All logs
pm2 logs

# Specific process logs
pm2 logs gmail-watcher --lines 50

# Error logs only
pm2 logs --err
```

### Restart Processes

```bash
# Restart all
pm2 restart all

# Restart specific process
pm2 restart gmail-watcher
```

### Stop Everything

```bash
pm2 stop all
```

---

## File Locations

### Vault

`AI_Employee_Vault/` - All your data and files

### Important Folders

- `Needs_Action/` - Items detected by watchers
- `Pending_Approval/` - Awaiting your review
- `Approved/` - Ready to execute
- `Done/` - Completed items
- `Briefings/` - CEO briefings
- `Logs/` - Daily activity logs

---

## Troubleshooting

### Chrome Not Connecting

```bash
# Test CDP port
curl http://localhost:9222/json/version

# If error, start Chrome manually
start_chrome.bat
```

### Process Crashing

```bash
# Check error logs
pm2 logs process-name --err

# Common fixes
pm2 restart process-name
```

### File Not Being Created

```bash
# Verify vault exists
ls AI_Employee_Vault/

# Check folder permissions
```

---

## Next Steps

1. **Customize Your Settings**
   - Edit `AI_Employee_Vault/Company_Handbook.md`
   - Set business goals in `AI_Employee_Vault/Business_Goals.md`

2. **Add Your Credentials**
   - Gmail: OAuth on first run
   - Calendar: OAuth on first run
   - Slack: Bot token in `.env`

3. **Configure Social Media**
   - Set `LINKEDIN_DRY_RUN=false` for live posting
   - Log into all platforms in Chrome CDP

4. **Monitor Performance**
   - Check dashboard at http://localhost:3000
   - Review logs in `AI_Employee_Vault/Logs/`
   - Read CEO briefings in `Briefings/`

---

**Need Help?**

Check the main README: `docs/README.md`
