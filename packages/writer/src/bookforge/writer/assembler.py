from __future__ import annotations

from bookforge.writer.models import BookDraft, ChapterDraft


class MarkdownAssembler:
    def assemble(self, draft: BookDraft) -> str:
        parts: list[str] = []
        parts.append(f"# {draft.title}")
        if draft.subtitle:
            parts.append(f"\n> {draft.subtitle}\n")

        for fm in draft.front_matter:
            parts.append(f"\n## {fm.title}\n")
            parts.append(fm.content)

        for ch in draft.chapters:
            parts.append(self._assemble_chapter(ch))

        for bm in draft.back_matter:
            parts.append(f"\n## {bm.title}\n")
            parts.append(bm.content)

        if draft.glossary and draft.glossary.content:
            parts.append("\n## Glossary\n")
            parts.append(draft.glossary.content)

        if draft.references and draft.references.content:
            parts.append("\n## References\n")
            parts.append(draft.references.content)

        return "\n\n".join(parts)

    def assemble_chapter_markdown(self, chapter: ChapterDraft) -> str:
        return self._assemble_chapter(chapter)

    def _assemble_chapter(self, chapter: ChapterDraft) -> str:
        parts: list[str] = []
        if chapter.content:
            parts.append(chapter.content)
        else:
            parts.append(f"## {chapter.title}")
            if chapter.goal:
                parts.append(f"\n> {chapter.goal}\n")
            for section in chapter.sections:
                parts.append(self._assemble_section(section, 3))
        return "\n\n".join(parts)

    def _assemble_section(self, section, level: int = 3) -> str:
        parts: list[str] = []
        prefix = "#" * level
        if section.content:
            parts.append(f"{prefix} {section.heading}\n")
            parts.append(section.content)
        else:
            parts.append(f"{prefix} {section.heading}")
        for sub in section.subsections:
            parts.append(self._assemble_section(sub, level + 1))
        return "\n\n".join(parts)
