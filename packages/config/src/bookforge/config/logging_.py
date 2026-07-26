from __future__ import annotations

from bookforge.config.enums import LogFormat, LogLevel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    """Structured logging configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    format: LogFormat = Field(default=LogFormat.JSON, description="Log output format")
    output_file: str | None = Field(default=None, description="Log file path (stdout if None)")
    include_trace_id: bool = Field(default=True, description="Include trace ID in log records")
    include_subsystem: bool = Field(default=True, description="Include subsystem tag in log records")
    include_caller_info: bool = Field(default=False, description="Include file/line in log records")
    max_file_size_mb: int = Field(default=100, ge=1, le=1024, description="Max log file size before rotation")
    max_file_count: int = Field(default=10, ge=1, le=100, description="Max rotated log files to retain")
