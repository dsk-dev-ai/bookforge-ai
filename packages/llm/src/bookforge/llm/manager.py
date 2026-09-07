"""Provider manager — the facade for all provider interactions."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any, cast

from bookforge.llm.config_loader import ConfigLoader, RuntimeConfig
from bookforge.llm.errors import ProviderError, ProviderUnavailable
from bookforge.llm.health import HealthChecker, HealthStatus
from bookforge.llm.interfaces import Capability, LLMProvider
from bookforge.llm.models import (
    ChatConfig,
    ChatResponse,
    Chunk,
    Embedding,
    EmbeddingConfig,
    Message,
)
from bookforge.llm.rate_limiter import RateLimiter, TokenBucketRateLimiter
from bookforge.llm.registry import ProviderRegistry
from bookforge.llm.retry import RetryPolicy, with_retry
from bookforge.llm.router import ModelRouter, RouteResult, RoutingRule

logger = logging.getLogger(__name__)


class ProviderManager:
    """Central facade for all LLM provider interactions.

    Coordinates:
    - Provider lifecycle (registration, health monitoring)
    - Request routing (primary → fallback → error)
    - Circuit breaking (open after N consecutive failures)
    - Rate limiting (token bucket per provider)
    - Retry with exponential backoff

    Usage::

        manager = ProviderManager()
        await manager.register_providers(config)
        response = await manager.chat(messages)
    """

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self._registry = ProviderRegistry()
        self._config = config

        self._health = HealthChecker(
            interval_seconds=config.health_check_interval_seconds if config else 60.0,
            timeout_seconds=config.health_check_timeout_seconds if config else 10.0,
        )
        self._routing_rules = [
            RoutingRule(capability=Capability.CHAT, primary=config.provider, fallback=config.fallback_provider) if config else
            RoutingRule(capability=Capability.CHAT, primary="nvidia", fallback="ollama"),
            RoutingRule(capability=Capability.CHAT_STREAM, primary=config.provider, fallback=config.fallback_provider) if config else
            RoutingRule(capability=Capability.CHAT_STREAM, primary="nvidia", fallback="ollama"),
            RoutingRule(capability=Capability.EMBED, primary=config.provider, fallback=config.fallback_provider) if config else
            RoutingRule(capability=Capability.EMBED, primary="nvidia", fallback="ollama"),
            RoutingRule(capability=Capability.EMBED_STREAM, primary=config.provider, fallback=config.fallback_provider) if config else
            RoutingRule(capability=Capability.EMBED_STREAM, primary="nvidia", fallback="ollama"),
        ]
        self._router = ModelRouter(
            registry=self._registry,
            health=self._health,
            rules=self._routing_rules,
        )
        self._retry_policy = RetryPolicy(
            max_retries=config.max_retries if config else 3,
            backoff_factor=config.retry_backoff_factor if config else 2.0,
            max_delay=config.retry_max_delay if config else 60.0,
            jitter=config.retry_jitter if config else 0.25,
        )
        self._rate_limiters: dict[str, RateLimiter] = {}
        self._fallback_enabled = config.fallback_enabled if config else True
        self._started = False

    @classmethod
    def from_env(cls) -> ProviderManager:
        """Create a ProviderManager configured from environment variables.

        Returns:
            A fully configured ProviderManager instance.
        """
        config = ConfigLoader().load()
        return cls(config=config)

    @property
    def registry(self) -> ProviderRegistry:
        """Return the underlying provider registry."""
        return self._registry

    @property
    def health(self) -> HealthChecker:
        """Return the health checker."""
        return self._health

    def register_provider(self, provider: LLMProvider) -> None:
        """Register a single provider.

        Args:
            provider: The provider instance to register.
        """
        self._registry.register(provider)
        self._rate_limiters[provider.name] = TokenBucketRateLimiter(
            capacity=self._config.rate_limit_requests_per_minute if self._config else 60,
        )
        logger.info("Registered provider: %s", provider.name)

    async def start(self) -> None:
        """Start periodic health checks and prepare the manager.

        Call once after registering all providers.
        """
        self._health.set_providers(self._registry.providers())
        if not self._started:
            await self._health.start_periodic()
            self._started = True
            logger.info("ProviderManager started with providers: %s", self._registry.list_names())

    async def stop(self) -> None:
        """Gracefully stop the manager and its background tasks."""
        await self._health.stop_periodic()
        self._started = False
        logger.info("ProviderManager stopped")

    async def chat(self, messages: list[Message], config: ChatConfig | None = None) -> ChatResponse:
        """Send a chat request through the routed provider.

        Applies rate limiting, circuit breaking, retry, and fallback.

        Args:
            messages: The conversation messages.
            config: Optional chat configuration.

        Returns:
            The chat response.

        Raises:
            ProviderUnavailable: If no provider is available.
        """
        route = await self._router.route(Capability.CHAT)
        result = await self._execute_with_guards(route, "chat", messages, config)
        return cast(ChatResponse, result)

    def chat_stream(
        self,
        messages: list[Message],
        config: ChatConfig | None = None,
    ) -> AsyncIterator[Chunk]:
        """Stream a chat response through the routed provider."""
        raise NotImplementedError("Streaming support requires async generator orchestration")

    async def embed(self, texts: list[str], config: EmbeddingConfig | None = None) -> list[Embedding]:
        """Generate embeddings through the routed provider.

        Args:
            texts: The texts to embed.
            config: Optional embedding configuration.

        Returns:
            The embedding vectors.

        Raises:
            ProviderUnavailable: If no provider is available.
        """
        route = await self._router.route(Capability.EMBED)
        result = await self._execute_with_guards(route, "embed", texts, config)
        return cast(list[Embedding], result)

    async def get_provider_health(self, provider_name: str) -> HealthStatus | None:
        """Return cached health for a specific provider.

        Args:
            provider_name: The provider name.

        Returns:
            Health status or None if not yet checked.
        """
        return self._health.get_health(provider_name)

    async def get_all_provider_health(self) -> dict[str, HealthStatus | None]:
        """Return cached health for all registered providers.

        Returns:
            Dict mapping provider name to health status.
        """
        return {name: self._health.get_health(name) for name in self._registry.list_names()}

    async def _enforce_rate_limit(self, provider_name: str) -> None:
        limiter = self._rate_limiters.get(provider_name)
        if limiter is not None:
            wait = await limiter.acquire()
            if wait > 0:
                logger.debug("Rate limited %s: waited %.2fs", provider_name, wait)

    def _is_circuit_open(self, provider_name: str) -> bool:
        return False

    def _record_success(self, provider_name: str) -> None:
        self._router.record_success(provider_name)

    def _record_failure(self, provider_name: str) -> None:
        self._router.record_failure(provider_name)

    async def _execute_with_guards(
        self, route: RouteResult, operation: str, *args: Any, **kwargs: Any
    ) -> ChatResponse | list[Embedding]:
        provider = route.provider
        provider_name = route.provider_name

        await self._enforce_rate_limit(provider_name)

        if operation == "chat":
            return await self._execute_chat(provider, provider_name, operation, args, kwargs, route)
        if operation == "embed":
            return await self._execute_embed(provider, provider_name, operation, args, kwargs, route)
        raise ValueError(f"Unknown operation: {operation}")

    async def _execute_chat(
        self,
        provider: LLMProvider,
        provider_name: str,
        operation: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        route: RouteResult,
    ) -> ChatResponse:
        try:
            result = await with_retry(
                lambda: provider.chat(*args, **kwargs), policy=self._retry_policy
            )
            self._record_success(provider_name)
            return result
        except ProviderError:
            fallback = await self._fallback_or_raise(provider_name, operation, args, kwargs, route)
            return cast(ChatResponse, fallback)

    async def _execute_embed(
        self,
        provider: LLMProvider,
        provider_name: str,
        operation: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        route: RouteResult,
    ) -> list[Embedding]:
        try:
            result = await with_retry(
                lambda: provider.embed(*args, **kwargs), policy=self._retry_policy
            )
            self._record_success(provider_name)
            return result
        except ProviderError:
            fallback = await self._fallback_or_raise(provider_name, operation, args, kwargs, route)
            return cast(list[Embedding], fallback)

    async def _fallback_or_raise(
        self,
        provider_name: str,
        operation: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        route: RouteResult,
    ) -> ChatResponse | list[Embedding]:
        self._record_failure(provider_name)
        if self._fallback_enabled and not route.used_fallback:
            route = await self._router.route(
                Capability.CHAT if operation == "chat" else Capability.EMBED
            )
            return await self._execute_with_guards(route, operation, *args, **kwargs)
        raise ProviderUnavailable(
            provider_name=provider_name,
            reason=f"Operation '{operation}' failed on all available providers",
        )
