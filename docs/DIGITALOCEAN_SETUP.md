# DigitalOcean Setup for Platinum Tier

## Create Droplet

### Step 1: Create DigitalOcean Account
```
https://www.digitalocean.com/
Sign up → Add payment method ($6/month will be charged)
```

### Step 2: Create Droplet
```
1. Click "Create" → "Droplets"
2. Choose Region: Pick closest to you (e.g., New York, San Francisco, London)
3. Choose Image: Ubuntu 22.04 LTS
4. Choose Size: Basic - $6/month (1GB RAM, 1 vCPU, 25GB SSD)
   - Basic $4/mo (512MB RAM) may be too small
   - Recommended: Basic $6/mo (1GB RAM)
5. Choose Authentication: SSH Key
   - Add your local SSH key: cat ~/.ssh/id_rsa.pub
6. Hostname: ai-employee-cloud
7. Click "Create Droplet"
```

### Step 3: Connect to Droplet
```bash
# Get droplet IP from DigitalOcean dashboard
ssh root@your_droplet_ip

# Or with specific key:
ssh -i ~/.ssh/your_key root@your_droplet_ip
```

## Setup AI Employee on DigitalOcean

### Option A: Automated Setup (Recommended)
```bash
# Run this on your new droplet
curl -fsSL https://raw.githubusercontent.com/your-repo/AI_EMPLOYEE/main/scripts/setup_digitalocean.sh | bash
```

### Option B: Manual Setup
```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.13
apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.13 python3.13-venv python3.13-dev python3-pip git

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install PM2
npm install -g pm2

# Create user (recommended - don't run as root)
useradd -m -s /bin/bash aiemployee
usermod -aG sudo aiemployee
su - aiemployee

# Clone repository
cd ~
git clone https://github.com/your-repo/AI_EMPLOYEE_APP.git
cd AI_EMPLOYEE_APP

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install

# Create vault directory
mkdir -p AI_Employee_Vault
```

### Configure Environment
```bash
# As aiemployee user
cd ~/AI_EMPLOYEE_APP

# Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
GMAIL_CLOUD_TOKEN_PATH=/home/aiemployee/.gmail_token.json
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-signing-secret
VAULT_PATH=/home/aiemployee/AI_EMPLOYEE_APP/AI_Employee_Vault
EOF

# Setup Gmail OAuth (will prompt for auth)
python -m watchers.gmail_watcher --vault AI_Employee_Vault --cloud-mode
```

### Start Cloud Processes
```bash
# Start PM2 processes
pm2 start process-manager/pm2.cloud.config.js
pm2 save

# Check status
pm2 status
```

### Enable PM2 on Startup
```bash
# As root user
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u aiemployee --hp /home/aiemployee

# Or as aiemployee with sudo:
pm2 startup
```

## Setup Vault Sync (Git)

### On DigitalOcean:
```bash
cd ~/AI_EMPLOYEE_APP/AI_Employee_Vault
git init
git remote add origin https://github.com/your-username/ai-employee-vault.git
git pull origin main

# Set up periodic pulls
echo "export VAULT_REPO_URL=https://github.com/your-username/ai-employee-vault.git" >> ~/.bashrc
```

### On Local Machine:
```bash
cd AI_Employee_Vault
git init
git add .
git commit -m "Initial vault state"
git remote add origin https://github.com/your-username/ai-employee-vault.git
git push -u origin main
```

## Firewall Setup (Recommended)
```bash
# Enable firewall
ufw allow 22    # SSH
ufw allow 80    # HTTP (optional, for web access)
ufw allow 443   # HTTPS (optional, for web access)
ufw enable

# Check status
ufw status
```

## DigitalOcean Specific Features

### Backups (Optional - $1/month)
```bash
# Enable backups from DigitalOcean dashboard
# Droplets → Your Droplet → Backups → Enable
```

### Monitoring (Free)
```bash
# DigitalOcean provides built-in monitoring
# View in dashboard: Droplets → Your Droplet → Metrics
```

### Resize if Needed
```bash
# From DigitalOcean dashboard:
# Droplets → Your Droplet → Resize
# Can upgrade/downgrade instantly
```

## Cost Comparison

| Provider | Plan | Monthly | Annual | RAM | CPU | Storage |
|----------|------|---------|--------|-----|-----|---------|
| Oracle Cloud | Free Tier | FREE | FREE | 1GB | 1 | 10GB |
| DigitalOcean | Basic | $6 | $72 | 1GB | 1 | 25GB |
| DigitalOcean | Basic | $4 | $48 | 512MB | 1 | 10GB |
| AWS | t2.micro | ~$8 | ~$96 | 1GB | 1 | - |
| GCP | e2-micro | ~$5 | ~$60 | 1GB | 2 | 30GB |

## Performance Comparison

### Oracle Cloud Free Tier
- ✅ Free
- ⚠️ Can be slow during peak times
- ⚠️ May be rebooted without notice
- ⚠️ Limited regions
- ✅ 1GB RAM

### DigitalOcean $6/month
- ✅ Consistent performance
- ✅ Never reboots unexpectedly
- ✅ Many regions
- ✅ Excellent support/docs
- ✅ 1GB RAM
- ✅ 25GB storage
- ✅ Easy scaling

## Recommendation

**For Production:** DigitalOcean $6/month
- More reliable
- Better performance
- Professional support
- Easy to scale

**For Testing:** Oracle Cloud Free
- Free testing ground
- Learn the setup
- Migrate to DO later

## Troubleshooting DigitalOcean

### Droplet won't start
```bash
# Check droplet status in DigitalOcean dashboard
# If "Off", click "Power On"
# If stuck, try "Power Cycle" from console
```

### Out of memory (512MB droplet)
```bash
# Check memory usage
free -h

# If consistently >80%, upgrade to $6 plan
# From dashboard: Resize → Upgrade
```

### Can't SSH
```bash
# Use DigitalOcean web console from dashboard
# Check firewall: ufw status
# Check SSH service: systemctl status sshd
```

### PM2 processes crashing
```bash
# Check logs
pm2 logs

# Check if out of memory
dmesg | grep -i kill
```

## Migration from Oracle to DigitalOcean

```bash
# On DigitalOcean droplet
cd ~
git clone https://github.com/your-repo/AI_EMPLOYEE_APP.git
cd AI_EMPLOYEE_APP
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install

# Copy .env from Oracle (manually, securely)
# Copy .gmail_token.json from Oracle (manually, securely)

# Start processes
pm2 start process-manager/pm2.cloud.config.js
pm2 save
```

## Summary

**DigitalOcean is BETTER for production Platinum Tier:**
- ✅ More reliable ($6/month)
- ✅ Better performance
- ✅ Easier to manage
- ✅ Professional grade

**Oracle Cloud is GOOD for testing:**
- ✅ Free
- ⚠️ Less reliable
- ⚠️ Can be slow

**Recommendation:** Start with Oracle Free, migrate to DigitalOcean $6 when ready for production.
