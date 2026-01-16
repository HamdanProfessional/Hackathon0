# AI Employee Templates

This folder contains reusable templates for creating action files in your AI Employee system.

## Available Templates

### Communication

#### Email_Template.md
- **Purpose:** Gmail emails detected by gmail-watcher
- **Output:** `EMAIL_YYYYMMDD_HHMMSS_subject.md`
- **Actions:** Reply, forward, archive, add to task list

#### WhatsApp_MESSAGE_Template.md
- **Purpose:** WhatsApp messages detected by whatsapp-watcher
- **Output:** `WHATSAPP_WHATSAPP_PREVIEW_YYYYMMDD_HHMMSS_<id>.md`
- **Features:** Intelligent spam filtering, keyword detection

#### CALENDAR_EVENT_Template.md
- **Purpose:** Google Calendar events detected by calendar-watcher
- **Output:** `EVENT_YYYYMMDD_HHMMSS_meeting.md`
- **Features:** Meeting preparation checklist, attendee info

---

### Social Media

#### LINKEDIN_POST_Template.md
- **Purpose:** Professional LinkedIn posts
- **Output:** `LINKEDIN_POST_YYYYMMDD_HHMMSS.md`
- **Features:** Fast copy-paste method (100-200x faster), full markdown, 3,000 char limit

#### TWITTER_POST_Template.md
- **Purpose:** Twitter/X tweets
- **Output:** `TWITTER_POST_YYYYMMDD_HHMMSS.md`
- **Features:** 280 character limit, auto-truncation, fast posting

#### INSTAGRAM_POST_Template.md
- **Purpose:** Instagram posts with auto-generated images
- **Output:** `INSTAGRAM_POST_YYYYMMDD_HHMMSS.md`
- **Features:** 6 professional color themes, 1080x1080 auto-image, emoji handling

#### FACEBOOK_POST_Template.md
- **Purpose:** Facebook posts
- **Output:** `FACEBOOK_POST_YYYYMMDD_HHMMSS.md`
- **Features:** Full formatting, emoji support, 63,206 char limit

---

### Accounting

#### XERO_ALERT_Template.md
- **Purpose:** Xero accounting alerts
- **Output:** `XERO_OVERDUE_YYYYMMDD.md` or `XERO_ALERT_YYYYMMDD.md`
- **Features:** Invoice tracking, overdue alerts (7+ days), unusual expense alerts ($500+)

---

### Approval

#### Approval_Template.md
- **Purpose:** Generic approval request workflow
- **Output:** Custom filename based on action type
- **Features:** Risk assessment, reversible actions

---

## How to Use Templates

### Option 1: Manual Creation
1. Copy the template you need
2. Paste it in `Pending_Approval/` folder
3. Replace `{{placeholders}}` with your content
4. Rename with proper timestamp: `TYPE_YYYYMMDD_HHMMSS.md`
5. Move to `Approved/` to execute

### Option 2: AI-Generated
1. Ask Claude Code to create an action
2. Claude will use appropriate template
3. Review in `Pending_Approval/`
4. Move to `Approved/` to execute

### Option 3: Watcher-Created
1. Watchers automatically create files in `Needs_Action/`
2. Files use template format
3. Review and process as needed

---

## File Naming Convention

All action files follow this format:
```
{TYPE}_{YYYYMMDD}_{HHMMSS}_{description}.md
```

Examples:
- `EMAIL_20260114_143000_invoice.md`
- `LINKEDIN_POST_20260114_150000.md`
- `TWITTER_POST_20260114_150000.md`
- `INSTAGRAM_POST_20260114_150000.md`
- `FACEBOOK_POST_20260114_150000.md`
- `WHATSAPP_WHATSAPP_PREVIEW_20260114_150000_0.md`
- `XERO_OVERDUE_20260114.md`

---

## Social Media Posting Workflow

1. **Create Post** using template
2. **Review** in Obsidian
3. **Approve** by moving to `Approved/`
4. **Auto-Posted** within seconds (100-200x faster than typing)

**Note:** All social media platforms require Chrome automation window to be logged in:
```bash
scripts\social-media\START_AUTOMATION_CHROME.bat
```

---

## Template Fields

### Common Fields
- `{{timestamp}}` - ISO format datetime (e.g., 2026-01-14T15:00:00)
- `{{priority}}` - high, medium, low
- `{{status}}` - pending, pending_approval, approved, rejected

### Social Media Fields
- `{{platform}}` - linkedin, twitter, instagram, facebook
- `{{content}}` - Post content
- `{{hashtags}}` - Comma-separated hashtags

### Email Fields
- `{{sender}}` - Sender email address
- `{{subject}}` - Email subject line
- `{{body}}` - Email content

---

## Best Practices

1. **Always use proper timestamps** in filenames
2. **Include descriptive suffixes** for easy identification
3. **Fill all required fields** before approval
4. **Review content** before moving to `Approved/`
5. **Check platform-specific limits** (e.g., Twitter 280 chars)

---

**Updated:** 2026-01-14
**System Version:** 1.2.1
