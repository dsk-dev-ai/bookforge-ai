from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ReviewSettings(BaseSettings):
    """Review engine configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_REVIEW_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(default=True, description="Enable review engine")
    min_reviewers: int = Field(default=1, ge=1, le=5, description="Min reviewers per review pass")
    max_reviewers: int = Field(default=3, ge=1, le=10, description="Max reviewers per review pass")
    request_timeout_seconds: float = Field(default=120.0, ge=10.0, le=600.0, description="Review request timeout")
    require_technical_review: bool = Field(default=True, description="Require technical accuracy review")
    require_style_review: bool = Field(default=True, description="Require style consistency review")
    require_structural_review: bool = Field(default=True, description="Require structural integrity review")
    auto_approve_threshold: float = Field(default=0.9, ge=0.0, le=1.0, description="Auto-approve score threshold")
    max_review_iterations: int = Field(default=3, ge=1, le=10, description="Max review-fix cycles")
