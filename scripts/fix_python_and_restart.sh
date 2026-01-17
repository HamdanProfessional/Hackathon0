#!/bin/bash
#
# One-command fix for Platinum Tier Cloud
# Fixes Python 3.13 compatibility issues by switching to Python 3.12
#

set -e

echo "============================================================"
echo "   PLATINUM TIER - PYTHON 3.12 FIX"
echo "============================================================"
echo ""

echo "[1/7] Installing Python 3.12..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

echo ""
echo "[2/7] Switching to AI Employee directory..."
cd /home/aiemployee/AI_EMPLOYEE_APP

echo ""
echo "[3/7] Recreating venv with Python 3.12..."
rm -rf venv
python3.12 -m venv venv

echo ""
echo "[4/7] Activating venv..."
source venv/bin/activate

echo ""
echo "[5/7] Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install urllib3==1.26.18
pip install slack-sdk
pip install pyopenssl certifi
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install psutil requests
pip install watchdog pyautogui pillow pyperclip
pip install playwright
pip install xero-python requests-oauthlib
pip install pyyaml

echo ""
echo "[6/7] Pulling latest PM2 config..."
git pull origin main

echo ""
echo "[7/7] Restarting PM2 processes..."
pm2 delete all
pm2 start process-manager/pm2.cloud.config.js
pm2 save

echo ""
echo "============================================================"
echo "   ✅ SETUP COMPLETE!"
echo "============================================================"
echo ""
pm2 status
echo ""
echo "All cloud processes should now be running with Python 3.12!"
echo ""
