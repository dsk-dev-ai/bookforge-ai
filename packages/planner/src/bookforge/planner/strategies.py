from __future__ import annotations

from abc import ABC, abstractmethod

from bookforge.planner.models import (
    BookBlueprint,
    ChapterPlan,
    DependencyEdge,
    DependencyGraph,
    LearningPath,
    LearningStep,
    TopicCluster,
)


class PlanningStrategy(ABC):
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def apply(self, blueprint: BookBlueprint) -> BookBlueprint: ...


class ProgressiveLearningStrategy(PlanningStrategy):
    def name(self) -> str:
        return "progressive_learning"

    def apply(self, blueprint: BookBlueprint) -> BookBlueprint:
        if not blueprint.outline or not blueprint.outline.chapters:
            return blueprint

        dep_graph = blueprint.dependency_graph
        if dep_graph is None:
            dep_edges: list[DependencyEdge] = []
            for ch in blueprint.outline.chapters:
                for prereq in ch.prerequisites:
                    dep_edges.append(DependencyEdge(from_chapter=prereq, to_chapter=ch.title, reason="prerequisite"))
            titles = [c.title for c in blueprint.outline.chapters]
            dep_graph = DependencyGraph(edges=dep_edges, chapter_titles=titles)

        b = blueprint.model_copy()
        b.dependency_graph = dep_graph
        sorted_titles = dep_graph.topological_sort()

        title_map = {c.title: c for c in b.outline.chapters} if b.outline else {}
        sorted_chapters: list[ChapterPlan] = [title_map[t] for t in sorted_titles if t in title_map]
        placed = {c.title for c in sorted_chapters}
        for ch in (b.outline.chapters if b.outline else []):
            if ch.title not in placed:
                sorted_chapters.append(ch)

        if b.outline:
            b.outline.chapters = sorted_chapters

        steps = [
            LearningStep(
                chapter_title=c.title,
                order=i + 1,
                estimated_minutes=c.estimated_minutes,
                prerequisites_met=[p for p in c.prerequisites if p in title_map],
            )
            for i, c in enumerate(sorted_chapters)
        ]
        b.learning_path = LearningPath(
            title=f"Progressive learning path for {b.title}",
            steps=steps,
            total_estimated_pages=sum(c.total_pages for c in sorted_chapters),
            total_estimated_minutes=sum(c.total_minutes for c in sorted_chapters),
        )
        return b


class DependencyOrderedStrategy(PlanningStrategy):
    def name(self) -> str:
        return "dependency_ordered"

    def apply(self, blueprint: BookBlueprint) -> BookBlueprint:
        if not blueprint.outline or not blueprint.outline.chapters:
            return blueprint

        if not blueprint.dependency_graph:
            return blueprint

        b = blueprint.model_copy()
        if not b.outline or not b.dependency_graph:
            return blueprint

        sorted_titles = b.dependency_graph.topological_sort()
        if not sorted_titles:
            return blueprint
        title_map = {c.title: c for c in b.outline.chapters}
        sorted_chapters: list[ChapterPlan] = []
        for title in sorted_titles:
            if title in title_map:
                sorted_chapters.append(title_map[title])

        if not sorted_chapters:
            return blueprint

        deduped: list[ChapterPlan] = []
        seen: set[str] = set()
        for chapter in sorted_chapters:
            if chapter.title not in seen:
                seen.add(chapter.title)
                deduped.append(chapter)

        if b.outline:
            b.outline.chapters = deduped

        return b


class DifficultyProgressionStrategy(PlanningStrategy):
    def name(self) -> str:
        return "difficulty_progression"

    def apply(self, blueprint: BookBlueprint) -> BookBlueprint:
        if not blueprint.outline or not blueprint.outline.chapters:
            return blueprint

        b = blueprint.model_copy()
        if not b.outline:
            return blueprint

        sorted_chapters = sorted(b.outline.chapters, key=lambda c: c.difficulty)
        b.outline.chapters = sorted_chapters

        return b


class TopicClusteringStrategy(PlanningStrategy):
    def name(self) -> str:
        return "topic_clustering"

    def apply(self, blueprint: BookBlueprint) -> BookBlueprint:
        if not blueprint.outline or not blueprint.outline.chapters:
            return blueprint

        clusters: dict[str, list[ChapterPlan]] = {}
        for chapter in blueprint.outline.chapters:
            key = self._guess_cluster(chapter)
            if key not in clusters:
                clusters[key] = []
            clusters[key].append(chapter)

        sorted_chapters: list[ChapterPlan] = []
        topic_clusters: list[TopicCluster] = []
        for cluster_name, members in clusters.items():
            for c in members:
                sorted_chapters.append(c)
            topic_clusters.append(
                TopicCluster(
                    name=cluster_name,
                    topics=[c.title for c in members],
                    relevance_score=1.0,
                )
            )

        b = blueprint.model_copy()
        if b.outline:
            b.outline.chapters = sorted_chapters
        b.topic_clusters = topic_clusters
        return b

    def _guess_cluster(self, chapter: ChapterPlan) -> str:
        title_lower = chapter.title.lower()
        if any(w in title_lower for w in ("intro", "overview", "background", "getting started")):
            return "Introduction"
        if any(w in title_lower for w in ("advanced", "expert", "deep", "performance")):
            return "Advanced Topics"
        if any(w in title_lower for w in ("api", "sdk", "library", "tool")):
            return "APIs and Tools"
        if any(w in title_lower for w in ("deploy", "production", "ops", "monitoring")):
            return "Deployment and Operations"
        if any(w in title_lower for w in ("case study", "example", "tutorial", "hands-on")):
            return "Examples and Case Studies"
        if any(w in title_lower for w in ("appendix", "reference", "glossary")):
            return "Reference"
        return "Core Concepts"
