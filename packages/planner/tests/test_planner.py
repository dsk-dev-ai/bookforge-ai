from bookforge.planner.models import BookOutline, ChapterPlan
from bookforge.planner.planner import BookPlanner


class TestBookPlanner:
    def test_default_strategies(self) -> None:
        planner = BookPlanner()
        assert len(planner.strategies) == 4

    def test_custom_strategies(self) -> None:
        from bookforge.planner.strategies import DifficultyProgressionStrategy
        planner = BookPlanner(strategies=[DifficultyProgressionStrategy()])
        assert len(planner.strategies) == 1

    def test_generate_outline(self) -> None:
        planner = BookPlanner()
        topics = ["Introduction", "Core Concepts", "Advanced Topics"]
        outline = planner.generate_outline("Python Guide", topics, summary="A Python book")
        assert outline.title == "Python Guide"
        assert outline.chapter_count == 3
        assert len(outline.front_matter) == 2
        assert len(outline.back_matter) == 2

    def test_generate_outline_chapter_ordering(self) -> None:
        planner = BookPlanner()
        topics = ["Basics", "Intermediate", "Advanced"]
        outline = planner.generate_outline("Topic", topics)
        assert [c.title for c in outline.chapters] == topics

    def test_create_blueprint(self) -> None:
        planner = BookPlanner()
        chapters = [
            ChapterPlan(title="Ch1", estimated_pages=10.0, estimated_minutes=60),
            ChapterPlan(title="Ch2", prerequisites=["Ch1"], estimated_pages=15.0, estimated_minutes=90),
        ]
        outline = BookOutline(title="Test", chapters=chapters)
        bp = planner.create_blueprint(topic="Test", outline=outline)
        assert bp.title == "Test"
        assert bp.estimated_chapters == 2
        assert bp.dependency_graph is not None

    def test_plan_applies_strategies(self) -> None:
        planner = BookPlanner()
        chapters = [
            ChapterPlan(title="Ch2", difficulty=0.9, prerequisites=["Ch1"]),
            ChapterPlan(title="Ch1", difficulty=0.1),
        ]
        outline = BookOutline(title="T", chapters=chapters)
        bp = planner.create_blueprint(topic="T", outline=outline)
        result = planner.plan(bp)
        assert result is not None
        assert result.learning_path is not None
