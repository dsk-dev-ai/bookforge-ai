"""Tests for the circuit breaker."""

from bookforge.llm.circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitBreaker:
    def test_initial_state_closed(self) -> None:
        cb = CircuitBreaker(threshold=5, cooldown_seconds=300)
        assert cb.state == CircuitState.CLOSED
        assert cb.is_open() is False

    def test_opens_after_threshold_failures(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown_seconds=300)
        cb.record_failure()
        assert cb.is_open() is False
        cb.record_failure()
        assert cb.is_open() is False
        cb.record_failure()
        assert cb.is_open() is True
        assert cb.state == CircuitState.OPEN

    def test_success_resets_failure_count(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown_seconds=300)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.is_open() is False

    def test_reset(self) -> None:
        cb = CircuitBreaker(threshold=2, cooldown_seconds=300)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open() is True
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.is_open() is False

    def test_threshold_must_be_positive(self) -> None:
        try:
            CircuitBreaker(threshold=0)
            assert False
        except ValueError:
            pass

    def test_cooldown_must_be_positive(self) -> None:
        try:
            CircuitBreaker(cooldown_seconds=0)
            assert False
        except ValueError:
            pass
