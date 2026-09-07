"""Tests for the provider registry."""

import pytest

from bookforge.llm.base import BaseProvider
from bookforge.llm.errors import InvalidProvider
from bookforge.llm.registry import ProviderRegistry


class TestProviderRegistry:
    def test_register_and_get(self) -> None:
        registry = ProviderRegistry()
        provider = BaseProvider(name="test")
        registry.register(provider)
        assert registry.get("test") is provider

    def test_register_duplicate_raises(self) -> None:
        registry = ProviderRegistry()
        registry.register(BaseProvider(name="dup"))
        with pytest.raises(ValueError, match="already registered"):
            registry.register(BaseProvider(name="dup"))

    def test_get_missing_raises(self) -> None:
        registry = ProviderRegistry()
        with pytest.raises(InvalidProvider, match="unknown"):
            registry.get("unknown")

    def test_unregister(self) -> None:
        registry = ProviderRegistry()
        registry.register(BaseProvider(name="temp"))
        registry.unregister("temp")
        with pytest.raises(InvalidProvider):
            registry.get("temp")

    def test_list(self) -> None:
        registry = ProviderRegistry()
        p1 = BaseProvider(name="a")
        p2 = BaseProvider(name="b")
        registry.register(p1)
        registry.register(p2)
        assert len(registry.providers()) == 2
        assert p1 in registry.providers()
        assert p2 in registry.providers()

    def test_list_names(self) -> None:
        registry = ProviderRegistry()
        registry.register(BaseProvider(name="alpha"))
        registry.register(BaseProvider(name="beta"))
        assert "alpha" in registry.list_names()
        assert "beta" in registry.list_names()

    def test_contains(self) -> None:
        registry = ProviderRegistry()
        registry.register(BaseProvider(name="exists"))
        assert "exists" in registry
        assert "missing" not in registry

    def test_len(self) -> None:
        registry = ProviderRegistry()
        assert len(registry) == 0
        registry.register(BaseProvider(name="a"))
        assert len(registry) == 1

    def test_clear(self) -> None:
        registry = ProviderRegistry()
        registry.register(BaseProvider(name="a"))
        registry.register(BaseProvider(name="b"))
        registry.clear()
        assert len(registry) == 0
