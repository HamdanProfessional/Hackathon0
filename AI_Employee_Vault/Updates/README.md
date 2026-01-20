# Updates - Cloud → Local Communication

This folder is used by the **Cloud Agent** to write updates that the **Local Agent** should merge into the Dashboard.

## Purpose

The **single-writer rule** states that only Local should update `Dashboard.md` directly. Cloud writes updates to this folder, and Local merges them.

## Why This Pattern?

**Problem:** If both Cloud and Local write to `Dashboard.md` simultaneously, you get git merge conflicts.

**Solution:** Cloud writes updates to `/Updates/`, Local merges them into `Dashboard.md`.

## Update Types

### Status Updates
```markdown
---
type: status_update
source: cloud
timestamp: 2026-01-20T12:00:00Z
---

## Cloud Status Summary

**Emails Processed:** 15
**Events Detected:** 3
**Drafts Created:** 8
**AI Decisions:** 12 (10 approved, 2 rejected)
```

### Alert Updates
```markdown
---
type: alert
source: cloud
timestamp: 2026-01-20T12:00:00Z
priority: high
---

## Alert: High Volume of Emails

Cloud detected 25+ emails in the last hour. Consider reviewing.
```

### Summary Updates
```markdown
---
type: summary
source: cloud
timestamp: 2026-01-20T12:00:00Z
period: 2026-01-20 11:00 - 12:00
---

## Hourly Summary

**New Items:** 12
**Processed:** 10
**Pending:** 2
**Errors:** 0
```

## Dashboard Merger Process

The `dashboard_merger.py` script runs every 2 minutes on Local:

1. Reads all files from `/Updates/`
2. Merges content into `Dashboard.md`
3. Deletes processed update files
4. Logs the merge operation

## Creating Update Files

### Cloud Agent

```python
from pathlib import Path
from datetime import datetime

updates_folder = Path("AI_Employee_Vault/Updates")

# Write update
update_file = updates_folder / f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
update_file.write_text(update_content)
```

### Local Agent (Automatic)

```bash
# Dashboard merger runs automatically via PM2 cron
# No manual action needed - it reads /Updates/ every 2 minutes
```

## File Naming Convention

- `update_YYYYMMDD_HHMMSS.md` - Timestamped updates
- `status_*.md` - Status updates
- `alert_*.md` - Alert notifications
- `summary_*.md` - Summary reports

## Cleanup

Processed update files are automatically deleted after merging. No manual cleanup needed.

---

*Last Updated: 2026-01-20*
*System Version: v1.5.0 (Platinum Tier)*
*Reference: scripts/dashboard_merger.py*
