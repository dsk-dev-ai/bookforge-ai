"""Tests for the retry policy."""

import pytest

from bookforge.llm.errors import (
    AuthenticationError,
    ConfigurationError,
    ProviderError,
    ProviderTimeout,
    RateLimitError,
)
from bookforge.llm.retry import RetryPolicy, with_retry


class TestRetryPolicy:
    def test_default_max_retries(self) -> None:
        policy = RetryPolicy()
        assert policy.max_retries == 3

    def test_retryable_errors(self) -> None:
        policy = RetryPolicy()
        assert policy.is_retryable(ProviderTimeout("test", 30))
        assert policy.is_retryable(RateLimitError("test"))
        assert policy.is_retryable(ProviderError("generic"))

    def test_non_retryable_errors(self) -> None:
        policy = RetryPolicy()
        assert not policy.is_retryable(AuthenticationError("test"))
        assert not policy.is_retryable(ConfigurationError("bad config"))

    def test_delay_increases_with_attempts(self) -> None:
        policy = RetryPolicy(backoff_factor=2.0, max_delay=60.0, jitter=0)
        d1 = policy.delay(1)
        d2 = policy.delay(2)
        d3 = policy.delay(3)
        assert d2 > d1
        assert d3 >= d2

    def test_delay_capped_at_max(self) -> None:
        policy = RetryPolicy(backoff_factor=100.0, max_delay=10.0, jitter=0)
        delay = policy.delay(10)
        assert delay <= 10.0


class TestWithRetry:
    async def test_succeeds_first_try(self) -> None:
        call_count = 0

        async def operation() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await with_retry(operation, policy=RetryPolicy(max_retries=3))
        assert result == "ok"
        assert call_count == 1

    async def test_retries_on_failure_then_succeeds(self) -> None:
        call_count = 0

        async def operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ProviderTimeout("test", 30)
            return "ok"

        result = await with_retry(operation, policy=RetryPolicy(max_retries=3, jitter=0))
        assert result == "ok"
        assert call_count == 3

    async def test_exhausts_retries_and_raises(self) -> None:
        call_count = 0

        async def operation() -> str:
            nonlocal call_count
            call_count += 1
            raise ProviderTimeout("test", 30)

        with pytest.raises(ProviderError):
            await with_retry(operation, policy=RetryPolicy(max_retries=2, jitter=0))
        assert call_count == 3  # initial + 2 retries

    async def test_non_retryable_error_immediately_raises(self) -> None:
        call_count = 0

        async def operation() -> str:
            nonlocal call_count
            call_count += 1
            raise AuthenticationError("test")

        with pytest.raises(AuthenticationError):
            await with_retry(operation, policy=RetryPolicy(max_retries=3))
        assert call_count == 1
