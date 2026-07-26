# `@bookforge/llm`

LLM provider abstraction layer.

## Responsibilities

- Defines the `LLMProvider` interface (`generate`, `generate_stream`, `embed`, `health`)
- Implements provider adapters for NVIDIA NIM, OpenAI, Anthropic, and Ollama
- Normalises provider-specific responses into a common `LLMResponse` type
- Handles provider selection, fallback, and circuit breaking
- Enforces rate limits per provider (token bucket algorithm)
- Manages retry logic with exponential backoff and jitter
- Provides health-check endpoint for each configured provider

## Dependencies

- `shared` — Types, configuration, utilities
