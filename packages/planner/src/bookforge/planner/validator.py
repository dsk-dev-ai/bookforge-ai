from __future__ import annotations

from bookforge.planner.enums import ValidationSeverity
from bookforge.planner.models import BookBlueprint, BookOutline, ChapterPlan, SectionPlan


class ValidationMessage:
    def __init__(
        self,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        field: str = "",
        item_id: str = "",
    ) -> None:
        self.message = message
        self.severity = severity
        self.field = field
        self.item_id = item_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValidationMessage):
            return NotImplemented
        return (
            self.message == other.message
            and self.severity == other.severity
            and self.field == other.field
            and self.item_id == other.item_id
        )

    def __repr__(self) -> str:
        return (
            f"ValidationMessage(message={self.message!r}, "
            f"severity={self.severity!r}, field={self.field!r}, item_id={self.item_id!r})"
        )


class OutlineValidator:
    def validate_blueprint(self, blueprint: BookBlueprint) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []

        if not blueprint.outline:
            messages.append(ValidationMessage("Blueprint has no outline", ValidationSeverity.ERROR, "outline"))
            return messages

        messages.extend(self.validate_outline(blueprint.outline))
        messages.extend(self._check_dependencies(blueprint))
        messages.extend(self._check_cycles(blueprint))
        messages.extend(self._check_estimates(blueprint))

        return messages

    def validate_outline(self, outline: BookOutline) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []

        if not outline.title.strip():
            messages.append(ValidationMessage("Outline has empty title", ValidationSeverity.ERROR, "title"))

        if not outline.chapters:
            messages.append(ValidationMessage("Outline has no chapters", ValidationSeverity.ERROR, "chapters"))
            return messages

        messages.extend(self._check_duplicate_chapters(outline))
        messages.extend(self._check_empty_chapters(outline))

        for chapter in outline.chapters:
            messages.extend(self._validate_chapter(chapter))

        return messages

    def validate_chapter(self, chapter: ChapterPlan) -> list[ValidationMessage]:
        return self._validate_chapter(chapter)

    def _validate_chapter(self, chapter: ChapterPlan) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []

        if not chapter.title.strip():
            messages.append(ValidationMessage("Chapter has empty title", ValidationSeverity.ERROR, "title"))

        if not chapter.goal.strip():
            messages.append(ValidationMessage(f"Chapter '{chapter.title}' has no goal", ValidationSeverity.WARNING, "goal"))

        if not chapter.learning_objectives:
            messages.append(ValidationMessage(f"Chapter '{chapter.title}' has no learning objectives", ValidationSeverity.WARNING, "learning_objectives"))

        messages.extend(self._check_duplicate_sections(chapter))

        seen_headings: set[str] = set()
        for section in chapter.sections:
            messages.extend(self._validate_section(section, chapter.title, seen_headings))

        return messages

    def _validate_section(
        self,
        section: SectionPlan,
        chapter_title: str,
        seen_headings: set[str],
    ) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []

        if not section.heading.strip():
            messages.append(ValidationMessage("Section has empty heading", ValidationSeverity.ERROR, "section.heading", chapter_title))

        heading_lower = section.heading.lower().strip()
        if heading_lower in seen_headings:
            messages.append(ValidationMessage(f"Duplicate section heading '{section.heading}' in '{chapter_title}'", ValidationSeverity.WARNING, "section.heading", chapter_title))
        seen_headings.add(heading_lower)

        for sub in section.subsections:
            messages.extend(self._validate_section(sub, chapter_title, seen_headings))

        return messages

    def _check_duplicate_chapters(self, outline: BookOutline) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        seen: set[str] = set()
        for chapter in outline.chapters:
            title_lower = chapter.title.lower().strip()
            if title_lower in seen:
                messages.append(ValidationMessage(f"Duplicate chapter title '{chapter.title}'", ValidationSeverity.ERROR, "chapters"))
            seen.add(title_lower)
        return messages

    def _check_duplicate_sections(self, chapter: ChapterPlan) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        seen: set[str] = set()
        for section in chapter.sections:
            heading_lower = section.heading.lower().strip()
            if heading_lower in seen:
                messages.append(ValidationMessage(f"Duplicate section '{section.heading}' in chapter '{chapter.title}'", ValidationSeverity.WARNING, "sections"))
            seen.add(heading_lower)
        return messages

    def _check_empty_chapters(self, outline: BookOutline) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        for chapter in outline.chapters:
            if not chapter.sections and not chapter.goal.strip():
                messages.append(ValidationMessage(f"Chapter '{chapter.title}' is empty (no sections, no goal)", ValidationSeverity.WARNING, "chapters", chapter.title))
        return messages

    def _check_dependencies(self, blueprint: BookBlueprint) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        if not blueprint.outline:
            return messages

        chapter_titles = {c.title for c in blueprint.outline.chapters}

        for ch in blueprint.outline.chapters:
            for prereq in ch.prerequisites:
                if prereq not in chapter_titles:
                    messages.append(ValidationMessage(
                        f"Chapter '{ch.title}' has missing prerequisite '{prereq}'",
                        ValidationSeverity.ERROR,
                        "prerequisites",
                        ch.title,
                    ))

        return messages

    def _check_cycles(self, blueprint: BookBlueprint) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        if blueprint.dependency_graph and blueprint.dependency_graph.has_cycle():
            messages.append(ValidationMessage("Dependency graph contains a cycle", ValidationSeverity.ERROR, "dependency_graph"))
        return messages

    def _check_estimates(self, blueprint: BookBlueprint) -> list[ValidationMessage]:
        messages: list[ValidationMessage] = []
        if blueprint.estimated_pages <= 0:
            messages.append(ValidationMessage("Estimated pages is zero or negative", ValidationSeverity.WARNING, "estimated_pages"))
        if blueprint.estimated_chapters <= 0:
            messages.append(ValidationMessage("Estimated chapter count is zero or negative", ValidationSeverity.ERROR, "estimated_chapters"))
        return messages
