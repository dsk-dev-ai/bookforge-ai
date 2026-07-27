from __future__ import annotations

from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    DraftChapter,
    WritingConfig,
)
from bookforge.writer.prompt_builder import PromptBuilder
from bookforge.writer.prompt_renderer import PromptRenderer


class IntroductionWriter:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        prompt_renderer: PromptRenderer | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._prompt_renderer = prompt_renderer or PromptRenderer()

    async def write_introduction(
        self,
        chapter: DraftChapter,
        draft: DraftBook,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> DraftChapter:
        cfg = config or WritingConfig.default()
        research = getattr(draft, "research_summary", "")
        template = self._prompt_builder.introduction_prompt(
            topic=draft.topic,
            title=draft.title,
            chapter_title=chapter.title,
            chapter_goal=chapter.goal,
            research=str(research),
            target_words=cfg.target_word_count // 2,
        )
        system, user = template.compose()
        messages = self._prompt_renderer.render(system, user)
        prompt = self._prompt_renderer.format_messages_for_provider(messages)
        intro_content = await generator.generate(prompt, temperature=cfg.temperature)
        full_content = f"{intro_content}\n\n{chapter.content}" if chapter.content else intro_content
        return chapter.model_copy(update={"content": full_content})
