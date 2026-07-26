from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    """Security and authentication configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_SECURITY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: SecretStr | None = Field(default=None, description="API authentication key")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    jwt_secret: SecretStr | None = Field(default=None, description="JWT signing secret")
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_expire_minutes: int = Field(default=60, ge=1, le=1440, description="JWT expiration in minutes")
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_rpm: int = Field(default=100, ge=1, le=100000, description="Rate limit requests per minute")
    rate_limit_burst: int = Field(default=20, ge=1, le=1000, description="Rate limit burst size")
    allowed_hosts: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1"],
        description="Allowed HTTP hostnames",
    )
    enable_cors: bool = Field(default=True, description="Enable CORS")
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    encryption_key: SecretStr | None = Field(default=None, description="Database encryption key")
