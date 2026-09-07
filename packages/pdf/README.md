# `@bookforge/pdf`

> **Status: planned** — this subsystem is specified in `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` for a future phase. No implementation ships yet. See [docs/ROADMAP.md](../../docs/ROADMAP.md).


Publishing Engine subsystem — PDF and EPUB compilation.

## Responsibilities

- Compiles formatted markdown into publication-ready PDF
- Compiles formatted markdown into EPUB ebook format
- Generates cover page from book metadata
- Renders table of contents with page numbers (PDF) or spine (EPUB)
- Applies consistent typography (fonts, spacing, margins, headers, footers)
- Embeds diagrams and images inline
- Generates PDF bookmarks for navigation
- Part of the **Production** phase of the pipeline (Stages 11-12)

## Pipeline Stages

| Stage | Role |
|---|---|
| Stage 11: PDF | Compile markdown to PDF |
| Stage 12: EPUB | Compile markdown to EPUB |

## Dependencies

- `markdown` — Input markdown content
- `shared` — Types, configuration

## Referenced In

- `docs/PIPELINE.md` — Stages 11-12
- `docs/ARCHITECTURE.md` — Publishing Engine subsystem
