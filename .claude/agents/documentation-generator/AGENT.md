---
name: documentation-generator
description: Generate docs from code structure. Use for auto-generating README, API docs, and setup guides.
---

# Documentation Generator Agent

Automatically generate documentation from source code.

## When to Use

- After writing new watcher
- After adding MCP server
- To keep docs in sync with code
- To generate API references

## What It Generates

1. **README.md** - Project overview and setup
2. **API Docs** - Function and class documentation
3. **Setup Guides** - Step-by-step installation
4. **Architecture Diagrams** - Visual representations
5. **Troubleshooting** - Common issues

## Quick Start

```
Generate documentation for gmail-watcher
```

## Usage

```bash
python .claude/agents/documentation-generator/scripts/generate.py --target watchers/gmail_watcher.py
python .claude/agents/documentation-generator/scripts/generate.py --all
```

## Features

- Parses docstrings
- Extracts function signatures
- Generates markdown
- Creates diagrams
- Auto-updates existing docs
