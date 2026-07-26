# Security

> Security policies, best practices, and configuration for BookForge AI.

---

## Table of Contents

- [Overview](#overview)
- [API Key Management](#api-key-management)
- [Secrets Handling](#secrets-handling)
- [LLM Provider Security](#llm-provider-security)
- [Input Validation](#input-validation)
- [Rate Limiting](#rate-limiting)
- [Dependency Security](#dependency-security)

---

## Overview

BookForge AI handles sensitive data including LLM API keys and user content. Security is enforced at multiple layers: configuration, code, infrastructure, and CI/CD.

---

## API Key Management

- API keys for the REST API are stored as environment variables, never committed to the repository
- Production keys are managed through a secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager)
- Keys are scoped per environment and rotated regularly
- The `.env.example` file contains placeholder values only — real secrets are loaded from `.env` (gitignored)

```env
# .env.example — never contains real secrets
BOOKFORGE_API_KEY=replace-with-your-api-key
```

---

## Secrets Handling

| Secret | Storage | Access |
|---|---|---|
| LLM Provider API Keys | Environment variables | Worker process only |
| Database Credentials | Environment variables | API + Worker processes |
| API Authentication Keys | Environment variables | API process only |
| Session Secrets | Environment variables | API process only |

All secrets follow the principle of least privilege:
- Each service only has access to the secrets it requires
- Secrets are never logged, exposed in error messages, or included in responses
- `.env` files are gitignored and never committed

---

## LLM Provider Security

- API keys for NVIDIA NIM, OpenAI, Anthropic, and Ollama are stored in environment variables
- Keys are passed to provider adapters at initialisation, never exposed in prompts or responses
- All LLM API communication occurs over HTTPS
- Local Ollama instances communicate over HTTP on localhost only
- Provider responses are scanned for sensitive data patterns before storage

---

## Input Validation

- All API inputs are validated using Pydantic schemas
- String inputs are sanitised to prevent injection attacks
- Book topics are validated against the allowed list
- File uploads (if any) are scanned for size and type
- LLM prompt inputs are sanitised before template rendering

---

## Rate Limiting

| Layer | Limit | Enforcement |
|---|---|---|
| REST API | 100 requests/minute per API key | FastAPI middleware |
| LLM Provider | 60 requests/minute per provider | Token bucket in `llm` package |
| PDF Generation | 10 concurrent jobs | Worker concurrency limit |

Rate limit headers are returned on all API responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705387200
```

---

## Dependency Security

- Dependencies are pinned to specific versions in `pyproject.toml`
- Automated Dependabot scanning runs weekly on the default branch
- `ruff` security rules (`S` rules) are enabled in the linter configuration
- A `SECURITY.md` policy file documents how to report vulnerabilities
