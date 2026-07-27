from __future__ import annotations

from typing import Any

from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    DraftReferences,
    ReferenceEntry,
    WritingConfig,
)
from bookforge.writer.prompt_builder import PromptBuilder
from bookforge.writer.prompt_renderer import PromptRenderer


class ReferenceWriter:
    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        prompt_renderer: PromptRenderer | None = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._prompt_renderer = prompt_renderer or PromptRenderer()

    async def write_references(
        self,
        draft: DraftBook,
        generator: ContentGenerator,
        references: list[dict[str, str]] | None = None,
        config: WritingConfig | None = None,
    ) -> DraftBook:
        cfg = config or WritingConfig.default()
        if references is not None:
            if not references:
                return draft
            ref_list = references
        else:
            extracted = self._extract_references(draft)
            if not extracted:
                return draft
            ref_list = extracted

        template = self._prompt_builder.reference_prompt(
            topic=draft.topic,
            title=draft.title,
            references=ref_list,
        )
        system, user = template.compose()
        messages = self._prompt_renderer.render(system, user)
        prompt = self._prompt_renderer.format_messages_for_provider(messages)
        content = await generator.generate(prompt, temperature=cfg.temperature)
        ref_draft = DraftReferences(
            entries=[ReferenceEntry(title=r.get("title", ""), content="", category=r.get("category", "general")) for r in ref_list],
            content=content,
        )
        return draft.model_copy(update={"references": ref_draft})

    def _extract_references(self, draft: DraftBook) -> list[dict[str, str]]:
        refs: list[dict[str, str]] = []
        seen: set[str] = set()
        for ch in draft.chapters:
            for sec in ch.sections:
                self._extract_from_section(sec, seen, refs)
        return refs

    def _extract_from_section(
        self,
        section: Any,
        seen: set[str],
        refs: list[dict[str, str]],
    ) -> None:
        words = section.heading.split()
        for w in words:
            clean = w.strip(".,;:!?")
            if clean and clean[0].isupper() and clean.lower() not in seen and len(clean) > 3:
                seen.add(clean.lower())
                refs.append({"title": clean, "description": "", "category": "general"})
        for sub in section.subsections:
            self._extract_from_section(sub, seen, refs)
