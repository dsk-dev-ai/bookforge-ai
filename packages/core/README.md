# `@bookforge/core`

Domain entities, business logic, and pipeline orchestration.

## Responsibilities

- Defines `Book`, `Chapter`, `Section`, `Author` domain entities
- Implements the pipeline state machine (draft → researching → ... → completed)
- Orchestrates pipeline stage execution across all packages
- Manages book lifecycle (CRUD, validation, status transitions)
- Coordinates data flow between research, writing, review, formatting, and rendering stages
- Provides the `Pipeline` and `Stage` abstractions for composable processing

## Dependencies

- `shared` — Types, configuration, utilities
- `llm` — Content generation via LLM providers
- `prompts` — Prompt template loading and rendering
- `research` — Topic research and outline generation
- `markdown` — Markdown processing and formatting
- `pdf` — PDF compilation
- `review` — Content review pipeline
- `rag` — Context retrieval
- `diagrams` — Diagram generation
- `images` — Image generation
