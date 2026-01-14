# 🎯 AI Employee Demo - Quick Reference

## Pre-Demo Check (1 Minute)

```bash
# 1. Check system status
pm2 status
# Expected: 16 processes online

# 2. Check watchers are active
pm2 logs gmail-watcher --lines 5 --nostream

# 3. Check vault
ls AI_Employee_Vault/
```

---

## Demo Commands (In Order)

### 1. Show System (30 seconds)
```bash
pm2 status                                    # Show 16 processes
ls AI_Employee_Vault/                         # Show vault structure
```

### 2. Show Watchers (2 minutes)
```bash
ls -lt AI_Employee_Vault/Needs_Action/ | head -10    # Recent action files
cat "$(ls -t AI_Employee_Vault/Needs_Action/*.md | head -1)"  # Read one
pm2 logs whatsapp-watcher --lines 10 --nostream        # Watcher logs
```

### 3. Ralph Demo (5 minutes)
```bash
# Check Ralph status
./scripts/check-ralph-status.sh

# Show task list
cat .claude/skills/ralph/prd_monday_ceo_briefing.json | head -50

# Start Ralph (if not running)
./scripts/start-ralph.sh 10

# In separate terminal, watch progress
watch -n 5 './scripts/check-ralph-status.sh'

# Check for approvals needed
ls AI_Employee_Vault/Pending_Approval/

# If file exists, approve it
mv "$(ls -t AI_Employee_Vault/Pending_Approval/*.md | head -1)" AI_Employee_Vault/Approved/

# Check progress
./scripts/check-ralph-status.sh

# If briefing created, show it
cat "$(ls -t AI_Employee_Vault/Briefings/*Monday_Briefing*.md 2>/dev/null | head -1)" | head -100
```

### 4. Social Media Demo (4 minutes)
```bash
# Create LinkedIn post
cat > "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_demo_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
status: pending_approval
---

# The Future of Autonomous AI Agents

Excited to share my Personal AI Employee project!

## Key Features:
✅ Local-first architecture
✅ Human-in-the-loop approval
✅ Autonomous task execution
✅ 85-90% cost savings

#AI #Automation
EOF

# Review and approve
cat "$(ls -t AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md | head -1)"
mv "$(ls -t AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md | head -1)" AI_Employee_Vault/Approved/

# Watch it post (in separate terminal)
pm2 logs linkedin-approval-monitor --lines 0

# Verify completion
ls AI_Employee_Vault/Done/ | grep LINKEDIN_POST
```

### 5. System Health (2 minutes)
```bash
pm2 monit                                      # Resource monitor
cat "AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json" | head -30  # Audit log
cat AI_Employee_Vault/Dashboard.md | head -80          # Dashboard
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| PM2 stopped | `pm2 start process-manager/pm2.config.js` |
| Ralph stuck | `/cancel-ralph` then `./scripts/start-ralph.sh 10` |
| Chrome not working | Start: `chrome.exe --remote-debugging-port=9222 --user-data-dir="..."` |
| No action files | Check watcher logs: `pm2 logs [watcher-name]` |

---

## Key Stats to Mention

- **20 Agent Skills** - All documented
- **16 PM2 Processes** - 0 crashes
- **168 Hours/Week** - 4.5x human FTE
- **85-90% Cost Savings** - $0.50/task vs $5.00/task
- **10-15 Minutes** - CEO Briefing (vs 30-60 min manual)
- **100-200x Faster** - Social media posting

---

## File Locations

```
AI_Employee_Vault/
├── Dashboard.md              # System status
├── Company_Handbook.md       # AI Employee rules
├── Business_Goals.md         # Business targets
├── Needs_Action/             # Action files from watchers
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Ready to execute
├── Done/                     # Completed actions
├── Briefings/                # Generated reports
└── Logs/                     # Audit trails

.claude/skills/
├── INDEX.md                  # Skills catalog
├── ralph/SKILL.md            # Ralph documentation
└── [skill-name]/SKILL.md     # Individual skills

scripts/
├── start-ralph.sh            # Start Ralph
└── check-ralph-status.sh     # Check Ralph progress
```

---

## Presentation Flow

1. **Introduction** (2 min) - System status, architecture
2. **Watchers** (3 min) - Live monitoring demo
3. **Ralph** (5 min) - Autonomous CEO Briefing
4. **Social Media** (4 min) - LinkedIn posting demo
5. **Health** (2 min) - PM2, logs, dashboard
6. **Conclusion** (1 min) - Summary, stats, GitHub

**Total:** ~17 minutes

---

*Quick Reference v1.1.0 | AI Employee App | Gold Tier 100% Complete*
