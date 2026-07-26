from __future__ import annotations

from typing import Any

from bookforge.planner.estimators import (
    AudienceAnalyzer,
    ChapterEstimator,
    DifficultyEstimator,
    PageEstimator,
    TimeEstimator,
)
from bookforge.planner.exporter import OutlineExporter
from bookforge.planner.manager import PlannerManager
from bookforge.planner.models import BookBlueprint, BookOutline
from bookforge.planner.optimizer import SequenceOptimizer
from bookforge.planner.planner import BookPlanner
from bookforge.planner.validator import OutlineValidator, ValidationMessage


class PlannerEngine:
    def __init__(
        self,
        planner: BookPlanner | None = None,
        manager: PlannerManager | None = None,
        validator: OutlineValidator | None = None,
        exporter: OutlineExporter | None = None,
        optimizer: SequenceOptimizer | None = None,
        audience_analyzer: AudienceAnalyzer | None = None,
        difficulty_estimator: DifficultyEstimator | None = None,
        chapter_estimator: ChapterEstimator | None = None,
        page_estimator: PageEstimator | None = None,
        time_estimator: TimeEstimator | None = None,
    ) -> None:
        self._planner = planner or BookPlanner()
        self._manager = manager or PlannerManager(planner=self._planner)
        self._validator = validator or OutlineValidator()
        self._exporter = exporter or OutlineExporter()
        self._optimizer = optimizer or SequenceOptimizer()
        self._audience_analyzer = audience_analyzer or AudienceAnalyzer()
        self._difficulty_estimator = difficulty_estimator or DifficultyEstimator()
        self._chapter_estimator = chapter_estimator or ChapterEstimator()
        self._page_estimator = page_estimator or PageEstimator()
        self._time_estimator = time_estimator or TimeEstimator()

    @property
    def planner(self) -> BookPlanner:
        return self._planner

    @property
    def manager(self) -> PlannerManager:
        return self._manager

    @property
    def validator(self) -> OutlineValidator:
        return self._validator

    @property
    def exporter(self) -> OutlineExporter:
        return self._exporter

    @property
    def optimizer(self) -> SequenceOptimizer:
        return self._optimizer

    def plan_book(
        self,
        topic: str,
        chapter_titles: list[str],
        title: str | None = None,
        summary: str = "",
    ) -> BookBlueprint:
        outline = self._planner.generate_outline(topic=topic, chapter_titles=chapter_titles, summary=summary)
        blueprint = self._planner.create_blueprint(topic=topic, outline=outline)
        if title:
            blueprint.title = title
        planned = self._planner.plan(blueprint)
        optimized = self._optimizer.optimize(planned)
        return optimized

    def export_blueprint(
        self,
        blueprint: BookBlueprint,
        format: str = "json",
    ) -> str | dict[str, Any]:
        if format == "json":
            return self._exporter.to_json(blueprint)
        if format == "yaml":
            return self._exporter.to_yaml(blueprint)
        if format == "dict":
            return self._exporter.to_dict(blueprint)
        raise ValueError(f"Unsupported export format: {format}")

    def validate_blueprint(self, blueprint: BookBlueprint) -> list[ValidationMessage]:
        return self._validator.validate_blueprint(blueprint)

    def analyze_audience(self, blueprint: BookBlueprint) -> dict[str, float]:
        return self._audience_analyzer.analyze(blueprint)

    def estimate_difficulty(self, blueprint: BookBlueprint) -> float:
        return self._difficulty_estimator.estimate_overall_difficulty(blueprint)

    def estimate_chapter_count(
        self,
        topic: str,
        page_count: int | None = None,
        chapter_count: int | None = None,
    ) -> int:
        return self._chapter_estimator.estimate_count(topic, page_count, chapter_count)

    def estimate_pages(
        self,
        chapter_count: int,
        sections_per_chapter: int = 5,
    ) -> float:
        return self._page_estimator.estimate_total(chapter_count, sections_per_chapter)

    def estimate_reading_time(self, blueprint: BookBlueprint) -> int:
        return self._time_estimator.estimate_total_time(blueprint)

    def generate_outline(
        self,
        topic: str,
        chapter_titles: list[str],
        summary: str = "",
    ) -> BookOutline:
        return self._planner.generate_outline(topic=topic, chapter_titles=chapter_titles, summary=summary)
