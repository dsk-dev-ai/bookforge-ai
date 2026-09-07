"""Ollama provider adapter.

Communicates with a local Ollama instance for chat, embedding, and health checking.
All configuration comes from the configuration system.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from bookforge.llm.base import BaseProvider
from bookforge.llm.config_loader import ProviderEndpointConfig
from bookforge.llm.errors import ProviderUnavailable
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


class OllamaProvider(BaseProvider):
    """Provider adapter for local Ollama instances.

    Uses the Ollama REST API format. All connection parameters are
    resolved from the provided config.
    """

    def __init__(
        self,
        config: ProviderEndpointConfig,
        http_client: Any = None,
    ) -> None:
        super().__init__(name="ollama", config={"endpoint_config": config})
        self._cfg = config
        self._http = http_client

    async def chat(self, messages: list[Message], config: ChatConfig | None = None) -> ChatResponse:
        cfg = config or ChatConfig()
        model = cfg.model or self._cfg.model
        timeout = cfg.timeout_seconds or self._cfg.timeout_seconds

        payload = self._build_chat_payload(messages, model, cfg)

        try:
            response = await self._post("/api/chat", payload, timeout)
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

        async for chunk in self._post_stream("/api/chat", payload, timeout):
            yield self._parse_chunk(chunk)

    async def embed(self, texts: list[str], config: EmbeddingConfig | None = None) -> list[Embedding]:
        cfg = config or EmbeddingConfig()
        model = cfg.model or self._cfg.model
        timeout = cfg.timeout_seconds or self._cfg.timeout_seconds

        results: list[Embedding] = []
        for text in texts:
            payload = {"model": model, "input": text}
            try:
                response = await self._post("/api/embed", payload, timeout)
            except Exception as exc:
                raise ProviderUnavailable(
                    provider_name=self.name,
                    reason=str(exc),
                ) from exc
            vector = response.get("embedding", [])
            results.append(Embedding(vector=vector, index=len(results)))

        return results

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
            response = await self._get("/api/tags", timeout=10.0)
            models = self._parse_models(response)
            return HealthStatus(
                healthy=True,
                provider=self.name,
                model=models[0] if models else None,
                capabilities=["chat", "chat_stream", "embed"],
            )
        except Exception as exc:  # noqa: BLE001 — degrade gracefully on any provider failure
            return HealthStatus(
                healthy=False,
                provider=self.name,
                error=str(exc),
            )

    async def list_models(self) -> list[str]:
        try:
            response = await self._get("/api/tags", timeout=10.0)
            return self._parse_models(response)
        except Exception:  # noqa: BLE001 — degrade to configured model on failure
            return [self._cfg.model]

    def _build_chat_payload(self, messages: list[Message], model: str, config: ChatConfig) -> dict:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
        }
        if config.temperature is not None:
            payload["temperature"] = config.temperature
        if config.max_tokens is not None:
            payload["options"] = {"num_predict": config.max_tokens}
        if config.stop:
            payload.setdefault("options", {})["stop"] = config.stop
        return payload

    def _parse_chat_response(self, response: dict, model: str) -> ChatResponse:
        message = response.get("message", {})
        usage_data = response.get("usage", {}) or {}
        return ChatResponse(
            content=message.get("content", ""),
            model=model,
            provider=self.name,
            finish_reason=response.get("done_reason"),
            usage=TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0) or response.get("prompt_eval_count", 0),
                completion_tokens=usage_data.get("completion_tokens", 0)
                or response.get("eval_count", 0),
                total_tokens=usage_data.get("total_tokens", 0)
                or (response.get("prompt_eval_count", 0) + response.get("eval_count", 0)),
            ),
        )

    def _parse_chunk(self, chunk: dict) -> Chunk:
        return Chunk(
            content=chunk.get("message", {}).get("content", ""),
            finish_reason=chunk.get("done_reason"),
        )

    def _parse_models(self, response: dict) -> list[str]:
        raw = response.get("models", [])
        return [item.get("name", "") for item in raw if item.get("name")]

    async def _post(self, path: str, payload: dict, timeout: float) -> dict:
        raise NotImplementedError("HTTP client not injected — override _post in integration")

    def _post_stream(self, path: str, payload: dict, timeout: float) -> AsyncIterator[dict]:
        raise NotImplementedError("Streaming HTTP not injected — override _post_stream in integration")

    async def _get(self, path: str, timeout: float) -> dict:
        raise NotImplementedError("HTTP client not injected — override _get in integration")
