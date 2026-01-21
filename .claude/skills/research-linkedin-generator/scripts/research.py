#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research LinkedIn Generator - AI Employee Skill

Automatically research topics and generate professional LinkedIn posts.
Integrates with the AI Employee approval workflow.
"""

import sys
import os

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import argparse
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Add project root to path (go up 5 levels: scripts/ -> skill/ -> skills/ -> .claude/ -> root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Try to use trafilatura, fall back to simple extractor
try:
    from utils.content_extractor import ContentExtractor
except ImportError:
    from utils.content_extractor_simple import ContentExtractor

from utils.research_analyzer import ResearchAnalyzer


class ResearchLinkedInGenerator:
    """Research topics and generate LinkedIn posts"""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.plans_path = self.vault_path / "Plans"
        self.pending_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"

        # Initialize utilities
        self.content_extractor = ContentExtractor()
        self.research_analyzer = ResearchAnalyzer()

        # MCP server path
        self.playwright_mcp = Path(__file__).parent.parent.parent.parent / "mcp-servers" / "playwright-mcp"

    def create_research_request(self, topic: str, urls: List[str] = None) -> Path:
        """Create a research request file in Inbox"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic.lower().replace(" ", "_")[:50]
        filename = f"RESEARCH_REQUEST_{timestamp}_{slug}.md"

        request_file = self.inbox_path / filename

        urls_section = ""
        if urls:
            urls_section = "\n## Source URLs (provided)\n" + "\n".join(f"- {url}" for url in urls)

        content = f"""---
type: research_request
action: research_and_linkedin_post
topic: {topic}
created: {datetime.now().isoformat()}
---

# Research Request: {topic}

Please research this topic and create a professional LinkedIn post.
{urls_section}
## Research Requirements
- Search for recent articles (past 30 days) if URLs not provided
- Analyze 8-10 relevant sources
- Extract key insights, statistics, and quotes
- Generate a 1,000-2,000 character LinkedIn post
- Cite all sources for statistics and quotes

## Output Format
- Professional tone
- Include hook, body, call-to-action
- Add 5-10 relevant hashtags
- Cite sources inline

## Approval
The generated post will require approval before posting.
"""

        request_file.parent.mkdir(parents=True, exist_ok=True)
        request_file.write_text(content)

        print(f"✓ Research request created: {request_file}")
        return request_file

    def process_inbox_requests(self):
        """Process all research requests in Inbox"""
        requests = list(self.inbox_path.glob("RESEARCH_REQUEST_*.md"))

        if not requests:
            print("No research requests found in Inbox")
            return

        print(f"Found {len(requests)} research request(s)")

        for request_file in requests:
            print(f"\nProcessing: {request_file.name}")

            # Parse request
            content = request_file.read_text()
            topic = self._extract_topic(content)

            if topic:
                self._process_research(topic, request_file)
            else:
                print(f"  ✗ Could not extract topic from request")

    def process_daily_research(self):
        """Process daily research with pre-configured topics"""
        import json
        from datetime import datetime

        # Load daily topics config
        config_path = Path(__file__).parent.parent / "daily_topics.json"

        if not config_path.exists():
            print(f"Config file not found: {config_path}")
            return

        with open(config_path) as f:
            config = json.load(f)

        # Get today's topic based on day of week
        today = datetime.now().strftime("%A").lower()
        topics = config.get("daily_topics", [])

        if not topics:
            print("No topics configured")
            return

        # Select topic for today (rotate through topics)
        topics_per_day = config.get("schedule", {}).get("topics_per_day", 1)
        day_index = (datetime.now().weekday()) % len(topics)

        print(f"Daily Research Run - {today}")
        print(f"=" * 50)

        for i in range(topics_per_day):
            topic_index = (day_index + i) % len(topics)
            topic_config = topics[topic_index]

            print(f"\nProcessing: {topic_config['topic']}")
            print("-" * 40)

            try:
                self._process_research_with_urls(
                    topic_config['topic'],
                    topic_config['sources']
                )
            except Exception as e:
                print(f"  ✗ Error: {e}")

        print("\n" + "=" * 50)
        print("Daily research complete!")

    def _extract_topic(self, content: str) -> str:
        """Extract topic from request file"""
        for line in content.split('\n'):
            if line.startswith('topic: '):
                return line.split(':', 1)[1].strip()
        return None

    def _process_research_with_urls(self, topic: str, source_urls: List[str]):
        """Process research for a topic with provided URLs - for cloud VM"""
        print(f"  Topic: {topic}")
        print(f"  URLs: {len(source_urls)} provided")

        try:
            # Skip search, use provided URLs
            print("  → Step 1: Using provided URLs...")

            # Step 2: Extract content from URLs
            print("  → Step 2: Extracting content...")
            articles = self.content_extractor.extract_multiple(source_urls)

            if not articles:
                print("  ✗ No content could be extracted")
                return

            print(f"  ✓ Extracted content from {len(articles)} sources")

            # Step 3: Analyze research with GLM-4.7
            print("  → Step 3: Analyzing research...")
            analysis = self.research_analyzer.analyze_research(topic, articles)
            print(f"  ✓ Analysis complete: {analysis.get('sources_analyzed', 0)} sources analyzed")

            # Step 4: Generate LinkedIn post
            print("  → Step 4: Generating LinkedIn post...")
            linkedin_post = self.research_analyzer.generate_linkedin_post(topic, analysis)
            print(f"  ✓ Generated {len(linkedin_post)} character post")

            # Step 5: Create approval file
            print("  → Step 5: Creating approval file...")
            approval_file = self._create_approval_file(topic, analysis, linkedin_post, source_urls)
            print(f"  ✓ Created: {approval_file.name}")

            print("\n  === SUMMARY ===")
            print(f"  Post length: {len(linkedin_post)} chars")
            print(f"  Sources used: {len(articles)}")
            print(f"  Review at: {approval_file}")

        except Exception as e:
            print(f"  ✗ Error processing research: {e}")
            import traceback
            traceback.print_exc()

    def _process_research(self, topic: str, request_file: Path):
        """Process research for a topic - full workflow implementation"""
        print(f"  Topic: {topic}")

        try:
            # Step 1: Search Google for the topic
            print("  → Step 1: Searching Google...")
            source_urls = self._search_google(topic)

            if not source_urls:
                print("  ✗ No search results found")
                return

            print(f"  ✓ Found {len(source_urls)} sources")

            # Step 2: Extract content from URLs
            print("  → Step 2: Extracting content...")
            articles = self.content_extractor.extract_multiple(source_urls)

            if not articles:
                print("  ✗ No content could be extracted")
                return

            print(f"  ✓ Extracted content from {len(articles)} sources")

            # Step 3: Analyze research with GLM-4.7
            print("  → Step 3: Analyzing research...")
            analysis = self.research_analyzer.analyze_research(topic, articles)
            print(f"  ✓ Analysis complete: {analysis.get('sources_analyzed', 0)} sources analyzed")

            # Step 4: Generate LinkedIn post
            print("  → Step 4: Generating LinkedIn post...")
            linkedin_post = self.research_analyzer.generate_linkedin_post(topic, analysis)
            print(f"  ✓ Generated {len(linkedin_post)} character post")

            # Step 5: Create approval file
            print("  → Step 5: Creating approval file...")
            approval_file = self._create_approval_file(topic, analysis, linkedin_post, source_urls)
            print(f"  ✓ Created: {approval_file.name}")

            # Move request to Plans
            plan_file = self.plans_path / request_file.name.replace("REQUEST", "")
            request_file.rename(plan_file)
            print(f"  ✓ Moved request to Plans/")

            print("\n  === SUMMARY ===")
            print(f"  Post length: {len(linkedin_post)} chars")
            print(f"  Sources used: {len(articles)}")
            print(f"  Review at: {approval_file}")

        except Exception as e:
            print(f"  ✗ Error processing research: {e}")
            import traceback
            traceback.print_exc()

    def _search_google(self, topic: str, max_results: int = 10) -> List[str]:
        """
        Search for articles about a topic.
        For cloud VM: Uses DuckDuckGo HTML (more permissive than Google).
        Falls back to trafilatura's built-in search if available.
        """
        try:
            import requests
            from html.parser import HTMLParser

            # Use DuckDuckGo HTML search (more permissive for headless/cloud)
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(topic)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Parse results using regex
            url_pattern = r'class="result__url"[^>]*><a[^>]*href="(https?://[^"]+)"'
            matches = re.findall(url_pattern, response.text)

            # DuckDuckGo redirects, so we need to resolve the actual URLs
            urls = []
            for match in matches[:max_results * 2]:  # Get more to filter
                # Remove DuckDuckGo redirect prefix if present
                clean_url = match
                if 'uddg=' in match:
                    clean_url = re.sub(r'^https?://[^/]*//uddg=', '', match)
                    # URL decode
                    from urllib.parse import unquote
                    try:
                        clean_url = unquote(clean_url)
                    except:
                        pass

                # Filter quality domains
                if self._is_quality_url(clean_url):
                    urls.append(clean_url)
                    if len(urls) >= max_results:
                        break

            if urls:
                print(f"  ✓ Found {len(urls)} URLs via DuckDuckGo")
                return urls
            else:
                print("  ⚠ No URLs found, using fallback")
                return self._fallback_urls(topic)

        except Exception as e:
            print(f"  ⚠ Search error ({e}), using fallback")
            return self._fallback_urls(topic)

    def _is_quality_url(self, url: str) -> bool:
        """Check if URL is from a quality source"""
        exclude_patterns = [
            'google.', 'youtube.', 'facebook.', 'twitter.', 'linkedin.',
            'instagram.', 'pinterest.', 'reddit.', 'amazon.', 'ebay.',
            'duckduckgo', 'yandex.', 'bing.'
        ]

        url_lower = url.lower()

        # Exclude low-quality sources
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False

        # Include good sources
        good_patterns = [
            '.com/', '.org/', '.edu/', '.net/', '.io/', '.co/',
            'blog.', 'news.', 'tech.', 'medium.com', 'dev.to'
        ]

        return any(pattern in url_lower for pattern in good_patterns)

    def _extract_urls_from_search_result(self, result_text: str) -> List[str]:
        """Extract URLs from search result (legacy, for Playwright MCP compatibility)"""
        urls = []
        url_pattern = r'https?://[^\s\)"\'\>]+'
        matches = re.findall(url_pattern, result_text)

        for url in matches:
            if self._is_quality_url(url):
                urls.append(url)

        return urls[:10]

    def _fallback_urls(self, topic: str) -> List[str]:
        """
        Fallback: Use a few reputable tech/news sources with topic in URL.
        This is a simple heuristic for when search fails.
        """
        # Generate likely search URLs based on topic keywords
        keywords = topic.lower().split()[:3]
        fallback_urls = []

        # Common tech news domains
        domains = [
            'techcrunch.com',
            'theverge.com',
            'wired.com',
            'arstechnica.com',
            'news.ycombinator.com'
        ]

        # This is just a placeholder - in real use you'd want proper search
        # For now return empty to signal that proper URLs should be provided
        print("  ℹ No search results available. Please provide URLs manually.")
        return []

    def _create_approval_file(self, topic: str, analysis: Dict, post: str, sources: List[str]) -> Path:
        """Create approval file in Pending_Approval/"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic.lower().replace(" ", "_")[:30]
        filename = f"LINKEDIN_POST_RESEARCH_{timestamp}_{slug}.md"

        approval_file = self.pending_path / filename

        # Format sources list
        sources_text = "\n".join(f"{i+1}. {url}" for i, url in enumerate(sources[:8]))

        # Format analysis
        themes_text = "\n".join(f"  - {t}" for t in analysis.get("themes", [])[:5])
        stats_text = "\n".join(f"  - {s}" for s in analysis.get("key_statistics", [])[:5])

        content = f"""---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=7)).isoformat()}
status: pending
research_topic: {topic}
sources_count: {len(sources)}
char_count: {len(post)}
---

# LinkedIn Post: {topic}

## Research Summary
{analysis.get('summary', '')}

## Key Themes
{themes_text}

## Key Statistics
{stats_text}

## LinkedIn Post
{post}

## Sources
{sources_text}

---
*This post was auto-generated from research on {len(sources)} sources.*
*Review for accuracy and tone before approving.*
"""

        approval_file.parent.mkdir(parents=True, exist_ok=True)
        approval_file.write_text(content, encoding='utf-8')

        return approval_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Research LinkedIn Generator - AI Employee Skill"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--topic",
        help="Topic to research (creates request in Inbox)"
    )
    parser.add_argument(
        "--urls",
        help="Comma-separated URLs to use as sources (optional, for --topic or --process-topic)"
    )
    parser.add_argument(
        "--process-topic",
        help="Research topic directly and create approval file"
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Process all requests in Inbox"
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Run daily research with pre-configured topics"
    )

    args = parser.parse_args()

    # Parse URLs if provided
    source_urls = None
    if args.urls:
        source_urls = [url.strip() for url in args.urls.split(",") if url.strip()]
        print(f"Using {len(source_urls)} provided source URLs")

    generator = ResearchLinkedInGenerator(args.vault)

    if args.topic:
        print(f"Creating research request for: {args.topic}")
        generator.create_research_request(args.topic, source_urls)
        print("\nNext steps:")
        print("1. Run with --process to handle all Inbox requests")
        print("2. Or run with --process-topic '{}' to process immediately".format(args.topic))
        print("3. Research will be saved to Plans/")
        print("4. LinkedIn post will be created in Pending_Approval/")
        print("5. Review and move to Approved/ to publish")

    elif args.process_topic:
        print(f"Processing research topic: {args.process_topic}\n")
        # Pass URLs directly if provided, otherwise search
        if source_urls:
            print(f"Using {len(source_urls)} provided URLs")
            generator._process_research_with_urls(args.process_topic, source_urls)
        else:
            generator._process_research(args.process_topic, None)
        print("\nNext steps:")
        print("1. Review the generated post in Pending_Approval/")
        print("2. Move to Approved/ to publish to LinkedIn")

    elif args.process:
        print("Processing research requests...")
        generator.process_inbox_requests()

    elif args.daily:
        print("Running daily research...")
        generator.process_daily_research()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
