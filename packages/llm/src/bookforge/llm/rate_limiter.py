"""Rate limiter interface and token bucket implementation."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod


class RateLimiter(ABC):
    """Abstract interface for rate limiting strategies."""

    @abstractmethod
    async def acquire(self) -> float:
        """Block until a request is allowed and return the wait time.

        Returns:
            The time in seconds the caller waited.
        """

    @abstractmethod
    def reset(self) -> None:
        """Reset the rate limiter state."""


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter.

    Allows up to ``capacity`` tokens per ``window_seconds`` window.
    Tokens refill continuously at ``capacity / window_seconds`` per second.
    """

    def __init__(self, capacity: int, window_seconds: float = 60.0) -> None:
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        if window_seconds <= 0:
            raise ValueError("Window must be positive")

        self._capacity = float(capacity)
        self._window = window_seconds
        self._refill_rate = self._capacity / self._window
        self._tokens = self._capacity
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    async def acquire(self) -> float:
        """Block until a token is available.

        Returns:
            The time in seconds the caller waited.
        """
        start = time.monotonic()

        async with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return 0.0

            wait_time = (1.0 - self._tokens) / self._refill_rate

        await asyncio.sleep(wait_time)

        async with self._lock:
            self._refill()
            self._tokens -= 1.0

        return time.monotonic() - start

    def reset(self) -> None:
        """Reset the bucket to full capacity."""
        self._tokens = self._capacity
        self._last_refill = time.monotonic()
