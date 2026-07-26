# `@bookforge/api`

REST API service for BookForge AI.

## Responsibilities

- Exposes RESTful endpoints for book CRUD operations
- Manages pipeline lifecycle (start, pause, resume, cancel, status)
- Handles authentication via API keys
- Serves generated content (markdown and PDF downloads)
- Provides review workflow endpoints (approve, request changes)
- Validates all inputs via Pydantic schemas
- Returns consistent JSON responses with pagination support
- Delegates long-running operations to the background worker

## Configuration

| Variable | Description |
|---|---|
| `BOOKFORGE_API_HOST` | API server host (default: `0.0.0.0`) |
| `BOOKFORGE_API_PORT` | API server port (default: `8000`) |
| `BOOKFORGE_API_KEY` | Authentication key for API requests |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string for Celery |

## Running

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Dependencies

- `core` — Domain entities and pipeline orchestration
- `shared` — Types, configuration, utilities
