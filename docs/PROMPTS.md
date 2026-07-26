# Prompts

> Prompt template management.

## Template System

Versioned prompt templates managed by the Prompt Manager subsystem. Templates are stored in the database and rendered via Jinja2 with pipeline context variables.

## Template Catalog

| Template | Purpose | Used By |
|---|---|---|
| `outline-generator` | Generate chapter outline | Outline Engine |
| `research-synthesis` | Synthesise research | Research Manager |
| `chapter-writer` | Generate chapter content | Writing Engine |
| `section-writer` | Generate section content | Writing Engine |
| `code-example` | Generate code examples | Writing Engine |
| `technical-review` | Technical accuracy check | Review Engine |
| `style-review` | Style consistency check | Review Engine |
| `structural-review` | Structural check | Review Engine |
| `consistency-review` | Cross-chapter consistency | Review Engine |
| `diagram-description` | Generate diagram | Diagram Engine |

## Versioning

Semantic versioning. Usage tracked per pipeline event for reproducibility and A/B testing.
