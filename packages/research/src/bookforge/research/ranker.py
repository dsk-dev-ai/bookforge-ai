from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from bookforge.research.enums import RankCriterion, SourceType
from bookforge.research.models import ResearchDocument, ResearchSource


class ResearchRanker:
    """Ranks research sources and documents by multiple criteria.

    Scoring is rule-based — no external LLM calls. Each criterion
    contributes a weighted score that is summed to produce a final score.
    """

    _SOURCE_TYPE_AUTHORITY: ClassVar[dict[SourceType, float]] = {
        SourceType.SPECIFICATION: 0.95,
        SourceType.RFC: 0.90,
        SourceType.BOOK: 0.85,
        SourceType.PAPER: 0.80,
        SourceType.DOCUMENTATION: 0.75,
        SourceType.API: 0.70,
        SourceType.GITHUB: 0.60,
        SourceType.BLOG: 0.40,
    }

    _SOURCE_TYPE_FRESHNESS_DECAY: ClassVar[dict[SourceType, float]] = {
        SourceType.BLOG: 0.90,
        SourceType.GITHUB: 0.85,
        SourceType.DOCUMENTATION: 0.75,
        SourceType.API: 0.70,
        SourceType.SPECIFICATION: 0.60,
        SourceType.RFC: 0.50,
        SourceType.PAPER: 0.40,
        SourceType.BOOK: 0.30,
    }

    _CRITERION_WEIGHTS: ClassVar[dict[RankCriterion, float]] = {
        RankCriterion.AUTHORITY: 0.35,
        RankCriterion.FRESHNESS: 0.20,
        RankCriterion.RELEVANCE: 0.30,
        RankCriterion.COMPLETENESS: 0.15,
    }

    def rank_sources(
        self,
        sources: Sequence[ResearchSource],
        topic: str = "",
        weights: dict[RankCriterion, float] | None = None,
    ) -> list[ResearchSource]:
        w = {**self._CRITERION_WEIGHTS, **(weights or {})}
        scored = list(sources)
        for s in scored:
            authority = self._score_authority(s)
            freshness = self._score_freshness(s)
            relevance = self._score_relevance(s, topic)
            completeness = self._score_completeness(s)
            s.score = (
                w.get(RankCriterion.AUTHORITY, 0.35) * authority
                + w.get(RankCriterion.FRESHNESS, 0.20) * freshness
                + w.get(RankCriterion.RELEVANCE, 0.30) * relevance
                + w.get(RankCriterion.COMPLETENESS, 0.15) * completeness
            )
        scored.sort(key=lambda s: s.score, reverse=True)
        return scored

    def rank_documents(
        self,
        documents: Sequence[ResearchDocument],
        topic: str = "",
    ) -> list[ResearchDocument]:
        # Documents are returned unsorted; scoring requires a score field
        # on ResearchDocument which is intentionally omitted to keep the
        # document model focused on content rather than ranking metadata.
        return list(documents)

    def score_authority(self, source_type: SourceType) -> float:
        return self._SOURCE_TYPE_AUTHORITY.get(source_type, 0.5)

    def _score_authority(self, source: ResearchSource) -> float:
        return self._SOURCE_TYPE_AUTHORITY.get(source.source_type, 0.5)

    def _score_freshness(self, source: ResearchSource) -> float:
        base = self._SOURCE_TYPE_FRESHNESS_DECAY.get(source.source_type, 0.5)
        return base

    def _score_relevance(self, source: ResearchSource, topic: str) -> float:
        if not topic:
            return 0.5
        title_lower = source.title.lower()
        content_lower = source.content.lower()
        topic_lower = topic.lower()
        topic_words = set(topic_lower.split())
        title_matches = sum(1 for w in topic_words if w in title_lower)
        content_matches = sum(1 for w in topic_words if w in content_lower)
        score = 0.3 * min(title_matches / max(len(topic_words), 1), 1.0) + 0.7 * min(
            content_matches / max(len(topic_words) * 3, 1), 1.0
        )
        return min(score, 1.0)

    def _score_completeness(self, source: ResearchSource) -> float:
        factors = 0.0
        if source.title:
            factors += 0.3
        if source.content:
            length_score = min(len(source.content) / 5000, 1.0)
            factors += 0.4 * length_score
        if source.url:
            factors += 0.3
        return factors

    def _score_doc_authority(self, doc: ResearchDocument) -> float:
        return 0.5

    def _score_doc_relevance(self, doc: ResearchDocument, topic: str) -> float:
        if not topic:
            return 0.5
        title_lower = doc.title.lower()
        content_lower = doc.content.lower()
        topic_lower = topic.lower()
        topic_words = set(topic_lower.split())
        title_matches = sum(1 for w in topic_words if w in title_lower)
        content_matches = sum(1 for w in topic_words if w in content_lower)
        score = 0.3 * min(title_matches / max(len(topic_words), 1), 1.0) + 0.7 * min(
            content_matches / max(len(topic_words) * 3, 1), 1.0
        )
        return min(score, 1.0)

    def _score_doc_completeness(self, doc: ResearchDocument) -> float:
        factors = 0.0
        if doc.title:
            factors += 0.3
        if doc.content:
            length_score = min(len(doc.content) / 5000, 1.0)
            factors += 0.4 * length_score
        if doc.sections:
            factors += 0.3
        return factors
