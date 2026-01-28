"""
Centralized Configuration Management for Research LinkedIn Generator

Provides:
- Single source of truth for all configuration
- Environment variable support
- Configuration validation
- Default values

Usage:
    from research_config import ResearchConfig, get_config

    # Get default config
    config = get_config()

    # Create custom config
    config = ResearchConfig(
        vault_path="Custom_Vault",
        cache_ttl_hours=12,
        max_sources=15
    )
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class ResearchDepth(Enum):
    """Research depth levels."""
    SURFACE = 1      # Articles only
    DOCUMENTATION = 2 # Articles + Documentation
    DEEP = 3         # Articles + Documentation + Libraries


class PostTone(Enum):
    """LinkedIn post tone options."""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    enabled: bool = True
    ttl_hours: int = 24
    max_size_mb: int = 500
    cache_dir: str = ".cache/research"

    def validate(self) -> None:
        """Validate cache configuration."""
        if self.ttl_hours < 0:
            raise ValueError("Cache TTL must be non-negative")
        if self.max_size_mb < 0:
            raise ValueError("Cache max size must be non-negative")


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 30
    requests_per_hour: int = 500
    enabled: bool = True

    def validate(self) -> None:
        """Validate rate limit configuration."""
        if self.requests_per_minute < 1:
            raise ValueError("Requests per minute must be at least 1")
        if self.requests_per_hour < 1:
            raise ValueError("Requests per hour must be at least 1")
        if self.requests_per_minute > self.requests_per_hour:
            raise ValueError("Requests per minute cannot exceed requests per hour")


@dataclass
class ResearchConfig:
    """Main research configuration."""

    # Vault settings
    vault_path: str = "AI_Employee_Vault"

    # Research settings
    max_sources: int = 10
    min_content_length: int = 500
    max_content_length: int = 50000
    default_depth: int = 2

    # Deep research settings
    enable_deep_research: bool = True
    enable_github_api: bool = True
    enable_package_analysis: bool = True

    # Post generation settings
    post_min_chars: int = 1000
    post_max_chars: int = 2000
    post_min_hashtags: int = 5
    post_max_hashtags: int = 10
    post_max_emojis: int = 2
    post_tone: str = PostTone.PROFESSIONAL.value

    # API settings
    glm_api_key: Optional[str] = None
    glm_model: str = "glm-4"
    glm_temperature: float = 0.7

    # Cache configuration
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Rate limit configuration
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)

    # URL filtering
    skip_domains: List[str] = field(default_factory=lambda: [
        "ads.*",
        "*.sponsored",
        "*.facebook.com",
        "*.twitter.com",
        "*.instagram.com",
        "*.youtube.com",
        "*.google.com/search*"
    ])

    preferred_domains: List[str] = field(default_factory=lambda: [
        "medium.com",
        "dev.to",
        "towardsdatascience.com",
        "anthropic.com",
        "github.com",
        "stackoverflow.com"
    ])

    def __post_init__(self):
        """Initialize after dataclass creation."""
        # Load API key from environment if not provided
        if self.glm_api_key is None:
            self.glm_api_key = os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY")

        # Ensure cache and rate_limits are proper dataclass instances
        if isinstance(self.cache, dict):
            self.cache = CacheConfig(**self.cache)
        if isinstance(self.rate_limits, dict):
            self.rate_limits = RateLimitConfig(**self.rate_limits)

    def validate(self) -> None:
        """Validate all configuration settings."""
        if self.max_sources < 1:
            raise ValueError("max_sources must be at least 1")
        if self.min_content_length < 0:
            raise ValueError("min_content_length must be non-negative")
        if self.max_content_length < self.min_content_length:
            raise ValueError("max_content_length must be >= min_content_length")
        if self.default_depth not in [1, 2, 3]:
            raise ValueError("default_depth must be 1, 2, or 3")
        if self.post_min_chars < 1:
            raise ValueError("post_min_chars must be at least 1")
        if self.post_max_chars < self.post_min_chars:
            raise ValueError("post_max_chars must be >= post_min_chars")

        # Validate nested configs
        self.cache.validate()
        self.rate_limits.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = asdict(self)
        # Convert enums to values
        if isinstance(data.get('post_tone'), str):
            data['post_tone'] = self.post_tone
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchConfig":
        """Create configuration from dictionary."""
        # Handle nested configs
        if 'cache' in data and isinstance(data['cache'], dict):
            data['cache'] = CacheConfig(**data['cache'])
        if 'rate_limits' in data and isinstance(data['rate_limits'], dict):
            data['rate_limits'] = RateLimitConfig(**data['rate_limits'])
        return cls(**data)

    @classmethod
    def from_file(cls, path: str | Path) -> "ResearchConfig":
        """Load configuration from JSON file."""
        config_path = Path(path)
        if not config_path.exists():
            # Return default config if file doesn't exist
            return cls()

        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def save(self, path: str | Path) -> None:
        """Save configuration to JSON file."""
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def get_cache_dir(self) -> Path:
        """Get the full cache directory path."""
        vault = Path(self.vault_path)
        return vault / self.cache.cache_dir

    def get_logs_dir(self) -> Path:
        """Get the logs directory path."""
        vault = Path(self.vault_path)
        return vault / "Logs"

    def get_plans_dir(self) -> Path:
        """Get the plans directory path."""
        vault = Path(self.vault_path)
        return vault / "Plans"

    def get_pending_dir(self) -> Path:
        """Get the pending approval directory path."""
        vault = Path(self.vault_path)
        return vault / "Pending_Approval"


# Global configuration instance
_global_config: Optional[ResearchConfig] = None


def get_config(vault_path: Optional[str] = None) -> ResearchConfig:
    """
    Get the global configuration instance.

    Args:
        vault_path: Optional vault path override

    Returns:
        ResearchConfig instance
    """
    global _global_config

    if _global_config is None:
        # Try to load from vault
        vault = Path(vault_path or "AI_Employee_Vault")
        config_file = vault / ".research_config.json"

        if config_file.exists():
            _global_config = ResearchConfig.from_file(config_file)
        else:
            _global_config = ResearchConfig()

        # Override vault_path if specified
        if vault_path:
            _global_config.vault_path = vault_path

    return _global_config


def set_config(config: ResearchConfig) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset to default configuration."""
    global _global_config
    _global_config = None


# Predefined configurations for common use cases
def get_default_config() -> ResearchConfig:
    """Get default configuration."""
    return ResearchConfig()


def get_fast_config() -> ResearchConfig:
    """Get configuration for quick research (less thorough, faster)."""
    return ResearchConfig(
        max_sources=5,
        min_content_length=300,
        default_depth=1,
        enable_deep_research=False,
        cache_ttl_hours=48,  # Longer cache
        post_min_chars=800,
        post_max_chars=1500
    )


def get_deep_config() -> ResearchConfig:
    """Get configuration for deep research (more thorough, slower)."""
    return ResearchConfig(
        max_sources=15,
        min_content_length=800,
        default_depth=3,
        enable_deep_research=True,
        enable_github_api=True,
        enable_package_analysis=True,
        cache=CacheConfig(ttl_hours=12),  # Shorter cache for fresh data
        post_min_chars=1500,
        post_max_chars=2500
    )


def get_testing_config() -> ResearchConfig:
    """Get configuration for testing (minimal resources)."""
    return ResearchConfig(
        max_sources=3,
        min_content_length=100,
        default_depth=1,
        enable_deep_research=False,
        cache=CacheConfig(enabled=False),
        rate_limits=RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=50,
            enabled=False
        )
    )


# Configuration validation helper
def validate_config(config: ResearchConfig) -> List[str]:
    """
    Validate configuration and return list of errors.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    try:
        config.validate()
    except ValueError as e:
        errors.append(str(e))

    # Check for API key if needed
    if config.enable_github_api and not config.glm_api_key:
        errors.append("GLM API key required when GitHub API is enabled")

    # Check vault path exists
    vault_path = Path(config.vault_path)
    if not vault_path.exists():
        errors.append(f"Vault path does not exist: {config.vault_path}")

    return errors


# Convenience functions for common operations
def get_cache_manager(config: Optional[ResearchConfig] = None):
    """Get cache manager instance with current config."""
    if config is None:
        config = get_config()

    from research_performance import ResearchCacheManager
    return ResearchCacheManager(
        vault_path=config.vault_path,
        ttl_hours=config.cache.ttl_hours
    )


def get_rate_limiter(config: Optional[ResearchConfig] = None):
    """Get rate limiter instance with current config."""
    if config is None:
        config = get_config()

    from research_performance import ResearchRateLimiter
    return ResearchRateLimiter(
        requests_per_minute=config.rate_limits.requests_per_minute,
        requests_per_hour=config.rate_limits.requests_per_hour
    )
