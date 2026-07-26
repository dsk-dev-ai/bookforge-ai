# API

> REST API design, endpoints, and usage for BookForge AI.

---

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Common Patterns](#common-patterns)
- [Error Handling](#error-handling)

---

## Overview

The BookForge AI REST API is built with FastAPI and exposes endpoints for managing books, controlling pipelines, and retrieving generated content. It follows RESTful conventions with consistent request/response shapes.

---

## Base URL

```
http://localhost:8000/api/v1
```

---

## Authentication

All API requests require an API key in the `Authorization` header:

```
Authorization: Bearer <api_key>
```

API keys are configured server-side and provisioned per environment.

---

## Endpoints

### Books

| Method | Path | Description |
|---|---|---|
| `POST` | `/books` | Create a new book specification |
| `GET` | `/books` | List all books (paginated) |
| `GET` | `/books/{id}` | Get book details |
| `PATCH` | `/books/{id}` | Update book specification |
| `DELETE` | `/books/{id}` | Delete a book |

### Pipeline

| Method | Path | Description |
|---|---|---|
| `POST` | `/books/{id}/pipeline/start` | Start the book generation pipeline |
| `GET` | `/books/{id}/pipeline/status` | Get current pipeline status |
| `POST` | `/books/{id}/pipeline/pause` | Pause the running pipeline |
| `POST` | `/books/{id}/pipeline/resume` | Resume a paused pipeline |
| `POST` | `/books/{id}/pipeline/cancel` | Cancel the pipeline |

### Chapters

| Method | Path | Description |
|---|---|---|
| `GET` | `/books/{id}/chapters` | List chapters for a book |
| `GET` | `/books/{id}/chapters/{chapter_id}` | Get chapter content |
| `PATCH` | `/books/{id}/chapters/{chapter_id}` | Update chapter content |

### Review

| Method | Path | Description |
|---|---|---|
| `GET` | `/books/{id}/review` | Get review status and reports |
| `POST` | `/books/{id}/review/approve` | Approve current review stage |
| `POST` | `/books/{id}/review/request-changes` | Request revision with comments |

### Output

| Method | Path | Description |
|---|---|---|
| `GET` | `/books/{id}/output/markdown` | Download formatted markdown |
| `GET` | `/books/{id}/output/pdf` | Download compiled PDF |

---

## Common Patterns

### Pagination

List endpoints support cursor-based pagination:

```
GET /api/v1/books?cursor=eyJpZCI6IjEyMyJ9&limit=20
```

Response:

```json
{
    "data": [...],
    "pagination": {
        "next_cursor": "eyJpZCI6IjEyMyJ9",
        "has_more": true,
        "limit": 20
    }
}
```

### Status Responses

All endpoints return a consistent envelope:

```json
{
    "status": "success",
    "data": { ... },
    "meta": {
        "request_id": "req_abc123",
        "timestamp": "2026-01-15T10:30:00Z"
    }
}
```

---

## Error Handling

Errors follow RFC 7807 (Problem Details):

```json
{
    "type": "https://api.bookforge.ai/errors/validation-error",
    "title": "Validation Error",
    "status": 422,
    "detail": "The topic 'fiction' is not in the list of supported topics",
    "instance": "/api/v1/books",
    "errors": [
        {
            "field": "topic",
            "message": "Unsupported topic. Allowed: AI, ML, DevOps, ..."
        }
    ]
}
```

| Status | Description |
|---|---|
| `400` | Bad request — malformed input |
| `401` | Unauthorised — missing or invalid API key |
| `404` | Not found — book or resource does not exist |
| `409` | Conflict — pipeline cannot transition from current state |
| `422` | Validation error — request body failed validation |
| `429` | Too many requests — rate limit exceeded |
| `500` | Internal server error |
