# `@bookforge/review`

> **Status: planned** — this subsystem is specified in `docs/ARCHITECTURE.md` and `docs/PIPELINE.md` for a future phase. No implementation ships yet. See [docs/ROADMAP.md](../../docs/ROADMAP.md).


Review Engine subsystem — content quality assurance.

## Responsibilities

- **Technical review** — Verifies factual accuracy and code correctness
- **Style review** — Checks tone, terminology, and formatting consistency
- **Structural review** — Validates logical flow, section ordering, completeness
- **Consistency review** — Ensures terminology consistency across chapters
- Produces structured `ReviewReport` with pass/fail per finding
- Supports manual review intervention via the API
- Manages the review→revise feedback loop (max 3 cycles)
- Tracks revision cycle count per chapter
- Part of the **Creation** phase of the pipeline (Stage 7)

## Review Stages

| Stage | Prompt Template | What It Checks |
|---|---|---|
| Technical | `technical-review` | Facts, code, claims |
| Style | `style-review` | Tone, terminology, formatting |
| Structural | `structural-review` | Flow, ordering, completeness |
| Consistency | `consistency-review` | Cross-chapter terminology |

## Dependencies

- `llm` — Content review via Provider Manager
- `shared` — Types, configuration

## Referenced In

- `docs/PIPELINE.md` — Stage 7
- `docs/ARCHITECTURE.md` — Review Engine subsystem
