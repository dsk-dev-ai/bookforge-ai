from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel, Field

from bookforge.writer.enums import DraftQuality, WritingStatus


class SectionDraft(BaseModel):
    heading: str = Field(description="Section heading")
    content: str = Field(default="", description="Section content in markdown")
    subsections: list[SectionDraft] = Field(default_factory=list, description="Nested subsections")
    word_count: int = Field(default=0, ge=0, description="Section word count")
    estimated_minutes: int = Field(default=0, ge=0, description="Estimated reading time")

    @property
    def total_word_count(self) -> int:
        return self.word_count + sum(s.total_word_count for s in self.subsections)


class ChapterDraft(BaseModel):
    title: str = Field(description="Chapter title")
    goal: str = Field(default="", description="Chapter goal")
    content: str = Field(default="", description="Full chapter content in markdown")
    sections: list[SectionDraft] = Field(default_factory=list, description="Chapter sections")
    word_count: int = Field(default=0, ge=0, description="Chapter word count")
    estimated_minutes: int = Field(default=0, ge=0, description="Estimated reading time")
    status: WritingStatus = Field(default=WritingStatus.PENDING, description="Writing status")

    @property
    def total_word_count(self) -> int:
        return self.word_count + sum(s.total_word_count for s in self.sections)


class FrontMatterDraft(BaseModel):
    title: str = Field(description="Front matter title")
    content: str = Field(default="", description="Front matter content")
    word_count: int = Field(default=0, ge=0)


class BackMatterDraft(BaseModel):
    title: str = Field(description="Back matter title")
    content: str = Field(default="", description="Back matter content")
    word_count: int = Field(default=0, ge=0)


class GlossaryEntry(BaseModel):
    term: str = Field(description="Glossary term")
    definition: str = Field(description="Term definition")
    context: str = Field(default="", description="Context where term is used")


class GlossaryDraft(BaseModel):
    entries: list[GlossaryEntry] = Field(default_factory=list, description="Glossary entries")
    content: str = Field(default="", description="Glossary markdown content")


class ReferenceEntry(BaseModel):
    title: str = Field(description="Reference title")
    content: str = Field(description="Reference content in markdown")
    category: str = Field(default="general", description="Reference category")


class ReferenceDraft(BaseModel):
    entries: list[ReferenceEntry] = Field(default_factory=list, description="Reference entries")
    content: str = Field(default="", description="References markdown content")


class BookDraft(BaseModel):
    title: str = Field(description="Book title")
    subtitle: str | None = Field(default=None, description="Book subtitle")
    topic: str = Field(description="Book topic")
    chapters: list[ChapterDraft] = Field(default_factory=list, description="Chapter drafts")
    front_matter: list[FrontMatterDraft] = Field(default_factory=list, description="Front matter")
    back_matter: list[BackMatterDraft] = Field(default_factory=list, description="Back matter")
    glossary: GlossaryDraft | None = Field(default=None, description="Glossary")
    references: ReferenceDraft | None = Field(default=None, description="References")
    word_count: int = Field(default=0, ge=0, description="Total word count")
    estimated_minutes: int = Field(default=0, ge=0, description="Total estimated reading time")
    quality: DraftQuality = Field(default=DraftQuality.DRAFT, description="Draft quality level")
    status: WritingStatus = Field(default=WritingStatus.PENDING, description="Overall writing status")

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    @property
    def total_word_count(self) -> int:
        wc = self.word_count
        wc += sum(c.total_word_count for c in self.chapters)
        wc += sum(f.word_count for f in self.front_matter)
        wc += sum(b.word_count for b in self.back_matter)
        if self.glossary:
            wc += len(self.glossary.content.split())
        if self.references:
            wc += len(self.references.content.split())
        return wc


class ValidationMessage(BaseModel):
    message: str = Field(description="Validation message")
    severity: str = Field(default="warning", description="Severity level")
    location: str | None = Field(default=None, description="Where the issue was found")


class WritingConfig(BaseModel):
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=4096, ge=1, le=100000, description="Max tokens per generation")
    max_chapters_per_batch: int = Field(default=3, ge=1, le=20, description="Chapters per batch")
    max_concurrent_chapters: int = Field(default=2, ge=1, le=10, description="Parallel chapter count")
    max_section_depth: int = Field(default=3, ge=1, le=6, description="Max heading nesting")
    min_chunk_size_words: int = Field(default=500, ge=100, le=5000, description="Min generation chunk")
    max_chunk_size_words: int = Field(default=2000, ge=500, le=10000, description="Max generation chunk")
    target_word_count: int = Field(default=800, ge=100, le=10000, description="Target words per section")

    @classmethod
    def default(cls) -> WritingConfig:
        return cls()


class ContentGenerator(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        ...

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class WritingJob(BaseModel):
    id: str = Field(description="Job identifier")
    draft: BookDraft = Field(description="Book draft being written")
    status: WritingStatus = Field(default=WritingStatus.PENDING, description="Job status")
    current_stage: str | None = Field(default=None, description="Current pipeline stage")
    errors: list[str] = Field(default_factory=list, description="Job errors")
    created_at: str = Field(default="", description="Creation timestamp")
    updated_at: str = Field(default="", description="Last update timestamp")
