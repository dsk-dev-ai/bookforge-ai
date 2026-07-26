from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class NvidiaSettings(BaseSettings):
    """NVIDIA NIM provider connection and model settings."""

    model_config = SettingsConfigDict(
        env_prefix="NVIDIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nvidia_nim_api_key: str | None = Field(default=None, description="NVIDIA NIM API key")
    nvidia_nim_base_url: str = Field(
        default="http://localhost:8000",
        description="NVIDIA NIM base URL",
    )
    nvidia_nim_model: str = Field(
        default="meta/llama-3.1-70b-instruct",
        description="Default NVIDIA NIM model",
    )
    nvidia_nim_timeout_seconds: float = Field(
        default=120.0, ge=1.0, le=600.0, description="NVIDIA request timeout",
    )
    nvidia_nim_max_retries: int = Field(default=3, ge=0, le=10, description="NVIDIA max retries")
    nvidia_nim_rate_limit_rpm: int = Field(default=60, ge=1, description="NVIDIA requests per minute")


class OllamaSettings(BaseSettings):
    """Ollama provider connection and model settings."""

    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL",
    )
    ollama_model: str = Field(default="llama3.1", description="Default Ollama model")
    ollama_timeout_seconds: float = Field(
        default=120.0, ge=1.0, le=600.0, description="Ollama request timeout",
    )
    ollama_max_retries: int = Field(default=3, ge=0, le=10, description="Ollama max retries")
    ollama_rate_limit_rpm: int = Field(default=30, ge=1, description="Ollama requests per minute")

    @field_validator("ollama_base_url")
    @classmethod
    def _base_url_must_not_end_with_slash(cls, v: str) -> str:
        return v.rstrip("/")


class ProviderSettings(BaseSettings):
    """Global provider routing and fallback settings."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_PROVIDER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    primary: str = Field(default="nvidia", description="Primary provider name")
    fallback: str = Field(default="ollama", description="Fallback provider name")
    default_model: str | None = Field(default=None, description="Default model across providers")
    max_retries: int = Field(default=3, ge=0, le=20, description="Default max retries per request")
    retry_backoff_factor: float = Field(default=2.0, ge=1.0, le=10.0, description="Exponential backoff multiplier")
    retry_max_delay: float = Field(default=60.0, ge=1.0, le=300.0, description="Max backoff delay in seconds")
    retry_jitter: float = Field(default=0.25, ge=0.0, le=1.0, description="Jitter fraction for retry delays")
    health_check_interval_seconds: float = Field(default=60.0, ge=5.0, le=3600.0, description="Health check interval")
    health_check_timeout_seconds: float = Field(default=10.0, ge=1.0, le=60.0, description="Health check timeout")
    circuit_breaker_threshold: int = Field(default=5, ge=1, le=100, description="Failures before circuit opens")
    circuit_breaker_cooldown_seconds: float = Field(default=300.0, ge=10.0, le=3600.0, description="Cooldown before half-open")
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, le=10000, description="Max requests per minute per provider")
    rate_limit_tokens_per_minute: int = Field(default=100_000, ge=1, le=10_000_000, description="Max tokens per minute per provider")
