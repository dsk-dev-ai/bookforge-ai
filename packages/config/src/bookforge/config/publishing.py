from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PublishingSettings(BaseSettings):
    """Publishing and export engine configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_PUBLISHING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(default=True, description="Enable publishing engine")
    output_dir: str = Field(default="./books", description="Default output directory for generated books")
    pdf_engine: str = Field(default="weasyprint", description="PDF rendering engine")
    epub_enabled: bool = Field(default=True, description="Enable EPUB generation")
    mobi_enabled: bool = Field(default=False, description="Enable MOBI generation")
    docx_enabled: bool = Field(default=True, description="Enable DOCX generation")
    html_enabled: bool = Field(default=True, description="Enable HTML generation")
    max_export_concurrency: int = Field(default=2, ge=1, le=10, description="Max concurrent export jobs")
    request_timeout_seconds: float = Field(default=300.0, ge=10.0, le=3600.0, description="Publishing request timeout")
