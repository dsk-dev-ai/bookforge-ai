from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel, Field

from bookforge.writer.enums import DraftQuality, WritingStatus


class DraftSection(BaseModel):
    heading: str = Field(description="Section heading")
    content: str = Field(default="", description="Section content in markdown")
    subsections: list[DraftSection] = Field(default_factory=list, description="Nested subsections")
    word_count: int = Field(default=0, ge=0, description="Section word count")
    estimated_minutes: int = Field(default=0, ge=0, description="Estimated reading time")

    @property
    def total_word_count(self) -> int:
        return self.word_count + sum(s.total_word_count for s in self.subsections)


class DraftChapter(BaseModel):
    title: str = Field(description="Chapter title")
    goal: str = Field(default="", description="Chapter goal")
    content: str = Field(default="", description="Full chapter content in markdown")
    sections: list[DraftSection] = Field(default_factory=list, description="Chapter sections")
    word_count: int = Field(default=0, ge=0, description="Chapter word count")
    estimated_minutes: int = Field(default=0, ge=0, description="Estimated reading time")
    status: WritingStatus = Field(default=WritingStatus.PENDING, description="Writing status")

    @property
    def total_word_count(self) -> int:
        return self.word_count + sum(s.total_word_count for s in self.sections)


class DraftFrontMatter(BaseModel):
    title: str = Field(description="Front matter title")
    content: str = Field(default="", description="Front matter content")
    word_count: int = Field(default=0, ge=0)


class DraftBackMatter(BaseModel):
    title: str = Field(description="Back matter title")
    content: str = Field(default="", description="Back matter content")
    word_count: int = Field(default=0, ge=0)


class GlossaryEntry(BaseModel):
    term: str = Field(description="Glossary term")
    definition: str = Field(description="Term definition")
    context: str = Field(default="", description="Context where term is used")


class DraftGlossary(BaseModel):
    entries: list[GlossaryEntry] = Field(default_factory=list, description="Glossary entries")
    content: str = Field(default="", description="Glossary markdown content")


class ReferenceEntry(BaseModel):
    title: str = Field(description="Reference title")
    content: str = Field(description="Reference content in markdown")
    category: str = Field(default="general", description="Reference category")


class DraftReferences(BaseModel):
    entries: list[ReferenceEntry] = Field(default_factory=list, description="Reference entries")
    content: str = Field(default="", description="References markdown content")


class DraftBook(BaseModel):
    title: str = Field(description="Book title")
    subtitle: str | None = Field(default=None, description="Book subtitle")
    topic: str = Field(description="Book topic")
    chapters: list[DraftChapter] = Field(default_factory=list, description="Chapter drafts")
    front_matter: list[DraftFrontMatter] = Field(default_factory=list, description="Front matter")
    back_matter: list[DraftBackMatter] = Field(default_factory=list, description="Back matter")
    glossary: DraftGlossary | None = Field(default=None, description="Glossary")
    references: DraftReferences | None = Field(default=None, description="References")
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


class WritingContext(BaseModel):
    book_title: str = Field(description="Book title")
    book_topic: str = Field(description="Book topic")
    target_audience: str = Field(default="developers", description="Target audience")
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    research_summary: str = Field(default="", description="Research summary for context")
    key_concepts: list[str] = Field(default_factory=list, description="Key concepts to cover")
    learning_objectives: list[str] = Field(default_factory=list, description="Learning objectives")
    style_guidelines: str = Field(default="technical", description="Writing style")

    @classmethod
    def from_blueprint(
        cls,
        blueprint: Any,
        research: Any | None = None,
    ) -> WritingContext:
        ctx = cls(
            book_title=blueprint.title,
            book_topic=blueprint.topic,
            target_audience=getattr(blueprint, "target_audience", "developers"),
            difficulty=getattr(blueprint, "difficulty", 0.5),
        )
        if research is not None:
            ctx.research_summary = getattr(research, "summary", "")
            ctx.key_concepts = [
                getattr(c, "name", str(c)) for c in getattr(research, "key_concepts", [])
            ]
            ctx.learning_objectives = getattr(research, "learning_objectives", [])
        return ctx


class WritingSession(BaseModel):
    session_id: str = Field(description="Session identifier")
    context: WritingContext = Field(description="Writing context")
    draft: DraftBook | None = Field(default=None, description="Current draft")
    started_at: str = Field(default="", description="Session start timestamp")
    updated_at: str = Field(default="", description="Last activity timestamp")
    completed_at: str | None = Field(default=None, description="Completion timestamp")
    status: WritingStatus = Field(default=WritingStatus.PENDING)


class WritingStatistics(BaseModel):
    total_chapters: int = Field(default=0)
    written_chapters: int = Field(default=0)
    total_sections: int = Field(default=0)
    written_sections: int = Field(default=0)
    total_word_count: int = Field(default=0)
    total_estimated_minutes: int = Field(default=0)
    validation_errors: int = Field(default=0)
    validation_warnings: int = Field(default=0)

    @classmethod
    def from_draft(cls, draft: DraftBook, messages: list[ValidationMessage] | None = None) -> WritingStatistics:
        msgs = messages or []
        return cls(
            total_chapters=draft.chapter_count,
            written_chapters=sum(1 for c in draft.chapters if c.status == WritingStatus.COMPLETED),
            total_sections=sum(len(c.sections) for c in draft.chapters),
            written_sections=sum(1 for c in draft.chapters for s in c.sections if s.content),
            total_word_count=draft.total_word_count,
            total_estimated_minutes=draft.estimated_minutes,
            validation_errors=sum(1 for m in msgs if m.severity == "error"),
            validation_warnings=sum(1 for m in msgs if m.severity == "warning"),
        )


class WritingMetrics(BaseModel):
    prompt_token_count: int = Field(default=0, description="Tokens used in prompts")
    completion_token_count: int = Field(default=0, description="Tokens in completions")
    total_llm_calls: int = Field(default=0, description="Number of LLM calls made")
    total_latency_ms: float = Field(default=0.0, description="Total LLM latency")
    average_latency_ms: float = Field(default=0.0, description="Average call latency")
    chapters_generated: int = Field(default=0)
    sections_generated: int = Field(default=0)
    retry_count: int = Field(default=0, description="Number of retries")
    failed_calls: int = Field(default=0)


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
    draft: DraftBook = Field(description="Book draft being written")
    status: WritingStatus = Field(default=WritingStatus.PENDING, description="Job status")
    current_stage: str | None = Field(default=None, description="Current pipeline stage")
    errors: list[str] = Field(default_factory=list, description="Job errors")
    created_at: str = Field(default="", description="Creation timestamp")
    updated_at: str = Field(default="", description="Last update timestamp")
