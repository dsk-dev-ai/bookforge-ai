# `@bookforge/research`

Topic research and content gathering engine.

## Responsibilities

- Gathers structured research for a given technical topic
- Synthesises information from multiple LLM queries
- Extracts key concepts, definitions, prerequisites, and learning objectives
- Generates a chapter-level outline from research corpus
- Identifies cross-references and dependencies between concepts
- Produces a `ResearchCorpus` entity attached to the book

## Dependencies

- `llm` — Content generation via LLM providers
- `rag` — Context retrieval for related research
- `shared` — Types, configuration, utilities
