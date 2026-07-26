from __future__ import annotations

from bookforge.core.enums import CodeLanguage, DiagramType
from bookforge.core.value_objects import URL, ImageDimension
from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Paragraph(BaseModel):
    id: str = Field(default="", min_length=0, max_length=200)
    text: str = Field(min_length=1, max_length=50000)
    style: str | None = Field(default=None, max_length=100)
    is_code_block: bool = False
    is_list_item: bool = False
    list_type: str | None = Field(default=None, pattern=r"^(bullet|ordered|checklist)$")
    indent_level: int = Field(default=0, ge=0, le=10)

    @field_validator("text")
    @classmethod
    def _text_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("paragraph text must not be empty")
        return stripped


class CodeExample(BaseModel):
    id: str = Field(default="", min_length=0, max_length=200)
    code: str = Field(min_length=1, max_length=100000)
    language: CodeLanguage = CodeLanguage.PYTHON
    title: str | None = Field(default=None, max_length=300)
    explanation: str | None = Field(default=None, max_length=10000)
    filename: str | None = Field(default=None, max_length=300)
    highlight_lines: list[int] = Field(default_factory=list)
    show_line_numbers: bool = True
    is_executable: bool = False
    output: str | None = Field(default=None, max_length=50000)

    @field_validator("code")
    @classmethod
    def _code_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("code must not be empty")
        return stripped


class Diagram(BaseModel):
    id: str = Field(default="", min_length=0, max_length=200)
    diagram_type: DiagramType
    title: str | None = Field(default=None, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    source: str | None = Field(default=None, max_length=50000)
    caption: str | None = Field(default=None, max_length=1000)
    alt_text: str | None = Field(default=None, max_length=500)
    image_url: URL | None = None
    sort_order: int = Field(default=0, ge=0)

    @field_validator("title")
    @classmethod
    def _title_not_empty_if_set(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("diagram title must not be empty")
        return v


class ImageAsset(BaseModel):
    id: str = Field(default="", min_length=0, max_length=200)
    url: URL
    alt_text: str = Field(min_length=1, max_length=500)
    caption: str | None = Field(default=None, max_length=1000)
    dimensions: ImageDimension | None = None
    description: str | None = Field(default=None, max_length=5000)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("alt_text")
    @classmethod
    def _alt_text_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("alt_text must not be empty")
        return stripped


class Table(BaseModel):
    id: str = Field(default="", min_length=0, max_length=200)
    headers: list[str] = Field(min_length=1)
    rows: list[list[str]] = Field(min_length=1)
    caption: str | None = Field(default=None, max_length=1000)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("rows")
    @classmethod
    def _rows_match_header_count(cls, v: list[list[str]], info: ValidationInfo) -> list[list[str]]:
        if "headers" in info.data:
            expected = len(info.data["headers"])
            for i, row in enumerate(v):
                if len(row) != expected:
                    raise ValueError(
                        f"Row {i} has {len(row)} columns, expected {expected}"
                    )
        return v
