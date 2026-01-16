"""
Error Recovery Module

Provides error recovery utilities for watchers and MCP servers including:
- Exponential backoff retry logic
- Graceful degradation when services are unavailable
- Retry policies with configurable limits
- Dead letter queue for failed actions
- Error classification and handling

Usage:
    from error_recovery import with_retry, ErrorCategory
"""

import time
import logging
from functools import wraps
from enum import Enum
from typing import Callable, Any, Optional
from pathlib import Path
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Classification of error types for appropriate handling."""
    TRANSIENT = "transient"
    AUTHENTICATION = "authentication"
    LOGIC = "logic"
    DATA = "data"
    SYSTEM = "system"
    CRITICAL = "critical"


class ErrorConfig:
    """Configuration for retry behavior."""

    # Default retry policies by error category
    RETRY_POLICIES = {
        ErrorCategory.TRANSIENT: {
            "max_attempts": 3,
            "base_delay": 1,
            "max_delay": 60
        },

        ErrorCategory.AUTHENTICATION: {
            "max_attempts": 3,
            "base_delay": 60,
            "max_delay": 3600  # 1 hour
        },
        ErrorCategory.LOGIC: {
            "max_attempts": 2,
            "base_delay": 5,
            "max_delay": 300
        },
        ErrorCategory.DATA: {
            "max_attempts": 1,
            "base_delay": 10,
            "max_delay": 300
        },
        ErrorCategory.SYSTEM: {
            "max_attempts": 5,
            "base_delay": 10,
            "max_delay": 600
        },
        ErrorCategory.CRITICAL: {
            "max_attempts": 1,
            "base_delay": 0,  # No retry for critical errors
            "max_delay": 0
        }
    }

    @staticmethod
    def categorize_error(error: Exception) -> tuple:
        """
        Categorize an error and determine if it's retryable.

        Returns:
            tuple: (category, retryable)
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Authentication errors
        if any(kw in error_str for kw in ["unauthorized", "403", "401", "invalid credentials", "invalid token"]):
            return (ErrorCategory.AUTHENTICATION, True)

        # Rate limiting
        if any(kw in error_str for kw in ["rate limit", "429", "quota exceeded", "too many requests"]):
            return (ErrorCategory.TRANSIENT, True)

        # Data errors
        if any(kw in error_str for kw in ["not found", "no such", "invalid data", "parse error"]):
            return (ErrorCategory.DATA, False)  # Don't retry data errors

        # Logic errors
        if any(kw in error_str for kw in ["validation error", "invalid format", "type mismatch"]):
            return (ErrorCategory.LOGIC, False)  # Needs human review

        # System errors
        if any(kw in error_str for kw in ["connection refused", "connection reset", "broken pipe", "timeout"]):
            return (ErrorCategory.SYSTEM, True)

        # Default to transient
        return (ErrorCategory.TRANSIENT, True)


def with_retry(
    max_attempts: Optional[int] = None,
    base_delay: Optional[int] = None,
    max_delay: Optional[int] = None,
    error_category: ErrorCategory = None,
    allow_retry_on: ErrorCategory = None
):
    """
    Decorator for automatic retry logic with exponential backoff.

    Usage:
        @with_retry(max_attempts=3, base_delay=1, max_delay=60)
        def function():
            # Function that may fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        """Decorator that adds retry logic to a function."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Default to TRANSIENT if no category specified
            use_category = error_category or ErrorCategory.TRANSIENT

            # Determine retry policy
            policy = ErrorConfig.RETRY_POLICIES.get(use_category, {})

            attempts = max_attempts or policy.get("max_attempts", 3)
            delay_base = base_delay or policy.get("base_delay", 1)
            delay_max = max_delay or policy.get("max_delay", 60)

            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    # Categorize the error
                    category, is_retryable = ErrorConfig.categorize_error(error)

                    # Don't retry if not retryable
                    if not is_retryable:
                        raise error

                    # If we've used all attempts, re-raise the error
                    if attempt == attempts - 1:
                        raise error

                    # Calculate exponential backoff delay
                    delay = min(delay_base * (2 ** attempt), delay_max)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {error}")
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

        return wrapper

    return decorator


def with_retry_with_logging(
    vault_path: str,
    tool_name: str,
    max_attempts: int = 3
) -> Callable:
    """
    Decorator that adds retry logic with comprehensive audit logging.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            vault = Path(vault_path)
            logs_path = vault / "Logs"
            logs_path.mkdir(parents=True, exist_ok=True)

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as error:
                    # Log the error
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "tool": tool_name,
                        "function": func.__name__,
                        "attempt": attempt + 1,
                        "total_attempts": max_attempts,
                        "error": str(error),
                        "error_type": type(error).__name__,
                        "category": ErrorConfig.categorize_error(error)[0],
                        "args": str(args) if args else "no args",
                        "kwargs": str(kwargs) if kwargs else "no kwargs"
                    }

                    # Log to daily log
                    log_file = logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"
                    try:
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write(json.dumps(log_entry) + "\n")
                    except Exception as log_error:
                        logger.error(f"Failed to write error log: {log_error}")

                    # If last attempt, re-raise
                    if attempt == max_attempts - 1:
                        raise error

        return wrapper

    return decorator


def retry_operation(
    operation: Callable,
    vault_path: str,
    tool_name: str,
    max_attempts: int = 3,
    operation_name: str = "operation"
) -> Any:
    """
    Execute an operation with retry logic and logging.

    Args:
        operation: Callable to execute
        vault_path: Path to vault
            tool_name: Name of the tool/function
        max_attempts: Maximum retry attempts
        operation_name: Name of the operation for logging

    Returns:
        Result of the operation
    """
    vault = Path(vault_path)
    logs_path = vault / "Logs"
    logs_path.mkdir(parents=True, exist_ok=True)

    for attempt in range(max_attempts):
        try:
            result = operation()

            # Log success
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "operation": operation_name,
                "attempt": attempt + 1,
                "total_attempts": max_attempts,
                "status": "success",
                "result": str(result)[:500]  # Truncate long results
            }

            log_file = logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception as log_error:
                logger.error(f"Failed to write success log: {log_error}")

            return result

        except Exception as error:
            # Log the error
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "operation": operation_name,
                "attempt": attempt + 1,
                "total_attempts": max_attempts,
                "status": "error",
                "error": str(error),
                "error_type": type(error).__name__,
                "category": ErrorConfig.categorize_error(error)[0],
            }

            log_file = logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception as log_error:
                logger.error(f"Failed to write error log: {log_error}")

            # If last attempt, re-raise
            if attempt == max_attempts - 1:
                raise error

            # Exponential backoff
            import time
            delay = min(2 ** attempt, 60)  # Max 60 seconds
            logger.warning(f"Attempt {attempt + 1} failed for {operation_name}: {error}")
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    raise RuntimeError(f"Failed after {max_attempts} attempts")


class GracefulDegradation:
    """
    Manages system behavior when components fail or are unavailable.

    Provides:
    - Fallback behaviors for failed components
    - Queueing for failed operations
    - Status reporting
    - Recovery strategies
    """

    def __init__(self, vault_path: str, component_name: str):
        self.vault_path = Path(vault)
        self.component_name = component_name
        self.degraded = False

    def set_degraded(self) -> None:
        """Set component to degraded state and log."""
        self.degraded = True
        self._log_degradation()

    def clear_degraded(self) -> None:
        """Clear degraded state and log recovery."""
        self.degraded = False
        self._log_recovery()

    def is_degraded(self) -> bool:
        """Check if component is currently in degraded state."""
        return self.degraded

    def _log_degradation(self) -> None:
        """Log degradation event to log file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": self.component_name,
            "event": "degraded",
            "status": "degraded",
            "message": f"{self.component_name} is now in degraded state"
        }

        log_file = self.vault_path / "Logs" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as error:
            logger.error(f"Failed to write degradation log: {error}")

    def _log_recovery(self) -> None:
        """Log recovery event to log file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": self.component_name,
            "event": "recovered",
            "status": "operational",
            "message": f"{self.component_name} has recovered"
        }

        log_file = self.vault_path / "Logs" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as error:
            logger.error(f"Failed to write recovery log: {error}")


class DeadLetterQueue:
    """
    Queue for failed operations that need human intervention.

    Items are queued when:
    - All retry attempts exhausted
    - Approval required but cannot proceed without human input
    - System is in degraded state
    """
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault)
        self.queue_path = self.vault_path / "Dead_Letter"
        self.queue_path.mkdir(parents=True, exist_ok=True)

    def enqueue(self, item: Dict, queue_type: str) -> None:
        """
        Add a failed operation to the dead letter queue.

        Args:
            item: The item that failed (can be error, action_request, etc.)
            queue_type: Type of queue (error, approval_required, system_failure)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{queue_type}_{timestamp}_{item.get('id', 'unknown')}.md"

        content = f"""---
type: {queue_type}
queued_at: {datetime.now().isoformat()}
queue_type: {queue_type}
status: pending
---

# Dead Letter Queue: {queue_type}

## Item Details

## Original Action
**Type:** {item.get('type', 'unknown')}

## Error
**Error:** {item.get('error', 'Unknown')}

## Context
**Action:** {item.get('action', 'No action provided')}

## Next Steps

### To Retry
1. Fix the issue
2. Move this file to `/Approved/` to retry

### To Cancel
1. Move this file to `/Rejected/`

### To Hold
1. Keep in Dead_Letter/ until issue is resolved

---

*Created by Error Recovery System*
"""

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as error:
            logger.error(f"Failed to write dead letter queue item: {error}")

