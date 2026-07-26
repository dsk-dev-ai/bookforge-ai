"""Pydantic Settings-based configuration for the LLM provider system."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Configuration settings for the LLM provider system.

    Loaded from environment variables with optional ``.env`` file support.
    Environment variables take precedence over defaults.
    """

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Provider selection
    provider: str = Field(default="nvidia", description="Primary LLM provider name")
    fallback_provider: str = Field(default="ollama", description="Fallback LLM provider name")
    default_model: str | None = Field(default=None, description="Default model for chat")

    # Retry
    max_retries: int = Field(default=3, description="Maximum retry attempts per request")
    retry_backoff_factor: float = Field(default=2.0, description="Exponential backoff multiplier")
    retry_max_delay: float = Field(default=60.0, description="Maximum backoff delay in seconds")
    retry_jitter: float = Field(default=0.25, description="Jitter fraction for retry delays")

    # Rate limiting
    rate_limit_requests_per_minute: int = Field(default=60, description="Max requests per minute per provider")
    rate_limit_tokens_per_minute: int = Field(default=100_000, description="Max tokens per minute per provider")

    # Health checking
    health_check_interval_seconds: float = Field(default=60.0, description="Interval between health checks")
    health_check_timeout_seconds: float = Field(default=10.0, description="Health check request timeout")

    # Circuit breaker
    circuit_breaker_threshold: int = Field(default=5, description="Failures before circuit opens")
    circuit_breaker_cooldown_seconds: float = Field(default=300.0, description="Cooldown before half-open")

    # Feature flags
    fallback_enabled: bool = Field(default=True, description="Enable provider fallback")


class ProviderSettings(BaseSettings):
    """Per-provider connection settings.

    Loaded from environment variables with provider-specific prefixes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # NVIDIA NIM
    nvidia_nim_api_key: str | None = Field(default=None, description="NVIDIA NIM API key")
    nvidia_nim_base_url: str = Field(
        default="http://localhost:8000",
        description="NVIDIA NIM base URL",
    )
    nvidia_nim_model: str = Field(
        default="meta/llama-3.1-70b-instruct",
        description="Default NVIDIA NIM model",
    )
    nvidia_nim_timeout_seconds: float = Field(default=120.0, description="NVIDIA request timeout")

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    ollama_model: str = Field(default="llama3.1", description="Default Ollama model")
    ollama_timeout_seconds: float = Field(default=120.0, description="Ollama request timeout")
