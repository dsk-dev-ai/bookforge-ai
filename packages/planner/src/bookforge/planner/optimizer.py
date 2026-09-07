from __future__ import annotations

from bookforge.planner.models import (
    BookBlueprint,
    BookOutline,
    ChapterPlan,
    LearningPath,
    LearningStep,
    SectionPlan,
)


class SequenceOptimizer:
    def optimize(self, blueprint: BookBlueprint) -> BookBlueprint:
        if not blueprint.outline or not blueprint.outline.chapters:
            return blueprint

        b = blueprint.model_copy()
        if not b.outline:
            return blueprint

        b.outline.chapters = self._optimize_chapter_order(b.outline)
        b.learning_path = self._build_learning_path(b)
        return b

    def _optimize_chapter_order(self, outline: BookOutline) -> list[ChapterPlan]:
        chapters = list(outline.chapters)
        if not chapters:
            return chapters

        dep_map: dict[str, set[str]] = {}
        for ch in chapters:
            dep_map[ch.title] = set(ch.prerequisites)

        ordered: list[ChapterPlan] = []
        placed: set[str] = set()
        remaining = list(chapters)

        while remaining:
            candidates = [
                ch for ch in remaining
                if all(p in placed for p in dep_map.get(ch.title, set()))
            ]
            if not candidates:
                ordered.extend(remaining)
                break
            candidates.sort(key=lambda c: c.difficulty)
            chosen = candidates[0]
            ordered.append(chosen)
            placed.add(chosen.title)
            remaining.remove(chosen)

        return ordered

    def _build_learning_path(self, blueprint: BookBlueprint) -> LearningPath:
        if not blueprint.outline or not blueprint.outline.chapters:
            return LearningPath(title="", steps=[])

        path_steps: list[LearningStep] = []
        completed: set[str] = set()

        for i, chapter in enumerate(blueprint.outline.chapters):
            met = [p for p in chapter.prerequisites if p in completed]
            path_steps.append(
                LearningStep(
                    chapter_title=chapter.title,
                    order=i + 1,
                    estimated_minutes=chapter.estimated_minutes,
                    prerequisites_met=met,
                )
            )
            completed.add(chapter.title)

        return LearningPath(
            title=f"Learning path for {blueprint.title}",
            steps=path_steps,
            total_estimated_pages=blueprint.estimated_pages,
            total_estimated_minutes=sum(s.estimated_minutes for s in path_steps),
        )

    def _estimate_section_pages(
        self,
        sections: list[SectionPlan],
        level: int = 0,
    ) -> float:
        return sum(
            s.estimated_pages + self._estimate_section_pages(s.subsections, level + 1)
            for s in sections
        )
