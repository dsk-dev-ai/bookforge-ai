"""Tests for the model router."""

import pytest

from bookforge.llm.base import BaseProvider
from bookforge.llm.errors import ProviderUnavailable
from bookforge.llm.health import HealthChecker
from bookforge.llm.interfaces import Capability
from bookforge.llm.models import HealthStatus
from bookforge.llm.registry import ProviderRegistry
from bookforge.llm.router import ModelRouter, RoutingRule


class _HealthChecker(HealthChecker):
    def __init__(self) -> None:
        super().__init__(interval_seconds=9999, timeout_seconds=5)
        self._healthy_status: dict[str, HealthStatus] = {
            "primary": HealthStatus(healthy=True, provider="primary"),
            "fallback": HealthStatus(healthy=True, provider="fallback"),
        }

    def is_healthy(self, provider_name: str) -> bool:
        status = self._healthy_status.get(provider_name)
        return status is not None and status.healthy


def _make_router(primary: str = "primary", fallback: str | None = "fallback") -> ModelRouter:
    registry = ProviderRegistry()
    registry.register(BaseProvider(name="primary"))
    registry.register(BaseProvider(name="fallback"))

    health = _HealthChecker()

    rules = [
        RoutingRule(capability=Capability.CHAT, primary=primary, fallback=fallback),
    ]
    return ModelRouter(registry=registry, health=health, rules=rules)


class TestModelRouter:
    async def test_route_to_primary(self) -> None:
        router = _make_router()
        result = await router.route(Capability.CHAT)
        assert result.provider_name == "primary"
        assert result.used_fallback is False

    async def test_no_rule_raises(self) -> None:
        router = _make_router()
        with pytest.raises(ProviderUnavailable):
            await router.route(Capability.EMBED)
