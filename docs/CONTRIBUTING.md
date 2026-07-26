# Contributing

> Guide for contributors.

## Setup

```bash
git clone https://github.com/your-org/bookforge-ai.git
cd bookforge-ai
python3.12 -m venv .venv
source .venv/bin/activate
cp .env.example .env
docker compose up -d postgres redis
make migrate
make lint && make test
```

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
