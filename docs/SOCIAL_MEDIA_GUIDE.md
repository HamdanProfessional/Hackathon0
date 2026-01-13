# Social Media Automation Guide

**Complete guide to posting on LinkedIn, Twitter/X, and Instagram with AI Employee.**

---

## Overview

The AI Employee can automatically post to three major social media platforms:
- **LinkedIn** - Professional network with full formatting support
- **Twitter/X** - Micro-blogging with 280 character limit
- **Instagram** - Visual platform with auto-generated images

All posting is done via Chrome automation using the Chrome DevTools Protocol (CDP).

---

## Quick Start

### 1. Start Chrome Automation Session

```bash
# Windows
scripts\social-media\START_AUTOMATION_CHROME.bat

# Or manually:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"
```

**Important:** Log into all three platforms in this Chrome window before posting!

### 2. Create Post Approval File

Create a markdown file in `AI_Employee_Vault/Pending_Approval/`:

**LinkedIn Example:**
```markdown
---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: 2026-01-13T12:00:00Z
expires: 2026-01-14T12:00:00Z
status: pending_approval
---

Your LinkedIn post content here!

#Hashtags #MoreHashtags

## Supports markdown formatting
- Bullet points
- **Bold text**
- And more!
```

**Twitter Example:**
```markdown
---
type: twitter_post
action: post_to_twitter
platform: twitter
created: 2026-01-13T12:00:00Z
expires: 2026-01-14T12:00:00Z
status: pending_approval
---

Your tweet here #hashtags (max 280 chars)
```

**Instagram Example:**
```markdown
---
type: instagram_post
action: post_to_instagram
platform: instagram
created: 2026-01-13T12:00:00Z
expires: 2026-01-14T12:00:00Z
status: pending_approval
---

Your Instagram caption here! #hashtags

Image will be auto-generated from this text!
```

### 3. Approve and Post

```bash
# Move to Approved folder
mv "AI_Employee_Vault/Pending_Approval/POST_*.md" "AI_Employee_Vault/Approved/"

# Approval monitor will automatically:
# 1. Detect the approved file
# 2. Generate content (image for Instagram)
# 3. Post to platform
# 4. Move to Done/ folder
```

---

## Platform-Specific Details

### LinkedIn

**Character Limit:** None (3000 recommended)
**Features:**
- Full markdown support
- Hashtags supported
- Line breaks preserved
- **Fast copy-paste method** (~0.3 seconds for 1000 chars)

**Best Practices:**
- Use 3-5 hashtags
- Keep posts under 1000 characters for best engagement
- Use line breaks to separate sections
- Include call-to-action

**Example Post:**
```markdown
Excited to share our latest project! 🚀

We've built an AI Employee that automates business tasks 24/7.

#AI #Automation #Productivity #FutureOfWork

Link to project in comments! 👇
```

---

### Twitter/X

**Character Limit:** 280 characters (hard limit)
**Features:**
- Auto-truncates if longer than 280 chars
- Hashtags supported
- **Fast copy-paste method** (~0.3 seconds)
- Threads not yet supported

**Best Practices:**
- Use 1-3 hashtags
- Keep tweets under 200 characters for retweets
- Include relevant @mentions
- Add media (images) manually if needed

**Example Post:**
```
Just built an AI Employee that posts to social media automatically! 🤖

#AI #Automation #Tech

Check it out 👇
```

---

### Instagram

**Character Limit:** None (2200 recommended for captions)
**Features:**
- **Auto-generates professional image** from post text
- 6 stunning color themes (randomly selected)
- Decorative borders and professional typography
- Hashtags in caption (not in image)
- **Fast copy-paste for captions** (~0.3 seconds)

**Professional Image Themes:**

1. **Midnight Purple** - Elegant purple gradient
2. **Ocean Blue** - Fresh cyan/blue tones
3. **Sunset Orange** - Warm orange/red sunset
4. **Forest Green** - Natural green vibes
5. **Royal Gold** - Premium gold luxury
6. **Deep Navy** - Professional navy blue

**Image Features:**
- 1080x1080 pixels (1:1 ratio)
- Decorative double borders
- Smart text wrapping (24-30 chars)
- Professional footer with shadow
- Maximum quality (100%)
- Emojis removed from image (kept in caption)

**Best Practices:**
- Use 5-10 hashtags
- Write descriptive text for image generation
- Keep caption under 150 characters
- First line becomes title (accent color)
- Emojis work in caption (not in image)

**Example Post:**
```markdown
Transform your business with AI automation!

Our AI Employee works 24/7 handling emails, scheduling, and social media.

#AI #Automation #Business #Productivity #FutureOfWork #Tech
```

---

## Performance & Speed

### Posting Speed Comparison

**Before (character-by-character typing):**
- 100 characters: ~3 seconds
- 500 characters: ~15 seconds
- 1000 characters: ~30 seconds

**After (fast copy-paste method):**
- 100 characters: ~0.3 seconds
- 500 characters: ~0.3 seconds
- 1000 characters: ~0.3 seconds

**Speed Improvement: 10-100x faster!** ⚡

### Image Generation Speed

**Instagram Image Generation:**
- Text extraction: ~0.1 seconds
- Theme selection: ~0.01 seconds
- Image rendering: ~0.5-1 seconds
- Total: ~1-2 seconds per image

---

## Technical Details

### Chrome DevTools Protocol (CDP)

All posting uses Chrome automation via CDP on port 9222:
- **No API keys needed**
- Uses existing browser session
- Must be logged in before posting
- Works with 2FA enabled

### Copy-Paste Method

**How it works:**
1. Click on text area to focus
2. Copy text to clipboard using JavaScript
3. Paste using Ctrl+V keyboard shortcut
4. Total time: ~0.3 seconds

**Why it's faster:**
- Bypasses character-by-character typing
- Uses browser's native paste functionality
- No rate limiting issues
- More reliable than typing

### Professional Image Generation

**Technology Stack:**
- Python PIL (Pillow) for image generation
- 1080x1080 canvas (Instagram 1:1 ratio)
- Gradient backgrounds with smooth transitions
- Anti-aliased text rendering
- Unicode-safe emoji removal

**Design Elements:**
- Double decorative borders (15px + 5px)
- Title font: 64px Arial
- Body font: 46px Arial
- Footer font: 30px Arial
- Shadow effects for depth
- Decorative dots (5x 8px circles)

---

## Troubleshooting

### Post Not Appearing

**Check:**
1. Is Chrome automation window open?
2. Are you logged into the platform?
3. Did file move to `Approved/`?
4. Check PM2 logs: `pm2 logs linkedin-approval-monitor`

### Image Not Generated (Instagram)

**Check:**
1. Is Pillow installed? `pip install Pillow`
2. Check text doesn't contain only emojis
3. Verify Temp folder exists: `AI_Employee_Vault/Temp/`

### Copy-Paste Not Working

**Check:**
1. JavaScript clipboard API enabled
2. Chrome has clipboard permissions
3. Text area is focused before paste
4. No special characters breaking JavaScript

---

## File Naming Convention

**Format:** `{PLATFORM}_POST_{YYYYMMDD}_{HHMMSS}.md`

**Examples:**
- `LINKEDIN_POST_20260113_120000.md`
- `TWITTER_POST_20260113_120500.md`
- `INSTAGRAM_POST_20260113_121000.md`

---

## Approval Workflow

1. **Create** → File created in `Pending_Approval/`
2. **Review** → Human reviews content
3. **Approve** → Move to `Approved/`
4. **Execute** → Monitor detects and posts
5. **Complete** → File moved to `Done/` with summary

**Human-in-the-Loop:**
- All posts require approval
- No automatic posting
- Full control over content
- Audit trail in `Logs/`

---

## Environment Variables

Control posting behavior with environment variables:

```bash
# Enable live posting (default: false/dry-run)
export LINKEDIN_DRY_RUN=false
export TWITTER_DRY_RUN=false
export META_DRY_RUN=false
```

**PM2 Configuration:**
```javascript
{
  "name": "linkedin-approval-monitor",
  "env": {
    "LINKEDIN_DRY_RUN": "false"
  }
}
```

---

## Best Practices

### Content Strategy

1. **Consistency:** Post regularly (1-3 times per day per platform)
2. **Timing:** Post when audience is active
3. **Variety:** Mix promotional, educational, and engagement content
4. **Hashtags:** Use relevant, targeted hashtags
5. **Engagement:** Respond to comments and messages

### Quality Control

1. **Review before approving:** Check for typos and errors
2. **Test with dry-run:** Use DRY_RUN mode for testing
3. **Monitor posts:** Check if posts appear correctly
4. **Track performance:** Review analytics for each platform

### Security

1. **Never share credentials:** Tokens stored securely
2. **Use 2FA:** Enable two-factor authentication
3. **Monitor logs:** Check `Logs/YYYY-MM-DD.json` regularly
4. **Approval required:** Always review before posting

---

## Future Enhancements

Planned features:
- [ ] LinkedIn image posting
- [ ] Twitter threads support
- [ ] Instagram carousel posting
- [ ] Scheduled posting (post at specific time)
- [ ] Analytics tracking
- [ ] A/B testing for posts
- [ ] Bulk posting from CSV

---

## Support

For issues or questions:
1. Check `AI_Employee_Vault/Logs/YYYY-MM-DD.json` for error details
2. Check PM2 logs: `pm2 logs [monitor-name]`
3. Review this documentation
4. Check `CLAUDE.md` for system architecture

---

*Last Updated: 2026-01-13*
*Version: 1.0 - Professional Image Generation + Fast Copy-Paste*
