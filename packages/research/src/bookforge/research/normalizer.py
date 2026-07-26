from __future__ import annotations

import re
from datetime import datetime
from hashlib import sha256

from bookforge.research.models import ResearchDocument, ResearchSection, ResearchSource


class ResearchNormalizer:
    """Normalizes raw ResearchSources into structured ResearchDocuments.

    Extracts sections from content, cleans text, and produces a
    normalized representation suitable for further pipeline stages.
    """

    _HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def normalize(self, source: ResearchSource) -> ResearchDocument:
        doc_id = self._make_doc_id(source)
        sections = self._extract_sections(source.content)
        cleaned = self._clean_content(source.content)

        return ResearchDocument(
            id=doc_id,
            source_id=source.id,
            title=source.title,
            content=cleaned,
            sections=sections,
            normalized_at=datetime.now(),
        )

    def normalize_batch(self, sources: list[ResearchSource]) -> list[ResearchDocument]:
        return [self.normalize(s) for s in sources]

    def _make_doc_id(self, source: ResearchSource) -> str:
        raw = f"{source.id}:{source.title}:{source.content[:200]}"
        return sha256(raw.encode()).hexdigest()[:16]

    def _extract_sections(self, content: str) -> list[ResearchSection]:
        sections: list[ResearchSection] = []
        lines = content.splitlines()
        current_heading: str | None = None
        current_body: list[str] = []
        stack: list[list[ResearchSection]] = [sections]
        stack_depth: list[int] = [0]

        for line in lines:
            m = self._HEADING_PATTERN.match(line)
            if m:
                if current_heading:
                    self._flush_section(current_heading, current_body, stack, stack_depth)
                    current_body = []
                level = len(m.group(1))
                current_heading = m.group(2).strip()
                while stack_depth and stack_depth[-1] >= level:
                    stack.pop()
                    stack_depth.pop()
                stack_depth.append(level)
                if not stack:
                    stack.append(sections)
                    stack_depth = [0]
            else:
                current_body.append(line)

        if current_heading:
            self._flush_section(current_heading, current_body, stack, stack_depth)

        return sections

    def _flush_section(
        self,
        heading: str,
        body: list[str],
        stack: list[list[ResearchSection]],
        stack_depth: list[int],
    ) -> None:
        section = ResearchSection(
            heading=heading,
            content="\n".join(body).strip(),
        )
        if stack:
            stack[-1].append(section)

    def _clean_content(self, content: str) -> str:
        cleaned = re.sub(r"\r\n", "\n", content)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = cleaned.strip()
        return cleaned
