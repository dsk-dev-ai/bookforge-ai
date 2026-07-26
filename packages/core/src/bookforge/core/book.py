from __future__ import annotations

from datetime import datetime

from bookforge.core.content import CodeExample, Diagram, ImageAsset, Paragraph, Table
from bookforge.core.enums import (
    Audience,
    BloomLevel,
    BookStatus,
    Difficulty,
    GenerationStage,
    Language,
)
from bookforge.core.reference import Reference
from bookforge.core.value_objects import ISBN, URL, Color, Version
from pydantic import BaseModel, Field, field_validator, model_validator


class BookMetadata(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    subtitle: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    language: Language = Language.ENGLISH
    cover_image_url: URL | None = None
    cover_color: Color | None = None
    tags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    series: str | None = Field(default=None, max_length=200)
    volume: int | None = Field(default=None, ge=1)
    edition: int = Field(default=1, ge=1)

    @field_validator("title")
    @classmethod
    def _title_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be empty")
        return stripped


class BookSpecification(BaseModel):
    target_audience: Audience = Audience.DEVELOPERS
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    estimated_page_count: int | None = Field(default=None, ge=1, le=10000)
    estimated_chapter_count: int | None = Field(default=None, ge=1, le=200)
    learning_objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    bloom_level: BloomLevel = BloomLevel.APPLY
    code_first: bool = True
    include_exercises: bool = True
    include_diagrams: bool = True


class BookSettings(BaseModel):
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    max_tokens_per_chunk: int = Field(default=4096, ge=256, le=32768)
    style_guide: str | None = Field(default=None, max_length=10000)
    tone: str = Field(default="professional", min_length=1, max_length=100)
    verbosity: str = Field(default="balanced", pattern=r"^(concise|balanced|detailed)$")
    use_active_voice: bool = True
    include_code_snippets: bool = True
    code_style: str = Field(default="modern", min_length=1, max_length=100)


class BookConfiguration(BaseModel):
    status: BookStatus = BookStatus.DRAFT
    stage: GenerationStage = GenerationStage.CREATED
    is_locked: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: datetime | None = None
    version: Version = Version(major=0, minor=1, patch=0)
    generation_model: str | None = Field(default=None, max_length=200)
    review_model: str | None = Field(default=None, max_length=200)


class Section(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    heading: str = Field(min_length=1, max_length=500)
    heading_level: int = Field(default=2, ge=1, le=6)
    paragraphs: list[Paragraph] = Field(default_factory=list)
    code_examples: list[CodeExample] = Field(default_factory=list)
    diagrams: list[Diagram] = Field(default_factory=list)
    images: list[ImageAsset] = Field(default_factory=list)
    tables: list[Table] = Field(default_factory=list)
    subsections: list[Section] = Field(default_factory=list)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("heading")
    @classmethod
    def _heading_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("heading must not be empty")
        return stripped

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("section id must not be empty")
        return stripped


class Chapter(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    number: int = Field(ge=1, le=500)
    title: str = Field(min_length=1, max_length=500)
    introduction: str | None = Field(default=None, max_length=10000)
    summary: str | None = Field(default=None, max_length=10000)
    sections: list[Section] = Field(default_factory=list)
    estimated_page_count: int | None = Field(default=None, ge=1, le=500)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("title")
    @classmethod
    def _title_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("chapter title must not be empty")
        return stripped

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("chapter id must not be empty")
        return stripped


class Book(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    metadata: BookMetadata
    specification: BookSpecification = BookSpecification()
    settings: BookSettings = BookSettings()
    configuration: BookConfiguration = BookConfiguration()
    chapters: list[Chapter] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
    glossary_terms: dict[str, str] = Field(default_factory=dict)
    isbn: ISBN | None = None
    page_count: int | None = Field(default=None, ge=1, le=100000)

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("book id must not be empty")
        return stripped

    @model_validator(mode="after")
    def _validate_unique_chapter_numbers(self) -> Book:
        numbers = [ch.number for ch in self.chapters]
        if len(numbers) != len(set(numbers)):
            seen: list[int] = []
            dupes: list[int] = []
            for n in numbers:
                if n in seen:
                    dupes.append(n)
                seen.append(n)
            raise ValueError(f"Duplicate chapter numbers: {dupes}")
        return self

    def add_chapter(self, chapter: Chapter) -> None:
        existing_numbers = {ch.number for ch in self.chapters}
        if chapter.number in existing_numbers:
            raise ValueError(f"Chapter number {chapter.number} already exists")
        existing_ids = {ch.id for ch in self.chapters}
        if chapter.id in existing_ids:
            raise ValueError(f"Chapter id {chapter.id} already exists")
        self.chapters.append(chapter)

    def remove_chapter(self, chapter_id: str) -> None:
        self.chapters = [ch for ch in self.chapters if ch.id != chapter_id]

    def get_chapter_by_number(self, number: int) -> Chapter | None:
        for ch in self.chapters:
            if ch.number == number:
                return ch
        return None

    def get_chapter(self, chapter_id: str) -> Chapter | None:
        for ch in self.chapters:
            if ch.id == chapter_id:
                return ch
        return None

    def total_estimated_pages(self) -> int:
        return sum(ch.estimated_page_count or 0 for ch in self.chapters)


class Project(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    books: list[Book] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: Version = Version(major=0, minor=1, patch=0)

    @field_validator("name")
    @classmethod
    def _name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("project name must not be empty")
        return stripped

    @model_validator(mode="after")
    def _validate_no_duplicate_ids(self) -> Project:
        all_ids: list[str] = []
        for book in self.books:
            all_ids.append(book.id)
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("Duplicate book IDs detected across project")
        return self

    def add_book(self, book: Book) -> None:
        existing_ids = {b.id for b in self.books}
        if book.id in existing_ids:
            raise ValueError(f"Book id {book.id} already exists in project")
        self.books.append(book)

    def remove_book(self, book_id: str) -> None:
        self.books = [b for b in self.books if b.id != book_id]

    def get_book(self, book_id: str) -> Book | None:
        for b in self.books:
            if b.id == book_id:
                return b
        return None
