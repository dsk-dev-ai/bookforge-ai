from __future__ import annotations

from collections.abc import Sequence

from bookforge.research.cache import MemoryCache, ResearchCache
from bookforge.research.deduplicator import ResearchDeduplicator
from bookforge.research.enums import SupportedInput
from bookforge.research.exporter import ResearchExporter
from bookforge.research.manager import ResearchManager
from bookforge.research.models import ResearchResult, ResearchSource
from bookforge.research.normalizer import ResearchNormalizer
from bookforge.research.pipeline import ResearchPipeline
from bookforge.research.planner import ResearchPlanner
from bookforge.research.ranker import ResearchRanker
from bookforge.research.validator import ResearchValidator


class ResearchEngine:
    """Top-level entry point for the research subsystem.

    Provides a simplified API for performing research on a topic.
    Internally delegates to ResearchManager, ResearchPipeline, and
    all pipeline stage components.

    Usage::

        engine = ResearchEngine()
        result = engine.research("Kubernetes networking")
        print(result.summary)
    """

    def __init__(
        self,
        planner: ResearchPlanner | None = None,
        normalizer: ResearchNormalizer | None = None,
        deduplicator: ResearchDeduplicator | None = None,
        ranker: ResearchRanker | None = None,
        validator: ResearchValidator | None = None,
        exporter: ResearchExporter | None = None,
        cache: ResearchCache | None = None,
    ) -> None:
        self._planner = planner or ResearchPlanner()
        self._normalizer = normalizer or ResearchNormalizer()
        self._deduplicator = deduplicator or ResearchDeduplicator()
        self._ranker = ranker or ResearchRanker()
        self._validator = validator or ResearchValidator()
        self._exporter = exporter or ResearchExporter()
        self._cache = cache or MemoryCache(default_ttl=3600)
        pipeline = ResearchPipeline(
            planner=self._planner,
            normalizer=self._normalizer,
            deduplicator=self._deduplicator,
            ranker=self._ranker,
            validator=self._validator,
            exporter=self._exporter,
        )
        self._manager = ResearchManager(pipeline=pipeline, cache=self._cache)

    @property
    def manager(self) -> ResearchManager:
        return self._manager

    @property
    def planner(self) -> ResearchPlanner:
        return self._planner

    @property
    def normalizer(self) -> ResearchNormalizer:
        return self._normalizer

    @property
    def deduplicator(self) -> ResearchDeduplicator:
        return self._deduplicator

    @property
    def ranker(self) -> ResearchRanker:
        return self._ranker

    @property
    def validator(self) -> ResearchValidator:
        return self._validator

    @property
    def exporter(self) -> ResearchExporter:
        return self._exporter

    @property
    def cache(self) -> ResearchCache:
        return self._cache

    def research(
        self,
        topic: str,
        input_type: SupportedInput = SupportedInput.TECHNICAL_TOPIC,
    ) -> ResearchResult:
        cached = self._cache.get(f"research:{topic}:{input_type.value}")
        if cached is not None:
            return cached

        job = self._manager.create_job(topic=topic, input_type=input_type)
        job = self._manager.start_job(job.id)
        result = job.result or ResearchResult()
        self._cache.set(f"research:{topic}:{input_type.value}", result, ttl=3600)
        return result

    def research_with_sources(
        self,
        topic: str,
        sources: Sequence[ResearchSource],
        input_type: SupportedInput = SupportedInput.TECHNICAL_TOPIC,
    ) -> ResearchResult:
        job = self._manager.create_job(topic=topic, input_type=input_type)
        self._manager.add_sources(job.id, sources)
        job = self._manager.start_job(job.id)
        return job.result or ResearchResult()
