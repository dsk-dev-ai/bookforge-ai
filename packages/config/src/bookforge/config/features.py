from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureFlags(BaseSettings):
    """Feature flag configuration for enabling/disabling subsystems."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_FEATURE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nvidia_enabled: bool = Field(default=True, description="Enable NVIDIA NIM provider")
    ollama_enabled: bool = Field(default=True, description="Enable Ollama provider")
    research_enabled: bool = Field(default=True, description="Enable research engine")
    writer_enabled: bool = Field(default=True, description="Enable writing engine")
    publishing_enabled: bool = Field(default=True, description="Enable publishing engine")
    dashboard_enabled: bool = Field(default=True, description="Enable web dashboard")
    experimental_enabled: bool = Field(default=False, description="Enable experimental features")
    fallback_enabled: bool = Field(default=True, description="Enable provider fallback")
    telemetry_enabled: bool = Field(default=False, description="Enable anonymous telemetry")
