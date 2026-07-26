# `@bookforge/markdown`

Markdown processing, transformation, and formatting.

## Responsibilities

- Parses raw markdown content into structured AST
- Normalises heading hierarchy (enforces H1 → H2 → H3 ordering)
- Formats code blocks with syntax annotations
- Generates table of contents from heading structure
- Applies typographic conventions (quotes, dashes, spacing)
- Lints markdown for consistency issues
- Transforms content between markdown variants
- Validates internal cross-references and links

## Dependencies

- `shared` — Types, configuration, utilities
