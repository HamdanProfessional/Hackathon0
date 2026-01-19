#!/bin/bash
###############################################################################
# AI Employee - Platinum Tier Cloud Setup Script
# DigitalOcean Ubuntu 22.04 LTS
#
# This script automates 95% of the cloud VM setup
#
# USAGE:
#   ssh root@YOUR_DROPLET_IP 'bash -s' < setup_digitalocean_platinum_tier.sh
#
# Or download and run:
#   curl -O https://raw.githubusercontent.com/YOUR_USERNAME/AI_EMPLOYEE_APP/main/scripts/setup_digitalocean_platinum_tier.sh
#   bash setup_digitalocean_platinum_tier.sh
###############################################################################

set -e  # Exit on any error

REPO_URL="${REPO_URL:-https://github.com/YOUR_USERNAME/AI_EMPLOYEE_APP.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"
PROJECT_DIR="AI_EMPLOYEE_APP"
GITHUB_EMAIL="${GITHUB_EMAIL:-your-email@example.com}"
GITHUB_NAME="${GITHUB_NAME:-Your Name}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     AI Employee - Platinum Tier Cloud Setup                        ║"
echo "║     DigitalOcean Ubuntu 22.04 LTS                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ========================================
# Step 1: System Update
# ========================================
echo "[1/10] Updating system packages..."
apt update && apt upgrade -y

# ========================================
# Step 2: Install Dependencies
# ========================================
echo "[2/10] Installing Python 3.13, Node.js, Git, PM2..."

# Install Python 3.13
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.13 python3.13-venv python3-pip python3.13-dev

# Install Node.js 24.x
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt install -y nodejs

# Install Git
apt install -y git

# Install PM2 globally
npm install -g pm2

# Verify installations
echo ""
echo "✅ Installed versions:"
echo "   Python: $(python3.13 --version)"
echo "   Node.js: $(node --version)"
echo "   PM2: $(pm2 --version)"
echo "   Git: $(git --version)"
echo ""

# ========================================
# Step 3: Configure Git
# ========================================
echo "[3/10] Configuring Git..."
git config --global user.email "$GITHUB_EMAIL"
git config --global user.name "$GITHUB_NAME"

# ========================================
# Step 4: Clone Repository
# ========================================
echo "[4/10] Cloning repository..."
if [ -d "$PROJECT_DIR" ]; then
    echo "   Repository already exists, pulling latest..."
    cd "$PROJECT_DIR"
    git pull origin "$REPO_BRANCH"
else
    git clone -b "$REPO_BRANCH" "$REPO_URL"
    cd "$PROJECT_DIR"
fi
echo "   Repository location: $(pwd)"
echo ""

# ========================================
# Step 5: Install Python Dependencies
# ========================================
echo "[5/10] Installing Python dependencies..."
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# ========================================
# Step 6: Install MCP Servers
# ========================================
echo "[6/10] Installing MCP servers..."
cd mcp-servers

# Install Email MCP
cd email-mcp
npm install

# Install Calendar MCP
cd ../calendar-mcp
npm install

# Install Xero MCP
cd ../xero-mcp
npm install

cd ..
echo "✅ MCP servers installed"
echo ""

# ========================================
# Step 7: Create Cloud Environment File
# ========================================
echo "[7/10] Creating .env.cloud file..."
cat > .env.cloud << 'EOF'
# AI Employee Cloud Environment Variables
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Anthropic API for Auto-Approver (Claude 3 Haiku)
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE

# Slack Bot Token (for Slack Watcher)
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN_HERE

# Odoo Credentials (if using Odoo)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=admin
ODOO_PASSWORD=CHANGE_THIS_PASSWORD

# Git Configuration
GIT_REPO_URL=$REPO_URL
GIT_BRANCH=$REPO_BRANCH

# Timezone
TZ=UTC
EOF

chmod 600 .env.cloud
echo "✅ Created .env.cloud"
echo "   ⚠️  PLEASE EDIT .env.cloud and add your actual API keys!"
echo ""

# ========================================
# Step 8: Create PM2 Ecosystem Config
# ========================================
echo "[8/10] Creating PM2 ecosystem config..."
cp process-manager/pm2.config.js ecosystem.config.js

# Update for DigitalOcean (uses absolute path)
CURRENT_DIR=$(pwd)
sed -i "s|PROJECT_ROOT = process.cwd()|PROJECT_ROOT = '$CURRENT_DIR'|" ecosystem.config.js
sed -i "s|const PROJECT_ROOT = path.join('C:', 'Users', 'User', 'Desktop', 'AI_EMPLOYEE_APP');|const PROJECT_ROOT = '$CURRENT_DIR';|" ecosystem.config.js

echo "✅ PM2 config created"
echo ""

# ========================================
# Step 9: Start PM2 Processes
# ========================================
echo "[9/10] Starting PM2 processes..."

# Kill any existing PM2 processes
pm2 delete all || true

# Start all processes
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Setup PM2 startup on reboot
pm2 startup | tail -n 1 || true

echo "✅ PM2 processes started"
echo ""
pm2 list
echo ""

# ========================================
# Step 10: Setup Git Auto-Push Cron
# ========================================
echo "[10/10] Setting up Git auto-push cron..."

# Make scripts executable
chmod +x scripts/git_sync_push.sh

# Add cron job to push every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * cd $CURRENT_DIR && scripts/git_sync_push.sh >> /var/log/cloud_git_sync.log 2>&1") | crontab -

echo "✅ Git auto-push scheduled (every 5 minutes)"
echo ""

# ========================================
# Setup Complete!
# ========================================
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              🎉 SETUP COMPLETE! 🎉                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "NEXT STEPS:"
echo "───────────"
echo "1. 📝 Edit .env.cloud and add your API keys:"
echo "      nano .env.cloud"
echo ""
echo "2. 🔄 Restart PM2 processes with new env:"
echo "      pm2 reload all"
echo ""
echo "3. ✅ Verify all processes are online:"
echo "      pm2 list"
echo ""
echo "4. 🧪 Test the system:"
echo "      # Check if watchers are detecting items"
echo "      # Check if auto-approver is running"
echo "      pm2 logs auto-approver"
echo ""
echo "5. 📊 Monitor the system:"
echo "      pm2 logs"
echo "      pm2 monit"
echo ""
echo "6. 🌐 Your droplet IP:"
echo "      $(curl -s ifconfig.me || echo '<your-ip-here>')"
echo ""
echo "📖 For troubleshooting, see: docs/TROUBLESHOOTING.md"
echo "📋 Full implementation plan: docs/PLATINUM_TIER_IMPLEMENTATION_PLAN.md"
echo ""
echo "✨ Cloud VM is now running and ready for Platinum Tier!"
echo ""
