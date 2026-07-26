# Coding Standards

> Code style, conventions, and quality gates for BookForge AI.

---

## Table of Contents

- [Overview](#overview)
- [Language and Runtime](#language-and-runtime)
- [Python Style Guide](#python-style-guide)
- [Type Annotations](#type-annotations)
- [Documentation](#documentation)
- [Testing](#testing)
- [Git Conventions](#git-conventions)
- [Code Review](#code-review)
- [CI/CD Quality Gates](#cicd-quality-gates)

---

## Overview

This document defines the coding standards for all Python code in the BookForge AI repository. Adherence is enforced through automated CI checks and code review.

---

## Language and Runtime

- **Python version:** 3.12+
- **Package manager:** UV or pip
- **Virtual environment:** `.venv` (gitignored)
- **Dependency management:** `pyproject.toml` with exact version pins

---

## Python Style Guide

### Formatting

- **Tool:** `ruff format`
- **Line length:** 100 characters
- **Quotes:** Double quotes for strings
- **Indentation:** 4 spaces (no tabs)

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Packages | `short_lower` | `llm`, `markdown` |
| Modules | `snake_case` | `provider_base.py` |
| Classes | `PascalCase` | `LLMProvider` |
| Functions | `snake_case` | `generate_content()` |
| Variables | `snake_case` | `chapter_content` |
| Constants | `UPPER_SNAKE` | `MAX_RETRY_COUNT` |
| Private | `_leading_underscore` | `_normalise_response()` |
| Type params | `PascalCase` | `T`, `TResponse` |

### Imports

Ordered as:
1. Standard library
2. Third-party libraries
3. Local packages

```python
import uuid
from collections.abc import AsyncIterator

import httpx
from pydantic import BaseModel

from bookforge.shared.types import Message
```

---

## Type Annotations

- Every function signature must include type annotations for all parameters and return types
- Use `from __future__ import annotations` to enable deferred evaluation
- Prefer `collections.abc` types over `typing` equivalents (e.g., `Sequence` over `typing.Sequence`)
- Use `|` syntax for union types (Python 3.10+): `str | None`

```python
from __future__ import annotations

from collections.abc import Sequence


def generate_chapters(
    topic: str,
    count: int,
    style: str | None = None,
) -> Sequence[Chapter]:
    ...
```

---

## Documentation

### Docstrings

All public modules, classes, and functions must have Google-style docstrings:

```python
def generate_content(
    prompt: str,
    max_tokens: int = 2048,
) -> str:
    """Generate content using the configured LLM provider.

    Args:
        prompt: The input prompt for generation.
        max_tokens: Maximum tokens in the response.

    Returns:
        The generated text content.

    Raises:
        ProviderError: If the LLM provider returns an error.
    """
    ...
```

### Comments

- Comments explain *why*, not *what* — the code should be self-documenting
- Avoid commented-out code; delete it instead
- Inline comments are rare and used only for non-obvious logic

---

## Testing

- **Framework:** pytest
- **Coverage target:** 90%+ for business logic packages
- **Test location:** `tests/` directory at each package root
- **Naming:** `test_<module>_<behaviour>.py`
- **Fixtures:** Use `conftest.py` for shared fixtures

### Test Requirements

- Every public function must have at least one test
- LLM calls must be mocked — no real API calls in tests
- Database tests use a test PostgreSQL instance or SQLite in-memory
- CI runs tests on every push and pull request

---

## Git Conventions

### Branching Strategy

```
main          ─── Production-ready code
develop       ─── Integration branch for features
feat/*        ─── Feature branches (branch from develop)
fix/*         ─── Bug fix branches
docs/*        ─── Documentation-only changes
chore/*       ─── Maintenance, CI, dependencies
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Type | Usage |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `refactor` | Code refactoring |
| `test` | Test additions or changes |
| `chore` | Maintenance, CI, dependencies |
| `style` | Code style changes (formatting, linting) |

Examples:
```
feat(core): add pipeline state machine
docs(api): document book creation endpoint
fix(llm): handle rate limit retry backoff correctly
```

---

## Code Review

- All changes must be submitted as pull requests
- Every PR requires at least one approval before merging
- PRs should be small and focused on a single concern
- CI must pass (lint, type-check, test) before review

---

## CI/CD Quality Gates

The CI pipeline enforces:

| Check | Tool | Fail on |
|---|---|---|
| Format | `ruff format --check` | Formatting violations |
| Lint | `ruff check` | Any lint error |
| Types | `mypy --strict` | Type errors |
| Tests | `pytest --cov` | Test failures or coverage below 90% |
| Security | `ruff check --select S` | Security rule violations |
