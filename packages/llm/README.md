# `@bookforge/llm`

LLM provider abstraction layer — the Provider Manager subsystem.

## Responsibilities

- Defines `LLMProvider` interface (`chat`, `chat_stream`, `embed`, `embed_stream`, `health`)
- Implements the Provider Registry — providers self-register on startup
- Provider adapters for NVIDIA NIM (primary) and Ollama (fallback)
- Normalises all provider responses into a common `LLMResponse` type
- Provider selection logic: healthy primary → healthy fallback → error
- Circuit breaker: trips after 5 consecutive failures, cooldown 300 seconds
- Health checker: pings every provider every 60 seconds, caches status
- Rate limiting per provider (token bucket algorithm)
- Retry with exponential backoff and ±25% jitter

## Provider Interface

```python
class LLMProvider(ABC):
    async def chat(self, messages: list[Message], config: ChatConfig) -> ChatResponse: ...
    async def chat_stream(self, messages: list[Message], config: ChatConfig) -> AsyncIterator[Chunk]: ...
    async def embed(self, texts: list[str]) -> list[Embedding]: ...
    async def embed_stream(self, stream: AsyncIterator[str]) -> AsyncIterator[Embedding]: ...
    async def health(self) -> HealthStatus: ...
```

## Dependencies

- `shared` — Types, configuration, rate limiter, retry utilities

## Referenced In

- `docs/ARCHITECTURE.md` — Provider Architecture section
- `docs/LLM.md` — Full provider integration documentation
