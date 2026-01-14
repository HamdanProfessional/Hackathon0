---
name: debug-agent
description: Debug broken watchers, MCPs, and workflows by analyzing logs and detecting common error patterns. Use when components fail or behave unexpectedly.
---

# Debug Agent

Analyze and fix issues with watchers, MCP servers, and workflows.

## When to Use

- Watcher crashes or stops detecting items
- MCP server won't connect
- Workflow broken at some step
- Authentication errors
- Rate limiting issues

## What It Does

1. **Log Analysis** - Parses PM2 and application logs
2. **Pattern Detection** - Identifies common error patterns
3. **Root Cause** - Determines underlying issue
4. **Suggested Fixes** - Provides actionable solutions
5. **Verification** - Tests fixes work

## Quick Start

```
Debug gmail-watcher that's crashing with authentication errors
```

## Common Issues Detected

- Expired OAuth tokens
- Rate limiting (HTTP 429)
- Invalid credentials
- Network timeouts
- File permission errors
- Missing dependencies
- Configuration errors

## Usage

```bash
# Debug a watcher
python .claude/agents/debug-agent/scripts/debug.py gmail-watcher

# Analyze specific log file
python .claude/agents/debug-agent/scripts/debug.py --log /path/to/log

# Check all PM2 processes
python .claude/agents/debug-agent/scripts/debug.py --check-all
```

## Reference

See `references/reference.md` for error patterns and solutions
