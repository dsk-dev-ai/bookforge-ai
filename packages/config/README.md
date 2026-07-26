# `@bookforge/config`

Global configuration system for BookForge AI.

All application settings are obtained through this package. No module reads environment variables directly.

## Usage

```python
from bookforge.config import load_config, Environment

config = load_config()

# Access any settings group
host = config.application.host
port = config.application.port
log_level = config.logging.level
db_url = config.storage.local_path
nvidia_model = config.nvidia.nim_model
research_enabled = config.features.research_enabled

# Detect environment
env = config.environment.env
if env == Environment.PRODUCTION:
    ...
```

## Settings Groups

| Group | Class | Env Prefix | Description |
|---|---|---|---|
| Environment | `EnvironmentSettings` | `BOOKFORGE_` | Runtime environment detection |
| Application | `ApplicationSettings` | `BOOKFORGE_APP_` | Host, port, workers, CORS, rate limits |
| Feature Flags | `FeatureFlags` | `BOOKFORGE_FEATURE_` | Enable/disable subsystems and experiments |
| Provider | `ProviderSettings` | `BOOKFORGE_PROVIDER_` | Provider routing, retry, circuit breaker, health |
| NVIDIA | `NvidiaSettings` | `NVIDIA_` | NVIDIA NIM connection and model settings |
| Ollama | `OllamaSettings` | `OLLAMA_` | Ollama connection and model settings |
| Research | `ResearchSettings` | `BOOKFORGE_RESEARCH_` | Research engine concurrency, cache, quality |
| Writer | `WriterSettings` | `BOOKFORGE_WRITER_` | Writing engine batch size, chunk size, temperature |
| Review | `ReviewSettings` | `BOOKFORGE_REVIEW_` | Review engine passes, thresholds, iterations |
| Publishing | `PublishingSettings` | `BOOKFORGE_PUBLISHING_` | Export formats, output directory, PDF engine |
| Logging | `LoggingSettings` | `BOOKFORGE_LOG_` | Log level, format, file rotation, trace IDs |
| Storage | `StorageSettings` | `BOOKFORGE_STORAGE_` | Local/S3/GCS/Azure storage configuration |
| Security | `SecuritySettings` | `BOOKFORGE_SECURITY_` | API keys, JWT, CORS, rate limiting |

## Feature Flags

All flags are disabled/enabled via environment variables:

| Variable | Default | Description |
|---|---|---|
| `BOOKFORGE_FEATURE_NVIDIA_ENABLED` | `true` | Enable NVIDIA NIM provider |
| `BOOKFORGE_FEATURE_OLLAMA_ENABLED` | `true` | Enable Ollama provider |
| `BOOKFORGE_FEATURE_RESEARCH_ENABLED` | `true` | Enable research engine |
| `BOOKFORGE_FEATURE_WRITER_ENABLED` | `true` | Enable writing engine |
| `BOOKFORGE_FEATURE_PUBLISHING_ENABLED` | `true` | Enable publishing engine |
| `BOOKFORGE_FEATURE_DASHBOARD_ENABLED` | `true` | Enable web dashboard |
| `BOOKFORGE_FEATURE_EXPERIMENTAL_ENABLED` | `false` | Enable experimental features |
| `BOOKFORGE_FEATURE_FALLBACK_ENABLED` | `true` | Enable provider fallback |
| `BOOKFORGE_FEATURE_TELEMETRY_ENABLED` | `false` | Enable anonymous telemetry |

## Environment Detection

```python
from bookforge.config.environment import EnvironmentDetector

detector = EnvironmentDetector()
env = detector.detect()  # Environment.DEVELOPMENT, .TESTING, .STAGING, .PRODUCTION
```

Detection order: `BOOKFORGE_ENV` → `APP_ENV` → `ENVIRONMENT` → fallback to `development`.

## Validation

```python
from bookforge.config.validator import validate_settings, assert_valid_config

errors = validate_settings(settings)        # returns list of error dicts
assert_valid_config(settings)               # raises ConfigValidationError
```

## Configuration

Settings are loaded from:

1. Environment variables (highest priority)
2. `.env` file
3. Default values (lowest priority)

```text
# .env
BOOKFORGE_ENV=production
BOOKFORGE_APP_NAME=bookforge
BOOKFORGE_APP_PORT=8080
BOOKFORGE_FEATURE_EXPERIMENTAL_ENABLED=true
NVIDIA_NIM_API_KEY=nvapi-abc123
```

## Requirements

```text
pydantic>=2.0
pydantic-settings>=2.0
```
