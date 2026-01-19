# Agent Skills Catalog

**AI Employee v1.4.1**

---

## Overview

All AI functionality is organized as **Agent Skills** in `.claude/skills/`. Each skill has:

- `SKILL.md` - Documentation with YAML frontmatter
- `scripts/` - Executable code (if applicable)
- `invoke.py` - Direct invocation script (for 7 core skills)

---

## Skill Categories

### 📊 Watcher Skills (Perception Layer)

Monitor external services and create action files.

| Skill | Purpose | Platform | Status |
|-------|---------|----------|--------|
| **email-manager** | Monitor Gmail emails | Gmail API | ✅ Operational |
| **calendar-manager** | Monitor Calendar events | Google Calendar API | ✅ Operational |
| **slack-manager** | Monitor Slack messages | Slack Bot API | ✅ Operational |
| **whatsapp-manager** | Monitor WhatsApp messages | Playwright | ✅ Operational |
| **filesystem-manager** | Monitor drop folder | File system | ✅ Operational |
| **xero-manager** | Monitor accounting | Xero MCP | ✅ Operational |
| **odoo-manager** | Monitor ERP | Odoo XML-RPC | ✅ Operational |

---

### 📱 Social Media Skills (Action Layer)

Post content to social platforms.

| Skill | Platform | Features | Status |
|-------|----------|----------|--------|
| **linkedin-manager** | LinkedIn | Fast copy-paste (100-200x), unlimited characters | ✅ Operational |
| **twitter-manager** | Twitter/X | Fast copy-paste, 280 char limit | ✅ Operational |
| **facebook-instagram-manager** | Facebook & Instagram | FB: direct insertion, IG: auto-image generation (6 themes) | ✅ Operational |

---

### 🧠 Core System Skills

Critical infrastructure components.

| Skill | Purpose | Status |
|-------|---------|--------|
| **approval-manager** | Human-in-the-loop approval workflow | ✅ Operational |
| **ralph** | Autonomous task execution loop | ✅ Operational |
| **weekly-briefing** | CEO business audit (standout feature!) | ✅ Operational |
| **daily-review** | Daily task planning and prioritization | ✅ Operational |

---

### 📝 Supporting Skills

Enhance and support other skills.

| Skill | Purpose | Status |
|-------|---------|--------|
| **content-generator** | Generate content for various platforms | ✅ Operational |
| **planning-agent** | Create execution plans for complex tasks | ✅ Operational |
| **business-handover** | Generate CEO handoff documents | ✅ Operational |
| **accounting** | Financial reporting and aggregation | ✅ Operational |
| **social-media-manager** | Multi-platform coordination | ✅ Operational |
| **inbox-processor** | Process and organize inbox items | ✅ Operational |
| **skill-creator** | Guide for creating new skills | ✅ Operational |

---

## Skill Details

### weekly-briefing

**Purpose:** Generate Monday Morning CEO Briefing on demand

**Standout Feature:** Transforms AI from reactive to proactive

**Usage:**
```bash
python .claude/skills/weekly-briefing/invoke.py "Generate CEO briefing"
```

**Output:** `Briefings/YYYY-MM-DD_Monday_Briefing.md`

**Sections:**
- Executive summary
- Revenue analysis (weekly, MTD, vs target)
- Completed tasks
- Bottlenecks
- Proactive suggestions
- Action items

---

### ralph

**Purpose:** Autonomous multi-step task execution

**Key Feature:** Continues executing tasks until all complete

**Usage:**
```bash
python .claude/skills/ralph/invoke.py "Complete client onboarding"
```

**Workflow:**
1. Load task list
2. Pick highest priority incomplete task
3. Plan execution
4. Execute using available skills
5. Create approval request
6. Wait for human approval
7. Verify execution
8. Continue to next task

---

### linkedin-manager

**Purpose:** Post to LinkedIn

**Features:**
- Fast copy-paste method (100-200x faster than typing)
- No character limit
- Professional formatting

**Usage:**
```bash
python .claude/skills/linkedin-manager/invoke.py "Share business update"
```

**File:** Creates file in `Pending_Approval/`, moves to `Approved/` on approval

---

### twitter-manager

**Purpose:** Post to Twitter/X

**Features:**
- Fast copy-paste method
- 280 character limit (auto-truncates)
- Hashtag support

**Usage:**
```bash
python .claude/skills/twitter-manager/invoke.py "Tweet announcement"
```

---

### facebook-instagram-manager

**Purpose:** Post to Facebook and Instagram

**Facebook:**
- Direct content insertion
- Supports emojis and formatting

**Instagram:**
- **Auto-generates 1080x1080 professional images**
- 6 color themes:
  - Midnight Purple
  - Ocean Blue
  - Sunset Orange
  - Forest Green
  - Royal Gold
  - Deep Navy
- Emojis removed from image, kept in caption

**Usage:**
```bash
python .claude/skills/facebook-instagram-manager/invoke.py facebook "Post update"
python .claude/skills/facebook-instagram-manager/invoke.py instagram "Share photo"
```

---

### approval-manager

**Purpose:** Human-in-the-loop approval workflow

**AI Decision Categories:**
- **approve** - Safe actions (file ops, known contacts, Slack/WhatsApp)
- **reject** - Dangerous (scams, phishing, payments)
- **manual** - Needs human review (social media, payments, new contacts)

**Components:**
- Auto-approver (runs every 2 minutes)
- Approval monitors (watch Approved/ folder)

---

### daily-review

**Purpose:** Generate daily task plans

**Usage:**
```bash
python .claude/skills/daily-review/invoke.py "Generate daily plan"
```

**Output:** `Plans/daily_YYYY-MM-DD.md`

---

### planning-agent

**Purpose:** Create execution plans

**Usage:**
```bash
python .claude/skills/planning-agent/invoke.py "Create plan for project"
```

**Output:** `Plans/PLAN_YYYYMMDD_HHMMSS.md`

---

## Skill Invocation

### Via Python

All 7 core skills support direct invocation:

```bash
python .claude/skills/weekly-briefing/invoke.py "task description"
python .claude/skills/ralph/invoke.py "task description"
python .claude/skills/linkedin-manager/invoke.py "post content"
python .claude/skills/twitter-manager/invoke.py "tweet"
python .claude/skills/facebook-instagram-manager/invoke.py facebook "content"
python .claude/skills/facebook-instagram-manager/invoke.py instagram "content"
python .claude/skills/daily-review/invoke.py "task"
python .claude/skills/planning-agent/invoke.py "task"
```

### Via Claude Code (When Implemented)

```
/skill weekly-briefing "Generate CEO briefing"
/skill ralph "Complete project tasks"
/skill linkedin-manager "Share update"
```

---

## Response Format

All skills return JSON:

```json
{
  "status": "success|error",
  "action": "What was done",
  "file_path": "/path/to/file",
  "summary": "Brief description",
  "error": "null or error message"
}
```

---

## Summary

**Total Skills:** 20+

**Categories:**
- 6 Watcher skills
- 4 Social media skills
- 3 Core skills
- 7 Supporting skills

**Status:** All operational, ready for production

**Integration:** All skills work with PM2 processes and vault-based storage.

---

**Last Updated:** 2025-01-19
