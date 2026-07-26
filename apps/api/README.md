# `@bookforge/api`

FastAPI REST API service.

## Responsibilities

- Exposes RESTful endpoints for all resources: books, projects, chapters, review, pipeline, providers, configuration, system health
- Handles authentication via API key header
- Validates all inputs via Pydantic schemas
- Returns consistent JSON envelope with pagination support
- Delegates long-running operations to the background worker via the Job Queue
- Serves generated content via pre-signed object storage URLs
- CORS configuration for web dashboard access
- Rate limiting per API key
- Health and readiness endpoints for load balancers
- Webhook registration and dispatch for external integrations

## Architecture Role

The API is the **entry point** to the system. It does not execute pipeline stages — it validates requests and enqueues work. Long-running operations return `202 Accepted` with a status polling endpoint.

## Endpoint Groups

| Group | Prefix | Description |
|---|---|---|
| Books | `/v1/books` | Book CRUD and pipeline control |
| Projects | `/v1/projects` | Project and collaborator management |
| Review | `/v1/books/{id}/review` | Review workflow |
| Export | `/v1/books/{id}/outputs` | Output download |
| System | `/v1/system` | Providers, config, health |

## Configuration

| Variable | Description | Default |
|---|---|---|
| `BOOKFORGE_API_HOST` | Bind address | `0.0.0.0` |
| `BOOKFORGE_API_PORT` | Bind port | `8000` |
| `BOOKFORGE_API_KEY` | Authentication key | — |
| `DATABASE_URL` | PostgreSQL DSN | — |
| `REDIS_URL` | Redis DSN | — |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000` |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute | `100` |

## Running

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Dependencies

- `core` — Domain entities, book manager, pipeline orchestration
- `shared` — Types, configuration, response envelope
