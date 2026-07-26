"""Retry policy — configurable retry with exponential backoff and jitter."""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import ParamSpec, TypeVar

from bookforge.llm.errors import (
    AuthenticationError,
    ConfigurationError,
    ProviderError,
    ProviderTimeout,
    RateLimitError,
)

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class RetryPolicy:
    """Configuration for retry behaviour.

    Attributes:
        max_retries: Maximum number of retry attempts.
        backoff_factor: Multiplier for exponential backoff (2^N).
        max_delay: Maximum delay in seconds between retries.
        jitter: Fraction of delay to randomise (±jitter * delay).
    """

    max_retries: int = 3
    backoff_factor: float = 2.0
    max_delay: float = 60.0
    jitter: float = 0.25

    def is_retryable(self, error: Exception) -> bool:
        """Determine if an error should be retried.

        Args:
            error: The exception raised by the provider.

        Returns:
            True if the error type is retryable.
        """
        if isinstance(error, (AuthenticationError, ConfigurationError)):
            return False
        if isinstance(error, ProviderTimeout):
            return True
        if isinstance(error, RateLimitError):
            return True
        if isinstance(error, ProviderError):
            return True
        return False

    def delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry.

        Args:
            attempt: The current attempt number (0-indexed).

        Returns:
            Delay in seconds with jitter applied.
        """
        backoff = min(self.max_delay, self.backoff_factor**attempt)
        jitter_amount = backoff * self.jitter
        return backoff + random.uniform(-jitter_amount, jitter_amount)


async def with_retry(
    operation: Callable[P, Awaitable[R]],
    *args: P.args,
    policy: RetryPolicy | None = None,
    **kwargs: P.kwargs,
) -> R:
    """Execute an async operation with retry and backoff.

    Args:
        operation: The async callable to execute.
        *args: Positional arguments for the operation.
        policy: Retry policy configuration. Uses defaults if None.
        **kwargs: Keyword arguments for the operation.

    Returns:
        The result of the operation.

    Raises:
        ProviderError: If all retry attempts fail.
    """
    policy = policy or RetryPolicy()
    last_error: Exception | None = None

    for attempt in range(policy.max_retries + 1):
        try:
            return await operation(*args, **kwargs)
        except Exception as exc:
            last_error = exc

            if not policy.is_retryable(exc) or attempt >= policy.max_retries:
                raise

            delay = policy.delay(attempt + 1)
            await asyncio.sleep(delay)

    raise ProviderError("All retry attempts exhausted") from last_error
