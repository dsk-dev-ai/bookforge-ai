# `@bookforge/markdown`

Markdown Engine subsystem — formatting and transformation.

## Responsibilities

- Parses raw markdown into structured AST
- Normalises heading hierarchy (enforces H1 → H2 → H3 ordering)
- Formats code blocks with consistent syntax annotations
- Generates table of contents from heading structure
- Applies typographic conventions (curly quotes, em dashes, smart spacing)
- Lints markdown for consistency issues
- Validates internal cross-references and links
- Part of the **Production** phase of the pipeline (Stage 10)

## Pipeline Stages

| Stage | Role |
|---|---|
| Stage 10: Markdown | Assemble and format the complete book |

## Dependencies

- `shared` — Types, configuration

## Referenced In

- `docs/PIPELINE.md` — Stage 10
- `docs/ARCHITECTURE.md` — Markdown Engine subsystem
