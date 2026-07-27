from __future__ import annotations

from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    DraftChapter,
    WritingConfig,
)
from bookforge.writer.prompt_builder import PromptBuilder
from bookforge.writer.prompt_renderer import PromptRenderer


class ConclusionWriter:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        prompt_renderer: PromptRenderer | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._prompt_renderer = prompt_renderer or PromptRenderer()

    async def write_conclusion(
        self,
        chapter: DraftChapter,
        draft: DraftBook,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> DraftChapter:
        cfg = config or WritingConfig.default()
        first_200 = chapter.content[:200] if chapter.content else ""
        template = self._prompt_builder.conclusion_prompt(
            topic=draft.topic,
            title=draft.title,
            chapter_title=chapter.title,
            chapter_summary=first_200,
        )
        system, user = template.compose()
        messages = self._prompt_renderer.render(system, user)
        prompt = self._prompt_renderer.format_messages_for_provider(messages)
        conclusion_content = await generator.generate(prompt, temperature=cfg.temperature)
        full_content = f"{chapter.content}\n\n{conclusion_content}" if chapter.content else conclusion_content
        return chapter.model_copy(update={"content": full_content})
