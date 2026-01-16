# Process Management - Running Watchers 24/7

This guide explains how to keep your AI Employee watchers running continuously, automatically restart them if they crash, and start them on system boot.

## Why Process Management Matters

Python scripts run from terminal are fragile:
- **Terminate** when terminal closes
- **Crash** on unhandled exceptions
- **Don't recover** from system reboots

Process managers solve these problems by:
- **Auto-restarting** crashed processes
- **Logging** output to files
- **Starting** on system boot
- **Monitoring** process health

---

## Option 1: PM2 (Recommended - Easiest)

PM2 is a Node.js process manager that works great with Python scripts.

### Installation

```bash
# Install PM2 globally
npm install -g pm2
```

### Starting Watchers

```bash
# Start Gmail Watcher
pm2 start python --name "gmail-watcher" -- interpretersgmail_watcher

# Start Calendar Watcher
pm2 start python --name "calendar-watcher" -- interpreterscalendar_watcher

# Or use the orchestrator (runs both)
pm2 start python --name "ai-employee" -- interpretersorchestrator
```

### Managing Processes

```bash
# List all processes
pm2 list

# Show logs
pm2 logs

# Stop a process
pm2 stop gmail-watcher

# Restart a process
pm2 restart gmail-watcher

# Delete a process
pm2 delete gmail-watcher

# Stop all
pm2 stop all
```

### Auto-Start on Boot

```bash
# Save current process list
pm2 save

# Generate startup script
pm2 startup

# Run the command output by the above command
# (usually: sudo env PATH=$PATH:... pm2 startup systemd -u username)
```

### PM2 Configuration File

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: 'python',
      args: '-m watchers.gmail_watcher --vault . --credentials client_secret.json',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'calendar-watcher',
      script: 'python',
      args: '-m watchers.calendar_watcher --vault . --credentials client_secret.json',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    }
  ]
};
```

Then start with: `pm2 start ecosystem.config.js`

---

## Option 2: Supervisord (Python Native)

Supervisord is a Python-based process manager.

### Installation

```bash
# Install supervisord
pip install supervisor

# Generate configuration
echo_supervisord_conf > supervisord.conf
```

### Configuration

Add to `supervisord.conf`:

```ini
[program:gmail-watcher]
command=python -m watchers.gmail_watcher --vault . --credentials client_secret.json
directory=/path/to/PERSONAL_AI_EMPLOYEE
autostart=true
autorestart=true
stderr_logfile=/var/log/gmail-watcher.err.log
stdout_logfile=/var/log/gmail-watcher.out.log
user=yourusername

[program:calendar-watcher]
command=python -m watchers.calendar_watcher --vault . --credentials client_secret.json
directory=/path/to/PERSONAL_AI_EMPLOYEE
autostart=true
autorestart=true
stderr_logfile=/var/log/calendar-watcher.err.log
stdout_logfile=/var/log/calendar-watcher.out.log
user=yourusername
```

### Commands

```bash
# Start supervisord
supervisord -c supervisord.conf

# Control processes
supervisorctl status
supervisorctl stop gmail-watcher
supervisorctl start gmail-watcher
supervisorctl restart all
```

---

## Option 3: systemd (Linux Native)

If you're on Linux, systemd is built in.

### Service Files

Create `/etc/systemd/system/ai-employee-gmail.service`:

```ini
[Unit]
Description=AI Employee Gmail Watcher
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/PERSONAL_AI_EMPLOYEE
ExecStart=/usr/bin/python -m watchers.gmail_watcher --vault . --credentials client_secret.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Commands

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable ai-employee-gmail

# Start service
sudo systemctl start ai-employee-gmail

# Check status
sudo systemctl status ai-employee-gmail

# View logs
sudo journalctl -u ai-employee-gmail -f
```

---

## Option 4: Task Scheduler (Windows)

On Windows, use Task Scheduler.

### Setup

1. Open Task Scheduler
2. Create Basic Task
3. Name: "AI Employee Gmail Watcher"
4. Trigger: At startup
5. Action: Start a program
   - Program: `python.exe` (full path)
   - Arguments: `-m watchers.gmail_watcher --vault . --credentials client_secret.json`
   - Start in: `C:\Users\Hamdan\Desktop\testvault\PERSONAL_AI_EMPLOYEE`

### Keep Running

Task Scheduler doesn't auto-restart. Use a batch file wrapper:

```batch
@echo off
:loop
python -m watchers.gmail_watcher --vault . --credentials client_secret.json
timeout /t 10 /nobreak
goto loop
```

---

## Option 5: Custom Watchdog Script

The project includes a custom watchdog pattern in `orchestrator.py`.

### Running the Orchestrator

```bash
# Run in background
nohup python orchestrator.py --vault . --credentials client_secret.json &

# Or use screen/tmux
screen -S ai-employee
python orchestrator.py --vault . --credentials client_secret.json
# Ctrl+A, D to detach
```

### Custom Watchdog

Create `watchdog.py`:

```python
import subprocess
import time
import os

PROCESSES = [
    {'name': 'gmail-watcher', 'cmd': 'python -m watchers.gmail_watcher'},
    {'name': 'calendar-watcher', 'cmd': 'python -m watchers.calendar_watcher'},
]

running = {}

def start_process(name, cmd):
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    running[name] = proc
    print(f"Started {name}")

def check_and_restart():
    for proc_info in PROCESSES:
        name = proc_info['name']
        cmd = proc_info['cmd']

        if name not in running or running[name].poll() is not None:
            print(f"{name} not running, restarting...")
            start_process(name, cmd)

if __name__ == '__main__':
    for proc_info in PROCESSES:
        start_process(proc_info['name'], proc_info['cmd'])

    while True:
        check_and_restart()
        time.sleep(60)
```

---

## Monitoring

### Log Files

Watchers create logs at `/Logs/YYYY-MM-DD.json`

Check with:

```bash
# Today's activity
cat Logs/$(date +%Y-%m-%d).json | jq '.'

# Count actions today
cat Logs/$(date +%Y-%m-%d).json | jq '.action_type' | sort | uniq -c
```

### Health Check Script

Create `health_check.py`:

```python
#!/usr/bin/env python3
"""Check if watchers are healthy."""

import json
from pathlib import Path
from datetime import datetime, timedelta

vault_path = Path(".")
logs_path = vault_path / "Logs"

# Check for recent log activity (last 10 minutes)
cutoff = datetime.now() - timedelta(minutes=10)
today_log = logs_path / datetime.now().strftime("%Y-%m-%d.json")

if today_log.exists():
    with open(today_log) as f:
        for line in f:
            entry = json.loads(line)
            timestamp = datetime.fromisoformat(entry['timestamp'])
            if timestamp > cutoff:
                print(f"✓ {entry['watcher']} - Recent activity")
                break
        else:
            print("⚠️ No recent watcher activity")
else:
    print("⚠️ No log file for today")
```

---

## Summary

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| PM2 | Easy, cross-platform | Requires Node.js | Most users |
| Supervisord | Python native | Config complexity | Python-heavy setups |
| systemd | Built-in (Linux) | Linux only | Linux servers |
| Task Scheduler | Built-in (Windows) | No auto-restart | Windows desktop |
| Custom watchdog | Full control | Maintenance overhead | Learning |

---

*Process Management Documentation - Personal AI Employee v0.1*
