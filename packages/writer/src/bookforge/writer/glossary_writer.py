from __future__ import annotations

from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    DraftGlossary,
    GlossaryEntry,
    WritingConfig,
)
from bookforge.writer.prompt_builder import PromptBuilder
from bookforge.writer.prompt_renderer import PromptRenderer


class GlossaryWriter:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        prompt_renderer: PromptRenderer | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._prompt_renderer = prompt_renderer or PromptRenderer()

    async def write_glossary(
        self,
        draft: DraftBook,
        generator: ContentGenerator,
        terms: list[dict[str, str]] | None = None,
        config: WritingConfig | None = None,
    ) -> DraftBook:
        cfg = config or WritingConfig.default()
        term_list = terms or [{"term": t, "context": ""} for t in self._extract_terms(draft)]
        if not term_list:
            return draft

        template = self._prompt_builder.glossary_prompt(
            topic=draft.topic,
            title=draft.title,
            terms=term_list,
        )
        system, user = template.compose()
        messages = self._prompt_renderer.render(system, user)
        prompt = self._prompt_renderer.format_messages_for_provider(messages)
        content = await generator.generate(prompt, temperature=cfg.temperature)
        glossary = DraftGlossary(
            entries=[GlossaryEntry(term=t.get("term", ""), definition="", context=t.get("context", "")) for t in term_list],
            content=content,
        )
        return draft.model_copy(update={"glossary": glossary})

    def _extract_terms(self, draft: DraftBook) -> list[str]:
        terms: list[str] = []
        for ch in draft.chapters:
            words = ch.title.split()
            for w in words:
                if w[0].isupper() and len(w) > 2:
                    terms.append(w)
        return list(set(terms))
