#!/bin/bash
# Cloud VM Setup Script for Research LinkedIn Generator
# Run this on your cloud VM to set up the research system

set -e

echo "=========================================="
echo "Research LinkedIn Generator - Cloud VM Setup"
echo "=========================================="
echo ""

# Project directory
PROJECT_DIR="${HOME}/AI_EMPLOYEE_APP"
VAULT_DIR="${PROJECT_DIR}/AI_Employee_Vault"

# 1. Install system dependencies
echo "[1/6] Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm git curl

# 2. Install Python dependencies
echo "[2/6] Installing Python dependencies..."
cd "${PROJECT_DIR}"
pip3 install --user requests

# 3. Setup Node.js dependencies for Playwright MCP
echo "[3/6] Setting up Playwright MCP..."
cd "${PROJECT_DIR}/mcp-servers/playwright-mcp"
npm install
npm run build

# 4. Create directories
echo "[4/6] Creating vault directories..."
mkdir -p "${VAULT_DIR}"/{Inbox,Needs_Action,Pending_Approval,Approved,Rejected,Done,Plans,Briefings,Logs}

# 5. Setup environment
echo "[5/6] Setting up environment..."
cat >> "${HOME}/.bashrc" << 'EOF'

# Research LinkedIn Generator
export GLM_API_KEY="c414057ceccd4e8dae4ae3198f760c7a.BW9M3G4m8ers9woM"
export GLM_API_URL="https://api.z.ai/api/coding/paas/v4"
export USE_CDP="false"
export HEADLESS="true"
export PYTHONPATH="${PROJECT_DIR}"
EOF

source "${HOME}/.bashrc"

# 6. Test the setup
echo "[6/6] Testing setup..."
cd "${PROJECT_DIR}"
python3 .claude/skills/research-linkedin-generator/scripts/research.py --help

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To test daily research:"
echo "  cd ${PROJECT_DIR}"
echo "  python3 .claude/skills/research-linkedin-generator/scripts/research.py --daily"
echo ""
echo "To add to PM2:"
echo "  pm2 start process-manager/pm2.config.js --update-env"
echo ""
