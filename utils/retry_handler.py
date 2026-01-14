#!/usr/bin/env python3
"""
Retry Handler - Exponential Backoff Decorator

Provides automatic retry logic with exponential backoff for transient errors.
This is the implementation shown in Hackathon0.md (line 673).

Usage:
    from utils.retry_handler import with_retry, TransientError

    @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    def fetch_api_data():
        # Make API call that might fail temporarily
        return requests.get("https://api.example.com/data")
"""

import time
import functools
import logging
from typing import Callable, Any, Type, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransientError(Exception):
    """
    Base exception for transient/temporary errors that should trigger retries.

    Raise this exception (or a subclass) when an operation might succeed on retry.
    Examples: Network timeouts, temporary API failures, rate limits.
    """
    pass


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1,
    max_delay: float = 60,
    exceptions: Tuple[Type[Exception], ...] = (TransientError,)
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1)
        max_delay: Maximum delay between retries in seconds (default: 60)
        exceptions: Tuple of exception types to catch and retry (default: TransientError)

    Returns:
        Decorated function that will retry on specified exceptions

    Example:
        @with_retry(max_attempts=5, base_delay=2, max_delay=120)
        def call_external_api():
            response = requests.get("https://api.example.com")
            response.raise_for_status()
            return response.json()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_attempts - 1:
                        # Last attempt failed, raise the exception
                        logger.error(
                            f"[{func.__name__}] All {max_attempts} attempts failed"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)

                    logger.warning(
                        f"[{func.__name__}] Attempt {attempt + 1}/{max_attempts} "
                        f"failed: {e}. Retrying in {delay:.1f}s..."
                    )

                    time.sleep(delay)

            # Should never reach here, but just in case
            raise TransientError(f"{func.__name__} failed after {max_attempts} attempts")

        return wrapper
    return decorator


# ==================== CONVENIENCE DECORATORS ====================

def retry_network_errors(max_attempts: int = 3):
    """
    Retry decorator specifically for network-related errors.

    Catches common network exceptions:
    - ConnectionError, TimeoutError
    - requests.exceptions.RequestException
    - urllib3.exceptions.HTTPError
    """
    network_exceptions = (
        ConnectionError,
        TimeoutError,
        TransientError
    )

    try:
        import requests.exceptions
        network_exceptions += (requests.exceptions.RequestException,)
    except ImportError:
        pass

    try:
        import urllib3.exceptions
        network_exceptions += (urllib3.exceptions.HTTPError,)
    except ImportError:
        pass

    return with_retry(
        max_attempts=max_attempts,
        base_delay=2,
        max_delay=120,
        exceptions=network_exceptions
    )


def retry_api_rate_limit(max_attempts: int = 5):
    """
    Retry decorator specifically for API rate limits.

    Uses longer delays to give the API time to reset.
    """
    return with_retry(
        max_attempts=max_attempts,
        base_delay=5,
        max_delay=300,  # 5 minutes max delay
        exceptions=(TransientError,)
    )


# ==================== CONTEXT MANAGER VERSION ====================

class RetryContext:
    """
    Context manager version of retry logic.

    Useful when you can't use a decorator (e.g., for code blocks).

    Example:
        with RetryContext(max_attempts=3, base_delay=1):
            # Code that might fail
            risky_operation()
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1,
        max_delay: float = 60,
        exceptions: Tuple[Type[Exception], ...] = (TransientError,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Not used in context manager mode
        return False

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)

            except self.exceptions as e:
                if attempt == self.max_attempts - 1:
                    raise

                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_attempts} failed. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)

        raise TransientError(f"Failed after {self.max_attempts} attempts")


# ==================== EXAMPLES ====================

if __name__ == "__main__":
    print("="*60)
    print("RETRY HANDLER - EXAMPLE USAGE")
    print("="*60)

    # Example 1: Basic retry with TransientError
    print("\n1. Basic retry with exponential backoff:")
    print("-"*40)

    attempt_count = 0

    @with_retry(max_attempts=3, base_delay=0.5, max_delay=5)
    def flaky_function():
        global attempt_count
        attempt_count += 1
        print(f"   Attempt {attempt_count}...")

        if attempt_count < 3:
            raise TransientError("Not ready yet!")

        print("   Success!")
        return "Finally worked!"

    result = flaky_function()
    print(f"   Result: {result}\n")

    # Example 2: Retry with specific exceptions
    print("2. Retry on network errors:")
    print("-"*40)

    @retry_network_errors(max_attempts=3)
    def fetch_remote_data():
        print("   Fetching data...")
        # Simulate network failure
        if attempt_count == 3:  # Already succeeded above
            return "Data fetched!"
        raise ConnectionError("Network down!")

    try:
        result = fetch_remote_data()
        print(f"   Result: {result}\n")
    except Exception as e:
        print(f"   Failed: {e}\n")

    # Example 3: Context manager version
    print("3. Using context manager:")
    print("-"*40)

    def risky_operation():
        print("   Executing risky operation...")
        return "Success!"

    with RetryContext(max_attempts=2, base_delay=0.3):
        result = risky_operation()
        print(f"   Result: {result}\n")

    print("="*60)
    print("All examples completed!")
    print("="*60)
