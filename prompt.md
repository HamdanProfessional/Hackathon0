# Quick Reference: Research LinkedIn Generator

## One-Line Command

```bash
python -m watchers.research_watcher --topic "AI in manufacturing 2024"
```

## Manual Request

```bash
cat > "AI_Employee_Vault/Inbox/RESEARCH_REQUEST_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: research_request
action: research_and_linkedin_post
topic: Generative AI trends for small business
created: 2026-01-20T22:00:00Z
---

Research this topic and create a professional LinkedIn post.
EOF
```

## Workflow

```
Inbox/ (request) → Google Search → Extract Content → GLM-4.7 Analysis →
Generate Post → Pending_Approval/ (review) → Approved/ → LinkedIn → Done/
```

## Output

**File**: `Pending_Approval/LINKEDIN_POST_*.md`

Contains:
- Full LinkedIn post (1,000-2,000 characters)
- Hook, body, CTA, hashtags
- Research summary (themes, stats, quotes)
- Source list with links
- Approval instructions

## Quality Standards

- 8-10 sources analyzed
- All statistics cited
- Professional tone
- Readability score 60+
- No filler words

## Dependencies

```bash
pip install playwright trafilatura zhipuai
playwright install chromium
```

---

**Full spec**: `requirements/RESEARCH_LINKEDIN_FEATURE.md`
