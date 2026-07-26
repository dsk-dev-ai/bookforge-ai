# Architecture

> System architecture, component design, and data flow for BookForge AI.

---

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Component Diagram](#component-diagram)
- [Layer Overview](#layer-overview)
- [Package Dependency Graph](#package-dependency-graph)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)

---

## High-Level Architecture

BookForge AI follows a modular monolith architecture with clear domain boundaries. The system is organised into three application tiers and eleven packages, each with a single responsibility.

```mermaid
graph TB
    subgraph "Presentation Layer"
        WEB[Web UI - Next.js]
    end

    subgraph "API Layer"
        API[FastAPI REST API]
    end

    subgraph "Processing Layer"
        WRK[Celery Worker]
    end

    subgraph "Domain Packages"
        CORE[Core]
        SHARED[Shared]
        LLM[LLM]
        RESEARCH[Research]
        MD[Markdown]
        PDF[PDF]
        REVIEW[Review]
        RAG[RAG]
        DIAG[Diagrams]
        IMG[Images]
        PROMPTS[Prompts]
    end

    subgraph "Infrastructure"
        PG[(PostgreSQL)]
        RD[(Redis)]
        FS[(File Storage)]
    end

    WEB --> API
    API --> WRK
    API --> PG
    WRK --> CORE
    WRK --> RD
    CORE --> LLM
    CORE --> RESEARCH
    CORE --> MD
    CORE --> PDF
    CORE --> REVIEW
    CORE --> RAG
    CORE --> DIAG
    CORE --> IMG
    CORE --> PROMPTS
    CORE --> SHARED
    CORE --> PG
    RESEARCH --> LLM
    RESEARCH --> RAG
    MD --> SHARED
    PDF --> MD
    PDF --> FS
    REVIEW --> LLM
    DIAG --> LLM
    IMG --> LLM
```

---

## Layer Overview

### Presentation Layer

The **Web UI** is a Next.js application that provides the user-facing dashboard. It communicates exclusively with the REST API and does not access packages or databases directly.

### API Layer

The **REST API** (FastAPI) is the entry point for all user interactions. It handles authentication, request validation, and delegates long-running tasks to the worker. It also exposes endpoints for querying pipeline status and retrieving generated content.

### Processing Layer

The **Background Worker** (Celery) executes all pipeline stages asynchronously. Each pipeline stage is a Celery task that coordinates the relevant packages. This separation ensures the API remains responsive during long book generation runs.

### Domain Packages

The eleven packages contain all business logic. They are organised by domain concern and depend on each other through well-defined interfaces. The `core` package acts as the orchestrator, composing pipelines from lower-level packages.

---

## Package Dependency Graph

```mermaid
graph LR
    CORE --> LLM
    CORE --> PROMPTS
    CORE --> SHARED
    CORE --> RESEARCH
    CORE --> REVIEW
    CORE --> MD
    CORE --> PDF
    CORE --> RAG
    CORE --> DIAG
    CORE --> IMG
    RESEARCH --> LLM
    RESEARCH --> RAG
    REVIEW --> LLM
    DIAG --> LLM
    IMG --> LLM
    PDF --> MD
    MD --> SHARED
    RAG --> LLM
    RAG --> SHARED
    LLM --> SHARED
    PROMPTS --> SHARED
```

---

## Data Flow

```mermaid
sequenceDiagram
    actor User
    participant Web as Web UI
    participant API as REST API
    participant DB as PostgreSQL
    participant Worker as Celery Worker
    participant LLMProvider as LLM Provider

    User->>Web: Define book topic & outline
    Web->>API: Create book request
    API->>DB: Persist book record
    API->>Worker: Enqueue research task
    Worker->>LLMProvider: Gather research
    LLMProvider-->>Worker: Research results
    Worker->>DB: Store research
    Worker->>Worker: Generate outline
    Worker->>Worker: Write chapters
    Worker->>LLMProvider: Generate content
    LLMProvider-->>Worker: Chapter content
    Worker->>Worker: Review content
    Worker->>DB: Update book status
    Worker->>Worker: Render Markdown
    Worker->>Worker: Compile PDF
    Worker->>DB: Mark as complete
    API-->>Web: Status update
    User->>Web: Download PDF
```

---

## Design Decisions

### Why a modular monolith instead of microservices?

- The domain is cohesive — all packages serve the single goal of book generation
- Simpler deployment and development workflow
- Easy to extract individual services later if needed (packages are decoupled through interfaces)

### Why Celery for background tasks?

- Mature, well-documented task queue with rich monitoring (Flower)
- Native integration with Redis and PostgreSQL
- Reliable task retries, rate limiting, and scheduling

### Why an LLM abstraction layer?

- Multiple providers need to be supported (NVIDIA NIM, OpenAI, Anthropic, Ollama)
- Isolates business logic from provider-specific API details
- Enables provider fallback and A/B testing

### Why FastAPI?

- Native async support for concurrent request handling
- Automatic OpenAPI documentation generation
- Pydantic integration for robust request/response validation
