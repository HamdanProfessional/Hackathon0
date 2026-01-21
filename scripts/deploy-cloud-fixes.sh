#!/bin/bash
###############################################################################
# Deploy Cloud Fixes - Cloud VM
#
# Run this script on the cloud VM to fix git-sync-push and apply all updates.
# SSH into your cloud VM and run:
#
#   curl -o deploy-cloud-fixes.sh https://raw.githubusercontent.com/.../deploy-cloud-fixes.sh
#   chmod +x deploy-cloud-fixes.sh
#   ./deploy-cloud-fixes.sh
#
###############################################################################

set -e

echo "========================================="
echo "  AI Employee - Cloud Fixes Deployment"
echo "========================================="
echo ""

REPO_DIR="/root/AI_EMPLOYEE_APP"
cd "$REPO_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/7] Pulling latest code from GitHub...${NC}"
git pull origin main || echo -e "${RED}Warning: Git pull failed, continuing...${NC}"

echo -e "${YELLOW}[2/7] Making git_sync_push.sh executable...${NC}"
chmod +x scripts/git_sync_push.sh
ls -la scripts/git_sync_push.sh

echo -e "${YELLOW}[3/7] Stopping all PM2 processes...${NC}"
pm2 stop all || true

echo -e "${YELLOW}[4/7] Updating PM2 configuration...${NC}"
pm2 delete all || true
pm2 resurrect || pm2 start process-manager/pm2.cloud.config.js

echo -e "${YELLOW}[5/7] Starting git-sync-push...${NC}"
pm2 start process-manager/pm2.cloud.config.js --only git-sync-push
pm2 logs git-sync-push --lines 10 --nostream

echo -e "${YELLOW}[6/7] Saving PM2 configuration...${NC}"
pm2 save
pm2 startup | tail -1

echo -e "${YELLOW}[7/7] Verifying status...${NC}"
echo ""
echo "PM2 Process Status:"
pm2 status
echo ""
echo "Git Sync Status (last 5 lines):"
pm2 logs git-sync-push --lines 5 --nostream

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Monitor: pm2 logs git-sync-push"
echo "  2. Check status: pm2 status"
echo "  3. View dashboard: cat AI_Employee_Vault/Dashboard.md"
echo ""
echo -e "${YELLOW}Note: The git-sync-push will now run every 5 minutes and auto-restart if it fails.${NC}"
