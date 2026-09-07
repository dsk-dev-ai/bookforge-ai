# Contributing

> Guide for contributors.

## Setup

```bash
git clone https://github.com/dsk-dev-ai/bookforge-ai.git
cd bookforge-ai
make setup       # install dev deps for all packages (requires uv)
make lint && make test   # run quality gates
```

Requires Python >= 3.12 and [uv](https://docs.astral.sh/uv/).

## Process

1. Branch from `develop`: `feat/my-feature`
2. Make changes, follow coding standards
3. Run `make lint && make test`
4. Commit using Conventional Commits
5. Push and open PR against `develop`

## PR Checklist

- [ ] Code follows coding standards
- [ ] Tests added or updated
- [ ] Documentation updated if needed
- [ ] No TODOs or placeholder code
- [ ] CI passes
