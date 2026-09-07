"""Provider registry — stores and resolves provider implementations."""

from __future__ import annotations

from bookforge.llm.errors import InvalidProvider
from bookforge.llm.interfaces import LLMProvider


class ProviderRegistry:
    """Registry of available LLM providers.

    Providers self-register by name. The registry provides lookup by name
    and iteration over all registered providers. Registration happens at
    application startup.
    """

    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider) -> None:
        """Register a provider instance.

        Args:
            provider: The provider instance to register.

        Raises:
            ValueError: If a provider with the same name is already registered.
        """
        if provider.name in self._providers:
            raise ValueError(f"Provider '{provider.name}' is already registered")
        self._providers[provider.name] = provider

    def unregister(self, name: str) -> None:
        """Unregister a provider by name.

        Args:
            name: The name of the provider to unregister.
        """
        self._providers.pop(name, None)

    def get(self, name: str) -> LLMProvider:
        """Get a provider by name.

        Args:
            name: The provider name.

        Returns:
            The registered provider instance.

        Raises:
            InvalidProvider: If no provider is registered with that name.
        """
        provider = self._providers.get(name)
        if provider is None:
            raise InvalidProvider(name)
        return provider

    def providers(self) -> list[LLMProvider]:
        """Return all registered providers.

        Returns:
            A list of all registered provider instances.
        """
        return list(self._providers.values())

    def list_names(self) -> list[str]:
        """Return the names of all registered providers.

        Returns:
            A list of provider name strings.
        """
        return list(self._providers.keys())

    def clear(self) -> None:
        """Remove all registered providers."""
        self._providers.clear()

    def __contains__(self, name: str) -> bool:
        return name in self._providers

    def __len__(self) -> int:
        return len(self._providers)
