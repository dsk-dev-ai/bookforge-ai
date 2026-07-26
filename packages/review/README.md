# `@bookforge/review`

Content review and quality assurance pipeline.

## Responsibilities

- **Technical review** — Verifies factual accuracy and code correctness
- **Style review** — Checks tone, terminology, and formatting consistency
- **Structural review** — Validates logical flow and completeness
- **Consistency review** — Ensures terminology is consistent across chapters
- Produces structured `ReviewReport` with pass/fail per finding
- Supports manual review intervention via the API
- Manages the review→revise feedback loop

## Dependencies

- `llm` — Content review via LLM providers
- `shared` — Types, configuration, utilities
