---
name: workflow-validator
description: Validate complete workflows work end-to-end. Use when verifying watcher → approval → execution flows.
---

# Workflow Validator Agent

Validate that complete workflows function correctly.

## When to Use

- After deploying new watcher
- After system changes
- To validate all workflow steps
- To identify broken links

## What It Validates

1. **File Creation** - Watcher creates action files
2. **Vault Access** - Claude can read/write vault
3. **Approval Flow** - Files move through folders correctly
4. **MCP Execution** - Actions execute after approval
5. **Logging** - All steps logged correctly

## Quick Start

```
Validate the complete Gmail workflow from detection to email send
```

## Usage

```bash
python .claude/agents/workflow-validator/scripts/validate.py --workflow gmail
python .claude/agents/workflow-validator/scripts/validate.py --all
```

## Output

```
✅ Gmail workflow validated
  ✓ Watcher creates files
  ✓ Claude vault access works
  ✓ Approval flow works
  ✓ Email MCP connects
  ✓ End-to-end test passed
```
