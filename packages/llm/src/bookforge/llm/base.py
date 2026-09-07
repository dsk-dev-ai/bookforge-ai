"""Base provider implementation with shared plumbing."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from bookforge.llm.errors import ProviderError
from bookforge.llm.interfaces import LLMProvider
from bookforge.llm.models import (
    ChatConfig,
    ChatResponse,
    Chunk,
    Embedding,
    EmbeddingConfig,
    HealthStatus,
    Message,
)


class BaseProvider(LLMProvider):
    """Base class for provider implementations.

    Provides default implementations and shared utility methods.
    Override methods in subclasses for provider-specific behaviour.
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        self._name = name
        self._config = config or {}

    @property
    def name(self) -> str:
        return self._name

    async def chat(self, messages: list[Message], config: ChatConfig | None = None) -> ChatResponse:
        raise ProviderError(f"{self.name} does not support chat", provider_name=self.name)

    def chat_stream(
        self,
        messages: list[Message],
        config: ChatConfig | None = None,
    ) -> AsyncIterator[Chunk]:
        raise ProviderError(f"{self.name} does not support streaming chat", provider_name=self.name)

    async def embed(self, texts: list[str], config: EmbeddingConfig | None = None) -> list[Embedding]:
        raise ProviderError(f"{self.name} does not support embeddings", provider_name=self.name)

    def embed_stream(
        self,
        texts: AsyncIterator[str],
        config: EmbeddingConfig | None = None,
    ) -> AsyncIterator[Embedding]:
        raise ProviderError(f"{self.name} does not support streaming embeddings", provider_name=self.name)

    async def health(self) -> HealthStatus:
        return HealthStatus(healthy=False, provider=self.name, error="Health check not implemented")

    async def list_models(self) -> list[str]:
        return []
