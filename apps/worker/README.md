# `@bookforge/worker`

Celery background worker for pipeline execution.

## Responsibilities

- Executes all 13 pipeline stages as Celery tasks
- Routes tasks to appropriate queues (pipeline, review, export)
- Integrates with every domain subsystem for stage execution
- Handles provider calls with retry, fallback, and circuit breaking
- Performs checkpoint persistence after every stage
- Manages pipeline recovery on worker restart
- Enforces per-stage timeouts and concurrency limits

## Architecture Role

The worker is the **execution engine**. It has no public interface — it reads from the job queue and writes to the database. All 14 subsystems are available to the worker for stage execution.

## Queue Architecture

| Queue | Concurrency | Handles |
|---|---|---|
| `pipeline` | 2 | Main pipeline stages (outline, research, writing, diagrams, markdown, publishing) |
| `review` | 1 | Review stages (technical, style, structural, consistency) |
| `export` | 2 | Export and delivery |

## Configuration

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL DSN | — |
| `REDIS_URL` | Redis DSN (broker + backend) | — |
| `CELERY_CONCURRENCY` | Global worker concurrency | `4` |
| `LLM_PROVIDER` | Primary LLM provider | `nvidia` |
| `LLM_FALLBACK_PROVIDER` | Fallback provider | `ollama` |

## Running

```bash
celery -A app.worker worker --loglevel=info
celery -A app.worker flower          # Monitoring dashboard
```

## Dependencies

- `core` — Pipeline orchestration, domain entities
- All 11 domain packages (llm, research, markdown, pdf, review, rag, diagrams, images, prompts)
- `shared` — Types, configuration, logging
