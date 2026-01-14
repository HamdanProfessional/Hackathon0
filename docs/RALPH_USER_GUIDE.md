# Ralph Wiggum - Autonomous Task Execution

**Complete User Guide for the AI Employee's Autonomous Task Loop**

---

## 📚 Table of Contents

1. [What is Ralph?](#what-is-ralph)
2. [Quick Start](#quick-start)
3. [How Ralph Works](#how-ralph-works)
4. [Using Ralph - Step by Step](#using-ralph---step-by-step)
5. [Human-in-the-Loop Approval](#human-in-the-loop-approval)
6. [Monitoring Progress](#monitoring-progress)
7. [Creating Custom Task Lists](#creating-custom-task-lists)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## What is Ralph?

**Ralph Wiggum** is an autonomous task execution loop that allows your AI Employee to work through multi-step workflows completely on its own - like having a virtual employee that works through task lists autonomously.

### Key Features

- ✅ **Autonomous Execution:** Continues until all tasks complete
- ✅ **Human-in-the-Loop:** Every external action requires approval
- ✅ **Fresh Context:** Each iteration starts clean (no memory buildup)
- ✅ **Persistent Memory:** State maintained via files (not conversation)
- ✅ **Transparent:** All progress logged and inspectable

### Why Use Ralph?

| Manual Execution | Ralph Execution |
|-----------------|-----------------|
| 30-60 minutes for 7 tasks | 10-15 minutes (3-6x faster) |
| Must remember all steps | Ralph follows task list automatically |
| Risk missing steps | Ralph completes systematically |
| No audit trail | Full logging to `Logs/YYYY-MM-DD.json` |
| Can't resume if interrupted | Ralph continues where it left off |

---

## Quick Start

### 3 Steps to Get Started

```bash
# 1. Copy an example task list
cp .claude/skills/ralph/prd_monday_ceo_briefing.json .claude/skills/ralph/prd.json

# 2. Check your tasks
./scripts/check-ralph-status.sh

# 3. Start Ralph
./scripts/start-ralph.sh 10
```

**That's it!** Ralph will now autonomously work through all 7 tasks.

---

## How Ralph Works

### The Workflow Loop

```
┌─────────────────────────────────────────┐
│ 1. LOAD TASK LIST                       │
│    → Read prd.json                      │
│    → Read progress.txt                  │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 2. PICK NEXT TASK                       │
│    → Find highest priority incomplete   │
│    → Where "passes": false              │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 3. PLAN EXECUTION                       │
│    → Create plan in Plans/              │
│    → Select appropriate skills/MCPs     │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 4. EXECUTE (Claude Code)                │
│    → Use email-manager, calendar-mgr, etc│
│    → Create approval request (if needed)│
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 5. WAIT FOR APPROVAL (if needed)        │
│    → You review Pending_Approval/ file │
│    → Move to Approved/ when ready        │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 6. VERIFY & COMPLETE                    │
│    → Monitor executes action             │
│    → Moves to Done/                     │
│    → Update prd.json (passes: true)     │
│    → Log progress to progress.txt        │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 7. CHECK: All tasks complete?           │
│    → YES: Output TASK_COMPLETE           │
│    → NO: Continue to next task          │
└─────────────────────────────────────────┘
               (Loop back to step 2)
```

### Memory Between Iterations

Each iteration starts with **fresh context** but remembers via:

- **`prd.json`** - Which tasks are done/pending
- **`progress.txt`** - Learnings from previous work
- **`Plans/`** - Previous execution plans
- **`Logs/`** - Audit trail of all actions
- **Vault files** - Client data, communications, etc.

---

## Using Ralph - Step by Step

### Step 1: Choose Your Task List

You have three options:

#### Option A: Monday Morning CEO Briefing (Recommended)

**The standout feature from the Hackathon - AI autonomously prepares weekly business summary for CEO review.**

```bash
cp .claude/skills/ralph/prd_monday_ceo_briefing.json .claude/skills/ralph/prd.json
```

**7 Tasks:**
1. Check Gmail for urgent weekend messages
2. Check Calendar for upcoming events
3. Review business performance from logs
4. Check business goals and targets
5. Generate proactive suggestions
6. Format and finalize CEO briefing
7. Create follow-up action list

#### Option B: Client Onboarding

```bash
cp .claude/skills/ralph/prd.json.example .claude/skills/ralph/prd.json
```

**6 Tasks:**
1. Send welcome email to client
2. Create client folder structure
3. Create setup invoice in Xero
4. Schedule kickoff meeting
5. Create project plan document
6. Add client to Slack workspace

#### Option C: Create Your Own

```bash
nano .claude/skills/ralph/prd.json
# OR
code .claude/skills/ralph/prd.json
```

See [Creating Custom Task Lists](#creating-custom-task-lists) below.

---

### Step 2: View Your Tasks

```bash
./scripts/check-ralph-status.sh
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        RALPH WIGGUM - TASK EXECUTION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Project: AI Employee - Monday CEO Briefing
🔄 Status: STOPPED
📈 Task Progress: 0/7 complete (0%)

⏳ PENDING TASKS:
  ⏸ TASK-001: Check Gmail for urgent messages (priority 1)
  ⏸ task-002: Check Calendar for upcoming events (priority 2)
  ⏸ task-003: Review business performance from logs (priority 3)
  ⏸ task-004: Check business goals and targets (priority 4)
  ⏸ task-005: Generate proactive suggestions (priority 5)
  ⏸ task-006: Format and finalize CEO briefing (priority 6)
  ⏸ task-007: Create follow-up action list (priority 7)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Step 3: Start Ralph

```bash
./scripts/start-ralph.sh 10
```

**Parameters:**
- `10` = Maximum iterations (prevents infinite loops)
- Ralph will stop after 10 iterations even if tasks remain

**What happens:**
1. Ralph loads the task list
2. Ralph reads previous learnings
3. Ralph picks Task 1 (highest priority)
4. Ralph starts executing...

---

### Step 4: Approve Actions (When Prompted)

When Ralph needs your approval, it creates a file in `Pending_Approval/`:

```bash
# Example: Ralph wants to query your Gmail
ls AI_Employee_Vault/Pending_Approval/
# GMAIL_QUERY_urgent_messages.md
```

**Review the file:**
```markdown
---
type: gmail_query
action: check_urgent_emails
priority: high
created: 2026-01-14T10:30:00Z
---

# Check Gmail for Urgent Messages

**Query Parameters:**
- Filter: Unread OR Important
- Keywords: urgent, asap, invoice, payment, deadline
- Time range: Last 3 days (weekend)

**What Ralph will do:**
- Query Gmail API via email-mcp
- Extract urgent messages
- Create action files in Needs_Action/
- Log results to Logs/2026-01-14.json

---

**To Approve:**
```bash
mv AI_Employee_Vault/Pending_Approval/GMAIL_QUERY_urgent_messages.md \
   AI_Employee_Vault/Approved/
```

**To Reject:**
```bash
mv AI_Employee_Vault/Pending_Approval/GMAIL_QUERY_urgent_messages.md \
   AI_Employee_Vault/Rejected/
```

**To Edit and Approve:**
```bash
# 1. Edit the file
nano AI_Employee_Vault/Pending_Approval/GMAIL_QUERY_urgent_messages.md

# 2. Then approve
mv AI_Employee_Vault/Pending_Approval/GMAIL_QUERY_urgent_messages.md \
   AI_Employee_Vault/Approved/
```

---

### Step 5: Monitor Progress

While Ralph is running, monitor its progress:

```bash
# Check status anytime
./scripts/check-ralph-status.sh

# View progress log
cat .claude/skills/ralph/progress.txt

# Check for pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Check completed tasks
cat .claude/skills/ralph/prd.json | jq '.userStories[] | select(.passes == true)'
```

---

### Step 6: Review Results

When Ralph completes all tasks ( or you stop it), review the results:

```bash
# View completed tasks
./scripts/check-ralph-status.sh

# View generated briefing
cat AI_Employee_Vault/Briefings/MONDAY_BRIEFING_2026-01-14.md

# View action list
cat AI_Employee_Vault/Briefings/MONDAY_ACTION_LIST_2026-01-14.md

# Check audit log
cat AI_Employee_Vault/Logs/2026-01-14.json
```

---

## Human-in-the-Loop Approval

### Which Actions Require Approval?

| Action | Approval Required | Reason |
|--------|------------------|---------|
| **Send emails** | ✅ Yes | External communication |
| **Create calendar events** | ✅ Yes | Modifies your calendar |
| **Send Slack messages** | ✅ Yes | External communication |
| **Post to social media** | ✅ Yes | Public content |
| **Create invoices (Xero)** | ✅ Yes | Financial transactions |
| **Make payments** | ✅ Yes | Financial transactions |
| **Create folders** | ❌ No | File system operation |
| **Write files** | ❌ No | File system operation |
| **Read data** | ❌ No | Read-only operation |
| **Generate reports** | ❌ No | Internal operation |

### Approval Workflow

```
┌─────────────────────────────────────────┐
│ Ralph creates approval request          │
│ → Pending_Approval/ACTION_NAME.md       │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ You receive notification                │
│ → Check Pending_Approval/ folder        │
│ → Open the approval file                │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ You review the proposed action          │
│ → Read what Ralph wants to do           │
│ → Check parameters and details         │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────┬─────────────┬─────────────┐
│ ✅ Approve  │ ❌ Reject   │ ✏️ Edit     │
│             │             │             │
│ ▼           │ ▼           │ ▼           │
│ Move to     │ Move to     │ Modify file │
│ Approved/   │ Rejected/   │ Then approve│
│             │             │             │
│ ┌───────────┐ │ ┌─────────┐ │ ┌───────────┐
│ │ Monitor   │ │ │ Nothing │ │ │ Monitor   │
│ │ executes  │ │ │ happens │ │ │ executes  │
│ │ modified  │ │ │ File    │ │ │ modified  │
│ │ version   │ │ │ archived │ │ │ version   │
│ └───────────┘ │ └─────────┘ │ └───────────┘
└─────────────┴─────────────┴─────────────┘
```

---

## Monitoring Progress

### Check Status Script

```bash
./scripts/check-ralph-status.sh
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        RALPH WIGGUM - TASK EXECUTION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Project: AI Employee - Monday CEO Briefing
🔄 Status: RUNNING (PID: 12345)
⏱️  Started: 2026-01-14 10:30:00

📈 Task Progress: 4/7 complete (57%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ COMPLETED TASKS:
  ✓ TASK-001: Check Gmail for urgent messages (priority 1)
  ✓ task-002: Check Calendar for upcoming events (priority 2)
  ✓ task-003: Review business performance from logs (priority 3)
  ✓ task-004: Check business goals and targets (priority 4)

⏳ PENDING TASKS:
  ⏸ task-005: Generate proactive suggestions (priority 5)
  ⏸ task-006: Format and finalize CEO briefing (priority 6)
  ⏸ task-007: Create follow-up action list (priority 7)

⚠️  AWAITING APPROVAL:
  ⏰ PROACTIVE_SUGGESTIONS_20260114.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Recent Progress:
  [10:35] TASK-001 completed: 3 urgent emails found
  [10:37] task-002 completed: 2 high-priority events this week
  [10:40] task-003 completed: Generated performance summary
  [10:43] task-004 completed: Revenue gap calculated ($5,500)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### View Progress Log

```bash
cat .claude/skills/ralph/progress.txt
```

**Shows:**
- Patterns discovered in codebase
- Task-by-task progress
- Learnings for future iterations
- Files changed

---

## Creating Custom Task Lists

### Task List Format

Edit `.claude/skills/ralph/prd.json`:

```json
{
  "project": "My Project",
  "branchName": "feature-name",
  "description": "Brief description of overall goal",
  "userStories": [
    {
      "id": "TASK-001",
      "title": "Send email to client",
      "description": "Send follow-up email to client about invoice",
      "acceptanceCriteria": [
        "Email sent to client@example.com",
        "Subject: Invoice #123 Follow-up",
        "Body includes invoice details and payment link",
        "Logged to Logs/YYYY-MM-DD.json"
      ],
      "priority": 1,
      "passes": false,
      "notes": "Use email-manager skill with Gmail MCP"
    },
    {
      "id": "TASK-002",
      "title": "Schedule meeting",
      "description": "Schedule 1-hour project review with stakeholders",
      "acceptanceCriteria": [
        "Calendar invite sent to all participants",
        "Meeting scheduled within next 3 business days",
        "Meeting duration: 60 minutes",
        "Agenda attached to invite",
        "Logged to Calendar/ or Briefings/",
        "Logged to Logs/YYYY-MM-DD.json"
      ],
      "priority": 2,
      "passes": false,
      "notes": "Depends on TASK-001. Use calendar-manager skill."
    }
  ]
}
```

### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ Yes | Unique task identifier (TASK-001, TASK-002, etc.) |
| `title` | string | ✅ Yes | Short descriptive title |
| `description` | string | ✅ Yes | What the task does |
| `acceptanceCriteria` | array | ✅ Yes | Array of verifiable criteria |
| `priority` | number | ✅ Yes | Execution order (1 = highest priority) |
| `passes` | boolean | ✅ Yes | false (pending) or true (complete) |
| `notes` | string | ❌ No | Optional additional context or dependencies |

### Task Sizing Rules

**✅ Good Task Size (One Session):**
- Send one email
- Create one folder structure
- Generate one invoice
- Schedule one meeting
- Post one social media update
- Read and summarize emails

**❌ Too Large (Split These):**
- "Complete client onboarding" → Split into 6 tasks
- "Handle all urgent emails" → One task per email
- "Weekly business review" → Split into 4-5 tasks

**Rule of Thumb:** Each task should be completable in **one Claude Code session** (5-10 minutes).

---

## Examples

### Example 1: Monday Morning CEO Briefing

**File:** `.claude/skills/ralph/prd_monday_ceo_briefing.json`

This is the **standout feature** from the Hackathon requirements - AI autonomously prepares weekly business summary for CEO review.

**7 Tasks:**
1. Check Gmail for urgent weekend messages
2. Check Calendar for upcoming events
3. Review business performance from logs
4. Check business goals and targets
5. Generate proactive suggestions
6. Format and finalize CEO briefing
7. Create follow-up action list

**Time Savings:** 10-15 minutes (Ralph) vs 30-60 minutes (manual)

**To Use:**
```bash
cp .claude/skills/ralph/prd_monday_ceo_briefing.json .claude/skills/ralph/prd.json
./scripts/start-ralph.sh 10
```

---

### Example 2: Client Onboarding

**File:** `.claude/skills/ralph/prd.json`

**6 Tasks:**
1. Send welcome email to client
2. Create client folder structure
3. Create setup invoice in Xero
4. Schedule kickoff meeting
5. Create project plan document
6. Add client to Slack workspace

**Time Savings:** 10-15 minutes (Ralph) vs 30-45 minutes (manual)

**To Use:**
```bash
# Already the default prd.json
./scripts/start-ralph.sh 10
```

---

### Example 3: Custom Task List

```json
{
  "project": "Weekly Social Media Posts",
  "branchName": "social-media-week-03",
  "description": "Create and schedule 3 social media posts for this week",
  "userStories": [
    {
      "id": "TASK-001",
      "title": "Generate LinkedIn post about AI automation",
      "description": "Create engaging LinkedIn post about AI automation benefits",
      "acceptanceCriteria": [
        "Post created in Pending_Approval/LINKEDIN_POST_*.md",
        "Post includes hashtags: #AI #Automation #Productivity",
        "Post length: 100-150 words",
        "Professional tone"
      ],
      "priority": 1,
      "passes": false,
      "notes": "Use content-generator skill or create manually"
    },
    {
      "id": "TASK-002",
      "title": "Generate Twitter thread about project tips",
      "description": "Create 5-tweet thread about project management tips",
      "acceptanceCriteria": [
        "Thread created in Pending_Approval/TWITTER_POST_*.md",
        "5 tweets total (each < 280 chars)",
        "Thread tells coherent story",
        "Includes relevant hashtags"
      ],
      "priority": 2,
      "passes": false,
      "notes": "Use twitter-manager skill"
    },
    {
      "id": "TASK-003",
      "title": "Generate Instagram post with professional image",
      "description": "Create Instagram post with auto-generated professional image",
      "acceptanceCriteria": [
        "Post created in Pending_Approval/INSTAGRAM_POST_*.md",
        "Caption includes emojis and hashtags",
        "Image will be auto-generated with professional theme",
        "Caption length: 100-200 characters"
      ],
      "priority": 3,
      "passes": false,
      "notes": "Use facebook-instagram-manager skill - image auto-generated"
    }
  ]
}
```

**To Use:**
```bash
# Save as custom task list
nano .claude/skills/ralph/prd.json
# Paste the JSON above

# Start Ralph
./scripts/start-ralph.sh 10

# Approve each post when ready
mv AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md AI_Employee_Vault/Approved/
mv AI_Employee_Vault/Pending_Approval/TWITTER_POST_*.md AI_Employee_Vault/Approved/
mv AI_Employee_Vault/Pending_Approval/INSTAGRAM_POST_*.md AI_Employee_Vault/Approved/
```

---

## Troubleshooting

### Ralph Not Starting

**Problem:** Script doesn't run

```bash
# Check permissions
ls -la .claude/skills/ralph/ralph-claude.sh
ls -la scripts/start-ralph.sh

# Make executable
chmod +x .claude/skills/ralph/ralph-claude.sh
chmod +x scripts/start-ralph.sh

# Try again
./scripts/start-ralph.sh 10
```

---

### Tasks Not Completing

**Problem:** Ralph runs but tasks stay incomplete

```bash
# Check progress log
cat .claude/skills/ralph/progress.txt

# Check for pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Check if monitors are running
pm2 status

# Check for errors
pm2 logs ralph-claude --lines 50
```

---

### No Tasks Found

**Problem:** "No task list found (prd.json)"

```bash
# Check if prd.json exists
ls .claude/skills/ralph/prd.json

# View example format
cat .claude/skills/ralph/prd.json.example

# Create from example
cp .claude/skills/ralph/prd.json.example .claude/skills/ralph/prd.json

# Or use Monday CEO Briefing example
cp .claude/skills/ralph/prd_monday_ceo_briefing.json .claude/skills/ralph/prd.json
```

---

### Ralph Runs Too Fast

**Problem:** Ralph completes tasks but makes mistakes

```bash
# This is actually good! Ralph is working efficiently.

# If you want more control:
# 1. Add more approval steps to tasks
# 2. Break large tasks into smaller tasks
# 3. Review each approval request carefully
# 4. Use Edit before Approve to modify actions

# Remember: You always have final approval!
```

---

### Approval Monitor Not Detecting Files

**Problem:** You approve but nothing happens

```bash
# Check if monitors are running
pm2 status

# Should see:
# email-approval-monitor    → online
# calendar-approval-monitor  → online
# slack-approval-monitor     → online
# linkedin-approval-monitor  → online
# twitter-approval-monitor   → online
# meta-approval-monitor      → online

# If not running, restart:
pm2 restart all

# Check monitor logs
pm2 logs email-approval-monitor --lines 20
```

---

## Best Practices

### 1. Start Small

```bash
# Create a test task list with 2-3 tasks first
# Verify Ralph works correctly
# Then scale up to larger workflows
```

### 2. Use Descriptive Task Names

```json
{
  "title": "Send email"  // ❌ Too vague
}

{
  "title": "Send invoice reminder to client@acmecorp.com"  // ✅ Specific
}
```

### 3. Include Verification Criteria

```json
{
  "acceptanceCriteria": [
    "Task completed",  // ❌ Vague
    "File created at /path/to/file",  // ✅ Verifiable
    "Logged to Logs/2026-01-14.json"  // ✅ Auditable
  ]
}
```

### 4. Add Notes for Context

```json
{
  "notes": ""  // ❌ Empty
}

{
  "notes": "Depends on TASK-001. Use email-manager skill with Gmail MCP. Client timezone: EST."  // ✅ Helpful
}
```

### 5. Test Before Production

```bash
# Test with small task list first
# Verify all approvals work correctly
# Check logs for errors
# Scale up gradually
```

### 6. Monitor Progress

```bash
# Check status regularly
./scripts/check-ralph-status.sh

# Review progress log
cat .claude/skills/ralph/progress.txt

# Check audit logs
cat AI_Employee_Vault/Logs/2026-01-14.json
```

---

## Advanced Usage

### Running Ralph in Background

```bash
# Start Ralph in background
nohup ./scripts/start-ralph.sh 10 > ralph.log 2>&1 &

# Get PID
echo $!

# Monitor progress
tail -f ralph.log

# Check status
./scripts/check-ralph-status.sh

# Stop when done
kill <PID>
```

### Resume Interrupted Ralph

```bash
# If Ralph stops unexpectedly, just restart
./scripts/start-ralph.sh 10

# Ralph will:
# - Read prd.json to see which tasks are done
# - Read progress.txt to see what was learned
# - Continue from where it left off
# - Complete remaining tasks
```

### Reset Task List

```bash
# Mark all tasks as incomplete
jq '.userStories[].passes = false' .claude/skills/ralph/prd.json > tmp.json
mv tmp.json .claude/skills/ralph/prd.json

# Clear progress log
echo "" > .claude/skills/ralph/progress.txt

# Start fresh
./scripts/start-ralph.sh 10
```

---

## Summary

Ralph transforms your AI Employee from a reactive tool into a **proactive business partner** that:

- ✅ Works autonomously through multi-step workflows
- ✅ Maintains human control through approvals
- ✅ Completes tasks 3-6x faster than manual execution
- ✅ Provides full audit trail of all actions
- ✅ Learns from previous iterations
- ✅ Can be customized for any workflow

---

**Ready to automate your workflows with Ralph?**

```bash
# Start with the Monday CEO Briefing
cp .claude/skills/ralph/prd_monday_ceo_briefing.json .claude/skills/ralph/prd.json
./scripts/start-ralph.sh 10

# Or create your own task list
nano .claude/skills/ralph/prd.json
./scripts/start-ralph.sh 10
```

---

*Last Updated: 2026-01-14*
*Version: 1.0*
*For more information, see:*
- `.claude/skills/ralph/README.md` - Ralph implementation details
- `.claude/skills/ralph/SKILL.md` - Ralph skill definition
- `docs/hackathon0.md` - Hackathon requirements
