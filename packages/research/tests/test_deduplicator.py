"""Tests for ResearchDeduplicator."""

from bookforge.research.deduplicator import ResearchDeduplicator
from bookforge.research.enums import SourceType
from bookforge.research.models import ResearchDocument, ResearchSource


class TestResearchDeduplicator:
    def test_deduplicate_sources_no_duplicates(self) -> None:
        dedup = ResearchDeduplicator()
        sources = [
            ResearchSource(id="s1", title="A", source_type=SourceType.BLOG, content="Content A"),
            ResearchSource(id="s2", title="B", source_type=SourceType.BLOG, content="Content B"),
        ]
        result = dedup.deduplicate_sources(sources)
        assert len(result) == 2

    def test_deduplicate_sources_removes_duplicates(self) -> None:
        dedup = ResearchDeduplicator()
        sources = [
            ResearchSource(id="s1", title="Same", source_type=SourceType.BLOG, content="Identical content"),
            ResearchSource(id="s2", title="Same", source_type=SourceType.BLOG, content="Identical content"),
        ]
        result = dedup.deduplicate_sources(sources)
        assert len(result) == 1

    def test_deduplicate_documents_no_duplicates(self) -> None:
        dedup = ResearchDeduplicator()
        docs = [
            ResearchDocument(id="d1", source_id="s1", title="Doc A", content="Content A"),
            ResearchDocument(id="d2", source_id="s2", title="Doc B", content="Content B"),
        ]
        result = dedup.deduplicate_documents(docs)
        assert len(result) == 2

    def test_deduplicate_documents_removes_duplicates(self) -> None:
        dedup = ResearchDeduplicator()
        docs = [
            ResearchDocument(id="d1", source_id="s1", title="Same", content="Identical"),
            ResearchDocument(id="d2", source_id="s2", title="Same", content="Identical"),
        ]
        result = dedup.deduplicate_documents(docs)
        assert len(result) == 1

    def test_find_duplicates_returns_pairs(self) -> None:
        dedup = ResearchDeduplicator()
        sources = [
            ResearchSource(id="s1", title="X", source_type=SourceType.API, content="Data"),
            ResearchSource(id="s2", title="X", source_type=SourceType.API, content="Data"),
            ResearchSource(id="s3", title="Y", source_type=SourceType.API, content="Other"),
        ]
        pairs = dedup.find_duplicates(sources)
        assert len(pairs) == 1
        assert pairs[0][0].id == "s1"
        assert pairs[0][1].id == "s2"

    def test_no_duplicates_find_returns_empty(self) -> None:
        dedup = ResearchDeduplicator()
        sources = [
            ResearchSource(id="s1", title="A", source_type=SourceType.BLOG, content="Content A"),
            ResearchSource(id="s2", title="B", source_type=SourceType.BLOG, content="Content B"),
        ]
        pairs = dedup.find_duplicates(sources)
        assert pairs == []
