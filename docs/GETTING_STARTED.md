# Getting Started Guide

**New to AI Employee?** This guide will get you set up in 15-20 minutes.

---

## 📋 Prerequisites

- **Windows 10/11** (system built for Windows)
- **Python 3.8+** installed
- **Node.js 16+** installed
- **PM2** installed (`npm install -g pm2`)
- **Google Chrome** browser
- **Accounts on services you want to connect** (Gmail, LinkedIn, etc.)

---

## 🔧 Step 1: Install Dependencies (2 min)

### Install PM2
```bash
npm install -g pm2
```

### Install Python Dependencies
```bash
pip install anthropic pyyaml playwright
```

### Verify Installation
```bash
pm2 --version
python --version
node --version
```

---

## 🔑 Step 2: Set Up Authentication (10 min)

### Gmail & Calendar
```bash
cd mcp-servers/email-mcp
npm run authenticate

cd mcp-servers/calendar-mcp
npm run authenticate
```
This will open a browser window. Log in to your Google account and authorize the app.

### Xero (Accounting)
```bash
cd mcp-servers/xero-mcp
npm run authenticate
```
Follow the prompts to connect your Xero account.

### Slack
```bash
cd mcp-servers/slack-mcp
npm run authenticate
```

### Verify Tokens Created
```bash
ls -la mcp-servers/*_mcp/
# Should see .gmail_mcp_token.json, .calendar_mcp_token.json, .xero_mcp_token.json
```

---

## 🌐 Step 3: Configure Chrome Automation (2 min)

### Start Chrome with Remote Debugging
```bash
# Run this batch file
scripts\social-media\START_AUTOMATION_CHROME.bat
```

### Log Into Social Platforms
In the Chrome window that opens:
1. **LinkedIn** - Log in at https://www.linkedin.com
2. **Twitter/X** - Log in at https://x.com
3. **Instagram** - Log in at https://www.instagram.com
4. **Facebook** - Log in at https://www.facebook.com

**Important:** Keep this Chrome window open while the system is running!

### Verify Chrome is Listening
```bash
netstat -ano | findstr :9222
```
Should show `LISTENING` with a PID.

---

## 🚀 Step 4: Start the System (1 min)

### Start All Services
```bash
pm2 start process-manager/pm2.config.js
```

### Check Everything is Running
```bash
pm2 status
```

**Expected Output:** All processes should show "online" status.

### Save Configuration
```bash
pm2 save
pm2 startup
```
The second command configures PM2 to start automatically on system boot.

---

## ✅ Step 5: Verify Setup (2 min)

### Open Dashboard
```bash
start http://localhost:3000
```

### Test AI Auto-Approver
```bash
pm2 logs auto-approver --lines 20
```

You should see:
```
AI-POWERED AUTO-APPROVAL PROCESSOR
Vault: C:\Users\User\Desktop\AI_EMPLOYEE_APP\AI_Employee_Vault
AI: Claude 3 Haiku
```

### Check Vault Structure
```bash
dir AI_Employee_Vault
```

You should see these folders created:
- Inbox/
- Needs_Action/
- Pending_Approval/
- Approved/
- Rejected/
- Done/
- Briefings/
- Plans/
- Logs/
- Templates/
- Accounting/

---

## 🎯 Step 6: Configure AI Auto-Approver (Optional)

The AI Auto-Approver uses Claude 3 Haiku to make intelligent decisions. To enable it:

### Set API Key
```bash
# Set your Anthropic API key as environment variable
setx ANTHROPIC_API_KEY "your-api-key-here"

# Or add to PM2 config directly
# Edit process-manager/pm2.config.js
# Add to auto-approver env section:
# "ANTHROPIC_API_KEY": "your-api-key-here"

# Restart auto-approver
pm2 restart auto-approver --update-env
```

**Get API Key:** https://console.anthropic.com/

**Cost:** ~$5-10/month for moderate usage

**Without API Key:** Auto-approver falls back to simple rule-based decisions.

---

## 📱 Step 7: Start Using It!

### Check Your Email
```
Open Claude Code and ask: "Check my urgent emails"
```

### Test Social Media
```bash
# Create a test post
cd AI_Employee_Vault/Pending_Approval/

# Create LinkedIn post
cat > LINKEDIN_POST_TEST.md << 'EOF'
---
type: linkedin_post
platform: linkedin
status: pending_approval
---

Testing AI Employee system! #AI #Automation
EOF

# Move to Approved to post
mv LINKEDIN_POST_TEST.md ../Approved/

# Check logs
pm2 logs linkedin-approval-monitor --lines 20
```

### View Dashboard
Visit **http://localhost:3000** to see your AI Employee dashboard.

---

## 🎓 What To Learn Next

### Essential Reading
1. **[USER_GUIDE.md](USER_GUIDE.md)** - How to use your AI Employee daily
2. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues

### Advanced Reading
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - How it works under the hood
4. **[SECURITY.md](SECURITY.md)** - Security model and best practices

### Reference Guides
5. **[SOCIAL_MEDIA_GUIDE.md](SOCIAL_MEDIA_GUIDE.md)** - Social media posting
6. **[PROCESS_CONTROL_GUIDE.md](PROCESS_CONTROL_GUIDE.md)** - PM2 management

---

## 🎉 You're Ready!

Your AI Employee is now:
- ✅ Monitoring your email, calendar, Slack, WhatsApp
- ✅ Tracking accounting (Xero & Odoo)
- ✅ Ready to post to social media
- ✅ Using AI to intelligently filter actions

**Next:** Read [USER_GUIDE.md](USER_GUIDE.md) to learn how to use it day-to-day.

---

## 🆘 Troubleshooting Setup Issues

### PM2 Won't Start
```bash
# Clear PM2 state
pm2 kill

# Start fresh
pm2 start process-manager/pm2.config.js
```

### Chrome Automation Not Working
```bash
# Close all Chrome windows

# Restart with batch file
scripts\social-media\START_AUTOMATION_CHROME.bat
```

### Authentication Failed
```bash
# Delete old token and re-authenticate
rm mcp-servers/email-mcp/.gmail_mcp_token.json

cd mcp-servers/email-mcp
npm run authenticate
```

---

*Last Updated: 2026-01-17*
*System Version: v1.3.0*
