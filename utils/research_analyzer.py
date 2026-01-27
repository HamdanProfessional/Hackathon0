#!/usr/bin/env python3
"""
Research Analyzer Utility

Analyzes research articles and generates LinkedIn posts using GLM-4.7.
Designed for the Research LinkedIn Generator feature.

Usage:
    from utils.research_analyzer import ResearchAnalyzer

    analyzer = ResearchAnalyzer(api_key="your_api_key")
    analysis = analyzer.analyze_research("AI in manufacturing", articles)
    post = analyzer.generate_linkedin_post("AI in manufacturing", analysis)
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Any
import requests


class ResearchAnalyzer:
    """Analyze research content and generate LinkedIn posts using GLM-4.7."""

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize the research analyzer.

        Args:
            api_key: GLM API key (defaults to GLM_API_KEY env var)
            api_url: GLM API URL (defaults to https://api.z.ai/api/coding/paas/v4)

        Raises:
            ValueError: If GLM_API_KEY is not set
        """
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        self.api_url = api_url or os.getenv("GLM_API_URL", "https://api.z.ai/api/coding/paas/v4")

        if not self.api_key:
            raise ValueError("GLM_API_KEY environment variable must be set")

    def analyze_research(self, topic: str, articles: List[Dict]) -> Dict:
        """
        Analyze research articles and extract key insights.

        Args:
            topic: Research topic
            articles: List of article dicts with url, title, text, word_count, domain

        Returns:
            Analysis dict with themes, statistics, quotes, summary
        """
        # Prepare article summaries for the prompt
        article_summaries = []
        for i, article in enumerate(articles[:8], 1):  # Limit to 8 for token efficiency
            article_summaries.append(f"""
{i}. {article['title']}
   Source: {article['domain']}
   URL: {article['url']}
   Key content: {article['text'][:1500]}...
            """.strip())

        articles_text = "\n".join(article_summaries)

        prompt = f"""You are a research analyst. Analyze the following articles about "{topic}" and extract key insights.

# ARTICLES TO ANALYZE
{articles_text}

# TASK
Provide a structured analysis in JSON format with these exact keys:
{{
  "themes": ["theme1", "theme2", "theme3"],
  "key_statistics": ["stat1", "stat2", "stat3"],
  "notable_quotes": ["quote1", "quote2", "quote3"],
  "summary": "2-3 sentence executive summary",
  "sources_analyzed": {len(articles)},
  "total_words": {sum(a['word_count'] for a in articles)}
}}

Return ONLY valid JSON, no markdown formatting."""

        response = self._call_glm(prompt, temperature=0.3, max_tokens=2000)

        try:
            # Parse JSON response
            response_text = response.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            analysis = json.loads(response_text)
            analysis["sources"] = [a["url"] for a in articles]
            return analysis

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse GLM JSON response: {e}")
            # Response preview for debugging (only show first 500 chars)
            if len(response) > 500:
                print(f"[ERROR] Response preview: {response[:500]}...")
            # Return fallback analysis
            return self._fallback_analysis(articles)

    def generate_linkedin_post(self, topic: str, analysis: Dict, target_chars: int = 1500) -> str:
        """
        Generate a LinkedIn post from research analysis.

        Args:
            topic: Research topic
            analysis: Analysis dict from analyze_research()
            target_chars: Target character count (1000-2000 recommended)

        Returns:
            LinkedIn post content as string
        """
        # Format the analysis for the prompt
        themes_text = "\n".join(f"• {t}" for t in analysis.get("themes", [])[:5])
        stats_text = "\n".join(f"• {s}" for s in analysis.get("key_statistics", [])[:5])
        quotes_text = "\n".join(f'"{q}"' for q in analysis.get("notable_quotes", [])[:3])

        prompt = f"""You are a professional LinkedIn content creator. Write an engaging LinkedIn post about "{topic}" based on the research analysis below.

# RESEARCH ANALYSIS
Summary: {analysis.get('summary', '')}

Key Themes:
{themes_text}

Key Statistics:
{stats_text}

Notable Quotes:
{quotes_text}

# REQUIREMENTS
1. Write {target_chars}-{int(target_chars * 1.2)} characters (LinkedIn ideal length)
2. Professional but conversational tone
3. Start with a compelling hook
4. Use short paragraphs (2-3 sentences max)
5. Include 3-5 relevant hashtags at the end
6. Focus on actionable insights
7. No emojis (keeps it professional)
8. End with a question to drive engagement

# OUTPUT
Return ONLY the LinkedIn post content, no additional text."""

        response = self._call_glm(prompt, temperature=0.7, max_tokens=1500)

        # Clean up the response
        post = response.strip()
        # Remove any markdown formatting
        if post.startswith("```"):
            post = post.split("```")[1]
            if post.startswith("markdown") or post.startswith("text"):
                post = post.split("\n", 1)[1] if "\n" in post else post

        return post.strip()

    def _call_glm(self, prompt: str, temperature: float = 0.5, max_tokens: int = 2000) -> str:
        """Make a GLM API call."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "glm-4",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content
            else:
                print(f"[ERROR] GLM API error: {response.status_code} - {response.text}")
                raise Exception(f"GLM API call failed: {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"[ERROR] GLM API timeout after 60 seconds")
            raise
        except Exception as e:
            print(f"[ERROR] GLM request failed: {e}")
            raise

    def _fallback_analysis(self, articles: List[Dict]) -> Dict:
        """Generate a basic analysis when GLM is unavailable."""
        all_text = " ".join(a.get("text", "")[:500] for a in articles[:5])

        return {
            "themes": [
                "Technology trends",
                "Industry developments",
                "Market insights"
            ],
            "key_statistics": [
                f"Analyzed {len(articles)} sources",
                f"Total {sum(a['word_count'] for a in articles)} words"
            ],
            "notable_quotes": [
                "See source articles for detailed quotes"
            ],
            "summary": f"Research analysis based on {len(articles)} articles covering various aspects of the topic.",
            "sources_analyzed": len(articles),
            "total_words": sum(a['word_count'] for a in articles),
            "sources": [a["url"] for a in articles]
        }


# Convenience function
def analyze_and_generate_post(topic: str, articles: List[Dict]) -> tuple[Dict, str]:
    """
    Quick analysis and post generation.

    Returns:
        Tuple of (analysis_dict, linkedin_post_content)
    """
    analyzer = ResearchAnalyzer()
    analysis = analyzer.analyze_research(topic, articles)
    post = analyzer.generate_linkedin_post(topic, analysis)
    return analysis, post


if __name__ == "__main__":
    # Test the analyzer
    import sys

    if len(sys.argv) < 2:
        print("Usage: python research_analyzer.py <topic>")
        sys.exit(1)

    topic = sys.argv[1]

    # Test data (you would normally get this from ContentExtractor)
    test_articles = [
        {
            "url": "https://example.com/article1",
            "title": "The Future of AI in Industry",
            "text": "This is a sample article about AI trends in 2025...",
            "word_count": 800,
            "domain": "example.com"
        }
    ]

    try:
        analyzer = ResearchAnalyzer()
        print(f"Analyzing research on: {topic}\n")

        analysis = analyzer.analyze_research(topic, test_articles)
        print("Analysis:")
        print(json.dumps(analysis, indent=2))

        post = analyzer.generate_linkedin_post(topic, analysis)
        print("\n\nLinkedIn Post:")
        print(post)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
