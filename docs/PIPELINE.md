# Pipeline

> Data pipeline architecture, transformations, and orchestration.

---

## Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Data Transformations](#data-transformations)
- [Pipeline Orchestration](#pipeline-orchestration)
- [Error Handling](#error-handling)

---

## Overview

The BookForge AI pipeline transforms a book specification into a published PDF through a series of discrete stages. Each stage receives input data, applies a transformation, and passes the result to the next stage.

```mermaid
flowchart TB
    subgraph Input
        SPEC[Book Specification]
    end

    subgraph Pipeline
        R[Research Stage]
        O[Outline Stage]
        W[Write Stage]
        RV[Review Stage]
        F[Format Stage]
        P[PDF Render Stage]
    end

    subgraph Output
        PDF[Published PDF]
    end

    SPEC --> R
    R --> O
    O --> W
    W --> RV
    RV -->|Pass| F
    RV -->|Revise| W
    F --> P
    P --> PDF
```

---

## Pipeline Architecture

### Stage Interface

Every pipeline stage implements a common interface:

| Component | Description |
|---|---|
| `StageInput` | Typed input data for the stage |
| `StageOutput` | Typed output data produced by the stage |
| `execute(input)` | Core transformation logic |
| `validate(output)` | Post-condition validation |
| `rollback(context)` | Cleanup logic on failure |

### Pipeline Context

A shared context object flows through all stages:

```python
PipelineContext:
    book_id: UUID
    specification: BookSpec
    research: ResearchCorpus | None
    outline: BookOutline | None
    chapters: list[Chapter] | None
    review_results: ReviewReport | None
    formatted_markdown: str | None
    pdf_path: Path | None
    metadata: dict
    errors: list[PipelineError]
```

---

## Data Transformations

```mermaid
flowchart LR
    A["YAML/JSON\nSpec"] --> B["Research Corpus\n(Structured Text)"]
    B --> C["Book Outline\n(Hierarchical)"]
    C --> D["Chapter Content\n(Markdown)"]
    D --> E["Reviewed Content\n(Annotated MD)"]
    E --> F["Formatted Book\n(Normalised MD)"]
    F --> G["Published PDF\n(Binary File)"]
```

| Transformation | From | To | Package |
|---|---|---|---|
| Topic research | Book specification | Research corpus | `research` |
| Outline generation | Research corpus | Chapter outline | `research` |
| Content generation | Chapter outline | Chapter markdown | `llm` + `prompts` |
| Review annotation | Chapter markdown | Annotated markdown | `review` |
| Content revision | Annotated markdown | Revised markdown | `llm` + `prompts` |
| Markdown formatting | Raw markdown | Normalised markdown | `markdown` |
| PDF compilation | Normalised markdown | PDF binary | `pdf` |

---

## Pipeline Orchestration

The `core` package owns pipeline orchestration. It defines:

- **Pipeline** — A sequence of stages to execute
- **Stage** — A single transformation unit
- **StageResult** — Success or failure with optional diagnostics

```mermaid
sequenceDiagram
    participant API as REST API
    participant Core as Core Package
    participant Worker as Celery Worker
    participant Stage as Stage N

    API->>Core: start_pipeline(book_id)
    Core->>Worker: dispatch(stage_1)
    Worker->>Stage: execute(context)
    Stage-->>Worker: StageResult
    Worker->>Core: update_context(context)
    Core->>Worker: dispatch(stage_2)
    Worker->>Stage: execute(context)
    Stage-->>Worker: StageResult
    Worker->>Core: pipeline_complete(context)
    Core-->>API: status_update
```

---

## Error Handling

### Retry Policy

| Failure Type | Retries | Backoff | Fallback |
|---|---|---|---|
| LLM provider timeout | 3 | Exponential (2s, 4s, 8s) | Fallback provider |
| LLM rate limit | 3 | Linear (60s) | Queue delay |
| Database connection | 5 | Exponential | Circuit breaker |
| PDF rendering | 2 | Immediate | — |

### Pipeline Recovery

- Each stage records checkpoint state in the database
- Failed pipelines can be resumed from the last successful checkpoint
- Partial output (e.g., completed chapters) is preserved for inspection
- Critical failures transition the book to a `failed` state with error details
