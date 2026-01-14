---
name: deployment-agent
description: Deploy AI Employee system to new machine/server. Use when setting up on fresh system or scaling to new instances.
---

# Deployment Agent

Deploy complete AI Employee system to new machines.

## When to Use

- Setting up on new machine
- Deploying to server
- Scaling to multiple instances
- Rebuilding after crash

## What It Does

1. **Prerequisites Check** - Verifies Python, Node.js, Obsidian
2. **Dependency Installation** - Installs all required packages
3. **PM2 Setup** - Configures process manager
4. **Configuration** - Sets up vault, credentials, configs
5. **Smoke Tests** - Validates deployment

## Quick Start

```
Deploy AI Employee to new machine:
1. Check prerequisites
2. Install dependencies
3. Configure vault
4. Set up PM2
5. Run smoke tests
```

## Usage

```bash
python .claude/agents/deployment-agent/scripts/deploy.py --check
python .claude/agents/deployment-agent/scripts/deploy.py --install
python .claude/agents/deployment-agent/scripts/deploy.py --full
```

## Prerequisites

- Python 3.13+
- Node.js 24+ LTS
- Obsidian (optional)
- Git
- PM2
