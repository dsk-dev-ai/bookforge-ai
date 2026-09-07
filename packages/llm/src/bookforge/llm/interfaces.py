"""Provider interface and capability definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from enum import Enum

from bookforge.llm.models import (
    ChatConfig,
    ChatResponse,
    Chunk,
    Embedding,
    EmbeddingConfig,
    HealthStatus,
    Message,
)


class Capability(Enum):
    """Capabilities a provider can support."""

    CHAT = "chat"
    CHAT_STREAM = "chat_stream"
    EMBED = "embed"
    EMBED_STREAM = "embed_stream"


class LLMProvider(ABC):
    """Abstract interface for all LLM providers.

    Every provider adapter must implement all methods in this interface.
    Providers that do not support a capability should raise ``ProviderError``
    with a descriptive message.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of this provider."""

    @abstractmethod
    async def chat(self, messages: list[Message], config: ChatConfig | None = None) -> ChatResponse:
        """Send a chat completion request and return the full response.

        Args:
            messages: The conversation messages.
            config: Optional chat configuration overrides.

        Returns:
            A normalised chat response.

        Raises:
            ProviderUnavailable: If the provider is unreachable.
            AuthenticationError: If authentication fails.
            RateLimitError: If the rate limit is exceeded.
            ProviderTimeout: If the request times out.
        """

    @abstractmethod
    def chat_stream(
        self,
        messages: list[Message],
        config: ChatConfig | None = None,
    ) -> AsyncIterator[Chunk]:
        """Send a chat completion request and stream the response.

        Args:
            messages: The conversation messages.
            config: Optional chat configuration overrides.

        Yields:
            Chunks of the response as they arrive.

        Raises:
            ProviderUnavailable: If the provider is unreachable.
            AuthenticationError: If authentication fails.
            RateLimitError: If the rate limit is exceeded.
            ProviderTimeout: If the request times out.
        """

    @abstractmethod
    async def embed(
        self,
        texts: list[str],
        config: EmbeddingConfig | None = None,
    ) -> list[Embedding]:
        """Generate embeddings for a list of texts.

        Args:
            texts: The texts to embed.
            config: Optional embedding configuration overrides.

        Returns:
            A list of embeddings, one per input text.

        Raises:
            ProviderUnavailable: If the provider is unreachable.
            AuthenticationError: If authentication fails.
            RateLimitError: If the rate limit is exceeded.
            ProviderTimeout: If the request times out.
        """

    @abstractmethod
    def embed_stream(
        self,
        texts: AsyncIterator[str],
        config: EmbeddingConfig | None = None,
    ) -> AsyncIterator[Embedding]:
        """Generate embeddings for a stream of texts.

        Args:
            texts: An async iterator of texts to embed.
            config: Optional embedding configuration overrides.

        Yields:
            Embeddings as each text is processed.

        Raises:
            ProviderUnavailable: If the provider is unreachable.
            AuthenticationError: If authentication fails.
            RateLimitError: If the rate limit is exceeded.
            ProviderTimeout: If the request times out.
        """

    @abstractmethod
    async def health(self) -> HealthStatus:
        """Check the health of this provider.

        Returns:
            A health status indicating whether the provider is reachable
            and functioning correctly.
        """

    @abstractmethod
    async def list_models(self) -> list[str]:
        """List available model identifiers from this provider.

        Returns:
            A list of model identifier strings available through this provider.
        """
