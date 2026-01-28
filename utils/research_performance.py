"""
Performance and Error Recovery Module for Research LinkedIn Generator

Provides caching, rate limiting, and performance optimizations.
"""

from __future__ import annotations

import json
import time
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Callable
from functools import wraps, lru_cache
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Represents a cached entry."""
    data: Any
    timestamp: datetime
    ttl_seconds: int


class ResearchCacheManager:
    """
    Cache manager for research data.

    Usage:
        cache = ResearchCacheManager(vault_path="AI_Employee_Vault")

        # Cache research results
        cache.set("research", "topic_key", research_data)

        # Get cached data
        data = cache.get("research", "topic_key")
    """

    def __init__(self, vault_path: str | Path = "AI_Employee_Vault", ttl_hours: int = 24):
        """
        Initialize cache manager.

        Args:
            vault_path: Path to vault for cache storage
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.vault_path = Path(vault_path)
        self.cache_dir = self.vault_path / ".cache" / "research"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600

    def _get_cache_path(self, category: str, key: str) -> Path:
        """Get cache file path."""
        safe_key = hashlib.md5(f"{category}:{key}".encode()).hexdigest()
        return self.cache_dir / f"{category}_{safe_key}.json"

    def set(self, category: str, key: str, data: Any) -> None:
        """
        Store data in cache.

        Args:
            category: Cache category (e.g., "research", "articles", "analysis")
            key: Unique key for this entry
            data: Data to cache (must be JSON-serializable)
        """
        cache_path = self._get_cache_path(category, key)

        cache_entry = {
            "cached_at": datetime.now().isoformat(),
            "category": category,
            "key": key,
            "data": data
        }

        cache_path.write_text(json.dumps(cache_entry, indent=2), encoding="utf-8")

    def get(self, category: str, key: str) -> Optional[Any]:
        """
        Retrieve cached data if valid.

        Args:
            category: Cache category
            key: Unique key for this entry

        Returns:
            Cached data if valid and exists, None otherwise
        """
        cache_path = self._get_cache_path(category, key)

        if not cache_path.exists():
            return None

        try:
            cache_data = json.loads(cache_path.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(cache_data.get("cached_at", ""))

            # Check if still valid
            age = (datetime.now() - cached_at).total_seconds()
            if age < cache_data.get("ttl_seconds", self.ttl_seconds):
                return cache_data.get("data")

            # Expired - delete cache file
            cache_path.unlink()

        except (json.JSONDecodeError, ValueError, OSError):
            # Invalid cache file - delete it
            if cache_path.exists():
                cache_path.unlink()

        return None

    def clear_category(self, category: str) -> int:
        """Clear all cache in a category."""
        cleared = 0
        pattern = f"{category}_*.json"
        for cache_file in self.cache_dir.glob(pattern):
            try:
                cache_file.unlink()
                cleared += 1
            except OSError:
                pass
        return cleared

    def clear_all(self) -> int:
        """Clear all cached data."""
        return self.clear_category("*")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))

        total_size = sum(f.stat().st_size for f in cache_files) if cache_files else 0

        by_category = {}
        for cache_file in cache_files:
            category = cache_file.stem.split("_")[0]
            by_category[category] = by_category.get(category, 0) + 1

        return {
            "total_entries": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "by_category": by_category
        }


class ResearchRateLimiter:
    """
    Rate limiter for external API calls.

    Usage:
        limiter = ResearchRateLimiter(requests_per_minute=30)

        if limiter.can_proceed():
            limiter.record_request()
            # Make API call
        else:
            limiter.wait_until_allowed()
    """

    def __init__(
        self,
        requests_per_minute: int = 30,
        requests_per_hour: int = 500
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        self.minute_window = 60  # seconds
        self.hour_window = 3600  # seconds

        self.minute_requests = []
        self.hour_requests = []

    def _clean_old_requests(self, now: float) -> None:
        """Remove requests outside the time windows."""
        cutoff_minute = now - self.minute_window
        cutoff_hour = now - self.hour_window

        self.minute_requests = [t for t in self.minute_requests if t > cutoff_minute]
        self.hour_requests = [t for t in self.hour_requests if t > cutoff_hour]

    def can_proceed(self) -> bool:
        """Check if a request can be made without violating limits."""
        now = time.time()
        self._clean_old_requests(now)

        minute_count = len(self.minute_requests)
        hour_count = len(self.hour_requests)

        return minute_count < self.requests_per_minute and hour_count < self.requests_per_hour

    def record_request(self) -> None:
        """Record that a request was made."""
        now = time.time()
        self.minute_requests.append(now)
        self.hour_requests.append(now)

    def wait_until_allowed(self, timeout: int = 60) -> bool:
        """
        Wait until a request can be made.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if allowed within timeout, False if timeout exceeded
        """
        start = time.time()

        while not self.can_proceed():
            if time.time() - start > timeout:
                return False

            if self.minute_requests:
                oldest_minute = min(self.minute_requests)
                wait_time = (oldest_minute + self.minute_window) - time.time() + 1
                wait_time = max(0.1, min(wait_time, 5))
                time.sleep(wait_time)
            else:
                time.sleep(1)

        return True

    def get_wait_time(self) -> float:
        """Get seconds to wait before next allowed request."""
        if self.can_proceed():
            return 0.0

        now = time.time()
        self._clean_old_requests(now)

        if self.minute_requests:
            oldest = min(self.minute_requests)
            minute_wait = (oldest + self.minute_window) - now + 1
        else:
            minute_wait = 0

        if self.hour_requests:
            oldest = min(self.hour_requests)
            hour_wait = (oldest + self.hour_window) - now + 1
        else:
            hour_wait = 0

        return max(minute_wait, hour_wait, 0.1)

    def reset(self) -> None:
        """Reset rate limiter (for testing)."""
        self.minute_requests = []
        self.hour_requests = []


def research_cache(ttl_seconds: int = 3600):
    """
    Decorator for caching research results.

    Usage:
        @research_cache(ttl_seconds=1800)
        def expensive_research(topic: str) -> Dict:
            return {"results": "..."}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"

            # Try to get from cache
            cache_mgr = ResearchCacheManager()  # Uses default vault path
            cached = cache_mgr.get("research", key)

            if cached is not None:
                return cached["data"]

            # Not in cache, compute and store
            result = func(*args, **kwargs)

            cache_mgr.set("research", key, {
                "result": result,
                "cached_at": datetime.now().isoformat()
            })

            return result

        wrapper.cache_clear = lambda: ResearchCacheManager().clear_category("research")
        return wrapper

    return decorator


class ResearchPerformanceMonitor:
    """
    Monitor and report on research performance metrics.

    Usage:
        monitor = ResearchPerformanceMonitor(vault_path="AI_Employee_Vault")

        with monitor.track_operation("content_extraction"):
            result = extractor.extract_content(url)
    """

    def __init__(self, vault_path: str | Path = "AI_Employee_Vault"):
        """Initialize performance monitor."""
        self.vault_path = Path(vault_path)
        self.stats_file = self.vault_path / ".performance_stats.json"

    def _load_stats(self) -> Dict:
        """Load existing stats from file."""
        if self.stats_file.exists():
            try:
                return json.loads(self.stats_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError, OSError):
                pass
        return {
            "operations": {},
            "last_updated": None
        }

    def _save_stats(self, stats: Dict) -> None:
        """Save stats to file."""
        stats["last_updated"] = datetime.now().isoformat()
        self.stats_file.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    def track_operation(self, operation_name: str):
        """
        Context manager for tracking an operation.

        Usage:
            with monitor.track_operation("extract_content"):
                result = extractor.extract_content(url)
        """
        class OperationTracker:
            def __init__(self, operation_name, monitor):
                self.operation_name = operation_name
                self.monitor = monitor
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:  # Success
                    duration = time.time() - self.start_time
                    stats = self._load_stats()

                    if operation_name not in stats["operations"]:
                        stats["operations"][operation_name] = {
                            "count": 0,
                            "total_time": 0,
                            "avg_time": 0
                        }

                    op_stats = stats["operations"][operation_name]
                    op_stats["count"] += 1
                    op_stats["total_time"] += duration
                    op_stats["avg_time"] = op_stats["total_time"] / op_stats["count"]

                    self._save_stats(stats)

                return False  # Don't suppress exceptions

        return OperationTracker(operation_name, self)

    def get_stats(self) -> Dict:
        """Get current performance statistics."""
        stats = self._load_stats()

        total_operations = sum(
            op.get("count", 0)
            for op in stats.get("operations", {}).values()
        )

        total_time = sum(
            op.get("total_time", 0)
            for op in stats.get("operations", {}).values()
        )

        stats["summary"] = {
            "total_operations": total_operations,
            "total_time": round(total_time, 2),
            "avg_time_per_operation": round(total_time / total_operations, 3) if total_operations > 0 else 0
        }

        return stats

    def get_slowest_operations(self, limit: int = 5) -> List[Dict]:
        """Get the slowest operations by average time."""
        stats = self._load_stats()

        operations = []
        for op_name, op_stats in stats.get("operations", {}).items():
            if op_stats.get("count", 0) > 0:
                operations.append({
                    "operation": op_name,
                    "avg_time": op_stats.get("avg_time", 0),
                    "count": op_stats.get("count", 0),
                    "total_time": op_stats.get("total_time", 0)
                })

        operations.sort(key=lambda x: x["avg_time"], reverse=True)
        return operations[:limit]


# Convenience functions
def get_research_cache_manager(vault_path: str = "AI_Employee_Vault") -> ResearchCacheManager:
    """Get or create cache manager instance."""
    return ResearchCacheManager(vault_path=vault_path)


def get_research_rate_limiter(
    requests_per_minute: int = 30,
    requests_per_hour: int = 500
) -> ResearchRateLimiter:
    """Get rate limiter instance with specified limits."""
    return ResearchRateLimiter(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour
    )


def get_research_performance_monitor(vault_path: str = "AI_Employee_Vault") -> ResearchPerformanceMonitor:
    """Get or create performance monitor instance."""
    return ResearchPerformanceMonitor(vault_path=vault_path)
