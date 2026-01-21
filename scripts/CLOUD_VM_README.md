# Cloud VM Deployment - Research LinkedIn Generator

## Quick Start (Ubuntu/Debian)

```bash
# 1. Clone/upload your AI_EMPLOYEE_APP folder to the VM
scp -r AI_EMPLOYEE_APP user@your-vm:/home/user/

# 2. SSH into the VM and run the deployment script
ssh user@your-vm
cd AI_EMPLOYEE_APP
chmod +x scripts/deploy-research-cloud.sh
./scripts/deploy-research-cloud.sh
```

## What Gets Installed

- **Python 3** with requests library
- **Node.js** with npm (for Playwright MCP)
- **Systemd service** that runs daily at 9 AM
- **Environment variables** for GLM API

## How It Works

### Schedule
- Runs **daily at 9:00 AM** (local VM time)
- Rotates through 5 pre-configured topics:
  1. AI coding assistants and Claude Code updates
  2. Google AI Studio and Gemini development
  3. Rust programming language features
  4. TypeScript and modern JavaScript
  5. Python development and AI/ML tools

### Output
- Generated LinkedIn posts are saved to:
  ```
  AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_RESEARCH_*.md
  ```
- Review and move to `Approved/` to publish via linkedin-approval-monitor

## Commands

### Manual Testing
```bash
cd ~/AI_EMPLOYEE_APP
python3 .claude/skills/research-linkedin-generator/scripts/research.py --daily
```

### Systemd Service
```bash
# Check status
systemctl --user status ai-research-daily.timer

# Run immediately (don't wait for schedule)
systemctl --user start ai-research-daily.service

# View logs
journalctl --user -u ai-research-daily.service -f

# View file logs
tail -f ~/AI_EMPLOYEE_APP/logs/research-service.log
```

### Custom Topic
```bash
cd ~/AI_EMPLOYEE_APP
python3 .claude/skills/research-linkedin-generator/scripts/research.py \
  --process-topic "Your custom topic" \
  --urls "url1,url2,url3"
```

## Configuration

Edit topics and sources:
```bash
nano ~/AI_EMPLOYEE_APP/.claude/skills/research-linkedin-generator/daily_topics.json
```

Example:
```json
{
  "daily_topics": [
    {
      "topic": "Your custom topic",
      "sources": [
        "https://example.com/article1",
        "https://example.com/article2"
      ]
    }
  ]
}
```

## Troubleshooting

### Check if service is running
```bash
systemctl --user list-timers
```

### View last run results
```bash
ls -la ~/AI_Employee_Vault/Pending_Approval/
```

### Check logs
```bash
tail -50 ~/AI_EMPLOYEE_APP/logs/research-service.log
```

### Test API connection
```bash
cd ~/AI_EMPLOYEE_APP
python3 -c "
import requests
response = requests.get('https://api.z.ai/api/coding/paas/v4/models',
    headers={'Authorization': 'Bearer c414057ceccd4e8dae4ae3198f760c7a.BW9M3G4m8ers9woM'})
print(response.status_code)
"
```

## Cloud VM Requirements

- **OS**: Ubuntu 20.04+, Debian 10+, CentOS 7+, or similar
- **Python**: 3.7+
- **Node.js**: 14+ (for Playwright MCP)
- **Memory**: 512MB minimum
- **Disk**: 100MB minimum

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `GLM_API_KEY` | `c414057ceccd4e8dae4ae3198f760c7a.BW9M3G4m8ers9woM` | GLM API key |
| `GLM_API_URL` | `https://api.z.ai/api/coding/paas/v4` | API endpoint |
| `USE_CDP` | `false` | Use headless mode (no Chrome CDP) |
| `HEADLESS` | `true` | Run browser headlessly |
| `PYTHONPATH` | `/home/user/AI_EMPLOYEE_APP` | Project root |

## Updating

To update topics or configuration:

```bash
cd ~/AI_EMPLOYEE_APP
git pull  # or upload new files

# Reload systemd service
systemctl --user daemon-reload
systemctl --user restart ai-research-daily.timer
```
