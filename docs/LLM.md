# LLM Integration

> Provider abstraction and configuration.

## Provider Architecture

See `docs/ARCHITECTURE.md` — Provider Architecture section for the complete design.

## Supported Providers

| Provider | Priority | Role |
|---|---|---|
| NVIDIA NIM | Primary | Default provider for all generation |
| Ollama | Fallback | Local fallback when primary is unavailable |

## Pluggability

New providers implement a 5-method interface (`chat`, `chat_stream`, `embed`, `embed_stream`, `health`), register in the provider registry, and configure environment variables. No code changes to any subsystem.

## Configuration

```env
LLM_PROVIDER=nvidia
LLM_FALLBACK_PROVIDER=ollama
LLM_DEFAULT_MODEL=meta/llama-3.1-70b-instruct
NVIDIA_NIM_API_KEY=
NVIDIA_NIM_BASE_URL=
OLLAMA_BASE_URL=http://localhost:11434
```

## Provider Selection

Healthy primary → healthy fallback → `ProviderUnavailable` error. Health checked every 60 seconds. Circuit breaker opens after 5 consecutive failures.
