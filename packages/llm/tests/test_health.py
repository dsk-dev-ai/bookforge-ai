"""Tests for the health checker."""


from bookforge.llm.base import BaseProvider
from bookforge.llm.health import HealthChecker, HealthStatusCache
from bookforge.llm.models import HealthStatus


class TestHealthStatusCache:
    def test_get_missing(self) -> None:
        cache = HealthStatusCache(ttl_seconds=60)
        assert cache.get("nonexistent") is None

    def test_set_and_get(self) -> None:
        cache = HealthStatusCache(ttl_seconds=60)
        status = HealthStatus(healthy=True, provider="test")
        cache.set("test", status)
        cached = cache.get("test")
        assert cached is not None
        assert cached.healthy is True
        assert cached.provider == "test"

    def test_expired_returns_none(self) -> None:
        cache = HealthStatusCache(ttl_seconds=0)
        status = HealthStatus(healthy=True, provider="test")
        cache.set("test", status)
        assert cache.get("test") is None

    def test_invalidate(self) -> None:
        cache = HealthStatusCache(ttl_seconds=60)
        status = HealthStatus(healthy=True, provider="test")
        cache.set("test", status)
        cache.invalidate("test")
        assert cache.get("test") is None

    def test_clear(self) -> None:
        cache = HealthStatusCache(ttl_seconds=60)
        cache.set("a", HealthStatus(healthy=True, provider="a"))
        cache.set("b", HealthStatus(healthy=True, provider="b"))
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None


class TestHealthChecker:
    async def test_check_nonexistent_provider(self) -> None:
        provider = BaseProvider(name="stub")
        checker = HealthChecker(interval_seconds=9999, timeout_seconds=5)
        status = await checker.check(provider)
        assert status.healthy is False
        assert "not implemented" in (status.error or "")

    async def test_check_all_with_no_providers(self) -> None:
        checker = HealthChecker(interval_seconds=9999, timeout_seconds=5)
        results = await checker.check_all()
        assert results == {}
