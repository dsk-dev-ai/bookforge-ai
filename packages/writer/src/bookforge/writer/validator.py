from __future__ import annotations

from bookforge.writer.enums import ValidationSeverity
from bookforge.writer.models import BookDraft, SectionDraft, ValidationMessage


class ContentValidator:
    def validate(self, draft: BookDraft) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        messages.extend(self._check_empty_chapters(draft))
        messages.extend(self._check_empty_sections(draft))
        messages.extend(self._check_word_counts(draft))
        messages.extend(self._check_heading_structure(draft))
        messages.extend(self._check_front_back_matter(draft))
        return messages

    def _check_empty_chapters(self, draft: BookDraft) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            if not ch.content and not ch.sections:
                msgs.append(
                    ValidationMessage(
                        message=f"Chapter '{ch.title}' has no content",
                        severity=ValidationSeverity.ERROR,
                        location=f"chapter:{ch.title}",
                    )
                )
        return msgs

    def _check_empty_sections(self, draft: BookDraft) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            for sec in ch.sections:
                if not sec.content:
                    msgs.append(
                        ValidationMessage(
                            message=f"Section '{sec.heading}' in chapter '{ch.title}' has no content",
                            severity=ValidationSeverity.WARNING,
                            location=f"chapter:{ch.title}/section:{sec.heading}",
                        )
                    )
                self._check_nested_empty(sec, ch.title, msgs)
        return msgs

    def _check_nested_empty(
        self,
        section: SectionDraft,
        chapter_title: str,
        msgs: list[ValidationMessage],
    ) -> None:
        for sub in section.subsections:
            if not sub.content:
                msgs.append(
                    ValidationMessage(
                        message=f"Subsection '{sub.heading}' in chapter '{chapter_title}' has no content",
                        severity=ValidationSeverity.WARNING,
                        location=f"chapter:{chapter_title}/section:{sub.heading}",
                    )
                )
            self._check_nested_empty(sub, chapter_title, msgs)

    def _check_word_counts(self, draft: BookDraft) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            if ch.word_count > 0 and ch.word_count < 50:
                msgs.append(
                    ValidationMessage(
                        message=f"Chapter '{ch.title}' is very short ({ch.word_count} words)",
                        severity=ValidationSeverity.WARNING,
                        location=f"chapter:{ch.title}",
                    )
                )
        return msgs

    def _check_heading_structure(self, draft: BookDraft) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            lines = (ch.content or "").split("\n")
            found_h1 = False
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# "):
                    found_h1 = True
                elif stripped.startswith("## "):
                    pass
            if found_h1:
                msgs.append(
                    ValidationMessage(
                        message=f"Chapter '{ch.title}' contains H1 headings (should use H2+)",
                        severity=ValidationSeverity.WARNING,
                        location=f"chapter:{ch.title}",
                    )
                )
        return msgs

    def _check_front_back_matter(self, draft: BookDraft) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for fm in draft.front_matter:
            if not fm.content:
                msgs.append(
                    ValidationMessage(
                        message=f"Front matter '{fm.title}' has no content",
                        severity=ValidationSeverity.WARNING,
                        location=f"front_matter:{fm.title}",
                    )
                )
        for bm in draft.back_matter:
            if not bm.content:
                msgs.append(
                    ValidationMessage(
                        message=f"Back matter '{bm.title}' has no content",
                        severity=ValidationSeverity.WARNING,
                        location=f"back_matter:{bm.title}",
                    )
                )
        return msgs
