import pytest

from bookforge.planner.enums import PlanningStrategyType
from bookforge.planner.manager import PlannerManager


class TestPlannerManager:
    def test_create_blueprint(self) -> None:
        manager = PlannerManager()
        bp = manager.create_blueprint("Python", ["Intro", "Basics", "Advanced"])
        assert bp.topic == "Python"
        assert bp.estimated_chapters == 3

    def test_create_blueprint_with_title(self) -> None:
        manager = PlannerManager()
        bp = manager.create_blueprint("Python", ["Ch1"], title="Python Guide")
        assert bp.title == "Python Guide"

    def test_get_blueprint(self) -> None:
        manager = PlannerManager()
        _ = manager.create_blueprint("T", ["Ch1"])
        bp_id = next(iter(manager._blueprints.keys()))
        fetched = manager.get_blueprint(bp_id)
        assert fetched is not None
        assert fetched.topic == "T"

    def test_get_blueprint_not_found(self) -> None:
        manager = PlannerManager()
        assert manager.get_blueprint("nonexistent") is None

    def test_list_blueprints(self) -> None:
        manager = PlannerManager()
        manager.create_blueprint("A", ["Ch1"])
        manager.create_blueprint("B", ["Ch1"])
        assert len(manager.list_blueprints()) == 2

    def test_delete_blueprint(self) -> None:
        manager = PlannerManager()
        _ = manager.create_blueprint("T", ["Ch1"])
        bp_id = next(iter(manager._blueprints.keys()))
        assert manager.delete_blueprint(bp_id) is True
        assert manager.get_blueprint(bp_id) is None

    def test_delete_nonexistent(self) -> None:
        manager = PlannerManager()
        assert manager.delete_blueprint("nonexistent") is False

    def test_plan_blueprint(self) -> None:
        manager = PlannerManager()
        _ = manager.create_blueprint("Python", ["Basics", "Advanced"])
        bp_id = next(iter(manager._blueprints.keys()))
        planned = manager.plan_blueprint(bp_id)
        assert planned.learning_path is not None

    def test_plan_blueprint_empty_strategies(self) -> None:
        manager = PlannerManager()
        _ = manager.create_blueprint("T", ["Ch1"])
        bp_id = next(iter(manager._blueprints.keys()))
        planned = manager.plan_blueprint(bp_id, strategy_types=[])
        assert planned is not None

    def test_plan_blueprint_with_strategies(self) -> None:
        manager = PlannerManager()
        _ = manager.create_blueprint("T", ["Ch1"])
        bp_id = next(iter(manager._blueprints.keys()))
        planned = manager.plan_blueprint(bp_id, strategy_types=[PlanningStrategyType.DIFFICULTY_PROGRESSION])
        assert planned is not None

    def test_plan_blueprint_not_found(self) -> None:
        manager = PlannerManager()
        with pytest.raises(ValueError, match="not found"):
            manager.plan_blueprint("nonexistent")

    def test_validate_blueprint(self) -> None:
        manager = PlannerManager()
        _ = manager.create_blueprint("T", ["Ch1"])
        bp_id = next(iter(manager._blueprints.keys()))
        errors = manager.validate_blueprint(bp_id)
        assert isinstance(errors, list)
