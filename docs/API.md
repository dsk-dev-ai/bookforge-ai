# API

> REST API design for BookForge AI — endpoints, contracts, and integration patterns.

---

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [Base URL and Versioning](#base-url-and-versioning)
- [Authentication](#authentication)
- [Standard Response Envelope](#standard-response-envelope)
- [Book Endpoints](#book-endpoints)
- [Pipeline Endpoints](#pipeline-endpoints)
- [Project Endpoints](#project-endpoints)
- [Review Endpoints](#review-endpoints)
- [Export Endpoints](#export-endpoints)
- [Provider Endpoints](#provider-endpoints)
- [Configuration Endpoints](#configuration-endpoints)
- [System Endpoints](#system-endpoints)
- [Webhook Endpoints](#webhook-endpoints)
- [Error Catalog](#error-catalog)
- [API Configuration](#api-configuration)

---

## Design Philosophy

The API follows a **resource-oriented** design. Every URL identifies a resource. Every HTTP verb maps to a standard operation. Responses are consistent, errors are descriptive, and pagination is cursor-based.

---

## Base URL and Versioning

```
https://api.bookforge.ai/v1
```

---

## Authentication

```
Authorization: Bearer bf_api_abc123def456
```

---

## Standard Response Envelope

### Success

```json
{
    "status": "success",
    "data": { ... },
    "meta": {
        "request_id": "req_abc123",
        "timestamp": "2026-07-26T14:30:00.123Z",
        "version": "1.0"
    }
}
```

### Error

```json
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "The provided topic is not supported",
        "details": { "topic": "Fiction" }
    },
    "meta": { "request_id": "req_def456" }
}
```

### Paginated List

```json
{
    "status": "success",
    "data": [ ... ],
    "pagination": {
        "cursor": "eyJpZCI6IjEyMyJ9",
        "next_cursor": "eyJpZCI6IjEyNCJ9",
        "has_more": true,
        "limit": 20
    }
}
```

---

## Book Endpoints

### Create Book

```
POST /books
```

```json
{
    "title": "Kubernetes in Production",
    "topic": "Kubernetes",
    "audience": "intermediate",
    "target_chapters": 12,
    "target_pages": 250,
    "description": "A comprehensive guide to running Kubernetes in production"
}
```

### List Books

```
GET /books?limit=20&cursor=...&status=completed
```

### Get Book

```
GET /books/{book_id}
```

### Update Book

```
PATCH /books/{book_id}
```

### Delete Book

```
DELETE /books/{book_id}
```

---

## Pipeline Endpoints

### Start Pipeline

```
POST /books/{book_id}/pipeline/start
```

### Get Pipeline Status

```
GET /books/{book_id}/pipeline/status
```

### Pause / Resume / Cancel

```
POST /books/{book_id}/pipeline/pause
POST /books/{book_id}/pipeline/resume
POST /books/{book_id}/pipeline/cancel
```

---

## Provider Endpoints

Provider endpoints return live data from the ``ProviderManager`` health checker
and registry.

### List Providers

```
GET /system/providers
```

```json
{
    "data": [
        {
            "name": "nvidia",
            "status": "healthy",
            "model": "meta/llama-3.1-70b-instruct",
            "capabilities": ["chat", "chat_stream", "embed"],
            "latency_ms": 1200,
            "uptime_percent": 99.7
        },
        {
            "name": "ollama",
            "status": "healthy",
            "model": "llama3.1",
            "capabilities": ["chat", "chat_stream"],
            "latency_ms": 3400,
            "uptime_percent": 100
        }
    ]
}
```

### Get Provider Details

```
GET /system/providers/{provider_name}
```

Returns detailed health information from the ``HealthChecker``:

```json
{
    "data": {
        "name": "nvidia",
        "status": "healthy",
        "model": "meta/llama-3.1-70b-instruct",
        "capabilities": ["chat", "chat_stream", "embed"],
        "circuit_breaker": "closed",
        "failure_count": 0,
        "health_checked_at": "2026-07-26T14:30:00.123Z"
    }
}
```

### Set Active Provider

```
PUT /system/providers/active
```

```json
{
    "primary": "nvidia",
    "fallback": "ollama"
}
```

Updates the ``ModelRouter`` routing rules at runtime.

### List Available Models

```
GET /system/providers/{provider_name}/models
```

Proxies to ``LLMProvider.list_models()``.

---

## Configuration Endpoints

Configuration is managed by ``packages/config/``. All settings are loaded from environment variables and ``.env`` files via Pydantic v2.

### Get All Config

```
GET /system/config
```

Returns the entire ``BookForgeConfig`` object (redacting secrets):

```json
{
    "data": {
        "application": {
            "name": "bookforge",
            "version": "1.0.0",
            "debug": false,
            "host": "0.0.0.0",
            "port": 8000,
            "workers": 4
        },
        "environment": { "env": "production" },
        "features": {
            "nvidia_enabled": true,
            "ollama_enabled": true,
            "research_enabled": true,
            "writer_enabled": true,
            "publishing_enabled": true,
            "dashboard_enabled": true,
            "experimental_enabled": false
        },
        "nvidia": {
            "nvidia_nim_base_url": "http://localhost:8000",
            "nvidia_nim_model": "meta/llama-3.1-70b-instruct"
        },
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "llama3.1"
        }
    }
}
```

### List Feature Flags

```
GET /system/config/features
```

### Update Feature Flag

```
PATCH /system/config/features/{flag_name}
```

```json
{ "enabled": true }
```

All feature flags are defined in ``packages/config/src/bookforge/config/features.py``:

| Flag Env Variable | Description |
|---|---|
| ``BOOKFORGE_FEATURE_NVIDIA_ENABLED`` | Enable NVIDIA provider |
| ``BOOKFORGE_FEATURE_OLLAMA_ENABLED`` | Enable Ollama provider |
| ``BOOKFORGE_FEATURE_RESEARCH_ENABLED`` | Enable research engine |
| ``BOOKFORGE_FEATURE_WRITER_ENABLED`` | Enable writing engine |
| ``BOOKFORGE_FEATURE_PUBLISHING_ENABLED`` | Enable publishing engine |
| ``BOOKFORGE_FEATURE_DASHBOARD_ENABLED`` | Enable web dashboard |
| ``BOOKFORGE_FEATURE_EXPERIMENTAL_ENABLED`` | Enable experimental features |
| ``BOOKFORGE_FEATURE_FALLBACK_ENABLED`` | Enable provider fallback |
| ``BOOKFORGE_FEATURE_TELEMETRY_ENABLED`` | Enable anonymous telemetry |

---

## System Endpoints

### Health Check

```
GET /system/health
```

```json
{
    "status": "healthy",
    "checks": {
        "database": "connected",
        "redis": "connected",
        "storage": "reachable",
        "providers": {
            "nvidia": "healthy",
            "ollama": "healthy"
        }
    },
    "uptime_seconds": 86400
}
```

Provider health is sourced from the ``HealthChecker`` cache.

### Readiness Check

```
GET /system/ready
```

---

## Error Catalog

| HTTP | Code | Description |
|---|---|---|
| 400 | `BAD_REQUEST` | Malformed request body |
| 401 | `UNAUTHORIZED` | Missing or invalid API key |
| 403 | `FORBIDDEN` | API key lacks permission |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | State conflict |
| 422 | `VALIDATION_ERROR` | Input validation failed |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 502 | `PROVIDER_ERROR` | LLM provider unavailable |
| 503 | `SERVICE_UNAVAILABLE` | System overloaded |

---

## API Configuration

All API settings are managed through the configuration package (``packages/config/``):

```python
from bookforge.config import load_config

config = load_config()
api_host = config.application.host       # BOOKFORGE_APP_HOST
api_port = config.application.port       # BOOKFORGE_APP_PORT
```

```text
# .env
BOOKFORGE_APP_HOST=0.0.0.0
BOOKFORGE_APP_PORT=8000
BOOKFORGE_SECURITY_RATE_LIMIT_ENABLED=true
BOOKFORGE_SECURITY_RATE_LIMIT_REQUESTS=100
```
