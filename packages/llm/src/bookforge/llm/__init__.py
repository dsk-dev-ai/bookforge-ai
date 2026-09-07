"""LLM provider abstraction layer for BookForge AI."""

from bookforge.llm.errors import (
    AuthenticationError,
    ConfigurationError,
    InvalidProvider,
    ProviderError,
    ProviderTimeout,
    ProviderUnavailable,
    RateLimitError,
)
from bookforge.llm.interfaces import Capability, LLMProvider
from bookforge.llm.manager import ProviderManager
from bookforge.llm.models import (
    ChatConfig,
    ChatResponse,
    Chunk,
    Embedding,
    EmbeddingConfig,
    HealthStatus,
    Message,
    MessageRole,
    ModelInfo,
    TokenUsage,
)
from bookforge.llm.registry import ProviderRegistry

__all__ = [
    "AuthenticationError",
    "Capability",
    "ChatConfig",
    "ChatResponse",
    "Chunk",
    "ConfigurationError",
    "Embedding",
    "EmbeddingConfig",
    "HealthStatus",
    "InvalidProvider",
    "LLMProvider",
    "Message",
    "MessageRole",
    "ModelInfo",
    "ProviderError",
    "ProviderManager",
    "ProviderRegistry",
    "ProviderTimeout",
    "ProviderUnavailable",
    "RateLimitError",
    "TokenUsage",
]
