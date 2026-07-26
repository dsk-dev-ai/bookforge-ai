from __future__ import annotations

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class WriterSettings(BaseSettings):
    """Writing engine configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_WRITER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(default=True, description="Enable writing engine")
    max_chapters_per_batch: int = Field(default=3, ge=1, le=20, description="Max chapters to write in a batch")
    max_concurrent_chapters: int = Field(default=2, ge=1, le=10, description="Max concurrent chapter writes")
    request_timeout_seconds: float = Field(default=120.0, ge=10.0, le=600.0, description="Writer request timeout")
    max_section_depth: int = Field(default=3, ge=1, le=6, description="Max heading nesting depth")
    min_chunk_size_words: int = Field(default=500, ge=100, le=5000, description="Min words per generation chunk")
    max_chunk_size_words: int = Field(default=2000, ge=500, le=10000, description="Max words per generation chunk")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Default generation temperature")
    top_p: float = Field(default=0.95, ge=0.0, le=1.0, description="Default nucleus sampling top-p")

    @model_validator(mode="after")
    def _chunk_sizes_consistent(self) -> WriterSettings:
        if self.min_chunk_size_words > self.max_chunk_size_words:
            raise ValueError(
                f"min_chunk_size_words ({self.min_chunk_size_words}) must not exceed "
                f"max_chunk_size_words ({self.max_chunk_size_words})"
            )
        return self
