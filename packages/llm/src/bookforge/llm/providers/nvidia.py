"""NVIDIA NIM provider adapter.

Communicates with NVIDIA NIM endpoints for chat, embedding, and health checking.
All configuration (URLs, models, keys) comes from the configuration system —
nothing is hardcoded.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from bookforge.llm.base import BaseProvider
from bookforge.llm.config_loader import ProviderEndpointConfig
from bookforge.llm.errors import AuthenticationError, ProviderTimeout, ProviderUnavailable
from bookforge.llm.models import (
    ChatConfig,
    ChatResponse,
    Chunk,
    Embedding,
    EmbeddingConfig,
    HealthStatus,
    Message,
    TokenUsage,
)


class NvidiaProvider(BaseProvider):
    """Provider adapter for NVIDIA NIM.

    Uses the OpenAI-compatible API format that NVIDIA NIM exposes.
    All connection parameters are resolved from the provided config.
    """

    def __init__(
        self,
        config: ProviderEndpointConfig,
        http_client: Any = None,
    ) -> None:
        super().__init__(name="nvidia", config={"endpoint_config": config})
        self._cfg = config
        self._http = http_client

    async def chat(self, messages: list[Message], config: ChatConfig | None = None) -> ChatResponse:
        cfg = config or ChatConfig()
        model = cfg.model or self._cfg.model
        timeout = cfg.timeout_seconds or self._cfg.timeout_seconds

        payload = self._build_chat_payload(messages, model, cfg)

        try:
            response = await self._post("/v1/chat/completions", payload, timeout)
        except ProviderTimeout:
            raise
        except Exception as exc:
            raise ProviderUnavailable(
                provider_name=self.name,
                reason=str(exc),
            ) from exc

        return self._parse_chat_response(response, model)

    async def chat_stream(
        self,
        messages: list[Message],
        config: ChatConfig | None = None,
    ) -> AsyncIterator[Chunk]:
        cfg = config or ChatConfig()
        model = cfg.model or self._cfg.model
        timeout = cfg.timeout_seconds or self._cfg.timeout_seconds

        payload = self._build_chat_payload(messages, model, cfg)
        payload["stream"] = True

        async for chunk in self._post_stream("/v1/chat/completions", payload, timeout):
            yield self._parse_chunk(chunk)

    async def embed(self, texts: list[str], config: EmbeddingConfig | None = None) -> list[Embedding]:
        cfg = config or EmbeddingConfig()
        model = cfg.model or self._cfg.model
        timeout = cfg.timeout_seconds or self._cfg.timeout_seconds

        payload = {"input": texts, "model": model}

        try:
            response = await self._post("/v1/embeddings", payload, timeout)
        except Exception as exc:
            raise ProviderUnavailable(
                provider_name=self.name,
                reason=str(exc),
            ) from exc

        return self._parse_embedding_response(response)

    async def embed_stream(
        self,
        texts: AsyncIterator[str],
        config: EmbeddingConfig | None = None,
    ) -> AsyncIterator[Embedding]:
        async for text in texts:
            embeddings = await self.embed([text], config)
            if embeddings:
                yield embeddings[0]

    async def health(self) -> HealthStatus:
        try:
            response = await self._get("/v1/health", timeout=10.0)
            models = await self.list_models()
            return HealthStatus(
                healthy=True,
                provider=self.name,
                model=models[0] if models else None,
                capabilities=["chat", "chat_stream", "embed", "embed_stream"],
            )
        except Exception as exc:
            return HealthStatus(
                healthy=False,
                provider=self.name,
                error=str(exc),
            )

    async def list_models(self) -> list[str]:
        try:
            response = await self._get("/v1/models", timeout=10.0)
            return self._parse_models(response)
        except Exception:
            return [self._cfg.model]

    def _build_chat_payload(self, messages: list[Message], model: str, config: ChatConfig) -> dict:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
        }
        if config.temperature is not None:
            payload["temperature"] = config.temperature
        if config.max_tokens is not None:
            payload["max_tokens"] = config.max_tokens
        if config.top_p is not None:
            payload["top_p"] = config.top_p
        if config.stop:
            payload["stop"] = config.stop
        return payload

    def _parse_chat_response(self, response: dict, model: str) -> ChatResponse:
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage_data = response.get("usage", {})
        return ChatResponse(
            content=message.get("content", ""),
            model=model,
            provider=self.name,
            finish_reason=choice.get("finish_reason"),
            usage=TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            ),
        )

    def _parse_chunk(self, chunk: dict) -> Chunk:
        choice = chunk.get("choices", [{}])[0]
        delta = choice.get("delta", {})
        usage_data = chunk.get("usage")
        return Chunk(
            content=delta.get("content", ""),
            finish_reason=choice.get("finish_reason"),
            usage=TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )
            if usage_data
            else None,
        )

    def _parse_embedding_response(self, response: dict) -> list[Embedding]:
        raw = response.get("data", [])
        return [
            Embedding(vector=item.get("embedding", []), index=item.get("index", i))
            for i, item in enumerate(raw)
        ]

    def _parse_models(self, response: dict) -> list[str]:
        raw = response.get("data", [])
        return [item.get("id", "") for item in raw if item.get("id")]

    async def _post(self, path: str, payload: dict, timeout: float) -> dict:
        raise NotImplementedError("HTTP client not injected — override _post in integration")

    async def _post_stream(self, path: str, payload: dict, timeout: float) -> AsyncIterator[dict]:
        raise NotImplementedError("Streaming HTTP not injected — override _post_stream in integration")

    async def _get(self, path: str, timeout: float) -> dict:
        raise NotImplementedError("HTTP client not injected — override _get in integration")
