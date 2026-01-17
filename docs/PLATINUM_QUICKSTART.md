# Platinum Tier Quick Start Guide

## 5-Minute Setup to Get Cloud + Local Hybrid Running

### Prerequisites

- Oracle Cloud Free VM (or AWS/GCP)
- Local machine (your laptop/PC)
- GitHub account (for vault sync)
- Anthropic API key (for Claude 3 Haiku)

---

## Step 1: Cloud VM Setup (10 minutes)

### 1.1 Create Oracle Cloud Free VM

```bash
# Go to: https://www.oracle.com/cloud/free/
# Create: VM.Standard.E2.1.Micro
# OS: Ubuntu 22.04
# Shape: 1 OCPU, 1GB RAM (Free Tier)

# Save your public IP: X.X.X.X
# SSH into VM:
ssh -i ~/.ssh/your_key ubuntu@X.X.X.X
```

### 1.2 Install Dependencies on Cloud

```bash
# Run this on your cloud VM
curl -fsSL https://raw.githubusercontent.com/your-repo/AI_EMPLOYEE/main/scripts/setup_cloud.sh | bash
```

Or manually:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13
sudo apt install -y python3.13 python3.13-venv python3-pip git

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2

# Install project
cd ~
git clone https://github.com/your-repo/AI_EMPLOYEE_APP.git
cd AI_EMPLOYEE_APP

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install
```

### 1.3 Configure Cloud Environment

```bash
# On cloud VM
cd ~/AI_EMPLOYEE_APP

# Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
GMAIL_CLOUD_TOKEN_PATH=/home/ubuntu/.gmail_token.json
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-signing-secret
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USER=admin
ODOE_PASSWORD=admin_password
VAULT_PATH=/home/ubuntu/AI_EMPLOYEE_APP/AI_Employee_Vault
EOF

# Create vault directory
mkdir -p AI_Employee_Vault
```

### 1.4 Setup Gmail OAuth on Cloud

```bash
# Run Gmail watcher to initiate OAuth
source venv/bin/activate
python -m watchers.gmail_watcher --vault AI_Employee_Vault --cloud-mode

# Follow OAuth flow, token will be saved to .gmail_token.json
```

### 1.5 Start Cloud Processes

```bash
# Start cloud PM2 processes
pm2 start process-manager/pm2.cloud.config.js
pm2 save

# Verify status
pm2 status
```

---

## Step 2: Local Machine Setup (5 minutes)

### 2.1 Update Local Configuration

```bash
# On your local machine
cd AI_EMPLOYEE_APP

# Stop existing processes
pm2 stop all

# Start local-only processes
pm2 start process-manager/pm2.local.config.js
pm2 save
```

### 2.2 Setup Vault Sync (Git)

```bash
# On local machine, initialize git repo for vault
cd AI_Employee_Vault
git init
git add .
git commit -m "Initial vault state"

# Create GitHub repository (private)
# Then:
git remote add origin https://github.com/your-username/ai-employee-vault.git
git push -u origin main
```

### 2.3 Create .gitignore for Secrets

```bash
# On local machine, in AI_Employee_Vault/
cat > .gitignore << 'EOF'
.env
.env.local
*_token.json
*_credentials.json
whatsapp_session/
.whatsapp_state.json
.banking/
.payment_tokens/
*.pem
*.key
EOF

git add .gitignore
git commit -m "Add gitignore for secrets"
git push
```

### 2.4 Configure Cloud Sync

```bash
# On cloud VM
cd ~/AI_EMPLOYEE_APP/AI_Employee_Vault
git init
git remote add origin https://github.com/your-username/ai-employee-vault.git
git pull origin main

# Set environment variable for sync
echo "export VAULT_REPO_URL=https://github.com/your-username/ai-employee-vault.git" >> ~/.bashrc
source ~/.bashrc

# Make sync scripts executable
chmod +x ../scripts/vault_sync_pull.sh
```

### 2.5 Start Local Processes

```bash
# On local machine
pm2 restart all

# Start Chrome automation
scripts\social-media\START_AUTOMATION_CHROME.bat  # Windows
# or
bash scripts/social-media/START_AUTOMATION_CHROME.sh  # Linux/Mac
```

---

## Step 3: Test the Flow (2 minutes)

### 3.1 Send Test Email

```
Send yourself an email with subject: "Platinum Tier Test"
```

### 3.2 Watch Cloud Process It

```bash
# SSH to cloud
ssh ubuntu@your-cloud-vm

# Watch logs
pm2 logs gmail-watcher-cloud --lines 50
```

Expected flow:
1. Cloud detects email
2. Creates file in `Needs_Action/`
3. Claims it (moves to `In_Progress/cloud-agent/`)
4. Auto-approver processes it
5. Moves to `Pending_Approval/` as draft

### 3.3 Approve on Local

```bash
# On local machine
ls AI_Employee_Vault/Pending_Approval/

# Review the draft
cat AI_Employee_Vault/Pending_Approval/DRAFT_EMAIL_*.md

# Approve by moving to Approved/
mv AI_Employee_Vault/Pending_Approval/DRAFT_EMAIL_*.md \
   AI_Employee_Vault/Approved/
```

### 3.4 Local Executes Action

```bash
# Watch local logs
pm2 logs email-approval-monitor --lines 50
```

Expected flow:
1. Local detects approved file
2. Sends email via Gmail API
3. Moves to `Done/`

---

## Step 4: Verify Dashboard Updates

```bash
# On local machine
cat AI_Employee_Vault/Dashboard.md

# Check for Cloud Updates section
# Should show system health, process status, alerts
```

---

## Summary

| Component | Where | What |
|-----------|-------|------|
| Gmail Watcher | Cloud | Monitors 24/7 |
| Calendar Watcher | Cloud | Monitors 24/7 |
| Slack Watcher | Cloud | Monitors 24/7 |
| Auto-Approver | Cloud | Claude 3 Haiku every 2 min |
| Health Monitor | Cloud | Reports every 5 min |
| WhatsApp Watcher | Local | Session required |
| Approval Monitors | Local | Execute approved actions |
| Dashboard | Local | Single writer |

---

## Troubleshooting

### Cloud not detecting emails

```bash
# Check cloud logs
pm2 logs gmail-watcher-cloud --lines 100

# Check Gmail token
ls -la ~/.gmail_token.json

# Re-authenticate if needed
python -m watchers.gmail_watcher --vault AI_Employee_Vault --cloud-mode
```

### Local not executing approved actions

```bash
# Check local logs
pm2 logs email-approval-monitor --lines 100

# Verify file in Approved/
ls AI_Employee_Vault/Approved/

# Check LIVE mode is set
pm2 env 0 | grep DRY_RUN
```

### Sync not working

```bash
# Check git status
cd AI_Employee_Vault
git status

# Manual sync
git pull origin main
git add .
git commit -m "Update"
git push origin main
```

---

## Next Steps

1. **Deploy Odoo on Cloud** (optional)
   - Follow `docs/PLATINUM_TIER_SETUP.md` Part 5

2. **Setup Syncthing** (alternative to Git)
   - Follow `docs/PLATINUM_TIER_SETUP.md` Part 3.2

3. **Configure Firewall**
   - `sudo ufw allow 22`
   - `sudo ufw allow 80`
   - `sudo ufw allow 443`
   - `sudo ufw enable`

4. **Enable PM2 Startup**
   - On cloud: `pm2 startup`
   - On local: `pm2 startup`

---

## Architecture Recap

```
┌─────────────────────────────────────────────────────────────┐
│ CLOUD VM (24/7)                                            │
│ ─────────────────                                          │
│ • Gmail/Calendar/Slack watchers                            │
│ • AI Auto-Approver (Claude 3 Haiku)                        │
│ • Health Monitor                                           │
│ • Draft-only actions (safe)                                │
└─────────────────────────────────────────────────────────────┘
                           ↕ Git Sync
┌─────────────────────────────────────────────────────────────┐
│ LOCAL MACHINE                                              │
│ ────────────────                                           │
│ • WhatsApp watcher (session required)                      │
│ • Approval monitors (execute actions)                      │
│ • Dashboard (single writer)                                │
│ • Sensitive data (banking, tokens)                         │
└─────────────────────────────────────────────────────────────┘
```

**You now have a production-ready AI Employee running 24/7!**
