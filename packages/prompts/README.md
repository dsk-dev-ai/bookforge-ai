# `@bookforge/prompts`

Prompt template management and versioning.

## Responsibilities

- Stores and manages versioned prompt templates
- Loads templates from YAML files and database records
- Renders templates with pipeline context variables
- Validates template variables against declared schemas
- Caches compiled templates for fast rendering
- Tracks template usage per pipeline event for reproducibility
- Supports template inheritance and partials

## Dependencies

- `shared` — Types, configuration, utilities
