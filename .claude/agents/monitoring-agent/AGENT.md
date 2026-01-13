---
name: monitoring-agent
description: Monitor health of running AI Employee system. Use for production health checks and performance metrics.
---

# Monitoring Agent

Monitor system health and generate reports.

## When to Use

- Daily health checks
- Performance issues
- Before deployments
- Troubleshooting problems

## What It Monitors

1. **PM2 Processes** - Status, CPU, memory
2. **Vault Folders** - Sizes, file counts
3. **Logs** - Growth, error rates
4. **Credentials** - Expiry warnings
5. **Disk Space** - Available storage

## Quick Start

```
Generate health dashboard for all components
```

## Usage

```bash
python .claude/agents/monitoring-agent/scripts/monitor.py
python .claude/agents/monitoring-agent/scripts/monitor.py --dashboard
python .claude/agents/monitoring-agent/scripts/monitor.py --alert
```

## Output

```
📊 System Health Dashboard

PM2 Processes:
  ✅ gmail-watcher (PID: 12345, CPU: 2%, MEM: 150MB)
  ✅ calendar-watcher (PID: 12346, CPU: 1%, MEM: 120MB)

Vault:
  📁 Needs_Action: 12 files
  📁 Logs: 156 files (24MB)

Status: All systems operational
```
