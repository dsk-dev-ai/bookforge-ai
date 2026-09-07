# `@bookforge/diagrams`

> **Status: planned** — this subsystem is specified in `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` for a future phase. No implementation ships yet. See [docs/ROADMAP.md](../../docs/ROADMAP.md).


Diagram Engine subsystem — automated diagram generation.

## Responsibilities

- Generates architecture diagrams from textual descriptions
- Supports Mermaid and PlantUML output formats
- Scans chapter content for diagram insertion points
- Generates diagram descriptions via the Provider Manager
- Renders diagram source to image assets
- Embeds diagram references in chapter content
- Part of the **Creation** phase of the pipeline (Stage 8)

## Supported Diagram Types

flowchart, sequence diagram, class diagram, ERD, component diagram, state diagram, Gantt chart

## Pipeline Stages

| Stage | Role |
|---|---|
| Stage 8: Diagrams | Generate diagram definitions and assets |

## Dependencies

- `llm` — Diagram description generation via Provider Manager
- `shared` — Types, configuration

## Referenced In

- `docs/PIPELINE.md` — Stage 8
- `docs/ARCHITECTURE.md` — Diagram Engine subsystem
