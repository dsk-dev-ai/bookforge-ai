"""Circuit breaker — prevents calls to failing providers."""

from __future__ import annotations

import time
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for provider calls.

    Tracks consecutive failures. When the threshold is reached, the circuit
    opens and rejects all calls. After a cooldown period, it transitions to
    half-open and allows a single probe call. If the probe succeeds, the
    circuit closes. If it fails, the circuit re-opens.
    """

    def __init__(self, threshold: int = 5, cooldown_seconds: float = 300.0) -> None:
        if threshold < 1:
            raise ValueError("Threshold must be at least 1")
        if cooldown_seconds <= 0:
            raise ValueError("Cooldown must be positive")

        self._threshold = threshold
        self._cooldown = cooldown_seconds
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._last_success_time: float | None = None

    @property
    def state(self) -> CircuitState:
        """Return the current circuit state."""
        self._check_cooldown()
        return self._state

    @property
    def failure_count(self) -> int:
        """Return the current consecutive failure count."""
        return self._failure_count

    def is_open(self) -> bool:
        """Check if the circuit is currently open.

        Returns:
            True if calls should be blocked.
        """
        self._check_cooldown()
        return self._state == CircuitState.OPEN

    def record_success(self) -> None:
        """Record a successful call.

        Resets failure count and closes the circuit if it was half-open.
        """
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_success_time = time.monotonic()

    def record_failure(self) -> None:
        """Record a failed call.

        Opens the circuit if the failure threshold is reached.
        """
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._failure_count >= self._threshold:
            self._state = CircuitState.OPEN

    def reset(self) -> None:
        """Reset the circuit breaker to initial state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._last_success_time = None

    def _check_cooldown(self) -> None:
        if self._state == CircuitState.OPEN and self._last_failure_time is not None:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self._cooldown:
                self._state = CircuitState.HALF_OPEN
