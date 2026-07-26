from __future__ import annotations

from datetime import date

from bookforge.core.enums import ReferenceType
from bookforge.core.value_objects import URL
from pydantic import BaseModel, Field, field_validator, model_validator


class Reference(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    reference_type: ReferenceType = ReferenceType.BOOK
    title: str = Field(min_length=1, max_length=1000)
    authors: list[str] = Field(min_length=1)
    year: int = Field(ge=1, le=9999)
    publisher: str | None = Field(default=None, max_length=500)
    journal: str | None = Field(default=None, max_length=500)
    conference: str | None = Field(default=None, max_length=500)
    volume: str | None = Field(default=None, max_length=100)
    issue: str | None = Field(default=None, max_length=100)
    pages: str | None = Field(default=None, max_length=50)
    doi: str | None = Field(default=None, max_length=500)
    url: URL | None = None
    isbn: str | None = Field(default=None, max_length=20)
    arxiv_id: str | None = Field(default=None, max_length=50)
    accessed_date: date | None = None
    note: str | None = Field(default=None, max_length=5000)

    @field_validator("title")
    @classmethod
    def _title_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("reference title must not be empty")
        return stripped

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("reference id must not be empty")
        return stripped


class Citation(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    reference_id: str = Field(min_length=1, max_length=200)
    context: str | None = Field(default=None, max_length=5000)
    page_range: str | None = Field(default=None, max_length=50)
    chapter_number: int | None = Field(default=None, ge=1)
    section_number: str | None = Field(default=None, max_length=50)
    quotation: str | None = Field(default=None, max_length=10000)

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("citation id must not be empty")
        return stripped

    @field_validator("reference_id")
    @classmethod
    def _ref_id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("reference_id must not be empty")
        return stripped


class Bibliography(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    title: str = Field(default="References", min_length=1, max_length=500)
    references: list[Reference] = Field(default_factory=list)
    style: str = Field(default="apa", pattern=r"^(apa|mla|chicago|ieee|harvard|vancouver|turabian)$")

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("bibliography id must not be empty")
        return stripped

    @model_validator(mode="after")
    def _validate_unique_reference_ids(self) -> Bibliography:
        ids = [r.id for r in self.references]
        if len(ids) != len(set(ids)):
            seen: list[str] = []
            dupes: list[str] = []
            for i in ids:
                if i in seen:
                    dupes.append(i)
                seen.append(i)
            raise ValueError(f"Duplicate reference IDs in bibliography: {dupes}")
        return self

    def add_reference(self, ref: Reference) -> None:
        existing_ids = {r.id for r in self.references}
        if ref.id in existing_ids:
            raise ValueError(f"Reference id {ref.id} already exists")
        self.references.append(ref)

    def remove_reference(self, ref_id: str) -> None:
        self.references = [r for r in self.references if r.id != ref_id]

    def get_reference(self, ref_id: str) -> Reference | None:
        for r in self.references:
            if r.id == ref_id:
                return r
        return None
