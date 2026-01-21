#!/usr/bin/env python3
"""
Content Extractor Utility

Extracts clean text from web URLs using trafilatura.
Designed for the Research LinkedIn Generator feature.

Usage:
    from utils.content_extractor import ContentExtractor

    extractor = ContentExtractor()
    result = extractor.extract("https://example.com/article")
    print(result["text"])
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
import trafilatura
import requests


class ContentExtractor:
    """Extract clean content from web pages."""

    def __init__(self, timeout: int = 30, min_word_count: int = 500):
        """
        Initialize the content extractor.

        Args:
            timeout: HTTP request timeout in seconds
            min_word_count: Minimum word count for quality content
        """
        self.timeout = timeout
        self.min_word_count = min_word_count
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract(self, url: str) -> Optional[Dict]:
        """
        Extract content from a single URL.

        Args:
            url: The URL to extract content from

        Returns:
            Dictionary with keys: url, title, text, word_count, domain
            Returns None if extraction fails or content is too short
        """
        try:
            # Download the page
            downloaded = trafilatura.fetch_url(url, timeout=self.timeout)

            if not downloaded:
                return None

            # Extract main content
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                target_language=None,
            )

            if not text:
                return None

            # Extract title
            title = trafilatura.extract_title(downloaded) or ""

            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')

            # Check quality
            word_count = len(text.split())

            if word_count < self.min_word_count:
                # Check for paywall or restricted content
                if self._is_paywall(text):
                    return None

            return {
                "url": url,
                "title": title.strip(),
                "text": text.strip(),
                "word_count": word_count,
                "domain": domain,
                "quality": "good" if word_count >= self.min_word_count else "short",
            }

        except Exception as e:
            print(f"[ERROR] Failed to extract {url}: {e}")
            return None

    def extract_multiple(self, urls: List[str], max_concurrent: int = 5) -> List[Dict]:
        """
        Extract content from multiple URLs concurrently.

        Args:
            urls: List of URLs to extract from
            max_concurrent: Maximum concurrent extractions

        Returns:
            List of extraction result dictionaries (filtered to successes only)
        """
        import concurrent.futures

        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_url = {executor.submit(self.extract, url): url for url in urls}

            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                if result:
                    results.append(result)

        return results

    def _is_paywall(self, text: str) -> bool:
        """Detect if content is behind a paywall."""
        paywall_indicators = [
            "subscribe to continue",
            "premium article",
            "subscribe for full access",
            "create an account to continue",
            "limited access",
            "subscription required",
            "paywall",
            "subscribe now",
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in paywall_indicators)

    def clean_text(self, text: str, max_length: int = 10000) -> str:
        """
        Clean extracted text for AI analysis.

        Args:
            text: Raw text to clean
            max_length: Maximum character length

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common navigation/footer text
        junk_patterns = [
            r'Share this article',
            r'Follow us on',
            r'Subscribe to our',
            r'Copyright \d{4}',
            r'All rights reserved',
            r'Click here for',
            r'View original article',
        ]

        for pattern in junk_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length] + "..."

        return text.strip()


# Convenience function
def extract_url(url: str) -> Optional[Dict]:
    """Quick extraction from a single URL."""
    extractor = ContentExtractor()
    return extractor.extract(url)


def extract_urls(urls: List[str]) -> List[Dict]:
    """Quick extraction from multiple URLs."""
    extractor = ContentExtractor()
    return extractor.extract_multiple(urls)


if __name__ == "__main__":
    # Test the extractor
    import sys

    if len(sys.argv) < 2:
        print("Usage: python content_extractor.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    extractor = ContentExtractor()

    print(f"Extracting from: {url}")
    result = extractor.extract(url)

    if result:
        print(f"\nTitle: {result['title']}")
        print(f"Domain: {result['domain']}")
        print(f"Words: {result['word_count']}")
        print(f"Quality: {result['quality']}")
        print(f"\nContent preview:\n{result['text'][:500]}...")
    else:
        print("Failed to extract content")
        sys.exit(1)
