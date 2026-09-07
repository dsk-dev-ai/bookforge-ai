# `@bookforge/prompts`

> **Status: planned** — this subsystem is specified in `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` for a future phase. No implementation ships yet. See [docs/ROADMAP.md](../../docs/ROADMAP.md).


Prompt Manager subsystem — template management and versioning.

## Responsibilities

- Stores and manages versioned prompt templates in the database
- Provides template catalog with 9+ templates for every pipeline stage
- Renders templates with pipeline context variables via Jinja2
- Validates template variables against declared schemas
- Tracks which template version generated which content (`prompt_usage` table)
- Caches compiled templates for fast rendering
- Supports template inheritance and partials
- Enables A/B testing of prompt versions

## Template Catalog

`chapter-writer`, `section-writer`, `code-example`, `technical-review`, `style-review`, `structural-review`, `consistency-review`, `outline-generator`, `research-synthesis`, `diagram-description`

## Dependencies

- `shared` — Types, configuration, Jinja2 rendering utilities

## Referenced In

- `docs/PROMPTS.md` — Full prompt management documentation
- `docs/ARCHITECTURE.md` — Prompt Manager subsystem
