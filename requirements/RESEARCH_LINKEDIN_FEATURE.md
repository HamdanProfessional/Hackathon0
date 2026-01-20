# Feature: Auto-Research LinkedIn Content Generator

**Status**: Proposed | **Priority**: High | **Complexity**: Medium-High
**Estimated Effort**: 3-5 days | **Tier**: Gold Enhancement

---

## Overview

Enable the AI Employee to autonomously research any topic and generate professional, well-sourced LinkedIn posts through a browser automation workflow with human-in-the-loop approval.

## Problem Statement

Currently, creating LinkedIn content requires:
- Manual research across multiple sources
- Copy-pasting content from various websites
- Manual summarization and synthesis
- Writing and formatting posts
- No systematic citation of sources

This feature automates 80% of that workflow while maintaining quality through human approval.

## Success Criteria

- [ ] System can research any topic via Google Search
- [ ] Extract clean content from 8-10 sources in <3 minutes
- [ ] Generate professional LinkedIn posts (1,000-2,000 chars)
- [ ] All statistics are cited with source attribution
- [ ] Posts require human approval before publishing
- [ ] Integration with existing vault folder structure
- [ ] Works with existing linkedin-approval-monitor

---

## User Stories

### Primary Use Case
```
As a business owner,
I want to say "Research AI in manufacturing and create a LinkedIn post",
So that I can consistently post high-quality, researched content without manual effort.
```

### Secondary Use Cases
1. **Manual Request**: Create a file in Inbox with topic details
2. **Batch Processing**: Queue multiple research requests
3. **Custom Parameters**: Specify audience, tone, date range, hashtag strategy
4. **Source Control**: Include/exclude specific domains

---

## Technical Architecture

### System Flow

```
┌─────────────────┐
│  User Input     │
│  (Topic)        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 1: RESEARCH                     │
│  • Playwright opens Chrome            │
│  • Searches Google                    │
│  • Extracts top 8-10 results           │
│  • Saves: Plans/RESEARCH_*.md         │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 2: EXTRACTION                   │
│  • Visit each source URL               │
│  • Extract article content             │
│  • Remove ads, nav, footer             │
│  • Skip paywalls/low quality           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 3: ANALYSIS                     │
│  • GLM-4.7 analyzes content            │
│  • Identifies common themes            │
│  • Extracts statistics + quotes        │
│  • Assesses credibility                │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 4: GENERATION                   │
│  • GLM-4.7 writes LinkedIn post         │
│  • Includes hook, body, CTA            │
│  • Cites all sources                   │
│  • Adds hashtags                       │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 5: APPROVAL                     │
│  • Creates file in Pending_Approval/   │
│  • Includes post + research metadata   │
│  • Human reviews, edits, approves      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Phase 6: PUBLISH                      │
│  • linkedin-approval-monitor detects    │
│  • Posts to LinkedIn via Chrome CDP     │
│  • Moves to Done/ with summary         │
└─────────────────────────────────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Employee Vault                        │
├─────────────────────────────────────────────────────────────┤
│  Inbox/              │  Trigger research requests          │
│  Plans/              │  Store research data                │
│  Pending_Approval/  │  Human review queue                  │
│  Approved/          │  Ready to publish                    │
│  Done/              │  Completed + analytics               │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────┐
│                Research Watcher (Python)                    │
│  • Monitors Inbox/ for requests                            │
│  • Orchestrates research workflow                           │
│  • Creates approval files                                   │
└────────┬───────────────┬───────────────┬──────────────────┘
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│  Playwright │  │ trafilatura │  │   GLM-4.7    │
│  MCP Server │  │  (Python)   │  │   (ZhipuAI)  │
│             │  │             │  │              │
│  Browser    │  │  Content    │  │   AI         │
│  Automation │  │  Extraction │  │   Analysis   │
└─────────────┘  └─────────────┘  └──────────────┘
```

---

## File Structure

```
AI_EMPLOYEE_APP/
├── watchers/
│   └── research_watcher.py           # Main orchestrator
├── utils/
│   ├── content_extractor.py          # Article extraction
│   └── research_analyzer.py          # GLM-4.7 integration
├── .claude/skills/
│   └── research-linkedin-generator/  # Already created
│       ├── SKILL.md
│       ├── README.md
│       └── scripts/
│           └── research.py
├── requirements/
│   └── RESEARCH_LINKEDIN_FEATURE.md  # This file
└── process-manager/
    └── pm2.config.js                 # Add research watcher
```

---

## Implementation Tasks

### Phase 1: Foundation (Day 1)

**Task 1.1: Install Dependencies**
```bash
pip install playwright trafilatura zhipuai watchdog
playwright install chromium
```

**Task 1.2: Create Base Watcher**
- [ ] Create `watchers/research_watcher.py`
- [ ] Inherit from `BaseWatcher`
- [ ] Implement file monitoring for Inbox/
- [ ] Add `@with_retry` decorator

**Task 1.3: Create Content Extractor**
- [ ] Create `utils/content_extractor.py`
- [ ] Implement `extract_article()` using trafilatura
- [ ] Implement `check_quality()` for validation
- [ ] Handle paywall detection

**Task 1.4: Create Research Analyzer**
- [ ] Create `utils/research_analyzer.py`
- [ ] Implement GLM-4.7 API integration
- [ ] Create `analyze_research()` function
- [ ] Create `generate_linkedin_post()` function

### Phase 2: Browser Automation (Day 2)

**Task 2.1: Google Search**
- [ ] Implement `search_google(topic)`
- [ ] Use Playwright to navigate Google
- [ ] Extract search results (title, URL, snippet)
- [ ] Filter by date (past 30 days default)
- [ ] Return top 10 results

**Task 2.2: Content Extraction**
- [ ] Implement `extract_content(url)`
- [ ] Navigate to each source
- [ ] Wait for page load
- [ ] Remove ads, nav, footer
- [ ] Extract article body text
- [ ] Handle JavaScript-rendered content

**Task 2.3: Error Handling**
- [ ] Handle rate limiting (backoff)
- [ ] Skip paywalls gracefully
- [ ] Handle network timeouts
- [ ] Log all errors to audit log

### Phase 3: Integration (Day 3)

**Task 3.1: Workflow Orchestration**
- [ ] Implement `process_request(request_file)`
- [ ] Coordinate all phases
- [ ] Save progress to Plans/
- [ ] Create final approval file

**Task 3.2: File Format**
- [ ] Define approval file YAML frontmatter
- [ ] Include research metadata
- [ ] Add approval instructions
- [ ] Follow naming convention

**Task 3.3: PM2 Integration**
- [ ] Add to `pm2.config.js`
- [ ] Set environment variables
- [ ] Configure auto-restart
- [ ] Test start/stop

### Phase 4: AI Integration (Day 4)

**Task 4.1: Analysis Prompts**
- [ ] Design analysis prompt for GLM-4.7
- [ ] Include few-shot examples
- [ ] Specify JSON output format
- [ ] Test with sample content

**Task 4.2: Post Generation**
- [ ] Design LinkedIn post prompt
- [ ] Include post template
- [ ] Specify formatting rules
- [ ] Add hashtag strategy

**Task 4.3: Quality Validation**
- [ ] Implement post length check
- [ ] Verify source citations
- [ ] Check readability score
- [ ] Validate hashtag relevance

### Phase 5: Testing (Day 5)

**Task 5.1: Unit Tests**
- [ ] Test Google search extraction
- [ ] Test content extraction
- [ ] Test GLM-4.7 API calls
- [ ] Test file creation

**Task 5.2: Integration Tests**
- [ ] End-to-end workflow test
- [ ] Test with various topics
- [ ] Test error scenarios
- [ ] Test approval workflow

**Task 5.3: Documentation**
- [ ] Update CLAUDE.md
- [ ] Create usage examples
- [ ] Document configuration
- [ ] Add troubleshooting guide

---

## Configuration

### Environment Variables

```bash
# Required
ZHIPUAI_API_KEY=your_api_key_here
PLAYWRIGHT_HEADLESS=true

# Optional
RESEARCH_MAX_SOURCES=10
RESEARCH_MIN_WORDS=500
RESEARCH_DATE_FILTER_DAYS=30
LINKEDIN_POST_MIN_CHARS=1000
LINKEDIN_POST_MAX_CHARS=2000
```

### PM2 Configuration

```javascript
{
  name: 'research-watcher',
  script: 'watchers/research_watcher.py',
  args: '--vault AI_Employee_Vault',
  interpreter: 'python',
  cwd: '/path/to/AI_EMPLOYEE_APP',
  instances: 1,
  autorestart: true,
  watch: ['AI_Employee_Vault/Inbox'],
  max_restarts: 3,
  min_uptime: '10s',
  env: {
    'PYTHONUNBUFFERED': '1',
    'ZHIPUAI_API_KEY': process.env.ZHIPUAI_API_KEY
  }
}
```

---

## API Specifications

### Input Format

**File**: `Inbox/RESEARCH_REQUEST_{timestamp}_{topic_slug}.md`

```yaml
---
type: research_request
action: research_and_linkedin_post
topic: Generative AI for small business 2024
audience: small_business_owners
tone: professional_approachable
created: 2026-01-20T22:00:00Z
priority: medium
---

Research this topic and create a LinkedIn post.

Additional requirements:
- Focus on practical applications
- Include ROI statistics if available
- Target small business audience
```

### Output Format

**File**: `Pending_Approval/LINKEDIN_POST_{timestamp}_{topic_slug}.md`

```yaml
---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: 2026-01-20T22:00:00Z
expires: 2026-01-21T22:00:00Z
status: pending_approval
topic: Generative AI for small business
research_sources: 8
character_count: 1847
---

# LinkedIn Post: Generative AI for Small Business

## Post Content

🤖 Small businesses are finally getting access to AI tools that were once reserved for enterprises.

Generative AI can now help small teams:
• Draft marketing copy in seconds
• Analyze customer feedback automatically
• Generate product descriptions at scale

According to a 2024 McKinsey study, small businesses using AI report 40% faster task completion.

The best part? You don't need technical expertise. Tools like ChatGPT and Claude are ready to use out of the box.

Start small: Pick one repetitive task and let AI handle it this week.

Have you tried AI in your business? What was your experience? 👇

#AI #SmallBusiness #Automation #Productivity #BusinessTips

## Research Summary
**Sources Analyzed**: 8
**Key Themes**: Cost reduction, productivity boost, ease of use
**Statistics**: 3
**Expert Quotes**: 2

## Sources
1. [McKinsey: AI for Small Business](mckinsey.com) - mckinsey.com
2. [Harvard Business Review](hbr.org) - hbr.org
3. [Forbes: AI Tools 2024](forbes.com) - forbes.com
4. [Small Business Trends](smallbiztrends.com) - smallbiztrends.com
5. [TechCrunch](techcrunch.com) - techcrunch.com
6. [Wired: AI Adoption](wired.com) - wired.com
7. [Business Insider](businessinsider.com) - businessinsider.com
8. [Entrepreneur](entrepreneur.com) - entrepreneur.com

## Approval Required
This post will be published to LinkedIn when approved.

**To Approve**: Move to `AI_Employee_Vault/Approved/`
**To Reject**: Move to `AI_Employee_Vault/Rejected/`
**To Edit**: Edit content above, then move to `Approved/`
```

---

## Dependencies

### Python Packages

```txt
# Core
playwright==1.40.0
trafilatura==1.6.0
zhipuai==2.0.0
watchdog==3.0.0

# Utilities
python-dotenv==1.0.0
python-dateutil==2.8.2

# Existing (already in project)
pyyaml>=6.0
requests>=2.31.0
```

### External Services

- **ZhipuAI GLM-4.7**: For content analysis and generation
- **Google Search**: Via Playwright browser automation
- **LinkedIn**: Via existing linkedin-approval-monitor

---

## Testing Strategy

### Unit Tests

```python
# tests/test_research_watcher.py

def test_google_search_extraction():
    """Test Google search result extraction"""
    watcher = ResearchWatcher(vault_path="test_vault")
    results = await watcher.search_google("AI in business")
    assert len(results) >= 8
    assert all('url' in r for r in results)
    assert all('title' in r for r in results)

def test_content_extraction():
    """Test article content extraction"""
    extractor = ContentExtractor()
    content = extractor.extract_from_url("https://example.com/article")
    assert len(content.split()) >= 500
    assert 'subscribe' not in content.lower()[:100]

def test_quality_check():
    """Test content quality validation"""
    extractor = ContentExtractor()
    assert extractor.check_quality("a" * 100) == (False, "Content too short")
    assert extractor.check_quality("subscribe now " + "a" * 600) == (False, "Paywall detected")
```

### Integration Test

```python
# tests/test_research_workflow.py

def test_end_to_end_workflow():
    """Test complete research workflow"""
    # Create request
    request = create_test_request("AI in healthcare")

    # Process request
    watcher = ResearchWatcher()
    watcher.process_request(request)

    # Verify approval file created
    approval_files = list((vault_path / "Pending_Approval").glob("LINKEDIN_POST_*.md"))
    assert len(approval_files) == 1

    # Verify content
    content = approval_files[0].read_text()
    assert "## Post Content" in content
    assert "## Sources" in content
    assert len([l for l in content.split('\n') if l.startswith('1. [')]) >= 5
```

### Test Cases

| Test Case | Input | Expected Output |
|----------|-------|-----------------|
| Simple topic | "AI trends 2024" | LinkedIn post with 5+ sources |
| Technical topic | "Kubernetes security" | Post with technical accuracy |
| Broad topic | "Digital marketing" | Post focused on specific aspects |
| No results | "Gibberish xyz123" | Error handling, graceful fail |
| Paywall only | "Wall Street Journal article" | Skip paywall, continue to others |

---

## Rollout Plan

### Phase 1: Alpha (Internal)
- [ ] Run locally only
- [ ] Test with 5-10 topics
- [ ] Verify output quality
- [ ] Fix critical bugs

### Phase 2: Beta (Selected Users)
- [ ] Deploy to development environment
- [ ] Enable for 1-2 test topics
- [ ] Monitor performance
- [ ] Gather feedback

### Phase 3: Production
- [ ] Add to PM2 config
- [ ] Deploy to Cloud VM
- [ ] Enable for all users
- [ ] Monitor usage metrics

---

## Success Metrics

### Performance Metrics
- Research completion time: <3 minutes
- Post generation time: <30 seconds
- End-to-end time: <5 minutes
- Success rate: >90% (without paywalls)

### Quality Metrics
- Posts approved: >80% (vs rejected)
- Engagement rate: >5% (LinkedIn average)
- Citation accuracy: 100% (no hallucinated stats)
- Readability score: >60/100

### User Satisfaction
- Manual editing required: <30% of posts
- Time saved: >80% vs manual research
- User adoption: >10 posts/week after 1 month

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Paywall blocking | High | Medium | Skip source, continue to next |
| Rate limiting | Medium | Medium | Add delays, rotate user agents |
| Low-quality sources | Medium | Low | Quality check before analysis |
| GLM-4.7 API down | Low | High | Graceful degradation, notify user |
| Hallucinated stats | Low | High | Require source citations |

---

## Future Enhancements

### Phase 2 Features
- [ ] Multi-language support (non-English sources)
- [ ] Image generation for posts
- [ ] A/B testing (generate 2-3 variations)
- [ ] Scheduling (auto-post at optimal times)
- [ ] Analytics tracking (monitor post performance)

### Phase 3 Features
- [ ] Trend detection (auto-identify trending topics)
- [ ] Competitor monitoring (track their content)
- [ ] Video content extraction
- [ ] Podcast transcription and summarization
- [ ] Integration with other platforms (Twitter, Facebook)

---

## Open Questions

1. **GLM-4.7 Cost**: What's the monthly API budget for 10-20 posts/day?
2. **Rate Limits**: How many Google searches before we get blocked?
3. **Source Quality**: Should we maintain a whitelist of preferred domains?
4. **Post Frequency**: Should we limit posts per day/week?
5. **Edit Workflow**: Should we track edit history for learning?

---

## References

- Existing: `.claude/skills/linkedin-manager/` (LinkedIn posting)
- Existing: `.claude/skills/twitter-manager/` (Twitter posting)
- Similar: `watchers/gmail_watcher.py` (Watcher pattern)
- Similar: `utils/odoo_client.py` (API integration)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-20
**Author**: AI Employee Team
**Status**: Ready for Implementation
