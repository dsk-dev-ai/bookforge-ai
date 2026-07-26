from __future__ import annotations

from collections.abc import Sequence

from bookforge.planner.models import (
    BookBlueprint,
    BookOutline,
    ChapterPlan,
    SectionPlan,
    TopicCluster,
)
from bookforge.planner.strategies import (
    DependencyOrderedStrategy,
    DifficultyProgressionStrategy,
    PlanningStrategy,
    ProgressiveLearningStrategy,
    TopicClusteringStrategy,
)


class BookPlanner:
    def __init__(
        self,
        strategies: Sequence[PlanningStrategy] | None = None,
    ) -> None:
        self._strategies = list(strategies) if strategies else self._default_strategies()

    def _default_strategies(self) -> list[PlanningStrategy]:
        return [
            ProgressiveLearningStrategy(),
            DependencyOrderedStrategy(),
            DifficultyProgressionStrategy(),
            TopicClusteringStrategy(),
        ]

    @property
    def strategies(self) -> list[PlanningStrategy]:
        return list(self._strategies)

    def plan(self, blueprint: BookBlueprint) -> BookBlueprint:
        current = blueprint.model_copy()
        for strategy in self._strategies:
            current = strategy.apply(current)
        return current

    def generate_outline(
        self,
        topic: str,
        chapter_titles: list[str],
        summary: str = "",
    ) -> BookOutline:
        chapters = [
            ChapterPlan(
                title=t,
                goal=f"Explore {t}",
                learning_objectives=[f"Understand {t}"],
                estimated_pages=max(8.0, 20.0 / max(len(chapter_titles), 1)),
                estimated_minutes=max(30, 120 // max(len(chapter_titles), 1)),
                difficulty=0.3 + (0.7 * i / max(len(chapter_titles) - 1, 1)) if chapter_titles else 0.5,
            )
            for i, t in enumerate(chapter_titles)
        ]

        return BookOutline(
            title=topic,
            chapters=chapters,
            front_matter=[
                SectionPlan(heading="Preface", goal="Introduce the book", estimated_pages=2.0, estimated_minutes=10),
                SectionPlan(heading="Introduction", goal="Set the context", estimated_pages=4.0, estimated_minutes=20),
            ],
            back_matter=[
                SectionPlan(heading="Appendix", goal="Supplementary material", estimated_pages=5.0, estimated_minutes=25),
                SectionPlan(heading="Index", goal="Topic index", estimated_pages=3.0, estimated_minutes=0),
            ],
        )

    def create_blueprint(
        self,
        topic: str,
        outline: BookOutline,
    ) -> BookBlueprint:
        from bookforge.planner.models import DependencyEdge, DependencyGraph

        dep_edges: list[DependencyEdge] = []
        for ch in outline.chapters:
            for prereq in ch.prerequisites:
                dep_edges.append(DependencyEdge(from_chapter=prereq, to_chapter=ch.title, reason="prerequisite"))

        chapter_titles = [c.title for c in outline.chapters]
        total_pages = outline.total_pages
        total_minutes = outline.total_minutes

        return BookBlueprint(
            title=outline.title,
            topic=topic,
            outline=outline,
            estimated_pages=total_pages,
            estimated_chapters=outline.chapter_count,
            estimated_reading_minutes=total_minutes,
            difficulty=(
                sum(c.difficulty for c in outline.chapters) / max(len(outline.chapters), 1)
                if outline.chapters
                else 0.5
            ),
            dependency_graph=DependencyGraph(edges=dep_edges, chapter_titles=chapter_titles) if dep_edges else None,
            topic_clusters=[
                TopicCluster(name="Core Concepts", topics=chapter_titles, relevance_score=1.0)
            ],
        )
