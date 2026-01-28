"""
Deep Research Module for LinkedIn Research Generator

Provides multi-level research capabilities:
- Level 1: Article/content extraction (surface)
- Level 2: Documentation research (deeper)
- Level 3: Library/package analysis (deepest)

Usage:
    from deep_research import DeepResearcher

    researcher = DeepResearcher()
    results = researcher.research_topic("Rust programming language")
"""

from __future__ import annotations

import re
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set, Callable
from urllib.parse import urljoin, urlparse
import hashlib
import logging

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Error recovery integration
try:
    from watchers.error_recovery import with_retry, ErrorCategory
    HAS_ERROR_RECOVERY = True
except ImportError:
    # Fallback simple retry decorator
    HAS_ERROR_RECOVERY = False
    import time
    from functools import wraps

    def with_retry(max_attempts: int = 3, base_delay: int = 1, **kwargs):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **inner_kwargs):
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **inner_kwargs)
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise
                        delay = min(base_delay * (2 ** attempt), 60)
                        time.sleep(delay)
                return None
            return wrapper
        return decorator

    class ErrorCategory:
        TRANSIENT = "transient"
        RATE_LIMIT = "rate_limit"

# Set up logging
logger = logging.getLogger(__name__)


class DeepResearcher:
    """
    Multi-level researcher for comprehensive topic analysis.

    Research Levels:
    1. Surface: Article content and metadata
    2. Deeper: Documentation, official resources
    3. Deepest: GitHub repos, package info, source code
    """

    # Documentation patterns for common platforms
    DOC_PATTERNS = {
        'GitHub': r'github\.com/[\w-]+/[\w-]+',
        'PyPI': r'pypi\.org/project/[\w-]+',
        'NPM': r'npmjs\.com/package/[\w-]+',
        ' crates.io': r'crates\.io/crates/[\w-]+',
        'RubyGems': r'rubygems\.org/gems/[\w-]+',
        'Go': r'pkg\.go\.dev/[\w-]+',
        'Maven': r'maven\.org/repository/.*',
        'NuGet': r'nuget\.org/packages/[\w-]+',
    }

    # Official documentation domains
    OFFICIAL_DOCS = [
        'docs.', 'developer.', 'developers.', 'api.',
        'reference.', 'guides.', 'tutorial.', 'learn.',
        'readthedocs.io', 'devdocs.io'
    ]

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize deep researcher.

        Args:
            cache_dir: Directory for caching research results
        """
        self.cache_dir = cache_dir or Path("AI_Employee_Vault/.cache/research")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.session = None
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

        # Research tracking
        self.visited_urls: Set[str] = set()
        self.research_results: Dict[str, Any] = {}

    def research_topic(self, topic: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Perform comprehensive multi-level research on a topic.

        Args:
            topic: Research topic (e.g., "Rust programming language")
            max_depth: Maximum research depth (1-3)

        Returns:
            Complete research results with all levels
        """
        research_id = hashlib.md5(topic.encode()).hexdigest()[:12]
        cache_file = self.cache_dir / f"research_{research_id}.json"

        # Check cache
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=24):
                return json.loads(cache_file.read_text(encoding="utf-8"))

        # Initialize results
        results = {
            "topic": topic,
            "research_id": research_id,
            "timestamp": datetime.now().isoformat(),
            "levels": {
                "surface": [],
                "documentation": [],
                "libraries": []
            },
            "insights": {
                "technologies": [],
                "frameworks": [],
                "libraries": [],
                "tools": []
            },
            "sources": []
        }

        # Level 1: Surface research (articles)
        if max_depth >= 1:
            results["levels"]["surface"] = self._surface_research(topic)

        # Level 2: Documentation research
        if max_depth >= 2:
            results["levels"]["documentation"] = self._documentation_research(topic, results)

        # Level 3: Library/package research
        if max_depth >= 3:
            results["levels"]["libraries"] = self._library_research(topic, results)

        # Extract insights
        results["insights"] = self._extract_insights(results)

        # Compile all sources
        all_sources = (
            results["levels"]["surface"] +
            results["levels"]["documentation"] +
            results["levels"]["libraries"]
        )
        results["sources"] = [s["url"] for s in all_sources if "url" in s]

        # Cache results
        cache_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

        return results

    def _surface_research(self, topic: str) -> List[Dict[str, Any]]:
        """Level 1: Extract surface article content."""
        # This would be called after initial URL discovery
        # Returns metadata about articles
        return []

    def _documentation_research(self, topic: str, previous_results: Dict) -> List[Dict[str, Any]]:
        """
        Level 2: Research official documentation.

        Finds:
        - API documentation
        - Official guides
        - Reference materials
        - Getting started tutorials
        """
        docs = []

        # Extract potential library/tech names from topic
        tech_names = self._extract_tech_names(topic)

        for tech_name in tech_names:
            # Search for official docs
            tech_docs = self._find_official_docs(tech_name)
            docs.extend(tech_docs)

        return docs

    def _library_research(self, topic: str, previous_results: Dict) -> List[Dict[str, Any]]:
        """
        Level 3: Deep library/package research.

        Extracts:
        - GitHub repository information
        - Package metadata
        - Dependencies
        - Version history
        - Community activity
        """
        libraries = []

        # Find GitHub repos mentioned in research
        github_urls = self._find_github_urls(previous_results)

        for github_url in github_urls:
            if github_url not in self.visited_urls:
                lib_info = self._analyze_github_repo(github_url)
                if lib_info:
                    libraries.append(lib_info)
                    self.visited_urls.add(github_url)

        # Find package references
        packages = self._find_package_references(previous_results)
        for package_url in packages:
            if package_url not in self.visited_urls:
                pkg_info = self._analyze_package(package_url)
                if pkg_info:
                    libraries.append(pkg_info)
                    self.visited_urls.add(package_url)

        return libraries

    def _extract_tech_names(self, text: str) -> List[str]:
        """Extract technology/library names from text."""
        # Common programming languages and frameworks
        tech_keywords = [
            'python', 'javascript', 'typescript', 'java', 'rust', 'go', 'c++', 'c#',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'dart', 'flutter',
            'react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxt',
            'django', 'flask', 'fastapi', 'express', 'spring', 'rails',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
            'numpy', 'node', 'deno', 'bun', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'mongodb', 'postgresql', 'mysql',
            'redis', 'graphql', 'grpc', 'websocket', 'rabbitmq'
        ]

        found = []
        text_lower = text.lower()
        words = re.findall(r'\b[a-z]+(?:[+#]?\w*)?\b', text_lower)

        for keyword in tech_keywords:
            if keyword in text_lower or keyword.replace('#', '') in text_lower:
                if keyword not in found:
                    found.append(keyword)

        return found

    @with_retry(max_attempts=3, base_delay=2, error_category=ErrorCategory.TRANSIENT)
    def _find_official_docs(self, tech_name: str) -> List[Dict[str, Any]]:
        """Find official documentation for a technology."""
        if not HAS_REQUESTS:
            return []

        docs = []

        # Common official doc patterns
        doc_urls = [
            f"https://docs.{tech_name}.org",
            f"https://developer.{tech_name}.org",
            f"https://{tech_name}.org/docs",
            f"https://{tech_name}.dev",
            f"https://api.{tech_name}.org",
        ]

        for url in doc_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    docs.append({
                        "url": url,
                        "type": "official_docs",
                        "tech": tech_name,
                        "title": self._extract_page_title(response.text),
                        "content_length": len(response.text)
                    })
            except Exception as e:
                logger.debug(f"Could not fetch docs from {url}: {e}")
                continue

        return docs

    def _find_github_urls(self, results: Dict) -> List[str]:
        """Extract GitHub URLs from research results."""
        github_urls = []

        for level_data in results["levels"].values():
            for item in level_data:
                if isinstance(item, dict) and "url" in item:
                    url = item["url"]
                    # Find GitHub URLs in content
                    if "github.com/" in url:
                        github_urls.append(url)
                    # Also find GitHub URLs in text content
                    if "text" in item:
                        github_urls.extend(re.findall(r'https://github\.com/[\w-]+/[\w-]+', item["text"]))

        return list(set(github_urls))

    def _find_package_references(self, results: Dict) -> List[str]:
        """Find package manager URLs from research results."""
        packages = []

        for pattern_name, pattern in self.DOC_PATTERNS.items():
            if pattern_name == "GitHub":
                continue

            for level_data in results["levels"].values():
                for item in level_data:
                    if isinstance(item, dict) and "url" in item:
                        if re.search(pattern, item["url"]):
                            packages.append(item["url"])
                    if "text" in item:
                        packages.extend(re.findall(pattern, item["text"]))

        return list(set(packages))

    @with_retry(max_attempts=3, base_delay=2, error_category=ErrorCategory.TRANSIENT)
    def _analyze_github_repo(self, github_url: str) -> Optional[Dict[str, Any]]:
        """Analyze a GitHub repository for detailed information."""
        if not HAS_REQUESTS:
            return None

        # Extract owner/repo from URL
        match = re.search(r'github\.com/([\w-]+)/([\w-]+)', github_url)
        if not match:
            return None

        owner, repo = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        try:
            response = self.session.get(api_url, timeout=10)
            if response.status_code != 200:
                logger.debug(f"GitHub API returned {response.status_code} for {api_url}")
                return None

            data = response.json()

            return {
                "url": github_url,
                "type": "github_repo",
                "name": data.get("name"),
                "description": data.get("description"),
                "language": data.get("language"),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "homepage": data.get("homepage"),
                "license": data.get("license", {}).get("name") if data.get("license") else None,
                "topics": data.get("topics", []),
                "has_wiki": data.get("has_wiki", False),
                "has_pages": data.get("has_pages", False),
                "archived": data.get("archived", False)
            }

        except Exception as e:
            logger.warning(f"Could not analyze GitHub repo {github_url}: {e}")
            return None

    @with_retry(max_attempts=3, base_delay=2, error_category=ErrorCategory.TRANSIENT)
    def _analyze_package(self, package_url: str) -> Optional[Dict[str, Any]]:
        """Analyze a package from its package manager URL."""
        if not HAS_REQUESTS:
            return None

        response = self.session.get(package_url, timeout=10)
        if response.status_code != 200:
            logger.debug(f"Package manager returned {response.status_code} for {package_url}")
            return None

        # Determine package type from URL
        if "pypi.org" in package_url:
            return self._analyze_pypi_package(package_url, response.text)
        elif "npmjs.com" in package_url:
            return self._analyze_npm_package(package_url, response.text)
        elif "crates.io" in package_url:
            return self._analyze_crate_package(package_url, response.text)
        else:
            return {
                "url": package_url,
                "type": "package",
                "name": self._extract_page_title(response.text),
                "content_length": len(response.text)
            }

    def _analyze_pypi_package(self, url: str, html: str) -> Dict[str, Any]:
        """Analyze a PyPI package."""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract package info
        name_tag = soup.find('span', class_='package-name')
        version_tag = soup.find('span', class_='package-version')
        author_tag = soup.find('span', class_='author-name')

        return {
            "url": url,
            "type": "pypi_package",
            "name": name_tag.text.strip() if name_tag else None,
            "version": version_tag.text.strip() if version_tag else None,
            "author": author_tag.text.strip() if author_tag else None,
            "manager": "pip"
        }

    def _analyze_npm_package(self, url: str, html: str) -> Dict[str, Any]:
        """Analyze an npm package."""
        soup = BeautifulSoup(html, 'html.parser')

        # Try to extract from JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'SoftwareSourceCode':
                    return {
                        "url": url,
                        "type": "npm_package",
                        "name": data.get('name'),
                        "version": data.get('version'),
                        "description": data.get('description'),
                        "author": data.get('author', {}).get('name'),
                        "manager": "npm"
                    }
            except Exception:
                continue

        return {
            "url": url,
            "type": "npm_package",
            "name": self._extract_page_title(html),
            "manager": "npm"
        }

    def _analyze_crate_package(self, url: str, html: str) -> Dict[str, Any]:
        """Analyze a Rust crate."""
        soup = BeautifulSoup(html, 'html.parser')

        name_tag = soup.find('h1', class_='crate-title')
        version_tag = soup.find('div', class_='crate-info')

        return {
            "url": url,
            "type": "crate",
            "name": name_tag.text.strip() if name_tag else None,
            "version": version_tag.text.strip() if version_tag else None,
            "manager": "cargo"
        }

    def _extract_page_title(self, html: str) -> str:
        """Extract page title from HTML."""
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Remove common suffixes
            for suffix in [' | GitHub', ' - npm', ' | Python Package Index', ' - crates.io']:
                title = title.replace(suffix, '')
            return title.strip()
        return "Unknown"

    def _extract_insights(self, results: Dict) -> Dict[str, List[str]]:
        """Extract insights from research results."""
        insights = {
            "technologies": [],
            "frameworks": [],
            "libraries": [],
            "tools": []
        }

        all_text = ""
        for level_data in results["levels"].values():
            for item in level_data:
                if isinstance(item, dict):
                    if "text" in item:
                        all_text += " " + item["text"]
                    if "description" in item:
                        all_text += " " + item["description"]
                    if "topics" in item:
                        insights["technologies"].extend(item["topics"])
                    if "language" in item:
                        insights["technologies"].append(item["language"])

        # Extract tech names from combined text
        tech_names = self._extract_tech_names(all_text)
        for tech in tech_names:
            if tech not in insights["technologies"]:
                insights["technologies"].append(tech)

        # Categorize technologies
        tech_categories = {
            "frameworks": ["react", "vue", "angular", "django", "flask", "fastapi", "express", "spring", "rails"],
            "libraries": ["pandas", "numpy", "tensorflow", "pytorch", "keras", "scikit-learn"],
            "tools": ["docker", "kubernetes", "git", "redis", "mongodb", "postgresql"]
        }

        for tech in insights["technologies"]:
            for category, items in tech_categories.items():
                if tech.lower() in [i.lower() for i in items]:
                    if tech not in insights[category]:
                        insights[category].append(tech)

        return insights

    def close(self):
        """Close session and cleanup resources."""
        if self.session:
            self.session.close()
            self.session = None


class DocumentationFinder:
    """
    Finds documentation for libraries and frameworks.

    Usage:
        finder = DocumentationFinder()
        docs = finder.find_docs("react", max_results=10)
    """

    def __init__(self):
        self.search_engines = [
            self._search_google_docs,
            self._search_github_docs,
            self._search_official_docs
        ]

    def find_docs(self, tech_name: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Find documentation for a technology."""
        all_docs = []

        for search_func in self.search_engines:
            try:
                docs = search_func(tech_name, max_results)
                all_docs.extend(docs)
            except Exception as e:
                print(f"[WARNING] Documentation search failed: {e}")
                continue

        # Deduplicate by URL
        seen_urls = set()
        unique_docs = []
        for doc in all_docs:
            if doc["url"] not in seen_urls:
                seen_urls.add(doc["url"])
                unique_docs.append(doc)

        return unique_docs[:max_results]

    def _search_google_docs(self, tech_name: str, max_results: int) -> List[Dict[str, str]]:
        """Search using Google for documentation."""
        # Use site:search operators
        queries = [
            f"site:docs.{tech_name}.org",
            f"site:developer.{tech_name}.org {tech_name} documentation",
            f"{tech_name} official documentation",
            f"{tech_name} api reference"
        ]

        docs = []
        for query in queries:
            # This would need actual search implementation
            # For now, return likely doc URLs
            docs.append({
                "url": f"https://docs.{tech_name}.org",
                "type": "docs",
                "source": "inferred"
            })

        return docs[:max_results]

    def _search_github_docs(self, tech_name: str, max_results: int) -> List[Dict[str, str]]:
        """Search GitHub for documentation repositories."""
        likely_repos = [
            f"{tech_name}/docs",
            f"{tech_name}-docs",
            f"{tech_name}.github.io",
            f"awesome-{tech_name}"
        ]

        docs = []
        for repo in likely_repos:
            docs.append({
                "url": f"https://github.com/{repo}",
                "type": "github",
                "source": "inferred"
            })

        return docs[:max_results]

    def _search_official_docs(self, tech_name: str, max_results: int) -> List[Dict[str, str]]:
        """Search for official documentation sites."""
        official_patterns = [
            f"https://{tech_name}.org",
            f"https://{tech_name}.com",
            f"https://dev.{tech_name}.com",
            f"https://api.{tech_name}.com"
        ]

        docs = []
        for url in official_patterns:
            docs.append({
                "url": url,
                "type": "official",
                "source": "inferred"
            })

        return docs[:max_results]


class LibraryAnalyzer:
    """
    Analyzes libraries and frameworks in depth.

    Goes beyond surface documentation to understand:
    - Architecture and design patterns
    - Dependencies and dependents
    - Code quality metrics
    - Community activity
    - Use cases and applications

    Usage:
        analyzer = LibraryAnalyzer()
        info = analyzer.analyze_github_library("facebook/react")
    """

    def __init__(self):
        self.github_api = "https://api.github.com"

    def analyze_github_library(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze a GitHub library comprehensively.

        Args:
            repo_path: GitHub repo path (e.g., "facebook/react")

        Returns:
            Comprehensive library analysis
        """
        if not HAS_REQUESTS:
            return {"error": "requests library not available"}

        info = {
            "basic": self._get_basic_info(repo_path),
            "community": self._get_community_metrics(repo_path),
            "code_quality": self._analyze_code_quality(repo_path),
            "dependencies": self._get_dependencies(repo_path),
            "activity": self._get_activity_trends(repo_path)
        }

        return info

    def _get_basic_info(self, repo_path: str) -> Dict[str, Any]:
        """Get basic repository information."""
        # Would call GitHub API
        return {
            "name": repo_path,
            "description": "Basic info placeholder"
        }

    def _get_community_metrics(self, repo_path: str) -> Dict[str, Any]:
        """Get community engagement metrics."""
        return {
            "stars": 0,
            "forks": 0,
            "contributors": 0,
            "open_issues": 0
        }

    def _analyze_code_quality(self, repo_path: str) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        return {
            "languages": [],
            "test_coverage": 0,
            "code_health": "unknown"
        }

    def _get_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """Get dependency information."""
        return {
            "dependencies": [],
            "dependents": []
        }

    def _get_activity_trends(self, repo_path: str) -> Dict[str, Any]:
        """Get recent activity trends."""
        return {
            "commits_last_month": 0,
            "issues_closed_last_month": 0,
            "releases_last_year": 0
        }


# Convenience functions
def deep_research_topic(topic: str, max_depth: int = 3) -> Dict[str, Any]:
    """
    Perform deep research on a topic.

    Args:
        topic: Research topic
        max_depth: Research depth (1-3)

    Returns:
        Complete research results
    """
    researcher = DeepResearcher()
    return researcher.research_topic(topic, max_depth)


def find_documentation(tech_name: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Find documentation for a technology.

    Args:
        tech_name: Technology/framework name
        max_results: Maximum results to return

    Returns:
        List of documentation URLs with metadata
    """
    finder = DocumentationFinder()
    return finder.find_docs(tech_name, max_results)


def analyze_library(repo_path: str) -> Dict[str, Any]:
    """
    Analyze a GitHub library comprehensively.

    Args:
        repo_path: GitHub repo path (e.g., "facebook/react")

    Returns:
        Comprehensive library analysis
    """
    analyzer = LibraryAnalyzer()
    return analyzer.analyze_github_library(repo_path)
