# `@bookforge/shared`

Shared utilities, types, and configuration.

## Responsibilities

- Common type definitions (`BookSpec`, `ChapterContent`, `LLMConfig`, etc.)
- Configuration management (environment variables, settings objects)
- Structured logging and error types
- Pydantic base models for consistent serialisation
- Utility functions (text processing, token counting, string normalisation)
- Rate limiter implementation (token bucket)
- Retry and backoff utilities

## Dependencies

- None (leaf package)
