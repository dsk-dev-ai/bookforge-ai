"""Request and response models for provider operations."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Generic, TypeVar


class MessageRole(Enum):
    """Role of a message in a chat conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class Message:
    """A single message in a chat conversation."""

    role: MessageRole
    content: str
    name: str | None = None


@dataclass(frozen=True)
class TokenUsage:
    """Token usage statistics for a provider request."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class ModelInfo:
    """Information about a model available from a provider."""

    name: str
    provider: str
    capabilities: list[str] = field(default_factory=list)
    context_window: int | None = None
    max_output_tokens: int | None = None


@dataclass(frozen=True)
class ChatConfig:
    """Configuration for a chat completion request."""

    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    stop: list[str] | None = None
    timeout_seconds: float = 60.0


@dataclass(frozen=True)
class ChatResponse:
    """A normalised response from a chat completion."""

    content: str
    model: str
    provider: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None
    latency_ms: float = 0.0


@dataclass(frozen=True)
class Chunk:
    """A streaming chunk from a chat completion."""

    content: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None


T = TypeVar("T")


@dataclass(frozen=True)
class Embedding(Generic[T]):
    """A vector embedding result."""

    vector: list[float]
    index: int = 0


@dataclass(frozen=True)
class EmbeddingConfig:
    """Configuration for an embedding request."""

    model: str | None = None
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class HealthStatus:
    """Health status of a provider."""

    healthy: bool
    provider: str
    latency_ms: float = 0.0
    model: str | None = None
    error: str | None = None
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    capabilities: list[str] = field(default_factory=list)
