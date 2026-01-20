# In Progress - Agent Claim Tracking

This folder implements the **claim-by-move rule** for multi-agent coordination.

## Purpose

When an agent (Cloud or Local) starts working on a task, it moves the task from `/Needs_Action/` to `/In_Progress/<agent>/` to claim ownership. Other agents must ignore tasks that are in progress.

## Claim-by-Move Rule

**Rule:** The first agent to move an item from `/Needs_Action/` to `/In_Progress/<agent>/` owns it. Other agents must ignore it.

## Folder Structure

### `/In_Progress/cloud/`
**Tasks being worked on by Cloud Agent:**
- Email triage (drafting replies)
- Event detection and categorization
- Social media content generation
- Accounting data collection
- Auto-approver decisions

**Cloud only performs DRAFT actions - never sends or posts without approval.**

### `/In_Progress/local/`
**Tasks being worked on by Local Agent:**
- Approval reviews
- Final execution (sending emails, posting to social media)
- WhatsApp monitoring
- File system processing
- Dashboard updates

**Local performs FINAL actions - only after human approval.**

## Usage

### Cloud Agent Claims a Task

```python
from watchers.claim_manager import CloudClaimManager

claim_manager = CloudClaimManager(vault_path)

# Claim a task
claim_manager.claim_task(
    task_file="AI_Employee_Vault/Needs_Action/EMAIL_123.md",
    agent="cloud"
)
# Moves: Needs_Action/EMAIL_123.md → In_Progress/cloud/EMAIL_123.md
```

### Local Agent Claims a Task

```python
from watchers.claim_manager import LocalClaimManager

claim_manager = LocalClaimManager(vault_path)

# Claim a task
claim_manager.claim_task(
    task_file="AI_Employee_Vault/Needs_Action/EMAIL_123.md",
    agent="local"
)
# Moves: Needs_Action/EMAIL_123.md → In_Progress/local/EMAIL_123.md
```

### Release a Task (When Complete)

```python
# When task is complete, move to Done
claim_manager.release_task(
    task_file="AI_Employee_Vault/In_Progress/cloud/EMAIL_123.md",
    destination="AI_Employee_Vault/Done/"
)
```

## Checking if Task is Claimed

```python
from watchers.claim_manager import is_task_claimed, get_task_owner

# Check if task is claimed
if is_task_claimed(vault_path, "EMAIL_123.md"):
    owner = get_task_owner(vault_path, "EMAIL_123.md")
    print(f"Task is claimed by: {owner}")  # "cloud" or "local"
```

## Rules for Agents

1. **Before starting work:** Check if task is in `/In_Progress/`
2. **If task is in `/In_Progress/`:** Skip it, another agent is working on it
3. **When starting work:** Move task to `/In_Progress/<agent>/`
4. **When done:** Move task to `/Done/` or `/Rejected/`

## Conflict Prevention

This system prevents:
- **Double work:** Two agents working on the same task
- **Race conditions:** Conflicting actions on the same item
- **Lost updates:** One agent overwriting another's work

---

*Last Updated: 2026-01-20*
*System Version: v1.5.0 (Platinum Tier)*
*Reference: watchers/claim_manager.py*
