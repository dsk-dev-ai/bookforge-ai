"""Tests for ResearchRanker."""

from bookforge.research.enums import RankCriterion, SourceType
from bookforge.research.models import ResearchDocument, ResearchSource
from bookforge.research.ranker import ResearchRanker


class TestResearchRanker:
    def test_rank_sources_by_score(self) -> None:
        ranker = ResearchRanker()
        sources = [
            ResearchSource(id="s1", title="Blog Post", source_type=SourceType.BLOG,
                           content="Short blog", score=0.0),
            ResearchSource(id="s2", title="RFC Doc", source_type=SourceType.RFC,
                           content="Longer RFC document content here", score=0.0),
        ]
        ranked = ranker.rank_sources(sources, topic="test")
        assert ranked[0].score >= ranked[1].score

    def test_authority_scores_by_type(self) -> None:
        ranker = ResearchRanker()
        assert ranker.score_authority(SourceType.SPECIFICATION) > ranker.score_authority(SourceType.BLOG)

    def test_relevance_score_matches_topic_title(self) -> None:
        ranker = ResearchRanker()
        source = ResearchSource(id="s1", title="Kubernetes Guide",
                                source_type=SourceType.BOOK,
                                content="Some content about orchestration")
        ranked = ranker.rank_sources([source], topic="Kubernetes")
        assert ranked[0].score > 0

    def test_completeness_score_longer_content(self) -> None:
        ranker = ResearchRanker()
        short = ResearchSource(id="s1", title="Short", source_type=SourceType.BLOG,
                                content="Hi")
        long_ = ResearchSource(id="s2", title="Long", source_type=SourceType.BOOK,
                                content="A" * 10000)
        ranked = ranker.rank_sources([short, long_])
        assert ranked[0].id == "s2"

    def test_custom_weights(self) -> None:
        ranker = ResearchRanker()
        sources = [
            ResearchSource(id="s1", title="X", source_type=SourceType.BLOG, content="X"),
            ResearchSource(id="s2", title="Y", source_type=SourceType.BOOK, content="Y"),
        ]
        weights = {RankCriterion.AUTHORITY: 1.0, RankCriterion.FRESHNESS: 0.0,
                   RankCriterion.RELEVANCE: 0.0, RankCriterion.COMPLETENESS: 0.0}
        ranked = ranker.rank_sources(sources, weights=weights)
        assert ranked[0].source_type == SourceType.BOOK

    def test_rank_documents(self) -> None:
        ranker = ResearchRanker()
        docs = [
            ResearchDocument(id="d1", source_id="s1", title="Kubernetes Doc", content="Kubernetes is great"),
            ResearchDocument(id="d2", source_id="s2", title="Rust Doc", content="Rust is fast"),
        ]
        ranked = ranker.rank_documents(docs, topic="Kubernetes")
        assert len(ranked) == 2

    def test_empty_sources(self) -> None:
        ranker = ResearchRanker()
        ranked = ranker.rank_sources([])
        assert ranked == []
