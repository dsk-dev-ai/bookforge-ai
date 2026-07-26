# BookForge AI

> AI-powered technical eBook publishing platform.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Subsystems](#subsystems)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Pipeline](#pipeline)
- [Provider Architecture](#provider-architecture)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

BookForge AI is a production-grade platform that transforms a technical book specification into a publication-ready PDF and EPUB through an automated pipeline of research, writing, review, diagramming, and rendering.

The platform only generates technical books. Allowed topics: AI, ML, LLMs, AI Agents, RAG, MLOps, DevOps, Kubernetes, Docker, Cloud, APIs, Databases, Software Engineering, Distributed Systems, Cybersecurity.

---

## Architecture

```mermaid
graph TB
    subgraph "API Layer"
        API[FastAPI REST API]
    end

    subgraph "Worker Layer"
        CEL[Celery Worker]
        ORCH[Pipeline Orchestrator]
    end

    subgraph "Subsystems"
        BM[Book Manager]
        PM[Project Manager]
        PRM[Provider Manager]
        PTM[Prompt Manager]
        RM[Research Manager]
        KM[Knowledge Manager]
        OE[Outline Engine]
        WE[Writing Engine]
        RVE[Review Engine]
        DE[Diagram Engine]
        IE[Image Engine]
        ME[Markdown Engine]
        PBE[Publishing Engine]
        EE[Export Engine]
    end

    subgraph "Cross-Cutting"
        CFG[Configuration Manager]
        LOG[Logging System]
        JQ[Job Queue]
        TE[Template Engine]
    end

    subgraph "Infrastructure"
        PG[(PostgreSQL)]
        RD[(Redis)]
        S3[(Object Storage)]
    end

    API --> BM
    API --> PM
    API --> JQ
    CEL --> ORCH
    ORCH --> BM
    ORCH --> PRM
    ORCH --> PTM
    ORCH --> RM
    ORCH --> KM
    ORCH --> OE
    ORCH --> WE
    ORCH --> RVE
    ORCH --> DE
    ORCH --> IE
    ORCH --> ME
    ORCH --> PBE
    ORCH --> EE
    BM --> PG
    PM --> PG
    PRM --> CFG
    KM --> RD
    PBE --> S3
    EE --> S3
```

---

## Subsystems

| Subsystem | Responsibility |
|---|---|
| Book Manager | Book entity lifecycle, state machine, CRUD |
| Project Manager | Project container, collaborators, version tags |
| Provider Manager | LLM provider registry, health checks, circuit breaker, provider selection |
| Prompt Manager | Versioned prompt templates, rendering, usage tracking |
| Research Manager | Topic research, source synthesis, concept extraction |
| Knowledge Manager | RAG engine, embeddings, vector indexes, context retrieval |
| Outline Engine | Chapter outline generation from book specification |
| Writing Engine | Chapter content generation with context-aware prompting |
| Review Engine | Multi-stage quality checks (technical, style, structural, consistency) |
| Diagram Engine | Mermaid/PlantUML diagram generation from content descriptions |
| Image Engine | Cover and illustration image generation |
| Markdown Engine | Markdown parsing, normalisation, formatting, linting |
| Publishing Engine | PDF and EPUB compilation with styling |
| Export Engine | Output delivery, file packaging, storage management |

---

## Project Structure

```
bookforge-ai/
├── apps/
│   ├── api/              # FastAPI REST API
│   ├── web/              # Next.js web dashboard
│   └── worker/           # Celery background worker
├── packages/
│   ├── core/             # Domain entities, pipeline orchestration
│   ├── shared/           # Types, utilities, base classes
│   ├── llm/              # Provider abstraction layer
│   ├── research/         # Research and content gathering
│   ├── markdown/         # Markdown processing
│   ├── pdf/              # PDF compilation
│   ├── review/           # Content review engine
│   ├── rag/              # RAG and knowledge management
│   ├── diagrams/         # Diagram generation
│   ├── images/           # Image generation
│   └── prompts/          # Prompt template management
├── config/
│   ├── defaults.yaml     # Default configuration
│   ├── development.yaml  # Dev overrides
│   ├── production.yaml   # Production overrides
│   ├── providers.yaml    # Provider configuration
│   ├── pipeline.yaml     # Pipeline stage configuration
│   ├── logging.yaml      # Logging configuration
│   └── features.yaml     # Feature flags
├── docs/                 # Architecture and design documentation
├── templates/            # Book, chapter, and section templates
├── books/                # Generated book output
├── assets/               # Static assets
├── scripts/              # Utility scripts
├── docker/               # Docker configurations
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.12+ | Runtime |
| API Framework | FastAPI | REST API |
| Web UI | Next.js + TypeScript | User interface |
| Database | PostgreSQL 16 | Persistent state |
| Cache / Queue | Redis 7 | Caching + Celery broker |
| Task Queue | Celery | Async background processing |
| PDF Engine | WeasyPrint / Typst | PDF rendering |
| LLM Providers | NVIDIA NIM (primary), Ollama (fallback) | Content generation |
| Linting | ruff | Code quality |
| Types | mypy | Static type checking |
| Testing | pytest | Test framework |
| Container | Docker + Docker Compose | Development environment |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/bookforge-ai.git
cd bookforge-ai

# Copy environment configuration
cp .env.example .env

# Start infrastructure
docker compose up -d postgres redis

# Run migrations
make migrate

# Start development
make dev
```

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | System architecture, subsystems, provider design, event flow |
| [Pipeline](docs/PIPELINE.md) | Complete 13-stage book generation pipeline |
| [API](docs/API.md) | REST API endpoint catalog and contracts |
| [Database](docs/DATABASE.md) | Schema design, ERD, migration strategy |
| [Workflow](docs/WORKFLOW.md) | User-facing and system workflows |
| [Project Specification](docs/PROJECT_SPECIFICATION.md) | Vision, scope, constraints |
| [LLM Integration](docs/LLM.md) | Provider abstraction and configuration |
| [Prompts](docs/PROMPTS.md) | Prompt template system |
| [Security](docs/SECURITY.md) | Security policies |
| [Roadmap](docs/ROADMAP.md) | Development phases |
| [Coding Standards](docs/CODING_STANDARDS.md) | Code conventions |
| [Contributing](docs/CONTRIBUTING.md) | Contribution guide |

---

## Pipeline

```
Book Request → Validation → Specification → Outline → Research →
Knowledge Base → Writing → Review → Diagrams → Cover →
Markdown → PDF → EPUB → Completed Book
```

13 stages across 4 phases. See [docs/PIPELINE.md](docs/PIPELINE.md) for details.

---

## Provider Architecture

| Priority | Provider | Role |
|---|---|---|
| Primary | NVIDIA NIM | Default LLM provider for all generation |
| Fallback | Ollama | Local fallback when primary is unavailable |

**Pluggable:** New providers implement a 5-method interface and register via configuration. No code changes required. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the provider architecture.

---

## Roadmap

| Phase | Focus |
|---|---|
| 01 — Foundation | Project structure, documentation, templates |
| 02 — Architecture | System architecture, pipeline design, subsystem specification |
| 03 — Core Pipeline | Research, writing, review, markdown, PDF |
| 04 — Intelligence | LLM integration, RAG, diagrams, images |
| 05 — Production | API, web UI, deployment, monitoring |

---

## Contributing

Please read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) and [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md) before submitting contributions.

---

## License

MIT License.
