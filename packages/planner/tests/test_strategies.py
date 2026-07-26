from bookforge.planner.models import BookBlueprint, BookOutline, ChapterPlan, DependencyEdge, DependencyGraph
from bookforge.planner.strategies import (
    DependencyOrderedStrategy,
    DifficultyProgressionStrategy,
    ProgressiveLearningStrategy,
    TopicClusteringStrategy,
)


class TestProgressiveLearningStrategy:
    def test_name(self) -> None:
        s = ProgressiveLearningStrategy()
        assert s.name() == "progressive_learning"

    def test_apply_no_outline(self) -> None:
        s = ProgressiveLearningStrategy()
        bp = BookBlueprint(title="T", topic="T")
        result = s.apply(bp)
        assert result is not None

    def test_apply_orders_by_dependency(self) -> None:
        s = ProgressiveLearningStrategy()
        chapters = [
            ChapterPlan(title="Advanced", prerequisites=["Basic"]),
            ChapterPlan(title="Basic", prerequisites=[]),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=2)
        result = s.apply(bp)
        assert result.outline is not None
        assert result.outline.chapters[0].title == "Basic"
        assert result.outline.chapters[1].title == "Advanced"

    def test_apply_with_cycle_preserves_all_chapters(self) -> None:
        s = ProgressiveLearningStrategy()
        chapters = [
            ChapterPlan(title="A", prerequisites=["B"]),
            ChapterPlan(title="B", prerequisites=["C"]),
            ChapterPlan(title="C", prerequisites=["A"]),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(
            title="T", topic="T", outline=outline, estimated_chapters=3,
            dependency_graph=DependencyGraph(
                edges=[
                    DependencyEdge(from_chapter="A", to_chapter="B"),
                    DependencyEdge(from_chapter="B", to_chapter="C"),
                    DependencyEdge(from_chapter="C", to_chapter="A"),
                ],
                chapter_titles=["A", "B", "C"],
            ),
        )
        result = s.apply(bp)
        assert result.outline is not None
        assert len(result.outline.chapters) == 3
        titles = {c.title for c in result.outline.chapters}
        assert titles == {"A", "B", "C"}

    def test_apply_creates_learning_path(self) -> None:
        s = ProgressiveLearningStrategy()
        chapters = [ChapterPlan(title="Ch1", estimated_minutes=30)]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=1)
        result = s.apply(bp)
        assert result.learning_path is not None
        assert result.learning_path.steps[0].chapter_title == "Ch1"


class TestDependencyOrderedStrategy:
    def test_name(self) -> None:
        s = DependencyOrderedStrategy()
        assert s.name() == "dependency_ordered"

    def test_apply_no_dependency_graph(self) -> None:
        s = DependencyOrderedStrategy()
        chapters = [ChapterPlan(title="A"), ChapterPlan(title="B")]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=2)
        result = s.apply(bp)
        assert result.outline is not None
        assert len(result.outline.chapters) == 2

    def test_apply_with_dependency_graph(self) -> None:
        s = DependencyOrderedStrategy()
        chapters = [
            ChapterPlan(title="Advanced", prerequisites=["Basic"]),
            ChapterPlan(title="Basic", prerequisites=[]),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(
            title="T", topic="T", outline=outline, estimated_chapters=2,
            dependency_graph=DependencyGraph(
                edges=[DependencyEdge(from_chapter="Basic", to_chapter="Advanced")],
                chapter_titles=["Basic", "Advanced"],
            ),
        )
        result = s.apply(bp)
        assert result.outline is not None
        assert result.outline.chapters[0].title == "Basic"
        assert result.outline.chapters[1].title == "Advanced"


class TestDifficultyProgressionStrategy:
    def test_name(self) -> None:
        s = DifficultyProgressionStrategy()
        assert s.name() == "difficulty_progression"

    def test_apply_orders_by_difficulty(self) -> None:
        s = DifficultyProgressionStrategy()
        chapters = [
            ChapterPlan(title="Hard", difficulty=0.9),
            ChapterPlan(title="Easy", difficulty=0.1),
            ChapterPlan(title="Medium", difficulty=0.5),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=3)
        result = s.apply(bp)
        assert result.outline is not None
        titles = [c.title for c in result.outline.chapters]
        assert titles == ["Easy", "Medium", "Hard"]


class TestTopicClusteringStrategy:
    def test_name(self) -> None:
        s = TopicClusteringStrategy()
        assert s.name() == "topic_clustering"

    def test_apply_clusters_chapters(self) -> None:
        s = TopicClusteringStrategy()
        chapters = [
            ChapterPlan(title="Introduction to Python"),
            ChapterPlan(title="Advanced Python"),
            ChapterPlan(title="Deploy to Production"),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=3)
        result = s.apply(bp)
        assert len(result.topic_clusters) >= 1
        all_topics = [t for c in result.topic_clusters for t in c.topics]
        assert len(all_topics) == 3
