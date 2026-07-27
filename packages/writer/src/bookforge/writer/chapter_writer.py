from __future__ import annotations

from bookforge.writer.enums import WritingStatus
from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    DraftChapter,
    WritingConfig,
)
from bookforge.writer.prompt_builder import PromptBuilder
from bookforge.writer.prompt_renderer import PromptRenderer


class ChapterWriter:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        prompt_renderer: PromptRenderer | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._prompt_renderer = prompt_renderer or PromptRenderer()

    async def write_chapter(
        self,
        chapter: DraftChapter,
        draft: DraftBook,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> DraftChapter:
        cfg = config or WritingConfig.default()
        research = getattr(draft, "research_summary", "")
        template = self._prompt_builder.chapter_prompt(
            topic=draft.topic,
            title=draft.title,
            chapter_title=chapter.title,
            chapter_goal=chapter.goal,
            audience="developers",
            research=str(research),
            target_words=cfg.target_word_count,
        )
        system, user = template.compose()
        messages = self._prompt_renderer.render(system, user)
        prompt = self._prompt_renderer.format_messages_for_provider(messages)
        content = await generator.generate(prompt, temperature=cfg.temperature)
        word_count = len(content.split())
        return DraftChapter(
            title=chapter.title,
            goal=chapter.goal,
            content=content,
            sections=chapter.sections,
            word_count=word_count,
            estimated_minutes=max(1, word_count // 200),
            status=WritingStatus.COMPLETED,
        )

    async def write_all_chapters(
        self,
        draft: DraftBook,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> DraftBook:
        cfg = config or WritingConfig.default()
        written: list[DraftChapter] = []
        for chapter in draft.chapters:
            result = await self.write_chapter(chapter, draft, generator, cfg)
            written.append(result)
        return draft.model_copy(update={"chapters": written})
