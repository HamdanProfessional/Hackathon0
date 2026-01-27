#!/bin/bash
#
# AI Employee Platinum Tier - DigitalOcean One-Command Setup
#
# USAGE:
#   ssh root@143.244.143.143 'bash -s' < scripts/setup_digitalocean_one_command.sh
#
# Or download and run:
#   curl -fsSL https://raw.githubusercontent.com/your-repo/main/scripts/setup_digitalocean_one_command.sh | bash
#

set -e

echo "============================================================"
echo "   AI EMPLOYEE PLATINUM TIER - DIGITALOCEAN SETUP"
echo "============================================================"
echo ""
echo "Droplet: hackathon0-1vcpu-1gb"
echo "This will take 5-10 minutes..."
echo ""

# ============================================================
# STEP 1: Update System
# ============================================================
echo "[1/8] Updating system..."
apt update && apt upgrade -y
export DEBIAN_FRONTEND=noninteractive

# ============================================================
# STEP 2: Install Dependencies
# ============================================================
echo "[2/8] Installing Python, Git, Curl, UFW..."
apt install -y python3 python3-venv python3-pip python3-dev git curl ufw wget

# ============================================================
# STEP 3: Install Node.js 20
# ============================================================
echo "[3/8] Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# ============================================================
# STEP 4: Install PM2
# ============================================================
echo "[4/8] Installing PM2 process manager..."
npm install -g pm2

# ============================================================
# STEP 5: Create AI Employee User
# ============================================================
echo "[5/8] Creating aiemployee user..."
if ! id "aiemployee" &>/dev/null; then
    useradd -m -s /bin/bash aiemployee
    usermod -aG sudo aiemployee
    echo "✅ User 'aiemployee' created"
else
    echo "✅ User 'aiemployee' already exists"
fi

# ============================================================
# STEP 6: Clone Repository
# ============================================================
echo "[6/8] Cloning AI Employee repository..."
cd /home/aiemployee

# Remove existing directory if present
if [ -d "AI_EMPLOYEE_APP" ]; then
    echo "⚠️  Removing existing AI_EMPLOYEE_APP directory"
    rm -rf AI_EMPLOYEE_APP
fi

# STEP: Clone your repository
# IMPORTANT: Update REPO_URL below with your actual repository URL before running this script
# If you don't have a repository yet, you can initialize one locally or skip this step.
REPO_URL="${REPO_URL:-}"
if [ -z "$REPO_URL" ]; then
    echo "⚠️  REPO_URL not set - skipping repository clone"
    echo "   To set your repository, run: export REPO_URL='git@github.com:username/AI_EMPLOYEE_APP.git'"
    echo "   Then re-run this script, or clone manually after setup completes"
    echo ""
else
    echo "📥 Cloning repository from $REPO_URL"
    git clone "$REPO_URL" AI_EMPLOYEE_APP
fi

# Create placeholder directory structure for now
mkdir -p AI_EMPLOYEE_APP/AI_Employee_Vault
chown -R aiemployee:aiemployee AI_EMPLOYEE_APP

# ============================================================
# STEP 7: Setup Python Environment
# ============================================================
echo "[7/8] Setting up Python virtual environment..."
cd /home/aiemployee/AI_EMPLOYEE_APP

# Create virtual environment
sudo -u aiemployee python3 -m venv venv

# Install Python dependencies (if requirements.txt exists)
if [ -f "requirements.txt" ]; then
    echo "Installing Python requirements..."
    sudo -u aiemployee bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
else
    echo "⚠️  requirements.txt not found, skipping Python packages"
    echo "   Install manually after cloning repository"
fi

# Install Node dependencies (if package.json exists)
if [ -f "package.json" ]; then
    echo "Installing Node dependencies..."
    sudo -u aiemployee npm install
else
    echo "⚠️  package.json not found, skipping Node packages"
fi

# ============================================================
# STEP 8: Configure Firewall
# ============================================================
echo "[8/8] Configuring firewall..."
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (optional)
ufw allow 443/tcp   # HTTPS (optional)
echo "y" | ufw enable

# ============================================================
# DONE!
# ============================================================
echo ""
echo "============================================================"
echo "   ✅ SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Clone your repository:"
echo "   cd /home/aiemployee"
echo "   rm -rf AI_EMPLOYEE_APP"
echo "   git clone https://github.com/your-username/AI_EMPLOYEE_APP.git"
echo "   cd AI_EMPLOYEE_APP"
echo ""
echo "2. Install dependencies:"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   npm install"
echo ""
echo "3. Configure environment:"
echo "   cp .env.cloud.example .env"
echo "   nano .env  # Add your API keys"
echo ""
echo "4. Setup Gmail OAuth:"
echo "   python -m watchers.gmail_watcher --vault AI_Employee_Vault --cloud-mode"
echo ""
echo "5. Start cloud processes:"
echo "   su - aiemployee"
echo "   cd AI_EMPLOYEE_APP"
echo "   pm2 start process-manager/pm2.cloud.config.js"
echo "   pm2 save"
echo "   pm2 startup"
echo ""
echo "============================================================"
echo ""
