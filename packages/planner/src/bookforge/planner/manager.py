from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from uuid import uuid4

from bookforge.planner.enums import PlanningStrategyType
from bookforge.planner.models import (
    BookBlueprint,
)
from bookforge.planner.planner import BookPlanner
from bookforge.planner.strategies import (
    DependencyOrderedStrategy,
    DifficultyProgressionStrategy,
    PlanningStrategy,
    ProgressiveLearningStrategy,
    TopicClusteringStrategy,
)
from bookforge.planner.validator import OutlineValidator, ValidationMessage


class PlannerManager:
    def __init__(
        self,
        planner: BookPlanner | None = None,
        validator: OutlineValidator | None = None,
    ) -> None:
        self._planner = planner or BookPlanner()
        self._validator = validator or OutlineValidator()
        self._blueprints: dict[str, BookBlueprint] = {}

    def create_blueprint(
        self,
        topic: str,
        chapter_titles: list[str],
        title: str | None = None,
        summary: str = "",
    ) -> BookBlueprint:
        outline = self._planner.generate_outline(
            topic=topic,
            chapter_titles=chapter_titles,
            summary=summary,
        )
        blueprint = self._planner.create_blueprint(topic=topic, outline=outline)
        if title:
            blueprint.title = title

        bp_id = uuid4().hex[:16]
        self._blueprints[bp_id] = blueprint
        blueprint = blueprint.model_copy(update={"created_at": datetime.now()})
        self._blueprints[bp_id] = blueprint
        return blueprint

    def plan_blueprint(
        self,
        blueprint_id: str,
        strategy_types: Sequence[PlanningStrategyType] | None = None,
    ) -> BookBlueprint:
        blueprint = self._get_blueprint(blueprint_id)
        if strategy_types is not None:
            strategies = self._resolve_strategies(strategy_types)
            planner = BookPlanner(strategies=strategies)
            planned = planner.plan(blueprint)
        else:
            planned = self._planner.plan(blueprint)
        self._blueprints[blueprint_id] = planned
        return planned

    def validate_blueprint(self, blueprint_id: str) -> list[ValidationMessage]:
        blueprint = self._get_blueprint(blueprint_id)
        return self._validator.validate_blueprint(blueprint)

    def get_blueprint(self, blueprint_id: str) -> BookBlueprint | None:
        return self._blueprints.get(blueprint_id)

    def list_blueprints(self) -> list[BookBlueprint]:
        return list(self._blueprints.values())

    def delete_blueprint(self, blueprint_id: str) -> bool:
        if blueprint_id in self._blueprints:
            del self._blueprints[blueprint_id]
            return True
        return False

    def _get_blueprint(self, blueprint_id: str) -> BookBlueprint:
        bp = self._blueprints.get(blueprint_id)
        if bp is None:
            raise ValueError(f"Blueprint not found: {blueprint_id}")
        return bp

    def _resolve_strategies(
        self,
        strategy_types: Sequence[PlanningStrategyType] | None,
    ) -> list[PlanningStrategy]:
        if strategy_types is None:
            return []

        mapping: dict[PlanningStrategyType, type[PlanningStrategy]] = {
            PlanningStrategyType.PROGRESSIVE_LEARNING: ProgressiveLearningStrategy,
            PlanningStrategyType.DEPENDENCY_ORDERED: DependencyOrderedStrategy,
            PlanningStrategyType.DIFFICULTY_PROGRESSION: DifficultyProgressionStrategy,
            PlanningStrategyType.TOPIC_CLUSTERING: TopicClusteringStrategy,
        }
        return [mapping[t]() for t in strategy_types if t in mapping]
