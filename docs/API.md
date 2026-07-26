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

**Why not GraphQL?** The primary consumers are a Next.js frontend and external automation scripts. Both benefit from predictable REST endpoints with clear caching semantics. GraphQL's flexibility adds complexity without a proportional benefit for this domain.

---

## Base URL and Versioning

```
https://api.bookforge.ai/v1
```

Versioning is via URL prefix. Breaking changes increment the major version. Backward-compatible additions do not change the version.

---

## Authentication

All requests require an API key in the `Authorization` header:

```
Authorization: Bearer bf_api_abc123def456
```

API keys are:
- Provisioned through the admin interface
- Scoped to a single project
- Revocable independently
- Never exposed in logs or error messages

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
        "details": {
            "topic": "Fiction",
            "allowed_topics": ["AI", "ML", "DevOps", "..."]
        }
    },
    "meta": {
        "request_id": "req_def456",
        "timestamp": "2026-07-26T14:30:01.456Z"
    }
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
    },
    "meta": { ... }
}
```

**Why cursor pagination?** Offset pagination breaks when items are inserted or deleted between pages. Cursor pagination is stable and performant at any scale.

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
    "description": "A comprehensive guide to running Kubernetes in production environments",
    "style_guide": "technical-formal",
    "outline": [
        {"title": "Introduction", "description": "..."},
        {"title": "Cluster Architecture", "description": "..."}
    ]
}
```

```json
// 201 Created
{
    "status": "success",
    "data": {
        "id": "b_abc123",
        "title": "Kubernetes in Production",
        "status": "draft",
        "created_at": "2026-07-26T14:30:00.123Z"
    }
}
```

### List Books

```
GET /books?limit=20&cursor=eyJpZCI6IjEyMyJ9&status=completed
```

### Get Book

```
GET /books/{book_id}
```

### Update Book

```
PATCH /books/{book_id}
```

Only updatable while status is `draft` or `invalid`.

### Delete Book

```
DELETE /books/{book_id}
```

Soft delete — sets status to `archived`. Hard delete after 30-day grace period.

---

## Pipeline Endpoints

### Start Pipeline

```
POST /books/{book_id}/pipeline/start
```

```json
// 202 Accepted
{
    "status": "success",
    "data": {
        "book_id": "b_abc123",
        "pipeline_id": "pl_def456",
        "status": "in_progress",
        "current_stage": "validation",
        "started_at": "2026-07-26T14:30:00.123Z"
    }
}
```

### Get Pipeline Status

```
GET /books/{book_id}/pipeline/status
```

```json
{
    "status": "success",
    "data": {
        "pipeline_id": "pl_def456",
        "status": "in_progress",
        "current_stage": "writing",
        "progress": {
            "total_stages": 12,
            "completed_stages": 5,
            "current_stage_progress": 0.4
        },
        "current_stage_started_at": "2026-07-26T14:35:00.000Z",
        "estimated_remaining_seconds": 540
    }
}
```

### Pause Pipeline

```
POST /books/{book_id}/pipeline/pause
```

Completes the current stage, then pauses before the next stage.

### Resume Pipeline

```
POST /books/{book_id}/pipeline/resume
```

### Cancel Pipeline

```
POST /books/{book_id}/pipeline/cancel
```

Cancels the current stage and marks the pipeline as cancelled. Partial output is preserved.

---

## Project Endpoints

### Create Project

```
POST /projects
```

A project wraps a book with collaboration settings.

### Get Project

```
GET /projects/{project_id}
```

### List Projects

```
GET /projects?limit=20
```

### Add Collaborator

```
POST /projects/{project_id}/collaborators
```

```json
{
    "user_email": "editor@example.com",
    "role": "editor"
}
```

### Tag Version

```
POST /projects/{project_id}/versions
```

```json
{
    "tag": "v1.0.0-rc1",
    "description": "Pre-release candidate 1"
}
```

---

## Review Endpoints

### Get Review Status

```
GET /books/{book_id}/review
```

```json
{
    "status": "success",
    "data": {
        "chapters": [
            {
                "chapter_id": "ch_001",
                "number": 1,
                "title": "Introduction",
                "overall_verdict": "pass",
                "revision_cycle": 1,
                "stages": [
                    {
                        "name": "technical",
                        "verdict": "pass",
                        "findings": []
                    },
                    {
                        "name": "style",
                        "verdict": "pass",
                        "findings": []
                    },
                    {
                        "name": "structural",
                        "verdict": "pass",
                        "findings": []
                    }
                ]
            }
        ]
    }
}
```

### Approve Chapter

```
POST /books/{book_id}/review/chapters/{chapter_id}/approve
```

### Request Revision

```
POST /books/{book_id}/review/chapters/{chapter_id}/request-revision
```

```json
{
    "comments": "Section 2.3 needs more detail on RBAC configuration"
}
```

---

## Export Endpoints

### List Outputs

```
GET /books/{book_id}/outputs
```

```json
{
    "status": "success",
    "data": {
        "outputs": [
            {
                "format": "pdf",
                "file_size_bytes": 4500000,
                "url": "https://storage.bookforge.ai/books/b_abc123/output.pdf",
                "created_at": "2026-07-26T15:30:00.123Z"
            },
            {
                "format": "epub",
                "file_size_bytes": 3200000,
                "url": "https://storage.bookforge.ai/books/b_abc123/output.epub",
                "created_at": "2026-07-26T15:30:00.456Z"
            }
        ]
    }
}
```

### Download Output

```
GET /books/{book_id}/outputs/{format}
```

Redirects to the object storage pre-signed URL.

---

## Provider Endpoints

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

---

## Configuration Endpoints

### List Feature Flags

```
GET /system/config/features
```

### Update Feature Flag

```
PATCH /system/config/features/{flag_name}
```

```json
{
    "enabled": true
}
```

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
    "uptime_seconds": 86400,
    "version": "1.0.0"
}
```

### Readiness Check

```
GET /system/ready
```

Used by load balancers and orchestrators.

---

## Webhook Endpoints

### Register Webhook

```
POST /webhooks
```

```json
{
    "url": "https://example.com/notify",
    "events": ["book.completed", "pipeline.stage.failed"],
    "secret": "whsec_abc123"
}
```

| Event | Triggered When |
|---|---|
| `book.created` | Book created |
| `book.completed` | All pipeline stages finished |
| `book.archived` | Book soft-deleted |
| `pipeline.stage.started` | Stage begins |
| `pipeline.stage.completed` | Stage finishes |
| `pipeline.stage.failed` | Stage fails with no retries |
| `pipeline.completed` | Entire pipeline finishes |
| `pipeline.aborted` | Pipeline aborted by user |

---

## Error Catalog

| HTTP Code | Error Code | Description | When |
|---|---|---|---|
| 400 | `BAD_REQUEST` | Malformed request body | JSON parse failure |
| 401 | `UNAUTHORIZED` | Missing or invalid API key | Auth header missing or invalid |
| 403 | `FORBIDDEN` | API key lacks permission | Key scoped to different project |
| 404 | `NOT_FOUND` | Resource does not exist | Invalid book or chapter ID |
| 409 | `CONFLICT` | State conflict | Pipeline already running |
| 422 | `VALIDATION_ERROR` | Input validation failed | Topic not supported, missing fields |
| 429 | `RATE_LIMITED` | Too many requests | Rate limit exceeded |
| 500 | `INTERNAL_ERROR` | Unexpected server error | Contact support |
| 502 | `PROVIDER_ERROR` | LLM provider unavailable | All providers unhealthy |
| 503 | `SERVICE_UNAVAILABLE` | System overloaded | Queue full, back off |

---

## API Configuration

```yaml
# config/api.yaml
api:
  host: "0.0.0.0"
  port: 8000
  rate_limit:
    requests_per_minute: 100
    burst: 20
  cors:
    allowed_origins:
      - "https://app.bookforge.ai"
    allowed_methods:
      - GET
      - POST
      - PATCH
      - DELETE
  webhooks:
    max_retries: 5
    retry_backoff: "exponential"
    timeout_seconds: 10
  pagination:
    default_limit: 20
    max_limit: 100
```
