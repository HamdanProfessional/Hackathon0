#!/bin/bash
# Quick System Status Check
# Shows essential AI Employee system status at a glance

echo "=================================="
echo "AI EMPLOYEE SYSTEM STATUS"
echo "=================================="
echo ""

echo "[LOCAL MACHINE]"
pm2 status --json 2>/dev/null | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    processes = data.get('processes', [])
    online = [p for p in processes if p.get('pm2_env', {}).get('status') == 'online']
    print(f\"  Online: {len(online)}/{len(processes)} processes\")

    # Show any with high restarts
    for p in processes:
        name = p.get('name', 'unknown')
        restarts = p.get('pm2_env', {}).get('restart_time', 0)
        if isinstance(restarts, int) and restarts > 5:
            print(f\"  [!] {name}: {restarts} restarts\")
except:
    pass
"

echo ""
echo "[CLOUD VM]"
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@143.244.143.143 "cd /root/AI_EMPLOYEE_APP && pm2 status --json 2>/dev/null" 2>&1 | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    processes = data.get('processes', [])
    online = [p for p in processes if p.get('pm2_env', {}).get('status') == 'online']
    print(f\"  Online: {len(online)}/{len(processes)} processes\")

    # Show any with high restarts
    for p in processes:
        name = p.get('name', 'unknown')
        restarts = p.get('pm2_env', {}).get('restart_time', 0)
        if isinstance(restarts, int) and restarts > 5:
            print(f\"  [!] {name}: {restarts} restarts\")
except:
    print('  [!] Could not connect to Cloud VM')
" 2>/dev/null || echo "  [!] Could not connect to Cloud VM"

echo ""
echo "[GIT SYNC]"
UNCOMMITTED=$(git status --short | wc -l)
echo "  Uncommitted changes: $UNCOMMITTED"

if [ $UNCOMMITTED -eq 0 ]; then
    AHEAD=$(git log -1 --oneline 2>/dev/null)
    BEHIND=$(git rev-list --count origin/main..HEAD 2>/dev/null)
    if [ "$BEHIND" != "0" ]; then
        echo "  Local is $BEHIND commits ahead of origin"
    else
        echo "  Local is up to date with origin"
    fi
else
    echo "  [!] Uncommitted changes exist"
fi

echo ""
echo "=================================="
echo "Run 'python scripts/system_health_report.py' for detailed report"
echo "=================================="
