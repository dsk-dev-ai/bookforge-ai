# `@bookforge/llm`

LLM provider abstraction layer — the Provider Manager subsystem.

## Responsibilities

- Defines `LLMProvider` interface (`chat`, `chat_stream`, `embed`, `embed_stream`, `health`, `list_models`)
- Implements the Provider Registry — providers self-register by name
- Provider adapters for NVIDIA NIM (primary) and Ollama (fallback)
- Normalises all provider responses into a common `ChatResponse`, `Chunk`, `Embedding` types
- Provider selection via `ModelRouter`: healthy primary → healthy fallback → error
- Circuit breaker: trips after N consecutive failures, cooldown before half-open
- `HealthChecker`: pings every provider periodically, caches status with configurable TTL
- Rate limiting: token bucket algorithm per provider
- Retry: exponential backoff with jitter via `with_retry()`
- Configuration: Pydantic Settings from environment variables
- Custom exception hierarchy: `ProviderError`, `ProviderUnavailable`, `AuthenticationError`, `RateLimitError`, `ProviderTimeout`, `ConfigurationError`, `InvalidProvider`

## Package Structure

```
llm/
├── pyproject.toml
├── README.md
├── src/bookforge/llm/
│   ├── __init__.py          # Public API exports
│   ├── interfaces.py        # LLMProvider ABC, Capability enum
│   ├── base.py              # BaseProvider with default implementations
│   ├── models.py            # ChatConfig, ChatResponse, Chunk, Embedding, etc.
│   ├── errors.py            # Exception hierarchy
│   ├── config.py            # Pydantic Settings (LLMSettings, ProviderSettings)
│   ├── config_loader.py     # ConfigLoader → RuntimeConfig
│   ├── registry.py          # ProviderRegistry
│   ├── manager.py           # ProviderManager facade
│   ├── router.py            # ModelRouter with routing rules
│   ├── health.py            # HealthChecker + HealthStatusCache
│   ├── rate_limiter.py      # RateLimiter ABC + TokenBucketRateLimiter
│   ├── retry.py             # RetryPolicy + with_retry()
│   ├── circuit_breaker.py   # CircuitBreaker
│   ├── logging.py           # Structured logging utilities
│   └── providers/
│       ├── __init__.py
│       ├── nvidia.py        # NVIDIA NIM adapter
│       └── ollama.py        # Ollama adapter
└── tests/
    ├── test_errors.py
    ├── test_models.py
    ├── test_registry.py
    ├── test_retry.py
    ├── test_router.py
    ├── test_circuit_breaker.py
    ├── test_rate_limiter.py
    ├── test_health.py
    └── test_fallback.py
```

## Provider Interface

```python
class LLMProvider(ABC):
    @property
    def name(self) -> str: ...
    async def chat(self, messages, config) -> ChatResponse: ...
    async def chat_stream(self, messages, config) -> AsyncIterator[Chunk]: ...
    async def embed(self, texts, config) -> list[Embedding]: ...
    async def embed_stream(self, texts) -> AsyncIterator[Embedding]: ...
    async def health(self) -> HealthStatus: ...
    async def list_models(self) -> list[str]: ...
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `nvidia` | Primary provider |
| `LLM_FALLBACK_PROVIDER` | `ollama` | Fallback provider |
| `LLM_DEFAULT_MODEL` | — | Default chat model |
| `LLM_MAX_RETRIES` | `3` | Max retry attempts |
| `LLM_RATE_LIMIT_REQUESTS_PER_MINUTE` | `60` | Max requests/minute/provider |
| `LLM_CIRCUIT_BREAKER_THRESHOLD` | `5` | Failures before circuit opens |
| `NVIDIA_NIM_API_KEY` | — | NVIDIA NIM key |
| `NVIDIA_NIM_BASE_URL` | `http://localhost:8000` | NVIDIA NIM URL |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama URL |

## Quick Start

```python
from bookforge.llm import ProviderManager
from bookforge.llm.models import Message, MessageRole

manager = ProviderManager.from_env()
await manager.start()

response = await manager.chat([
    Message(role=MessageRole.USER, content="Write a chapter on...")
])
print(response.content)

await manager.stop()
```

## Dependencies

- `pydantic>=2.0` — Settings and model validation
- `pydantic-settings>=2.0` — Environment variable loading

## Referenced In

- `docs/ARCHITECTURE.md` — Provider Architecture section
- `docs/LLM.md` — Full provider integration documentation
