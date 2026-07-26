# `@bookforge/research`

Research Manager subsystem — topic research and content gathering.

## Responsibilities

- Gathers structured research for a given technical topic via LLM
- Synthesises information from multiple queries into a cohesive corpus
- Extracts key concepts, definitions, prerequisites, and learning objectives
- Produces a `ResearchCorpus` entity attached to the book
- Cross-references concepts across chapters to identify dependencies
- Generates prerequisite chains for logical section ordering
- Part of the **Preparation** phase of the pipeline (Stage 4)

## Pipeline Stages

| Stage | Role |
|---|---|
| Stage 4: Research | Gather and synthesise technical research |
| Stage 5: Knowledge Base | Feed research into the vector index |

## Dependencies

- `llm` — Content generation via Provider Manager
- `rag` — Context retrieval for related research
- `shared` — Types, configuration

## Referenced In

- `docs/PIPELINE.md` — Stages 4-5
- `docs/ARCHITECTURE.md` — Research Manager subsystem
