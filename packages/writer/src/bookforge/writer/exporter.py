from __future__ import annotations

import json
from typing import Any

from bookforge.writer.assembler import MarkdownAssembler
from bookforge.writer.models import DraftBook


class WritingExporter:
    def __init__(self, assembler: MarkdownAssembler | None = None) -> None:
        self._assembler = assembler or MarkdownAssembler()

    def to_markdown(self, draft: DraftBook) -> str:
        return self._assembler.assemble(draft)

    def to_dict(self, draft: DraftBook) -> dict[str, Any]:
        return {
            "title": draft.title,
            "subtitle": draft.subtitle,
            "topic": draft.topic,
            "chapter_count": draft.chapter_count,
            "word_count": draft.total_word_count,
            "estimated_minutes": draft.estimated_minutes,
            "quality": draft.quality.value,
            "status": draft.status.value,
            "chapters": [
                {
                    "title": ch.title,
                    "word_count": ch.word_count,
                    "status": ch.status.value,
                }
                for ch in draft.chapters
            ],
            "has_glossary": draft.glossary is not None,
            "has_references": draft.references is not None,
        }

    def to_json(self, draft: DraftBook, indent: int = 2) -> str:
        return json.dumps(self.to_dict(draft), indent=indent, default=str)

    def to_file(self, draft: DraftBook, path: str) -> str:
        markdown = self.to_markdown(draft)
        with open(path, "w", encoding="utf-8") as f:
            f.write(markdown)
        return path
