#!/bin/bash
# Cron Setup for Research LinkedIn Generator (Alternative to PM2)
# Use this if you don't want to use PM2 on cloud VM

set -e

PROJECT_DIR="${HOME}/AI_EMPLOYEE_APP"

echo "Setting up cron job for daily research..."

# Create cron entry - runs daily at 9 AM
CRON_ENTRY="0 9 * * * cd ${PROJECT_DIR} && /usr/bin/python3 .claude/skills/research-linkedin-generator/scripts/research.py --daily >> ${PROJECT_DIR}/logs/research-cron.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null | grep -v "research-linkedin-generator"; echo "$CRON_ENTRY") | crontab -

echo "✓ Cron job installed"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "To view logs:"
echo "  tail -f ${PROJECT_DIR}/logs/research-cron.log"
echo ""
echo "To test immediately:"
echo "  cd ${PROJECT_DIR}"
echo "  python3 .claude/skills/research-linkedin-generator/scripts/research.py --daily"
