from __future__ import annotations

from bookforge.writer.models import (
    BookDraft,
    ChapterDraft,
    ContentGenerator,
    SectionDraft,
    WritingConfig,
)
from bookforge.writer.prompt_builder import PromptBuilder
from bookforge.writer.prompt_renderer import PromptRenderer


class SectionWriter:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        prompt_renderer: PromptRenderer | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._prompt_renderer = prompt_renderer or PromptRenderer()

    async def write_section(
        self,
        section: SectionDraft,
        chapter_title: str,
        draft: BookDraft,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> SectionDraft:
        cfg = config or WritingConfig.default()
        research = getattr(draft, "research_summary", "")
        system, user = self._prompt_builder.build_section_prompt(
            book_title=draft.title,
            chapter_title=chapter_title,
            section_heading=section.heading,
            section_goal=section.goal if hasattr(section, "goal") else "",
            research=str(research),
            target_words=min(cfg.target_word_count, cfg.max_chunk_size_words),
        )
        messages = self._prompt_renderer.render(system, user)
        prompt = self._prompt_renderer.format_messages_for_provider(messages)
        content = await generator.generate(prompt, temperature=cfg.temperature)
        word_count = len(content.split())
        return SectionDraft(
            heading=section.heading,
            content=content,
            subsections=section.subsections,
            word_count=word_count,
            estimated_minutes=max(1, word_count // 200),
        )

    async def write_all_sections(
        self,
        draft: BookDraft,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> BookDraft:
        cfg = config or WritingConfig.default()
        updated_chapters: list[ChapterDraft] = []
        for chapter in draft.chapters:
            written_sections: list[SectionDraft] = []
            for section in chapter.sections:
                result = await self.write_section(
                    section, chapter.title, draft, generator, cfg
                )
                written_sections.append(result)
            updated_chapters.append(
                chapter.model_copy(update={"sections": written_sections})
            )
        return draft.model_copy(update={"chapters": updated_chapters})
