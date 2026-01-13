---
name: migration-agent
description: Migrate data when updating vault structure. Use when reorganizing folders or renaming vault.
---

# Migration Agent

Migrate vault data and configurations safely.

## When to Use

- Renaming vault folder
- Reorganizing vault structure
- Updating file paths
- Merging multiple vaults

## What It Does

1. **Backup** - Creates backup before migration
2. **File Movement** - Moves files safely
3. **Config Updates** - Updates PM2, MCP configs
4. **Validation** - Verifies migration success
5. **Rollback** - Can undo if needed

## Quick Start

```
Migrate vault from vault/ to AI_Employee_Vault/
```

## Usage

```bash
python .claude/agents/migration-agent/scripts/migrate.py --source vault/ --target AI_Employee_Vault/
python .claude/agents/migration-agent/scripts/migrate.py --dry-run
python .claude/agents/migration-agent/scripts/migrate.py --rollback
```

## Safety Features

- Dry-run mode
- Automatic backups
- Validation checks
- Rollback support
- Migration logs
