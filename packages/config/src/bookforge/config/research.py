from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ResearchSettings(BaseSettings):
    """Research engine configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_RESEARCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(default=True, description="Enable research engine")
    max_sources_per_topic: int = Field(default=10, ge=1, le=100, description="Max sources to gather per topic")
    max_concurrent_requests: int = Field(default=5, ge=1, le=50, description="Max concurrent research requests")
    request_timeout_seconds: float = Field(default=30.0, ge=1.0, le=120.0, description="Research request timeout")
    cache_ttl_seconds: int = Field(default=3600, ge=0, le=86400, description="Research cache TTL in seconds")
    min_source_quality_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum source quality threshold")
