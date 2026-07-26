from bookforge.planner.engine import PlannerEngine


class TestPlannerEngine:
    def test_plan_book(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("Kubernetes", ["Intro", "Pods", "Services", "Deployment"])
        assert blueprint.title == "Kubernetes"
        assert blueprint.estimated_chapters == 4
        assert blueprint.outline is not None
        assert len(blueprint.outline.chapters) == 4

    def test_plan_book_with_custom_title(self) -> None:
        engine = PlannerEngine()
        bp = engine.plan_book("Docker", ["Intro", "Images"], title="Docker Deep Dive")
        assert bp.title == "Docker Deep Dive"

    def test_export_json(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("Rust", ["Ownership", "Borrowing"])
        result = engine.export_blueprint(blueprint, format="json")
        assert '"title"' in result
        assert '"Ownership"' in result

    def test_export_yaml(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("Go", ["Basics"])
        result = engine.export_blueprint(blueprint, format="yaml")
        assert "Go" in result

    def test_export_dict_format(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("Test", ["Ch1"])
        result = engine.export_blueprint(blueprint, format="dict")
        assert "title" in result

    def test_export_invalid_format(self) -> None:
        import pytest
        engine = PlannerEngine()
        blueprint = engine.plan_book("T", ["Ch1"])
        with pytest.raises(ValueError, match="Unsupported export format"):
            engine.export_blueprint(blueprint, format="xml")

    def test_validate_blueprint(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("T", ["Ch1"])
        errors = engine.validate_blueprint(blueprint)
        assert isinstance(errors, list)

    def test_analyze_audience(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("T", ["Ch1"])
        scores = engine.analyze_audience(blueprint)
        assert abs(sum(scores.values()) - 1.0) < 0.01

    def test_estimate_difficulty(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("T", ["Ch1"])
        diff = engine.estimate_difficulty(blueprint)
        assert 0.0 <= diff <= 1.0

    def test_estimate_chapter_count(self) -> None:
        engine = PlannerEngine()
        count = engine.estimate_chapter_count("T", chapter_count=7)
        assert count == 7

    def test_estimate_pages(self) -> None:
        engine = PlannerEngine()
        pages = engine.estimate_pages(chapter_count=5)
        assert pages > 0

    def test_estimate_reading_time(self) -> None:
        engine = PlannerEngine()
        blueprint = engine.plan_book("T", ["Ch1"])
        minutes = engine.estimate_reading_time(blueprint)
        assert minutes > 0

    def test_generate_outline(self) -> None:
        engine = PlannerEngine()
        outline = engine.generate_outline("Python", ["Intro", "Basics"])
        assert outline.title == "Python"
        assert outline.chapter_count == 2

    @property
    def planner(self) -> None:
        engine = PlannerEngine()
        assert engine.planner is not None

    @property
    def manager(self) -> None:
        engine = PlannerEngine()
        assert engine.manager is not None

    @property
    def validator(self) -> None:
        engine = PlannerEngine()
        assert engine.validator is not None

    @property
    def exporter(self) -> None:
        engine = PlannerEngine()
        assert engine.exporter is not None

    @property
    def optimizer(self) -> None:
        engine = PlannerEngine()
        assert engine.optimizer is not None
