from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from bookforge.core.enums import BookStatus, ExportFormat
from bookforge.core.value_objects import ISBN, URL, Version


class PublishingInfo(BaseModel):
    isbn: ISBN | None = None
    publisher: str | None = Field(default=None, max_length=500)
    imprint: str | None = Field(default=None, max_length=300)
    publish_date: datetime | None = None
    copyright_year: int | None = Field(default=None, ge=1900, le=2100)
    edition: int = Field(default=1, ge=1)
    format: ExportFormat = ExportFormat.PDF
    language: str = Field(default="en", min_length=2, max_length=10)
    page_count: int | None = Field(default=None, ge=1, le=100000)
    list_price_usd: float | None = Field(default=None, ge=0.0)
    rights: str = Field(default="All rights reserved", min_length=1, max_length=500)


class ReviewInfo(BaseModel):
    id: str = Field(default="", min_length=0, max_length=200)
    reviewer_id: str | None = Field(default=None, max_length=200)
    reviewer_name: str | None = Field(default=None, max_length=500)
    status: BookStatus = BookStatus.DRAFT
    comments: str | None = Field(default=None, max_length=50000)
    rating: int | None = Field(default=None, ge=1, le=5)
    revision_notes: list[str] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    version_reviewed: Version | None = None

    @field_validator("reviewer_name")
    @classmethod
    def _name_not_empty_if_set(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("reviewer_name must not be empty")
        return v


class ExportInfo(BaseModel):
    id: str = Field(default="", min_length=0, max_length=200)
    export_format: ExportFormat
    file_path: str = Field(min_length=1, max_length=2000)
    file_size_bytes: int | None = Field(default=None, ge=1)
    status: str = Field(default="pending", pattern=r"^(pending|processing|completed|failed)$")
    generated_at: datetime | None = None
    url: URL | None = None
    error_message: str | None = Field(default=None, max_length=5000)
    version: Version | None = None

    @field_validator("file_path")
    @classmethod
    def _file_path_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("file_path must not be empty")
        return stripped
