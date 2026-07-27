from __future__ import annotations

from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    WritingConfig,
)
from bookforge.writer.prompt_builder import PromptBuilder
from bookforge.writer.prompt_renderer import PromptRenderer


class CodeExampleWriter:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        prompt_renderer: PromptRenderer | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._prompt_renderer = prompt_renderer or PromptRenderer()

    async def write_code_example(
        self,
        draft: DraftBook,
        generator: ContentGenerator,
        language: str,
        description: str,
        config: WritingConfig | None = None,
    ) -> str:
        cfg = config or WritingConfig.default()
        template = self._prompt_builder.code_example_prompt(
            topic=draft.topic,
            title=draft.title,
            language=language,
            description=description,
        )
        system, user = template.compose()
        messages = self._prompt_renderer.render(system, user)
        prompt = self._prompt_renderer.format_messages_for_provider(messages)
        return await generator.generate(prompt, temperature=min(cfg.temperature, 0.5))
