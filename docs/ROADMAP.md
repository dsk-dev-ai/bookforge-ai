# Roadmap

> Development phases and future direction for BookForge AI.

---

## Table of Contents

- [Phase Overview](#phase-overview)
- [Phase 01 — Foundation](#phase-01--foundation)
- [Phase 02 — Core Pipeline](#phase-02--core-pipeline)
- [Phase 03 — Intelligence](#phase-03--intelligence)
- [Phase 04 — Production](#phase-04--production)
- [Future Considerations](#future-considerations)

---

## Phase Overview

```mermaid
gantt
    title BookForge AI Development Roadmap
    dateFormat  YYYY-MM-DD
    axisFormat  %Y Q%q

    section Foundation
    Project structure & docs       :done,    p1a, 2026-01-01, 30d
    CI/CD & templates              :done,    p1b, 2026-01-15, 30d

    section Core Pipeline
    Core entities & state machine  :active,  p2a, 2026-02-01, 45d
    Research & outline generation  :         p2b, 2026-02-15, 45d
    Markdown processing            :         p2c, 2026-03-01, 45d
    PDF rendering                  :         p2d, 2026-03-15, 45d

    section Intelligence
    LLM abstraction layer          :         p3a, 2026-04-01, 60d
    RAG engine                     :         p3b, 2026-04-15, 60d
    Review pipeline                :         p3c, 2026-05-01, 60d
    Prompt management              :         p3d, 2026-05-15, 60d
    Diagrams & images              :         p3e, 2026-06-01, 60d

    section Production
    REST API                       :         p4a, 2026-07-01, 45d
    Web UI                         :         p4b, 2026-07-15, 45d
    Deployment & monitoring        :         p4c, 2026-08-01, 60d
    Documentation & polish         :         p4d, 2026-08-15, 60d
```

---

## Phase 01 — Foundation

**Status:** ✅ Complete

**Goal:** Establish the project foundation with no AI logic.

| Deliverable | Description |
|---|---|
| Project structure | Monorepo layout with `apps/`, `packages/`, `docs/`, `templates/` |
| Documentation | Full documentation suite (architecture, roadmap, workflow, pipeline, etc.) |
| Package READMEs | Responsibility documentation for every package and app |
| Templates | Book, chapter, and section YAML/Markdown templates |
| CI/CD | GitHub Actions for lint, type-check, and test |
| Configuration | `docker-compose.yml`, `Makefile`, `.env.example` |
| Coding standards | Python style guide, commit conventions, branching strategy |

---

## Phase 02 — Core Pipeline

**Goal:** Implement the core book generation pipeline without LLM integration.

| Deliverable | Package | Description |
|---|---|---|
| Core entities | `core` | Book, Chapter, Section, Author, Pipeline state machine |
| Shared utilities | `shared` | Configuration, types, logging, error handling |
| Markdown processing | `markdown` | Parse, transform, lint, and format Markdown content |
| PDF rendering | `pdf` | Compile Markdown to publication-ready PDF with TOC, cover, headers |
| Research engine | `research` | Topic research, outline generation, source management |
| Template system | `templates` | Template loading, variable substitution, partial rendering |

---

## Phase 03 — Intelligence

**Goal:** Integrate LLM providers to power content generation, review, and enhancement.

| Deliverable | Package | Description |
|---|---|---|
| LLM abstraction | `llm` | Provider interface, NVIDIA NIM, OpenAI, Anthropic, Ollama adapters |
| RAG engine | `rag` | Vector storage, embedding management, context retrieval |
| Review pipeline | `review` | Technical accuracy, style consistency, structural review stages |
| Prompt management | `prompts` | Template versioning, rendering, experiment tracking |
| Diagram generation | `diagrams` | Mermaid and PlantUML generation from content descriptions |
| Image generation | `images` | DALL-E / Stable Diffusion integration for illustrations |

---

## Phase 04 — Production

**Goal:** Build the API and web interface, harden for production.

| Deliverable | App | Description |
|---|---|---|
| REST API | `api` | Full CRUD, pipeline control, review actions, status polling |
| Web UI | `web` | Dashboard, book editor, review interface, progress monitoring |
| Background worker | `worker` | Celery configuration, task routing, error handling |
| DevOps | — | Docker, CI/CD, monitoring with Prometheus/Grafana |
| Documentation | — | User guide, deployment guide, operational runbook |

---

## Future Considerations

- **Multi-language output** — Support for non-English book generation
- **Collaborative review** — Multiple reviewers with commenting and approval workflows
- **Plugin system** — Third-party provider plugins for LLM, images, and diagrams
- **Batch generation** — Generate multiple books from a single specification
- **Version tracking** — Track book revisions and regenerate specific chapters
- **Marketplace integration** — Direct publishing to Kindle, Gumroad, or Leanpub
