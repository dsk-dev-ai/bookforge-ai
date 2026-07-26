# `@bookforge/shared`

Shared types, base classes, configuration management, and cross-cutting utilities.

## Responsibilities

- Common type definitions used by all subsystems (`BookSpec`, `ChapterContent`, `LLMConfig`, `PipelineContext`, `StageResult`)
- Configuration Manager — loads from YAML, environment variables, database; layered merge with priority ordering
- Structured logging with consistent JSON schema, subsystem tagging, and trace IDs
- Base exception hierarchy (`BookForgeError`, `ProviderError`, `ConfigurationError`, `PipelineError`)
- Pydantic base models for serialisation consistency
- Rate limiter implementation (token bucket algorithm)
- Retry and backoff utilities with jitter
- Health check response types
- Pagination types for API responses

## Dependencies

- None (leaf package)

## Referenced In

- `docs/ARCHITECTURE.md` — Configuration Manager, Logging System
- `docs/API.md` — Response envelope types
