from __future__ import annotations

from typing import Any

from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    DraftChapter,
    DraftSection,
    WritingConfig,
    WritingContext,
    WritingStatistics,
)
from bookforge.writer.pipeline import WriterPipeline, WriterPipelineResult


class WriterEngine:
    def __init__(
        self,
        pipeline: WriterPipeline | None = None,
        config: WritingConfig | None = None,
    ) -> None:
        self._pipeline = pipeline or WriterPipeline()
        self._config = config or WritingConfig.default()

    async def write(
        self,
        draft: DraftBook,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
        context: WritingContext | None = None,
    ) -> WriterPipelineResult:
        cfg = config or self._config
        return await self._pipeline.run(draft, generator, cfg, context=context)

    async def write_from_blueprint(
        self,
        blueprint: Any,
        generator: ContentGenerator,
        research: Any | None = None,
        config: WritingConfig | None = None,
    ) -> WriterPipelineResult:

        context = WritingContext.from_blueprint(blueprint, research)
        chapter_titles = []
        outline = getattr(blueprint, "outline", None)
        if outline and hasattr(outline, "chapters"):
            chapter_titles = [c.title for c in outline.chapters]
        if not chapter_titles:
            chapter_titles = [f"Chapter {i + 1}" for i in range(getattr(blueprint, "estimated_chapters", 1))]
        draft = DraftBook(
            title=blueprint.title,
            subtitle=getattr(blueprint, "subtitle", None),
            topic=blueprint.topic,
            chapters=[DraftChapter(title=t) for t in chapter_titles],
        )
        return await self._pipeline.run(draft, generator, config or self._config, context=context)

    async def write_chapter(
        self,
        draft: DraftBook,
        chapter_title: str,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> DraftChapter:
        from bookforge.writer.chapter_writer import ChapterWriter

        chapter = next((c for c in draft.chapters if c.title == chapter_title), None)
        if chapter is None:
            raise ValueError(f"Chapter '{chapter_title}' not found in draft")
        writer = ChapterWriter()
        return await writer.write_chapter(chapter, draft, generator, config or self._config)

    def _find_section(
        self,
        sections: list[DraftSection],
        heading: str,
    ) -> DraftSection | None:
        for s in sections:
            if s.heading == heading:
                return s
            found = self._find_section(s.subsections, heading)
            if found is not None:
                return found
        return None

    async def write_section(
        self,
        draft: DraftBook,
        chapter_title: str,
        section_heading: str,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> DraftSection:
        from bookforge.writer.section_writer import SectionWriter

        chapter = next((c for c in draft.chapters if c.title == chapter_title), None)
        if chapter is None:
            raise ValueError(f"Chapter '{chapter_title}' not found in draft")
        section = self._find_section(chapter.sections, section_heading)
        if section is None:
            raise ValueError(f"Section '{section_heading}' not found in chapter '{chapter_title}'")
        writer = SectionWriter()
        return await writer.write_section(section, chapter_title, draft, generator, config or self._config)

    def create_draft(
        self,
        title: str,
        topic: str,
        chapter_titles: list[str],
        subtitle: str | None = None,
    ) -> DraftBook:
        chapters = [DraftChapter(title=t) for t in chapter_titles]
        return DraftBook(
            title=title,
            subtitle=subtitle,
            topic=topic,
            chapters=chapters,
        )

    def compute_statistics(
        self,
        draft: DraftBook,
        messages: list[Any] | None = None,
    ) -> WritingStatistics:
        return WritingStatistics.from_draft(draft, messages)
