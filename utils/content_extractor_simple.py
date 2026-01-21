#!/usr/bin/env python3
"""
Simple Content Extractor Utility

Extracts clean text from web URLs using requests + beautifulsoup.
Simplified version that avoids trafilatura dependency issues.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
import requests


def extract_text_from_html(html: str) -> str:
    """Extract visible text from HTML using regex."""
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove common tags
    html = re.sub(r'<[^>]+>', '\n', html)

    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', html)
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


class SimpleContentExtractor:
    """Extract clean content from web pages - simplified version."""

    def __init__(self, timeout: int = 30, min_word_count: int = 300):
        self.timeout = timeout
        self.min_word_count = min_word_count
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract(self, url: str) -> Optional[Dict]:
        """Extract content from a single URL."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            html = response.text
            text = extract_text_from_html(html)

            # Extract title
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""

            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')

            # Check quality
            word_count = len(text.split())

            if word_count < self.min_word_count:
                return None

            return {
                "url": url,
                "title": title,
                "text": text[:10000],  # Limit to 10k chars
                "word_count": word_count,
                "domain": domain,
                "quality": "good" if word_count >= self.min_word_count else "short",
            }

        except Exception as e:
            print(f"[ERROR] Failed to extract {url}: {e}")
            return None

    def extract_multiple(self, urls: List[str], max_concurrent: int = 3) -> List[Dict]:
        """Extract content from multiple URLs."""
        results = []
        for url in urls[:8]:  # Limit to 8 URLs
            result = self.extract(url)
            if result:
                results.append(result)
        return results


# For compatibility, also export as ContentExtractor
ContentExtractor = SimpleContentExtractor
