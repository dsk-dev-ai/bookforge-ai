from __future__ import annotations

import re

from bookforge.writer.models import DraftBook, DraftChapter


class MarkdownAssembler:
    def assemble(self, draft: DraftBook) -> str:
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

    def assemble_chapter_markdown(self, chapter: DraftChapter) -> str:
        return self._assemble_chapter(chapter)

    def _assemble_chapter(self, chapter: DraftChapter) -> str:
        parts: list[str] = []
        if chapter.content:
            parts.append(chapter.content)
        if chapter.sections:
            for section in chapter.sections:
                parts.append(self._assemble_section(section, 3))
        if not chapter.content and not chapter.sections:
            parts.append(f"## {chapter.title}")
            if chapter.goal:
                parts.append(f"\n> {chapter.goal}\n")
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

    def extract_headings(self, markdown: str) -> list[tuple[int, str]]:
        headings: list[tuple[int, str]] = []
        for line in markdown.split("\n"):
            stripped = line.strip()
            match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append((level, text))
        return headings

    def validate_markdown_structure(self, markdown: str) -> list[str]:
        issues: list[str] = []
        lines = markdown.split("\n")
        in_code_block = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block:
                    pass
            if not in_code_block and stripped.startswith("#"):
                if not re.match(r"^#{1,6}\s+\S", stripped):
                    issues.append(f"Line {i + 1}: Invalid heading format: {stripped}")
        return issues
