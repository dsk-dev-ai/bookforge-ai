from bookforge.planner.models import BookBlueprint, BookOutline, ChapterPlan
from bookforge.planner.optimizer import SequenceOptimizer


class TestSequenceOptimizer:
    def test_optimize_empty_outline(self) -> None:
        optimizer = SequenceOptimizer()
        bp = BookBlueprint(title="T", topic="T")
        result = optimizer.optimize(bp)
        assert result.outline is None

    def test_optimize_no_changes_for_simple(self) -> None:
        optimizer = SequenceOptimizer()
        chapters = [ChapterPlan(title="Ch1"), ChapterPlan(title="Ch2")]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=2)
        result = optimizer.optimize(bp)
        assert result.outline is not None
        assert result.outline.chapter_count == 2

    def test_optimize_places_prerequisites_first(self) -> None:
        optimizer = SequenceOptimizer()
        chapters = [
            ChapterPlan(title="Advanced", prerequisites=["Basic"]),
            ChapterPlan(title="Basic", prerequisites=[]),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=2)
        result = optimizer.optimize(bp)
        assert result.outline is not None
        titles = [c.title for c in result.outline.chapters]
        assert titles == ["Basic", "Advanced"]

    def test_optimize_handles_missing_prereq(self) -> None:
        optimizer = SequenceOptimizer()
        chapters = [
            ChapterPlan(title="Ch2", prerequisites=["Unknown"]),
            ChapterPlan(title="Ch1", prerequisites=[]),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=2)
        result = optimizer.optimize(bp)
        assert result.outline is not None
        assert len(result.outline.chapters) == 2

    def test_optimize_creates_learning_path(self) -> None:
        optimizer = SequenceOptimizer()
        chapters = [ChapterPlan(title="Ch1", estimated_minutes=30)]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=1)
        result = optimizer.optimize(bp)
        assert result.learning_path is not None
        assert len(result.learning_path.steps) == 1
