# Ralph Wiggum - Autonomous Task Execution Loop

Execute multi-step business tasks autonomously while maintaining human oversight and approval for all external actions.

## Purpose

The Ralph Wiggum skill **iterates** through a task list until all items are complete, **maintains** state between iterations via files, **requests** approval for external actions, and **persists** progress for transparency and recovery. This skill **transforms** a list of tasks into a fully-executed workflow with minimal human supervision.

## Design Philosophy

- **Autonomous Execution**: Continues until all tasks complete
- **Human-in-the-Loop**: Every external action requires approval
- **Fresh Context**: Each iteration starts clean (no memory buildup)
- **Persistent Memory**: State maintained via files (not conversation)
- **Transparent**: All progress logged and inspectable

## Workflow

1. **Load** `ralph/prd.json` task list (or custom path)
2. **Read** `ralph/progress.txt` for learnings from previous iterations
3. **Pick** highest priority task where `passes: false`
4. **Plan** execution in `Plans/` folder
5. **Execute** using available AI Employee capabilities (MCPs, skills)
6. **Create** approval request in `Pending_Approval/`
7. **Wait** for human to move file to `Approved/`
8. **Verify** execution in `Logs/YYYY-MM-DD.json`
9. **Update** `prd.json` to mark task complete (`passes: true`)
10. **Log** progress to `progress.txt`
11. **Check** if all tasks complete → Output `<promise>TASK_COMPLETE</promise>`
12. **Continue** to next iteration

## Modularity

Extensible with:
- Custom task list formats (JSON, YAML)
- Custom approval workflows
- Custom completion signals
- Custom progress tracking
- Integration with any skill/MCP

## Inputs

- **Task List**: JSON file with `userStories` array
- **Progress File**: Text file with learnings
- **Vault Path**: Path to AI_Employee_Vault

## Outputs

- **Plans**: Execution plans in `Plans/` folder
- **Approvals**: Request files in `Pending_Approval/`
- **Logs**: Action logs in `Logs/YYYY-MM-DD.json`
- **Completion Signal**: `<promise>TASK_COMPLETE</promise>`

## Usage

```bash
# Start Ralph with default task list (ralph/prd.json)
claude --cwd AI_Employee_Vault < ralph/prompt-ai-employee.md

# Or use the convenience script
./scripts/start-ralph.sh 10

# Check status
./scripts/check-ralph-status.sh
```

## Task List Format

```json
{
  "project": "Project Name",
  "branchName": "feature-identifier",
  "description": "Brief description of what you're accomplishing",
  "userStories": [
    {
      "id": "TASK-001",
      "title": "Task title",
      "description": "As a [role], I want [feature] so that [benefit]",
      "acceptanceCriteria": [
        "Verifiable criterion 1",
        "Verifiable criterion 2",
        "Logged to Logs/YYYY-MM-DD.json"
      ],
      "priority": 1,
      "passes": false,
      "notes": "Optional context"
    }
  ]
}
```

## Task Sizing Rules

**✅ Good (One Claude Code session):**
- Send one email
- Create one folder structure
- Generate one invoice
- Schedule one meeting
- Post one social media update
- Read and summarize emails

**❌ Too Large (split these):**
- "Complete client onboarding" → Split into individual tasks
- "Handle all urgent emails" → One task per email
- "Weekly business review" → Split into 4-5 tasks

## Error Handling

- **Max Iterations**: Stops after N iterations to prevent infinite loops
- **Progress Tracking**: All actions logged to progress.txt
- **State Persistence**: prd.json updated after each task
- **Graceful Degradation**: Continues on error, logs issues

## Examples

See `ralph/prd.json` for example client onboarding workflow with 6 tasks.

## Dependencies

- BaseWatcher (for file monitoring)
- AI Employee vault structure
- PM2 (for process management, optional)
- Claude Code CLI

## See Also

- `ralph/README.md` - Complete Ralph guide
- `ralph/prompt-ai-employee.md` - Instructions for Claude Code
- `docs/RALPH_IMPLEMENTATION_GUIDE.md` - Implementation details

---

*Ralph Wiggum Skill v1.0 - Autonomous Task Execution for AI Employee*
