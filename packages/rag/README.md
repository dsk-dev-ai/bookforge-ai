# `@bookforge/rag`

Retrieval-Augmented Generation engine.

## Responsibilities

- Manages vector storage for book content embeddings
- Generates embeddings for chapters, sections, and concepts
- Retrieves relevant context for content generation queries
- Ensures cross-chapter consistency by surfacing related content
- Supports similarity search with configurable thresholds
- Manages embedding model configuration per provider

## Dependencies

- `llm` — Embedding generation via LLM providers
- `shared` — Types, configuration, utilities
