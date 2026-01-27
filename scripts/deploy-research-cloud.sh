#!/bin/bash
# Complete Cloud VM Deployment for Research LinkedIn Generator
# Supports systemd (recommended) or cron fallback

set -e

echo "================================================"
echo "Research LinkedIn Generator - Cloud VM Deploy"
echo "================================================"
echo ""

# Configuration
PROJECT_DIR="${HOME}/AI_EMPLOYEE_APP"
SERVICE_NAME="ai-research-daily"
USER="${USER:-ubuntu}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="unknown"
fi

echo "Detected OS: $OS"
echo "Project directory: $PROJECT_DIR"
echo ""

# 1. Install system dependencies
echo "[1/8] Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip nodejs npm git curl
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-pip nodejs npm git curl
elif command -v apk &> /dev/null; then
    apk add python3 py3-pip nodejs npm git curl
else
    echo "⚠ Unknown package manager, skipping system packages"
fi

# 2. Install Python dependencies
echo "[2/8] Installing Python dependencies..."
pip3 install --user requests 2>/dev/null || pip install requests

# 3. Setup Node.js dependencies for Playwright MCP
echo "[3/8] Setting up Playwright MCP..."
if [ -d "${PROJECT_DIR}/mcp-servers/playwright-mcp" ]; then
    cd "${PROJECT_DIR}/mcp-servers/playwright-mcp"
    npm install
    npm run build
else
    echo "⚠ Playwright MCP not found, skipping"
fi

# 4. Create directories
echo "[4/8] Creating directories..."
mkdir -p "${PROJECT_DIR}/AI_Employee_Vault"/{Inbox,Needs_Action,Pending_Approval,Approved,Rejected,Done,Plans,Briefings,Logs}
mkdir -p "${PROJECT_DIR}/logs"

# 5. Setup environment
echo "[5/8] Setting up environment..."

# Require GLM_API_KEY to be set
if [ -z "$GLM_API_KEY" ]; then
    echo "Error: GLM_API_KEY environment variable is required but not set"
    echo "Usage: GLM_API_KEY=your_key bash $0"
    exit 1
fi

export GLM_API_URL="https://api.z.ai/api/coding/paas/v4"
export USE_CDP="false"
export HEADLESS="true"
export PYTHONPATH="${PROJECT_DIR}"

# Add to .bashrc
if ! grep -q "GLM_API_KEY" "${HOME}/.bashrc" 2>/dev/null; then
    cat >> "${HOME}/.bashrc" << 'EOF'

# Research LinkedIn Generator
export GLM_API_KEY="\${GLM_API_KEY:-}"
export GLM_API_URL="https://api.z.ai/api/coding/paas/v4"
export USE_CDP="false"
export HEADLESS="true"
export PYTHONPATH="\${HOME}/AI_EMPLOYEE_APP"
EOF
    echo "✓ Environment added to .bashrc"
fi

# 6. Setup systemd (preferred method)
echo "[6/8] Setting up systemd service..."
SYSTEMD_DIR="${HOME}/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"

# Create service file
cat > "$SYSTEMD_DIR/${SERVICE_NAME}.service" << EOF
[Unit]
Description=AI Research LinkedIn Generator - Daily
After=network.target

[Service]
Type=oneshot
User=${USER}
WorkingDirectory=${PROJECT_DIR}
Environment="PYTHONPATH=${PROJECT_DIR}"
Environment="GLM_API_KEY=\${GLM_API_KEY}"
Environment="GLM_API_URL=https://api.z.ai/api/coding/paas/v4"
Environment="USE_CDP=false"
Environment="HEADLESS=true"
ExecStart=/usr/bin/python3 ${PROJECT_DIR}/.claude/skills/research-linkedin-generator/scripts/research.py --daily
StandardOutput=append:${PROJECT_DIR}/logs/research-service.log
StandardError=append:${PROJECT_DIR}/logs/research-service.log

[Install]
WantedBy=default.target
EOF

# Create timer file
cat > "$SYSTEMD_DIR/${SERVICE_NAME}.timer" << EOF
[Unit]
Description=Daily AI Research LinkedIn Generator
Requires=${SERVICE_NAME}.service

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload systemd and enable timer
systemctl --user daemon-reload 2>/dev/null || echo "⚠ systemctl --user not available (may need login session)"
systemctl --user enable ${SERVICE_NAME}.timer 2>/dev/null || true
systemctl --user start ${SERVICE_NAME}.timer 2>/dev/null || true

echo "✓ Systemd service and timer installed"

# 7. Test the setup
echo "[7/8] Testing setup..."
cd "${PROJECT_DIR}"
python3 .claude/skills/research-linkedin-generator/scripts/research.py --help

# 8. Show status
echo "[8/8] Installation complete!"
echo ""
echo "================================================"
echo "Deployment Summary"
echo "================================================"
echo ""
echo "Project: $PROJECT_DIR"
echo "Service: ${SERVICE_NAME}"
echo ""
echo "To test manually:"
echo "  cd ${PROJECT_DIR}"
echo "  python3 .claude/skills/research-linkedin-generator/scripts/research.py --daily"
echo ""
echo "Systemd commands:"
echo "  systemctl --user status ${SERVICE_NAME}.timer"
echo "  systemctl --user start ${SERVICE_NAME}.service  # Run immediately"
echo "  journalctl --user -u ${SERVICE_NAME}.service -f  # View logs"
echo ""
echo "Logs:"
echo "  tail -f ${PROJECT_DIR}/logs/research-service.log"
echo ""
echo "Generated posts will be in:"
echo "  ${PROJECT_DIR}/AI_Employee_Vault/Pending_Approval/"
echo ""
