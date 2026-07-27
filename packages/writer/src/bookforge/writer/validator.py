from __future__ import annotations

import re

from bookforge.writer.enums import ValidationSeverity
from bookforge.writer.models import DraftBook, DraftSection, ValidationMessage


class ContentValidator:
    def validate(self, draft: DraftBook) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        messages.extend(self._check_empty_chapters(draft))
        messages.extend(self._check_empty_sections(draft))
        messages.extend(self._check_word_counts(draft))
        messages.extend(self._check_heading_structure(draft))
        messages.extend(self._check_front_back_matter(draft))
        messages.extend(self._check_duplicate_sections(draft))
        messages.extend(self._check_code_fences(draft))
        messages.extend(self._check_broken_markdown(draft))
        messages.extend(self._check_missing_references(draft))
        return messages

    def _check_empty_chapters(self, draft: DraftBook) -> list[ValidationMessage]:
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

    def _check_empty_sections(self, draft: DraftBook) -> list[ValidationMessage]:
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
        section: DraftSection,
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

    def _check_word_counts(self, draft: DraftBook) -> list[ValidationMessage]:
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

    def _check_heading_structure(self, draft: DraftBook) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            lines = (ch.content or "").split("\n")
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# "):
                    msgs.append(
                        ValidationMessage(
                            message=f"Chapter '{ch.title}' contains H1 headings (should use H2+)",
                            severity=ValidationSeverity.WARNING,
                            location=f"chapter:{ch.title}",
                        )
                    )
                    break
        return msgs

    def _check_front_back_matter(self, draft: DraftBook) -> list[ValidationMessage]:
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

    def _check_duplicate_sections(self, draft: DraftBook) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            seen: set[str] = set()
            for sec in ch.sections:
                key = sec.heading.lower().strip()
                if key in seen:
                    msgs.append(
                        ValidationMessage(
                            message=f"Duplicate section '{sec.heading}' in chapter '{ch.title}'",
                            severity=ValidationSeverity.ERROR,
                            location=f"chapter:{ch.title}/section:{sec.heading}",
                        )
                    )
                seen.add(key)
                self._check_nested_duplicates(sec, ch.title, seen, msgs)
        return msgs

    def _check_nested_duplicates(
        self,
        section: DraftSection,
        chapter_title: str,
        seen: set[str],
        msgs: list[ValidationMessage],
    ) -> None:
        for sub in section.subsections:
            key = sub.heading.lower().strip()
            if key in seen:
                msgs.append(
                    ValidationMessage(
                        message=f"Duplicate subsection '{sub.heading}' in chapter '{chapter_title}'",
                        severity=ValidationSeverity.ERROR,
                        location=f"chapter:{chapter_title}/section:{sub.heading}",
                    )
                )
            seen.add(key)
            self._check_nested_duplicates(sub, chapter_title, seen, msgs)

    def _check_code_fences(self, draft: DraftBook) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            content = ch.content or ""
            fences = re.findall(r"```(\S+)", content)
            for lang in fences:
                if lang and not lang.isidentifier():
                    msgs.append(
                        ValidationMessage(
                            message=f"Chapter '{ch.title}' has invalid code fence language: '{lang}'",
                            severity=ValidationSeverity.WARNING,
                            location=f"chapter:{ch.title}",
                        )
                    )
            opens = content.count("```")
            if opens % 2 != 0:
                msgs.append(
                    ValidationMessage(
                        message=f"Chapter '{ch.title}' has unclosed code fences",
                        severity=ValidationSeverity.ERROR,
                        location=f"chapter:{ch.title}",
                    )
                )
        return msgs

    def _check_broken_markdown(self, draft: DraftBook) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        for ch in draft.chapters:
            content = ch.content or ""
            lines = content.split("\n")
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("|---") and i > 0:
                    prev = lines[i - 1].strip()
                    if not prev or not re.search(r"\|", prev):
                        msgs.append(
                            ValidationMessage(
                                message=f"Chapter '{ch.title}' has orphaned table separator at line {i + 1}",
                                severity=ValidationSeverity.WARNING,
                                location=f"chapter:{ch.title}",
                            )
                        )
        return msgs

    def _check_missing_references(self, draft: DraftBook) -> list[ValidationMessage]:
        msgs: list[ValidationMessage] = []
        if not draft.references or not draft.references.content:
            all_content = " ".join(ch.content or "" for ch in draft.chapters)
            ref_keywords = ["see also", "as described in", "refer to", "more information"]
            has_ref_patterns = any(kw in all_content.lower() for kw in ref_keywords)
            if has_ref_patterns:
                msgs.append(
                    ValidationMessage(
                        message="Content references external resources but no references section found",
                        severity=ValidationSeverity.WARNING,
                        location="book",
                    )
                )
        return msgs
