"""Logging interface for provider operations."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timezone
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from bookforge.llm.errors import ProviderError

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("bookforge.llm")


def get_logger(name: str) -> logging.Logger:
    """Return a logger for a submodule within the llm package.

    Args:
        name: The submodule name, typically ``__name__``.

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(f"bookforge.llm.{name}")


def log_provider_call(
    level: int = logging.DEBUG,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that logs provider method calls with timing.

    Args:
        level: The log level for successful calls.

    Returns:
        A decorator that wraps an async function with logging.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = datetime.now(timezone.utc)
            func_name = func.__qualname__

            try:
                result = await func(*args, **kwargs)  # type: ignore
                elapsed = (datetime.now(timezone.utc) - start).total_seconds()
                logger.log(level, "%s succeeded in %.3fs", func_name, elapsed)
                return result
            except ProviderError:
                elapsed = (datetime.now(timezone.utc) - start).total_seconds()
                logger.warning("%s failed after %.3fs", func_name, elapsed)
                raise

        return wrapper

    return decorator


def build_log_context(
    provider_name: str,
    operation: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a structured log context dict.

    Args:
        provider_name: The provider name.
        operation: The operation being performed.
        extra: Additional context key-value pairs.

    Returns:
        A dict suitable for structured logging.
    """
    context: dict[str, Any] = {
        "subsystem": "provider_manager",
        "provider": provider_name,
        "operation": operation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        context.update(extra)
    return context
