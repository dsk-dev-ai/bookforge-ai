from __future__ import annotations

from bookforge.writer.models import (
    BookDraft,
    ChapterDraft,
    ContentGenerator,
    SectionDraft,
    WritingConfig,
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
        draft: BookDraft,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> WriterPipelineResult:
        cfg = config or self._config
        return await self._pipeline.run(draft, generator, cfg)

    async def write_chapter(
        self,
        draft: BookDraft,
        chapter_title: str,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> ChapterDraft:
        from bookforge.writer.chapter_writer import ChapterWriter

        chapter = next((c for c in draft.chapters if c.title == chapter_title), None)
        if chapter is None:
            raise ValueError(f"Chapter '{chapter_title}' not found in draft")
        writer = ChapterWriter()
        return await writer.write_chapter(chapter, draft, generator, config or self._config)

    async def write_section(
        self,
        draft: BookDraft,
        chapter_title: str,
        section_heading: str,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> SectionDraft:
        from bookforge.writer.section_writer import SectionWriter

        chapter = next((c for c in draft.chapters if c.title == chapter_title), None)
        if chapter is None:
            raise ValueError(f"Chapter '{chapter_title}' not found in draft")
        section = next((s for s in chapter.sections if s.heading == section_heading), None)
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
    ) -> BookDraft:
        chapters = [ChapterDraft(title=t) for t in chapter_titles]
        return BookDraft(
            title=title,
            subtitle=subtitle,
            topic=topic,
            chapters=chapters,
        )
