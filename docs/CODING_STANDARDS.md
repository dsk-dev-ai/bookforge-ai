# Coding Standards

> Code conventions for BookForge AI.

## Python

- Version 3.12+
- Formatter: `ruff format` (100 char line length)
- Linter: `ruff check` with security rules enabled
- Types: `mypy --strict`
- Tests: `pytest` with 90%+ coverage

## Naming

| Element | Convention |
|---|---|
| Packages | `short_lower` |
| Modules | `snake_case` |
| Classes | `PascalCase` |
| Functions | `snake_case` |
| Constants | `UPPER_SNAKE` |

## Git

Conventional Commits: `type(scope): description`. Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

Branch from `develop`. PR into `develop`. Squash merge.
