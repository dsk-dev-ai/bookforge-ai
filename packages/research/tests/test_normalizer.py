"""Tests for ResearchNormalizer."""

from bookforge.research.enums import SourceType
from bookforge.research.models import ResearchSource
from bookforge.research.normalizer import ResearchNormalizer


class TestResearchNormalizer:
    def test_normalize_source(self) -> None:
        normalizer = ResearchNormalizer()
        source = ResearchSource(
            id="src1",
            title="Test Source",
            source_type=SourceType.DOCUMENTATION,
            content="Some content here",
        )
        doc = normalizer.normalize(source)
        assert doc.source_id == "src1"
        assert doc.title == "Test Source"
        assert "Some content here" in doc.content

    def test_normalize_batch(self) -> None:
        normalizer = ResearchNormalizer()
        sources = [
            ResearchSource(id="s1", title="S1", source_type=SourceType.BLOG, content="Content 1"),
            ResearchSource(id="s2", title="S2", source_type=SourceType.BOOK, content="Content 2"),
        ]
        docs = normalizer.normalize_batch(sources)
        assert len(docs) == 2

    def test_extract_sections(self) -> None:
        normalizer = ResearchNormalizer()
        source = ResearchSource(
            id="src2",
            title="With Sections",
            source_type=SourceType.DOCUMENTATION,
            content="# Introduction\nHello\n\n# Getting Started\nInstall it\n",
        )
        doc = normalizer.normalize(source)
        assert len(doc.sections) >= 2
        assert doc.sections[0].heading == "Introduction"
        assert doc.sections[1].heading == "Getting Started"

    def test_clean_content_removes_excess_newlines(self) -> None:
        normalizer = ResearchNormalizer()
        source = ResearchSource(
            id="src3",
            title="Messy",
            source_type=SourceType.BLOG,
            content="Line1\n\n\n\n\nLine2",
        )
        doc = normalizer.normalize(source)
        assert "\n\n\n" not in doc.content

    def test_make_doc_id_unique(self) -> None:
        normalizer = ResearchNormalizer()
        d1 = normalizer.normalize(
            ResearchSource(id="a", title="Same", source_type=SourceType.API, content="X")
        )
        d2 = normalizer.normalize(
            ResearchSource(id="a", title="Same", source_type=SourceType.API, content="X")
        )
        assert d1.id == d2.id

    def test_make_doc_id_differs_for_diff_content(self) -> None:
        normalizer = ResearchNormalizer()
        d1 = normalizer.normalize(
            ResearchSource(id="a", title="Same", source_type=SourceType.API, content="X")
        )
        d2 = normalizer.normalize(
            ResearchSource(id="a", title="Same", source_type=SourceType.API, content="Y")
        )
        assert d1.id != d2.id

    def test_empty_content(self) -> None:
        normalizer = ResearchNormalizer()
        source = ResearchSource(
            id="empty",
            title="Empty",
            source_type=SourceType.BLOG,
            content="",
        )
        doc = normalizer.normalize(source)
        assert doc.content == ""
        assert doc.sections == []
