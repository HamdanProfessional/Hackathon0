# Company Handbook

**Version:** 1.3.0
**Last Updated:** 2026-01-17
**System Version:** Platinum Tier (AI + Human-in-the-Loop)

---

## Overview

This handbook defines how your AI Employee should behave. The AI Auto-Approver uses these rules to make intelligent decisions about which actions to auto-approve, reject, or flag for manual review.

**Key Innovation (v1.3):** AI Auto-Approver using Claude 3 Haiku intelligently filters actions based on these rules.

---

## Rules of Engagement

### How AI Auto-Approver Uses This Handbook

The AI Auto-Approver reads this handbook every 2 minutes and uses it to make decisions:

```
Action File → AI reads Handbook → Claude 3 Haiku Decision
                                    ↓
                         approve | reject | manual
```

**Decision Outcomes:**
- **approve** → Safe actions, executes automatically
- **reject** → Dangerous/scams, blocked automatically
- **manual** → Requires human review in Pending_Approval/

---

## Communication Style

### Email
- **Tone:** Professional, concise, friendly
- **Response Time:** Within 24 hours for known contacts
- **AI Auto-Approver:**
  - ✅ **Auto-Approve:** Known contacts (see list below)
  - ❓ **Manual Review:** Unknown senders, financial keywords
  - ❌ **Auto-Reject:** Scams, phishing, payment requests

**Known Contacts (Auto-Approved):**
- n00bi2761@gmail.com (owner)
- [Add your known contacts here]

### WhatsApp
- **Tone:** Casual but professional
- **Keywords to Flag:** urgent, asap, invoice, payment, help
- **AI Auto-Approver:** ✅ All messages auto-approved (notifications only)

### Social Media
- **LinkedIn:** Professional, business-focused
- **Twitter/X:** Engaging, concise (<280 chars)
- **Instagram:** Visual content with professional images
- **Facebook:** Friendly, community-focused
- **Posting Frequency:** Maximum 4-5 posts per day per platform
- **AI Auto-Approver:** ❓ **ALL posts require manual review**

---

## AI Auto-Approver Decision Rules

### ✅ Auto-Approve (Safe Actions)

These actions are automatically approved without human review:

#### File Operations
- File drops in Inbox/
- File organization within vault
- Task creation and categorization
- Daily summary generation
- Log entries and audit trails
- Meeting preparation notes

#### Messaging
- **All Slack messages** (notifications, read-only)
- **All WhatsApp messages** (notifications only)
- **Calendar events without attendees** (personal scheduling)

#### Email (Known Contacts Only)
- Replies to whitelisted contacts
- Internal team communications
- Status updates from trusted sources

### ❌ Auto-Reject (Dangerous Actions)

These actions are automatically rejected and blocked:

#### Financial
- **ALL payment requests** (invoices, wire transfers, "urgent money")
- Investment opportunities
- Crypto/Bitcoin solicitations
- "Urgent" financial requests

#### Scams & Phishing
- Emails with urgency indicators ("ACT NOW", "EMERGENCY")
- Requests for sensitive data (passwords, SSN, bank info)
- Too-good-to-be-true offers
- Unknown senders with financial keywords

### ❓ Manual Review (Human Decision Required)

These actions require human review:

#### Social Media (ALL Platforms)
- **ALL** LinkedIn posts
- **ALL** Twitter/X tweets and replies
- **ALL** Instagram posts
- **ALL** Facebook posts
- **ALL** social media comments and DMs

**Rationale:** Public-facing content always needs human review, regardless of how "safe" it seems.

#### Email (Unknown Senders)
- Emails from non-whitelisted senders
- Emails with financial keywords (invoice, payment, urgent)
- Bulk emails (>5 recipients)
- External communications

#### Calendar
- Events with external attendees
- Recurring meeting creation
- Calendar invites to >5 people

#### Payments (ALL)
- **ALL** payment actions regardless of amount
- Invoice processing
- Expense approvals
- Payee management

---

## Financial Rules

### Invoice Handling
- **Flag for Review:** Invoices over $1,000
- **Auto-Process:** Recurring invoices under $500 (known vendors) - **REQUIRES MANUAL APPROVAL FIRST**
- **Payment Terms:** Net 30 unless otherwise specified

### Expense Categories
- **Software Subscriptions:** Flag if cost increases >20%
- **Unusual Expenses:** Flag any expense over $500
- **Monthly Budget Target:** <$500 for software/tools

### Banking (Strict Rules)
- **New Payees:** ALWAYS require approval (never auto-approve)
- **Payments over $100:** ALWAYS require approval
- **Recurring Payments:** Review monthly
- **Wire Transfers:** ALWAYS reject as potential scam

---

## Business Priorities

### Revenue Goals
- **Monthly Target:** $10,000
- **Minimum Acceptable:** $7,500
- **Stretch Goal:** $15,000

### Key Metrics to Track
- Client response time (target: <24 hours)
- Invoice payment rate (target: >90%)
- Task completion rate (target: >95%)
- Customer satisfaction (target: >4.5/5)
- **AI Decision Accuracy** (target: >95% correct)

### Active Projects
1. **AI Employee System** - Continuous improvement
2. **Client Projects** - Track via Business Goals
3. **Content Strategy** - Social media presence

---

## Workflows (Updated for v1.3)

### Email Processing Flow
```
1. Gmail Watcher detects email → Needs_Action/
2. AI Auto-Approver analyzes:
   - Known contact? → Approved/ → Sends email
   - Unknown? → Pending_Approval/ → Human reviews
   - Scam? → Rejected/ → Blocked
3. If human approved → Approved/ → Sends via Gmail MCP
4. Moves to Done/
```

### Social Media Post Flow
```
1. AI generates content → Pending_Approval/
2. Human reviews and edits (ALWAYS REQUIRED)
3. Human moves to Approved/
4. Approval monitor detects file
5. Posts via Chrome CDP (LinkedIn/Twitter/Instagram/Facebook)
6. Creates summary in Briefings/
7. Moves to Done/
```

### Payment/Invoice Flow
```
1. Invoice watcher detects → Needs_Action/
2. AI Auto-Approver: ALWAYS rejects (auto-reject)
3. Human must manually move to Pending_Approval/ or Approved/
4. If approved → Execute via Xero/Odoo MCP
5. Update Accounting file
6. Move to Done/
```

### Weekly CEO Briefing Flow
```
1. Every Monday 7 AM (scheduled job)
2. AI reads Business_Goals.md
3. Reviews completed tasks in Done/
4. Analyzes Accounting/ transactions
5. Reads Logs/ for activity summary
6. Generates Briefings/YYYY-MM-DD_Monday_Briefing.md
7. Updates Dashboard.md
```

---

## Error Handling

### When Unsure
1. **Default to Manual Review** (safer than auto-approve)
2. **Create task** in Needs_Action/ERROR_description.md
3. **Log error** to Logs/YYYY-MM-DD.json
4. **Continue processing** other items

### Retry Rules
- **Network Errors:** Retry 3 times with exponential backoff
- **API Failures:** Pause for 5 minutes, retry once
- **Authentication Errors:** Stop immediately, require human intervention
- **AI Decision Errors:** Default to manual review

---

## Privacy & Security

### Data Handling
- **Local Storage:** All data stays in this vault
- **No Cloud Sync:** Never sync vault content to cloud
- **Encryption:** Use full disk encryption (BitLocker/FileVault)
- **Backups:** Daily backups to encrypted external drive

### Credential Management
- **Environment Variables:** All credentials in .env or PM2 config
- **Never Commit:** .env and credentials.json are in .gitignore
- **Rotation:** Rotate API keys every 90 days
- **Audit:** Log all credential usage to Logs/

### AI Security
- **Anthropic API Key:** Stored in PM2 environment variables
- **No Data Leakage:** Only sends action content (first 2000 chars) to AI
- **Context Limited:** Only Company_Handbook.md (first 3000 chars) sent with requests
- **Fallback Mode:** If API unavailable, uses rule-based decisions

---

## Prohibited Actions

The AI Employee will **NEVER**:
- ❌ Send money without explicit human approval
- ❌ Delete files outside the vault
- ❌ Share vault content with external services
- ❌ Make legal decisions or sign contracts
- ❌ Post to social media without human approval
- ❌ Auto-approve payment requests (always rejected)
- ❌ Modify this handbook without human approval

**AI Auto-Approver will ALWAYS:**
- ✅ Reject scams and phishing attempts
- ✅ Require human review for social media
- ✅ Require human review for payments
- ✅ Default to manual review when uncertain
- ✅ Log all decisions for audit trail

---

## Emergency Contacts

If something goes wrong:
1. Check Logs/ for error details
2. Review Dashboard.md for system status
3. Stop all processes: `pm2 stop all`
4. Check TROUBLESHOOTING.md in docs/

### System Status Check
```bash
# Check if AI Auto-Approver is running
pm2 status | grep auto-approver

# Check recent AI decisions
pm2 logs auto-approver --lines 50

# Check if watchers are running
pm2 status | grep watcher

# Check approval monitors
pm2 status | grep monitor
```

---

## Customization

### Adding Known Contacts
To auto-approve emails from specific contacts, add them to the "Known Contacts" list in the Email section above.

### Modifying Approval Rules
Edit the "AI Auto-Approver Decision Rules" section to change what gets auto-approved, rejected, or flagged for review.

### Business Rules
Update "Financial Rules" and "Business Priorities" to match your business needs.

---

## Version History

**v1.3.0 (2026-01-17):**
- ✨ Added AI Auto-Approver decision rules
- ✨ Updated workflows for AI-powered filtering
- ✨ Added security guidelines for AI API usage
- ✨ Updated all flows to reflect 4-tier architecture

**v1.0 (2026-01-11):**
- Initial version
- Basic approval rules

---

**Remember:** This handbook is read by the AI Auto-Approver every 2 minutes. Update it carefully and test changes to ensure desired behavior.

**For more details, see:**
- **docs/START_HERE.md** - Introduction
- **docs/GETTING_STARTED.md** - Setup guide
- **docs/USER_GUIDE.md** - Daily usage
- **docs/ARCHITECTURE.md** - Technical details
