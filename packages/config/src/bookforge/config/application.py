from __future__ import annotations

from bookforge.config.enums import Environment
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentSettings(BaseSettings):
    """Environment identification and metadata settings."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Environment = Field(default=Environment.DEVELOPMENT, description="Runtime environment")


class ApplicationSettings(BaseSettings):
    """Core application settings — binding, API, and worker configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    name: str = Field(default="bookforge", description="Application name")
    version: str = Field(default="1.0.0", description="Application version string")
    debug: bool = Field(default=True, description="Enable debug mode")
    host: str = Field(default="0.0.0.0", description="API server bind host")
    port: int = Field(default=8000, ge=1, le=65535, description="API server bind port")
    workers: int = Field(default=4, ge=1, le=64, description="Number of worker processes")
    api_key: SecretStr | None = Field(default=None, description="API authentication key")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )
    request_timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0, description="Request timeout")
    max_request_size_mb: int = Field(default=10, ge=1, le=100, description="Max request body size in MB")
    rate_limit_rpm: int = Field(default=100, ge=1, le=100000, description="API rate limit per minute")

    @field_validator("host")
    @classmethod
    def _host_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("host must not be empty")
        return stripped
