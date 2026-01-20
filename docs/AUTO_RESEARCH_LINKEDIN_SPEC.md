# Auto-Research & LinkedIn Post Generator

## Objective

Design and implement a browser-based research automation system that autonomously:
1. Researches any given topic/term
2. Visits relevant blogs and articles
3. Extracts and processes textual content
4. Synthesizes insights into a professional LinkedIn post

## Technical Requirements

### Browser Automation
- **Tool**: Playwright (Python/Node.js) or Chrome DevTools Protocol (CDP)
- **Headless Mode**: Configurable (headless for production, headed for debugging)
- **Session Persistence**: Support for authenticated sessions (if needed)
- **Anti-Detection**: Realistic user behavior delays (2-5s between actions)

### Research Workflow
```
Input Topic → Search → Select Sources → Extract Content → Summarize → Generate Post → Save
```

## Implementation Specification

### 1. Search Module
**Purpose**: Find relevant content for the given term

**Requirements**:
- Support multiple search engines (Google, Bing, or DuckDuckGo)
- Filter by:
  - Date (past 7 days, 30 days, or all time)
  - Content type (articles, blogs, research papers)
  - Domain authority (optional: prioritize well-known sources)
- Extract top 5-10 results
- Return: URL, title, snippet, domain, publish date

**Configuration**:
```yaml
search:
  engines: ["google", "bing"]
  max_results: 8
  date_filter: "past_30_days"
  exclude_domains: ["ads.", "sponsored."]
  preferred_domains: ["medium.com", "harvard.edu", "mckinsey.com"]
```

### 2. Content Extraction Module
**Purpose**: Extract clean, readable text from web pages

**Requirements**:
- Remove HTML, CSS, JavaScript, ads, navigation
- Extract:
  - Main article content
  - Headline and subheadings
  - Author name and publication
  - Publish date
  - Key quotes/statistics
- Handle:
  - Paywall detection (skip or mark for manual review)
  - JavaScript-rendered content (wait for load)
  - Multi-page articles (concatenate)
- Output: Clean markdown or plain text

**Libraries**:
- Python: `trafilatura`, `readability-lxml`, or `beautifulsoup4`
- Node.js: `@mozilla/readability`, `turndown`

**Quality Thresholds**:
- Minimum content length: 500 words
- Maximum ads/tracking: <5% of content
- Language detection: English only (configurable)

### 3. Content Analysis Module
**Purpose**: Synthesize multiple sources into key insights

**Requirements**:
- **Identify Common Themes**: What do multiple sources agree on?
- **Extract Statistics**: Numbers, percentages, data points
- **Find Contrarian Views**: Alternative perspectives on the topic
- **Assess Credibility**: Cross-reference claims across sources
- **Timeline**: Historical context and recent developments

**Output Structure**:
```markdown
## Key Insights
- Insight 1 (supported by 3 sources)
- Insight 2 (supported by 2 sources)
- Insight 3 (controversial - Source A says X, Source B says Y)

## Statistics
- Statistic 1: [value] from [source]
- Statistic 2: [value] from [source]

## Expert Quotes
> "Quote 1" — [Author], [Publication]
> "Quote 2" — [Author], [Publication]
```

### 4. LinkedIn Post Generator Module
**Purpose**: Transform research into engaging LinkedIn content

**Post Structure** (max 3,000 characters):
```markdown
[Hook: Question, bold statement, or surprising statistic]

[Body Paragraph 1: Context and problem statement]

[Body Paragraph 2: Key insights or data points]

[Body Paragraph 3: Actionable takeaway or recommendation]

[Call to Action: Question to engage audience]

#Hashtags [5-10 relevant tags]
```

**Style Guidelines**:
- **Tone**: Professional, conversational, authoritative but approachable
- **Length**: 1,500-2,500 characters optimal (not too short, not wall-of-text)
- **Formatting**:
  - Use bullet points for lists
  - Use numbered lists for steps
  - Bold key phrases sparingly
  - Include 1-2 relevant emojis maximum
- **Hashtags**: Mix of broad (#TechTrends) and specific (#AIResearch) tags
- **Attribution**: Cite sources when sharing statistics or quotes

**Templates** (based on content type):

*Industry Update Template*:
```
🚀 [Industry] is shifting rapidly.

Here's what's happening:
• Trend 1 with data point
• Trend 2 with example
• Trend 3 with implication

The opportunity? [Your insight]

What do you think? [Question]

#[Hashtags]
```

*Research Summary Template*:
```
📊 New research on [Topic] reveals [Key Finding].

The study of [N] companies showed:
• Statistic 1
• Statistic 2
• Statistic 3

This matters because [Implication].

Full study: [Link] #[Hashtags]
```

*How-To Guide Template*:
```
💡 How to [Achieve Goal]:

1️⃣ Step 1 with brief explanation
2️⃣ Step 2 with brief explanation
3️⃣ Step 3 with brief explanation

Pro tip: [Bonus insight]

Save this post for later! #[Hashtags]
```

### 5. Quality Assurance Module
**Purpose**: Ensure output meets professional standards

**Checks**:
1. **Accuracy**: Statistics are attributed to sources
2. **Readability**: Flesch-Kincaid grade level 8-12
3. **Engagement**: Includes hook and call-to-action
4. **Compliance**: No trademark violations, no controversial claims
5. **Formatting**: Proper line breaks, no broken links

**Auto-Correction**:
- Remove filler words ("very", "really", "just")
- Fix passive voice
- Correct grammar and spelling
- Ensure consistent tense usage
- Optimize paragraph length (2-4 sentences)

## API/Integration Points

### Input Format
```json
{
  "topic": "artificial intelligence in healthcare 2024",
  "audience": "healthcare_professionals",
  "tone": "professional",
  "max_length": 2500,
  "include_statistics": true,
  "date_range": "past_30_days",
  "excluded_domains": ["competitor.com"],
  "hashtag_strategy": "industry_specific"
}
```

### Output Format
```json
{
  "success": true,
  "post": {
    "content": "[Full LinkedIn post content]",
    "character_count": 1847,
    "hashtags": ["#HealthTech", "#AI", "#DigitalHealth"],
    "sources_cited": 3,
    "statistics": 2
  },
  "research": {
    "sources_analyzed": 8,
    "themes": ["AI diagnosis", "patient outcomes", "cost reduction"],
    "confidence_score": 0.87
  },
  "metadata": {
    "generated_at": "2024-01-20T22:00:00Z",
    "model_version": "v1.2",
    "processing_time_seconds": 45
  }
}
```

## Deployment Options

### Option 1: Standalone Python Script
```python
# research_to_linkedin.py
python research_to_linkedin.py \
  --topic "AI in healthcare" \
  --output posts/ \
  --template "industry_update"
```

### Option 2: MCP Server Integration
```json
{
  "name": "research-linkedin-generator",
  "command": "python",
  "args": ["-m", "research_linkedin_mcp.server"],
  "env": {
    "OPENAI_API_KEY": "...",
    "BROWSER_HEADLESS": "true"
  }
}
```

### Option 3: Claude Code Skill
```
/.claude/skills/research-linkedin-generator/
├── SKILL.md
├── prompt.md
└── scripts/
    └── research.py
```

## Error Handling

| Error Type | Detection | Recovery |
|------------|-----------|----------|
| Rate limiting | HTTP 429 | Wait 60s, retry with backoff |
| Paywall | Paywall detection text | Skip source, log warning |
| Low-quality content | <500 words or >50% ads | Skip source |
| No results found | Search returns 0 items | Try broader query, report failure |
| Extraction failure | No readable text | Try alternative extraction method |
| Post generation fail | LLM error | Retry with simplified prompt |

## Performance Targets

| Metric | Target |
|--------|--------|
| End-to-end time | <2 minutes per post |
| Source quality | >70% relevant sources |
| Content accuracy | No hallucinated statistics |
| Readability score | >60/100 |
| Engagement prediction | >5% estimated CTR |

## Example Usage

```python
from research_linkedin import ResearchToPostGenerator

generator = ResearchToPostGenerator()

result = generator.generate(
    topic="Generative AI for small business",
    audience="small_business_owners",
    tone="approachable"
)

if result.success:
    print(result.post.content)
    # Post to LinkedIn or save for review
else:
    print(f"Failed: {result.error}")
```

## Testing Checklist

- [ ] Search returns relevant results
- [ ] Content extraction handles JavaScript sites
- [ ] Paywalls are detected and handled
- [ ] Summaries capture key insights accurately
- [ ] Generated posts match LinkedIn format guidelines
- [ ] Hashtags are relevant and not overused
- [ ] Statistics are properly attributed
- [ ] Tone matches audience preference
- [ ] No copyrighted text is reproduced verbatim
- [ ] Posts are saved in correct output location

## Future Enhancements

- **Multi-language**: Support for non-English content
- **Image generation**: Create accompanying graphics for posts
- **A/B testing**: Generate 2-3 variations, select best performer
- **Scheduling**: Auto-post at optimal times
- **Analytics tracking**: Monitor post performance
- **Trend detection**: Automatically identify trending topics
