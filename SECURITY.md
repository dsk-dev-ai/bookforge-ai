# Security

> Security policies and configuration.

## API Key Authentication

Bearer token in `Authorization` header. Scoped per project. Revocable independently.

## Secrets Management

LLM API keys, database credentials, and API keys stored as environment variables. Production secrets via HashiCorp Vault or AWS Secrets Manager. Never logged. Never exposed in responses.

## Rate Limiting

| Layer | Limit |
|---|---|
| REST API | 100 requests/min per API key |
| LLM Provider | 60 requests/min per provider |
| PDF Generation | 10 concurrent jobs |

## Data Protection

All API communication over HTTPS. LLM provider communication over HTTPS (local Ollama over HTTP on localhost only). Input sanitisation via Pydantic validation.
