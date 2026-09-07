# `@bookforge/rag`

> **Status: planned** — this subsystem is specified in `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` for a future phase. No implementation ships yet. See [docs/ROADMAP.md](../../docs/ROADMAP.md).


Knowledge Manager subsystem — Retrieval-Augmented Generation engine.

## Responsibilities

- Manages vector storage for book content embeddings
- Generates embeddings for research corpus, chapters, and concepts via Provider Manager
- Retrieves relevant context for writing stage to ensure cross-chapter consistency
- Chunks research corpus into segments for embedding
- Supports similarity search with configurable thresholds
- Supplies context snippets to the Writing Engine for each chapter
- Part of the **Preparation** phase of the pipeline (Stage 5)

## Pipeline Stages

| Stage | Role |
|---|---|
| Stage 5: Knowledge Base | Populate vector index with research embeddings |

## Dependencies

- `llm` — Embedding generation via Provider Manager
- `shared` — Types, configuration

## Referenced In

- `docs/PIPELINE.md` — Stage 5
- `docs/ARCHITECTURE.md` — Knowledge Manager subsystem
