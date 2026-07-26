# `@bookforge/worker`

Background task processor for BookForge AI.

## Responsibilities

- Executes pipeline stages as Celery tasks
- Processes research, writing, review, formatting, and rendering stages
- Manages LLM provider calls with retry and fallback logic
- Updates book and chapter status in the database
- Handles pipeline errors and checkpoint recovery
- Integrates with all domain packages for stage execution

## Configuration

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string (broker) |
| `CELERY_CONCURRENCY` | Worker concurrency (default: `4`) |

## Running

```bash
celery -A app.worker worker --loglevel=info
```

## Dependencies

- `core` — Pipeline orchestration and domain entities
- `llm` — LLM provider abstraction
- `research` — Topic research
- `markdown` — Markdown processing
- `pdf` — PDF compilation
- `review` — Content review
- `rag` — Context retrieval
- `diagrams` — Diagram generation
- `images` — Image generation
- `prompts` — Prompt templates
- `shared` — Types, configuration, utilities
