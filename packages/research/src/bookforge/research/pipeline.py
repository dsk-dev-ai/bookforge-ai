from __future__ import annotations

from collections.abc import Callable

from bookforge.research.deduplicator import ResearchDeduplicator
from bookforge.research.enums import ResearchStatus
from bookforge.research.exporter import ResearchExporter
from bookforge.research.models import (
    ResearchJob,
    ResearchResult,
)
from bookforge.research.normalizer import ResearchNormalizer
from bookforge.research.planner import ResearchPlanner
from bookforge.research.ranker import ResearchRanker
from bookforge.research.validator import ResearchValidator

StageHandler = Callable[[ResearchJob], ResearchJob]


class ResearchPipeline:
    """Orchestrates the research pipeline stages in order.

    Pipeline: Planning → Normalization → Deduplication → Ranking
             → Validation → Export

    Each stage receives the current ResearchJob and returns an
    updated ResearchJob. Stages can be added, removed, or reordered.
    """

    def __init__(
        self,
        planner: ResearchPlanner | None = None,
        normalizer: ResearchNormalizer | None = None,
        deduplicator: ResearchDeduplicator | None = None,
        ranker: ResearchRanker | None = None,
        validator: ResearchValidator | None = None,
        exporter: ResearchExporter | None = None,
    ) -> None:
        self._planner = planner or ResearchPlanner()
        self._normalizer = normalizer or ResearchNormalizer()
        self._deduplicator = deduplicator or ResearchDeduplicator()
        self._ranker = ranker or ResearchRanker()
        self._validator = validator or ResearchValidator()
        self._exporter = exporter or ResearchExporter()

        self._stages: list[tuple[ResearchStatus, StageHandler]] = [
            (ResearchStatus.PLANNING, self._stage_planning),
            (ResearchStatus.NORMALIZING, self._stage_normalizing),
            (ResearchStatus.DEDUPLICATING, self._stage_deduplicating),
            (ResearchStatus.RANKING, self._stage_ranking),
            (ResearchStatus.VALIDATING, self._stage_validating),
            (ResearchStatus.EXPORTING, self._stage_exporting),
        ]

    @property
    def stages(self) -> list[tuple[ResearchStatus, StageHandler]]:
        return list(self._stages)

    def run(self, job: ResearchJob) -> ResearchJob:
        for stage_status, handler in self._stages:
            job.pipeline_stage = stage_status
            job.status = stage_status
            try:
                job = handler(job)
            except Exception:
                job.status = ResearchStatus.FAILED
                job.pipeline_stage = stage_status
                job.statistics.validation_errors += 1
                break
        else:
            job.status = ResearchStatus.COMPLETED
        return job

    def run_from(
        self,
        job: ResearchJob,
        start_stage: ResearchStatus,
    ) -> ResearchJob:
        started = False
        for stage_status, handler in self._stages:
            if stage_status == start_stage:
                started = True
            if not started:
                continue
            job.pipeline_stage = stage_status
            job.status = stage_status
            try:
                job = handler(job)
            except Exception:
                job.status = ResearchStatus.FAILED
                job.pipeline_stage = stage_status
                job.statistics.validation_errors += 1
                break
        else:
            job.status = ResearchStatus.COMPLETED
        return job

    def _stage_planning(self, job: ResearchJob) -> ResearchJob:
        plan = self._planner.create_plan(job.topic, job.input_type)
        job.plan = plan
        return job

    def _stage_normalizing(self, job: ResearchJob) -> ResearchJob:
        if job.sources:
            job.documents = self._normalizer.normalize_batch(job.sources)
            job.statistics.documents_normalized = len(job.documents)
        return job

    def _stage_deduplicating(self, job: ResearchJob) -> ResearchJob:
        if job.sources:
            before = len(job.sources)
            job.sources = self._deduplicator.deduplicate_sources(job.sources)
            job.statistics.duplicates_removed = before - len(job.sources)
        if job.documents:
            before = len(job.documents)
            job.documents = self._deduplicator.deduplicate_documents(job.documents)
            job.statistics.duplicates_removed += before - len(job.documents)
        return job

    def _stage_ranking(self, job: ResearchJob) -> ResearchJob:
        if job.sources:
            job.sources = self._ranker.rank_sources(job.sources, topic=job.topic)
            job.statistics.total_ranked = len(job.sources)
        if job.documents:
            job.documents = self._ranker.rank_documents(job.documents, topic=job.topic)
        return job

    def _stage_validating(self, job: ResearchJob) -> ResearchJob:
        source_errors = self._validator.validate_sources(job.sources) if job.sources else []
        doc_errors = self._validator.validate_documents(job.documents) if job.documents else []
        job.statistics.validation_errors = len(source_errors) + len(doc_errors)
        return job

    def _stage_exporting(self, job: ResearchJob) -> ResearchJob:
        result = ResearchResult(summary=f"Research results for: {job.topic}")
        result.suggested_chapters = []
        if job.plan:
            for i, obj in enumerate(job.plan.objectives, start=1):
                result.learning_objectives.append(obj)
        result.references = []
        job.result = result
        return job
