---
name: integration-tester
description: Test end-to-end workflows and integrations with mock APIs. Use when validating complete flows or preventing regressions.
---

# Integration Tester Agent

Test complete workflows from detection to execution.

## When to Use

- Test invoice flow (WhatsApp → plan → approval → email)
- Validate watcher → Claude → approval → execution
- Test with mock APIs before real deployment
- Prevent regressions after changes

## What It Does

1. **Mock Servers** - Simulates Gmail, WhatsApp, Xero APIs
2. **Workflow Tests** - Validates complete flows
3. **Test Reports** - HTML and markdown reports
4. **Coverage** - Tracks which workflows are tested

## Quick Start

```
Test the complete invoice flow:
1. WhatsApp message detected
2. Plan created
3. Approval file generated
4. Email sent
```

## Usage

```bash
python .claude/agents/integration-tester/scripts/test.py --workflow invoice
python .claude/agents/integration-tester/scripts/test.py --all
```

## Reference

See `references/reference.md` for testing patterns
