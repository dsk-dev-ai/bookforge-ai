"""Model router — selects the appropriate provider based on routing rules."""

from __future__ import annotations

from dataclasses import dataclass

from bookforge.llm.circuit_breaker import CircuitBreaker
from bookforge.llm.errors import ProviderUnavailable
from bookforge.llm.health import HealthChecker
from bookforge.llm.interfaces import Capability, LLMProvider
from bookforge.llm.registry import ProviderRegistry


@dataclass
class RoutingRule:
    """A single routing rule.

    Attributes:
        capability: The required capability.
        primary: Name of the primary provider.
        fallback: Name of the fallback provider when primary is unavailable.
    """

    capability: Capability
    primary: str
    fallback: str | None = None


@dataclass
class RouteResult:
    """The result of a routing decision.

    Attributes:
        provider: The selected provider.
        provider_name: Name of the selected provider.
        used_fallback: Whether the fallback was selected.
        circuit_open: Whether the primary's circuit was open.
    """

    provider: LLMProvider
    provider_name: str
    used_fallback: bool = False
    circuit_open: bool = False


class ModelRouter:
    """Routes requests to providers based on capability and health.

    Selection strategy:
    1. Check configured primary provider for the capability.
    2. If primary is healthy and circuit is closed → select primary.
    3. If primary is unhealthy or circuit is open → check fallback.
    4. If fallback is healthy → select fallback.
    5. If fallback is unavailable → raise ProviderUnavailable.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        health: HealthChecker,
        rules: list[RoutingRule] | None = None,
    ) -> None:
        self._registry = registry
        self._health = health
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._rules = rules or [
            RoutingRule(capability=Capability.CHAT, primary="nvidia", fallback="ollama"),
            RoutingRule(capability=Capability.CHAT_STREAM, primary="nvidia", fallback="ollama"),
            RoutingRule(capability=Capability.EMBED, primary="nvidia", fallback="ollama"),
            RoutingRule(capability=Capability.EMBED_STREAM, primary="nvidia", fallback="ollama"),
        ]

    def set_rules(self, rules: list[RoutingRule]) -> None:
        """Replace all routing rules.

        Args:
            rules: The new routing rules.
        """
        self._rules = list(rules)

    async def route(self, capability: Capability) -> RouteResult:
        """Select a provider for the given capability.

        Args:
            capability: The required capability.

        Returns:
            A RouteResult with the selected provider.

        Raises:
            InvalidProvider: If neither primary nor fallback are registered.
            ProviderUnavailable: If neither provider is available.
        """

        rule = self._find_rule(capability)
        if rule is None:
            available = [r.capability.value for r in self._rules]
            raise ProviderUnavailable(
                provider_name="router",
                reason=f"No routing rule for capability '{capability.value}'. Available: {available}",
            )

        breaker = self._get_breaker(rule.primary)

        if not breaker.is_open() and self._health.is_healthy(rule.primary):
            provider = self._registry.get(rule.primary)
            return RouteResult(
                provider=provider,
                provider_name=rule.primary,
                used_fallback=False,
                circuit_open=False,
            )

        circuit_was_open = breaker.is_open()

        if rule.fallback and self._health.is_healthy(rule.fallback):
            provider = self._registry.get(rule.fallback)
            return RouteResult(
                provider=provider,
                provider_name=rule.fallback,
                used_fallback=True,
                circuit_open=circuit_was_open,
            )

        if rule.fallback:
            raise ProviderUnavailable(
                provider_name=rule.primary,
                reason=f"Primary '{rule.primary}' unavailable and fallback '{rule.fallback}' unhealthy",
            )

        raise ProviderUnavailable(
            provider_name=rule.primary,
            reason=f"Provider '{rule.primary}' unavailable and no fallback configured",
        )

    def _find_rule(self, capability: Capability) -> RoutingRule | None:
        for rule in self._rules:
            if rule.capability == capability:
                return rule
        return None

    def record_success(self, provider_name: str) -> None:
        """Record a successful call for a provider.

        Closes the circuit breaker and resets failure count.
        """
        breaker = self._get_breaker(provider_name)
        breaker.record_success()

    def record_failure(self, provider_name: str) -> None:
        """Record a failed call for a provider.

        Opens the circuit breaker if the failure threshold is reached.
        """
        breaker = self._get_breaker(provider_name)
        breaker.record_failure()

    def _get_breaker(self, provider_name: str) -> CircuitBreaker:
        if provider_name not in self._circuit_breakers:
            self._circuit_breakers[provider_name] = CircuitBreaker()
        return self._circuit_breakers[provider_name]
