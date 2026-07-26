"""Health checker — periodically probes provider health."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from bookforge.llm.errors import ProviderError
from bookforge.llm.interfaces import LLMProvider
from bookforge.llm.models import HealthStatus

logger = logging.getLogger(__name__)


class HealthStatusCache:
    """Thread-safe cache for provider health check results.

    Caches the most recent health status per provider with a configurable TTL.
    """

    def __init__(self, ttl_seconds: float = 60.0) -> None:
        self._ttl = timedelta(seconds=ttl_seconds)
        self._cache: dict[str, tuple[HealthStatus, datetime]] = {}

    def get(self, provider_name: str) -> HealthStatus | None:
        """Return cached health status if still fresh.

        Args:
            provider_name: The provider name.

        Returns:
            The cached HealthStatus, or None if not cached or expired.
        """
        entry = self._cache.get(provider_name)
        if entry is None:
            return None
        status, cached_at = entry
        if datetime.now(timezone.utc) - cached_at > self._ttl:
            del self._cache[provider_name]
            return None
        return status

    def set(self, provider_name: str, status: HealthStatus) -> None:
        """Cache a health status.

        Args:
            provider_name: The provider name.
            status: The health status to cache.
        """
        self._cache[provider_name] = (status, datetime.now(timezone.utc))

    def invalidate(self, provider_name: str) -> None:
        """Remove a provider's cached status.

        Args:
            provider_name: The provider name.
        """
        self._cache.pop(provider_name, None)

    def clear(self) -> None:
        """Clear all cached health statuses."""
        self._cache.clear()


class HealthChecker:
    """Periodically checks health of registered providers.

    Runs health checks in the background at a configurable interval.
    Results are cached and available via ``get_health()``.
    """

    def __init__(
        self,
        interval_seconds: float = 60.0,
        timeout_seconds: float = 10.0,
        cache_ttl_seconds: float = 60.0,
    ) -> None:
        self._interval = interval_seconds
        self._timeout = timeout_seconds
        self._cache = HealthStatusCache(cache_ttl_seconds)
        self._providers: list[LLMProvider] = []
        self._task: asyncio.Task[None] | None = None

    def set_providers(self, providers: list[LLMProvider]) -> None:
        """Set the list of providers to monitor.

        Args:
            providers: Providers to health check.
        """
        self._providers = list(providers)

    async def check(self, provider: LLMProvider) -> HealthStatus:
        """Check a single provider's health.

        Args:
            provider: The provider to check.

        Returns:
            The health status result.
        """
        try:
            status = await asyncio.wait_for(
                provider.health(),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            status = HealthStatus(
                healthy=False,
                provider=provider.name,
                error=f"Health check timed out after {self._timeout}s",
            )
        except ProviderError as exc:
            status = HealthStatus(
                healthy=False,
                provider=provider.name,
                error=str(exc),
            )
        self._cache.set(provider.name, status)
        return status

    async def check_all(self) -> dict[str, HealthStatus]:
        """Check health of all registered providers.

        Returns:
            A dict mapping provider name to health status.
        """
        results: dict[str, HealthStatus] = {}
        for provider in self._providers:
            results[provider.name] = await self.check(provider)
        return results

    def get_health(self, provider_name: str) -> HealthStatus | None:
        """Return cached health status for a provider.

        Args:
            provider_name: The provider name.

        Returns:
            Cached health status, or None if not checked yet.
        """
        return self._cache.get(provider_name)

    def is_healthy(self, provider_name: str) -> bool:
        """Check cached health status for a provider.

        Args:
            provider_name: The provider name.

        Returns:
            True if the provider is cached and healthy.
        """
        status = self._cache.get(provider_name)
        return status is not None and status.healthy

    async def start_periodic(self) -> None:
        """Start periodic health checks in the background.

        Runs until ``stop_periodic()`` is called.
        """
        if self._task is not None:
            return

        async def _run() -> None:
            while True:
                try:
                    await self.check_all()
                except Exception:
                    logger.exception("Periodic health check failed")
                await asyncio.sleep(self._interval)

        self._task = asyncio.create_task(_run())

    async def stop_periodic(self) -> None:
        """Stop periodic health checks."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
