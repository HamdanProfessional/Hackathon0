#!/bin/bash
###############################################################################
# Fix Cloud Git Sync - Cloud VM
#
# Diagnoses and fixes git-sync-push issues on cloud VM.
# Run this script on the cloud VM via SSH.
###############################################################################

set -e

echo "========================================="
echo "  Cloud Git Sync Fix Script"
echo "========================================="
echo ""

REPO_DIR="/root/AI_EMPLOYEE_APP"
cd "$REPO_DIR"

echo "[1/5] Checking PM2 status..."
pm2 status

echo ""
echo "[2/5] Checking git-sync-push logs..."
echo "--- ERROR LOG ---"
pm2 logs git-sync-push --err --lines 20 --nostream || echo "No error logs"
echo ""
echo "--- OUTPUT LOG ---"
pm2 logs git-sync-push --lines 20 --nostream || echo "No output logs"

echo ""
echo "[3/5] Checking git remote..."
git remote -v
echo ""
git ls-remote origin HEAD &>/dev/null && echo "✅ Git remote accessible" || echo "❌ Git remote NOT accessible"

echo ""
echo "[4/5] Testing git credentials..."
git config user.name && git config user.email || echo "⚠️  Git credentials not configured"

echo ""
echo "[5/5] Restarting git-sync-push..."
pm2 restart git-sync-push || pm2 start process-manager/pm2.cloud.config.js --only git-sync-push
pm2 save

echo ""
echo "========================================="
echo "  Fix Complete!"
echo "========================================="
echo ""
echo "Status:"
pm2 status | grep git-sync-push
echo ""
echo "Monitor logs with: pm2 logs git-sync-push"
