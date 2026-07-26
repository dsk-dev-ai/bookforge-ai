"""Tests for the token bucket rate limiter."""

import pytest

from bookforge.llm.rate_limiter import TokenBucketRateLimiter


class TestTokenBucketRateLimiter:
    async def test_initial_capacity_allows_burst(self) -> None:
        limiter = TokenBucketRateLimiter(capacity=5, window_seconds=60)
        for _ in range(5):
            wait = await limiter.acquire()
            assert wait == 0.0

    async def test_exceeding_capacity_requires_wait(self) -> None:
        limiter = TokenBucketRateLimiter(capacity=2, window_seconds=0.1)
        await limiter.acquire()
        await limiter.acquire()
        wait = await limiter.acquire()
        assert wait > 0.0

    def test_invalid_capacity_raises(self) -> None:
        with pytest.raises(ValueError, match="at least 1"):
            TokenBucketRateLimiter(capacity=0)

    def test_invalid_window_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            TokenBucketRateLimiter(capacity=1, window_seconds=0)

    def test_reset(self) -> None:
        limiter = TokenBucketRateLimiter(capacity=3, window_seconds=60)
        limiter._tokens = 0.0
        limiter.reset()
        assert limiter._tokens == 3.0
