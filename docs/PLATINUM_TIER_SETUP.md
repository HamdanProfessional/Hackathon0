# Platinum Tier Setup Guide
## Cloud + Local Hybrid Architecture

### Overview

Platinum Tier implements a **cloud + local hybrid** where:
- **Cloud (24/7)**: Monitors services, drafts responses, schedules content
- **Local**: Approves actions, handles sensitive sessions (WhatsApp, banking), executes final sends

---

## Part 1: Cloud VM Setup

### 1.1 Create Oracle Cloud Free VM

```bash
# Sign up at: https://www.oracle.com/cloud/free/
# Create: VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM, 10GB boot)

# Connect to your VM
ssh -i ~/.ssh/your_key ubuntu@your_vm_public_ip
```

### 1.2 Install Dependencies on Cloud VM

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13+
sudo apt install -y python3.13 python3.13-venv python3-pip

# Install Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Install Git
sudo apt install -y git

# Install vault sync (choose one)
sudo apt install -y syncthing  # Option A: Syncthing
# OR use git (Option B: already installed)
```

### 1.3 Deploy AI Employee to Cloud

```bash
# Clone repository
git clone https://github.com/your-repo/AI_EMPLOYEE_APP.git
cd AI_EMPLOYEE_APP

# Create Python virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Create cloud-specific environment file
cp .env.cloud.example .env
```

### 1.4 Cloud Environment Configuration

Create `.env` on cloud (ONLY safe values):

```bash
# .env for Cloud VM - NO SECRETS!
ANTHROPIC_API_KEY=sk-ant-xxx  # For Claude 3 Haiku auto-approver
GMAIL_CLOUD_TOKEN_PATH=/home/ubuntu/.gmail_token.json
CALENDAR_CLOUD_TOKEN_PATH=/home/ubuntu/.calendar_token.json
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_SIGNING_SECRET=xxx
ODOO_URL=http://localhost:8069
ODOE_DB=ai_employee
ODOO_USER=admin
ODOO_PASSWORD=admin_password

# NEVER sync these to cloud:
# WHATSAPP_SESSION (local only)
# BANKING_CREDENTIALS (local only)
# PAYMENT_TOKENS (local only)
```

---

## Part 2: Work-Zone Specialization

### 2.1 Cloud Agent Configuration

The cloud agent runs ONLY these watchers:

```javascript
// File: process-manager/pm2.cloud.config.js
module.exports = {
  apps: [
    // === CLOUD-ONLY WATCHERS ===
    {
      name: 'gmail-watcher-cloud',
      script: './run_gmail_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --cloud-mode',
      env: {
        CLOUD_MODE: 'true',
        DRAFT_ONLY: 'true'
      }
    },
    {
      name: 'calendar-watcher-cloud',
      script: './run_calendar_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --cloud-mode'
    },
    {
      name: 'slack-watcher-cloud',
      script: './run_slack_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --cloud-mode'
    },
    {
      name: 'odoo-watcher-cloud',
      script: './run_odoo_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --draft-only'
    },

    // === CLOUD AI AUTO-APPROVER ===
    {
      name: 'auto-approver-cloud',
      script: './scripts/auto_approver.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --mode cloud'
    },

    // === CLOUD HEALTH MONITOR ===
    {
      name: 'cloud-health-monitor',
      script: './scripts/cloud_health_monitor.py',
      interpreter: 'python3'
    }
  ]
};
```

### 2.2 Local Agent Configuration

The local machine runs:

```javascript
// File: process-manager/pm2.local.config.js
module.exports = {
  apps: [
    // === LOCAL-ONLY WATCHERS ===
    {
      name: 'whatsapp-watcher',
      script: './run_whatsapp_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault'
    },
    {
      name: 'filesystem-watcher',
      script: './run_filesystem_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault'
    },

    // === LOCAL APPROVAL MONITORS (EXECUTE ONLY) ===
    {
      name: 'email-approval-monitor',
      script: './scripts/monitors/email_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
      env: { EMAIL_DRY_RUN: 'false' }
    },
    {
      name: 'slack-approval-monitor',
      script: './scripts/monitors/slack_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode'
    },
    {
      name: 'linkedin-approval-monitor',
      script: './scripts/social-media/linkedin_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
      env: { LINKEDIN_DRY_RUN: 'false' }
    },
    {
      name: 'twitter-approval-monitor',
      script: './scripts/social-media/twitter_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
      env: { TWITTER_DRY_RUN: 'false' }
    },
    {
      name: 'facebook-approval-monitor',
      script: './scripts/social-media/facebook_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
      env: { FACEBOOK_DRY_RUN: 'false' }
    },
    {
      name: 'instagram-approval-monitor',
      script: './scripts/social-media/instagram_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
      env: { INSTAGRAM_DRY_RUN: 'false' }
    },

    // === LOCAL DASHBOARD ===
    {
      name: 'ai-employee-dashboard',
      script: './dashboard/server.js',
      interpreter: 'node'
    }
  ]
};
```

---

## Part 3: Vault Sync (Git or Syncthing)

### Option A: Git-Based Sync (Recommended)

#### 3.1 Initialize Git Repository

```bash
# On LOCAL machine
cd AI_EMPLOYEE_APP/AI_Employee_Vault
git init
git add .
git commit -m "Initial vault state"

# Create private repository on GitHub/GitLab
# Then:
git remote add origin https://github.com/your-username/ai-employee-vault.git
git push -u origin main

# Create .gitignore for secrets
cat > .gitignore << 'EOF'
.env
*_token.json
*_credentials.json
whatsapp_session/
.banking/
.tokens/
EOF
```

#### 3.2 Cloud Sync Script

```bash
#!/bin/bash
# File: scripts/cloud_sync_pull.sh (on Cloud VM)

VAULT_PATH="AI_Employee_Vault"
REPO_URL="https://github.com/your-username/ai-employee-vault.git"

cd ~/$VAULT_PATH

# Pull latest changes from local
git pull origin main

# Merge any Updates/ into Dashboard.md
python3 ../scripts/merge_dashboard_updates.py

echo "Sync completed at $(date)"
```

#### 3.3 Local Sync Script

```bash
#!/bin/bash
# File: scripts/local_sync_push.sh (on Local machine)

VAULT_PATH="AI_Employee_Vault"

cd ~/$VAULT_PATH

# Add all changes
git add .
git commit -m "Update from local - $(date)"
git push origin main

echo "Sync completed at $(date)"
```

### Option B: Syncthing Sync

#### 3.1 Install Syncthing

```bash
# On both Cloud and Local
sudo apt install syncthing

# Start Syncthing
syncthing --gui-address=0.0.0.0:8384

# Access web UI
# Cloud: http://cloud-vm-ip:8384
# Local: http://localhost:8384
```

#### 3.2 Configure Folder Sharing

1. On **Cloud**:
   - Add folder: `AI_Employee_Vault`
   - Set ID: `ai-employee-vault`
   - Share with local device ID

2. On **Local**:
   - Add folder: `AI_Employee_Vault`
   - Accept share from cloud
   - Set: **Ignore Patterns** for secrets

---

## Part 4: Claim-by-Move Implementation

### 4.1 Directory Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── EMAIL_20260117_120000_invoice.md
│   └── SLACK_20260117_120001_urgent.md
├── In_Progress/
│   ├── cloud-agent/
│   │   └── EMAIL_20260117_120000_invoice.md  ← Cloud claimed
│   └── local-agent/
│       └── SLACK_20260117_120001_urgent.md   ← Local claimed
├── Pending_Approval/
│   ├── DRAFT_EMAIL_20260117_120000_invoice_reply.md
│   └── DRAFT_LINKEDIN_20260117_120002.md
├── Approved/
│   ├── EMAIL_20260117_120000_invoice_reply.md
│   └── LINKEDIN_20260117_120002.md
├── Done/
│   ├── EMAIL_20260117_120000_invoice_reply.md
│   └── LINKEDIN_20260117_120002.md
└── Updates/
    └── dashboard_update_20260117_120000.json
```

### 4.2 Claim Logic

```python
# File: watchers/claim_manager.py

import json
from pathlib import Path
from datetime import datetime
import time

class ClaimManager:
    """
    Implements claim-by-move rule for preventing double-work.
    """

    def __init__(self, vault_path: str, agent_name: str):
        self.vault_path = Path(vault_path)
        self.agent_name = agent_name  # 'cloud-agent' or 'local-agent'
        self.needs_action = self.vault_path / "Needs_Action"
        self.in_progress = self.vault_path / "In_Progress" / agent_name
        self.in_progress.mkdir(parents=True, exist_ok=True)

    def claim_item(self, item_path: Path) -> bool:
        """
        Try to claim an item by moving it to In_Progress/<agent>/.
        Returns True if claim successful, False if already claimed.
        """
        import shutil

        filename = item_path.name

        # Check if already claimed by another agent
        for agent_dir in (self.vault_path / "In_Progress").iterdir():
            if agent_dir.name == self.agent_name:
                continue
            claimed_file = agent_dir / filename
            if claimed_file.exists():
                return False  # Already claimed by another agent

        # Claim the item
        destination = self.in_progress / filename
        try:
            shutil.move(str(item_path), str(destination))

            # Log claim
            self._log_claim(filename, destination)
            return True
        except FileNotFoundError:
            # Item was claimed by another agent between our check and move
            return False

    def _log_claim(self, filename: str, claimed_path: Path):
        """Log claim event."""
        claim_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "item": filename,
            "path": str(claimed_path)
        }

        log_file = self.vault_path / "Logs" / f"{datetime.now().strftime('%Y-%m-%d')}_claims.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(claim_log) + "\n")

    def release_to_pending(self, item_path: Path) -> Path:
        """Move completed work to Pending_Approval/."""
        import shutil

        destination = self.vault_path / "Pending_Approval" / item_path.name
        shutil.move(str(item_path), str(destination))
        return destination
```

---

## Part 5: Odoo Cloud Deployment

### 5.1 Install Odoo on Cloud VM

```bash
# On Cloud VM

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres createuser --createdb --pwprompt odoo
# Enter password when prompted

# Install Python dependencies for Odoo
sudo apt install -y \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libtiff5-dev \
    libjpeg8-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libpq-dev

# Create Odoo user
sudo useradd -m -s /bin/bash odoo

# Clone Odoo 17
sudo su - odoo
git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0 odoo17

# Install Python requirements
cd odoo17
pip3 install -r requirements.txt

# Exit odoo user
exit
```

### 5.2 Configure Odoo

```python
# File: /etc/odoo17.conf

[options]
admin_passwd = STRONG_ADMIN_PASSWORD
db_host = localhost
db_port = 5432
db_user = odoo
db_password = YOUR_ODOO_DB_PASSWORD
dbfilter = ^ai_employee$
addons_path = /home/odoo/odoo17/addons,/home/odoo/odoo17/custom-addons
logfile = /var/log/odoo/odoo17.log
log_level = info
http_port = 8069
```

### 5.3 Create Systemd Service

```bash
# File: /etc/systemd/system/odoo17.service

[Unit]
Description=Odoo17
After=postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo17
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/home/odoo/odoo17/odoo-bin -c /etc/odoo17.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start Odoo
sudo systemctl daemon-reload
sudo systemctl enable odoo17
sudo systemctl start odoo17
```

### 5.4 Configure HTTPS with Let's Encrypt

```bash
# Install Nginx
sudo apt install -y nginx

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Configure Nginx for Odoo
sudo nano /etc/nginx/sites-available/odoo

# Add this configuration:
```

```nginx
# /etc/nginx/sites-available/odoo

server {
    listen 80;
    server_name your-odoo-domain.com;

    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_redirect off;
    }
}
```

```bash
# Enable site and get SSL certificate
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-odoo-domain.com

# Auto-renewal is configured automatically
```

---

## Part 6: Demo Flow

### 6.1 Test the Complete Flow

```bash
# === STEP 1: Start Cloud VM ===
ssh ubuntu@your-cloud-vm
cd AI_EMPLOYEE_APP
pm2 start process-manager/pm2.cloud.config.js
pm2 save
```

```bash
# === STEP 2: Start Local Machine ===
# On your local machine
cd AI_EMPLOYEE_APP
pm2 start process-manager/pm2.local.config.js
pm2 save

# Start Chrome automation
scripts\social-media\START_AUTOMATION_CHROME.bat
```

```bash
# === STEP 3: Test Email Flow ===

# 1. Send yourself a test email with subject: "Platinum Tier Test"

# 2. Watch cloud logs:
ssh ubuntu@your-cloud-vm "pm2 logs gmail-watcher-cloud --lines 50"

# 3. Cloud should:
#    - Detect email
#    - Create file in Needs_Action/
#    - Claim it (move to In_Progress/cloud-agent/)
#    - Draft reply
#    - Move to Pending_Approval/

# 4. On local, check Pending_Approval/
ls AI_Employee_Vault/Pending_Approval/

# 5. Review draft, approve by moving to Approved/
mv AI_Employee_Vault/Pending_Approval/DRAFT_EMAIL_*.md \
   AI_Employee_Vault/Approved/

# 6. Local email-approval-monitor will:
#    - Detect approved file
#    - Send email via Gmail API
#    - Move to Done/

# 7. Verify in Sent folder and Done/
```

### 6.2 Verify Dashboard Updates

```bash
# Cloud writes to Updates/
# Local merges into Dashboard.md (single writer rule)

cat AI_Employee_Vault/Updates/dashboard_update_*.json
cat AI_Employee_Vault/Dashboard.md
```

---

## Part 7: Security Rules

### 7.1 NEVER Sync These Files

Create `.gitignore` and Syncthing ignore patterns:

```
# Environment files
.env
.env.local
.env.cloud

# Authentication tokens
*_token.json
*_credentials.json
.gmail_token.json
.calendar_token.json
.slack_token.json

# WhatsApp sessions (LOCAL ONLY!)
whatsapp_session/
.whatsapp_state.json

# Banking credentials (LOCAL ONLY!)
.banking/
.payment_tokens/
.bank_*

# API keys
api_keys.json
secrets.json

# Certificates
*.pem
*.key
*.crt
```

### 7.2 Cloud VM Security

```bash
# Configure firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 8384  # Syncthing (if using)
sudo ufw enable

# Disable password login, use key-only
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no

# Restart SSH
sudo systemctl restart sshd
```

---

## Part 8: Health Monitoring

### 8.1 Cloud Health Monitor Script

```python
# File: scripts/cloud_health_monitor.py

#!/usr/bin/env python3
"""
Health monitor for Cloud VM.
Checks all processes and reports status to Updates/ for local to merge.
"""

import json
import os
import psutil
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path(os.getenv('VAULT_PATH', 'AI_Employee_Vault'))
UPDATES_PATH = VAULT_PATH / 'Updates'
UPDATES_PATH.mkdir(parents=True, exist_ok=True)

def get_health_status():
    """Collect health metrics from cloud VM."""

    status = {
        'timestamp': datetime.now().isoformat(),
        'hostname': os.uname().nodename,
        'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': {
            'percent': psutil.virtual_memory().percent,
            'available_gb': psutil.virtual_memory().available / (1024**3),
            'total_gb': psutil.virtual_memory().total / (1024**3)
        },
        'disk': {
            'percent': psutil.disk_usage('/').percent,
            'free_gb': psutil.disk_usage('/').free / (1024**3),
            'total_gb': psutil.disk_usage('/').total / (1024**3)
        },
        'processes': {}
    }

    # Check PM2 processes
    result = os.popen('pm2 jlist').read()
    try:
        pm2_processes = json.loads(result)
        for proc in pm2_processes:
            status['processes'][proc['name']] = {
                'status': proc['pm2_env']['status'],
                'cpu': proc['monit']['cpu'],
                'memory_mb': proc['monit']['memory'] / (1024**2),
                'uptime': proc['pm2_env'].get('pm_uptime', 0)
            }
    except:
        status['processes']['error'] = 'Could not read PM2 status'

    return status

def main():
    """Run health check and write to Updates/."""

    while True:
        try:
            status = get_health_status()

            # Write to Updates/ for local to merge
            update_file = UPDATES_PATH / f'cloud_health_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(update_file, 'w') as f:
                json.dump(status, f, indent=2)

            print(f"[Health Check] CPU: {status['cpu_percent']}% | "
                  f"Memory: {status['memory']['percent']}% | "
                  f"Disk: {status['disk']['percent']}%")

        except Exception as e:
            print(f"[ERROR] Health check failed: {e}")

        # Run every 5 minutes
        import time
        time.sleep(300)

if __name__ == '__main__':
    main()
```

---

## Checklist

### Cloud VM Setup
- [ ] Create Oracle/AWS VM
- [ ] Install Python 3.13+, Node.js 20+, PM2
- [ ] Clone AI Employee repository
- [ ] Configure `.env` (NO secrets)
- [ ] Set up vault sync (Git or Syncthing)
- [ ] Install Odoo with HTTPS
- [ ] Configure firewall
- [ ] Start cloud PM2 processes
- [ ] Test health monitor

### Local Machine Setup
- [ ] Update PM2 config for local-only processes
- [ ] Configure vault sync
- [ ] Start local PM2 processes
- [ ] Start Chrome automation
- [ ] Test approval flow

### Security Verification
- [ ] Secrets in `.gitignore`
- [ ] WhatsApp session NOT synced
- [ ] Banking credentials NOT synced
- [ ] Only tokens synced (safe)
- [ ] Firewall configured
- [ ] SSH key-only auth

### Demo Flow
- [ ] Cloud detects email while local offline
- [ ] Cloud drafts reply to Pending_Approval/
- [ ] Local comes online, approves draft
- [ ] Local sends email via MCP
- [ ] Logged to Done/

---

## Troubleshooting

### Sync Issues

```bash
# Check Git status
cd AI_Employee_Vault
git status

# Resolve merge conflicts
git pull origin main --rebase
git push origin main
```

### PM2 Process Issues

```bash
# Check cloud processes
ssh ubuntu@cloud-vm "pm2 status"

# Check logs
ssh ubuntu@cloud-vm "pm2 logs gmail-watcher-cloud --lines 100"
```

### Odoo Connection Issues

```bash
# Check Odoo status
sudo systemctl status odoo17

# Check logs
sudo tail -f /var/log/odoo/odoo17.log

# Restart Odoo
sudo systemctl restart odoo17
```

---

## Summary

**Platinum Tier delivers:**
- 24/7 monitoring via Cloud VM
- Draft-only actions on cloud (safe)
- Human approval on local (secure)
- Sensitive data stays local (WhatsApp, banking)
- Full audit trail in synced vault
- Automatic failover and health monitoring
- Production-ready AI Employee
