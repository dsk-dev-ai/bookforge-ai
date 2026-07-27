from bookforge.writer.enums import DraftQuality, WritingStatus
from bookforge.writer.models import (
    BookDraft,
    ChapterDraft,
    FrontMatterDraft,
    GlossaryDraft,
    GlossaryEntry,
    ReferenceDraft,
    ReferenceEntry,
    SectionDraft,
    ValidationMessage,
    WritingConfig,
)


class TestSectionDraft:
    def test_defaults(self) -> None:
        s = SectionDraft(heading="Intro")
        assert s.content == ""
        assert s.word_count == 0
        assert s.total_word_count == 0

    def test_total_word_count_includes_subsections(self) -> None:
        sub = SectionDraft(heading="Sub", content="words here", word_count=2)
        parent = SectionDraft(heading="Parent", content="hello", word_count=1, subsections=[sub])
        assert parent.total_word_count == 3


class TestChapterDraft:
    def test_defaults(self) -> None:
        c = ChapterDraft(title="Ch1")
        assert c.status == WritingStatus.PENDING
        assert c.word_count == 0

    def test_total_word_count(self) -> None:
        s = SectionDraft(heading="Sec", content="some words", word_count=2)
        c = ChapterDraft(title="Ch1", content="hello", word_count=1, sections=[s])
        assert c.total_word_count == 3


class TestBookDraft:
    def test_defaults(self) -> None:
        d = BookDraft(title="Test", topic="Testing")
        assert d.chapter_count == 0
        assert d.quality == DraftQuality.DRAFT
        assert d.status == WritingStatus.PENDING

    def test_total_word_count_aggregates(self) -> None:
        c1 = ChapterDraft(title="Ch1", content="hello", word_count=1)
        fm = FrontMatterDraft(title="Preface", content="intro", word_count=2)
        d = BookDraft(
            title="Test", topic="T", chapters=[c1], front_matter=[fm],
        )
        assert d.total_word_count == 3

    def test_chapter_count(self) -> None:
        d = BookDraft(
            title="Test", topic="T",
            chapters=[ChapterDraft(title="A"), ChapterDraft(title="B")],
        )
        assert d.chapter_count == 2


class TestGlossaryDraft:
    def test_defaults(self) -> None:
        g = GlossaryDraft()
        assert g.entries == []
        assert g.content == ""

    def test_with_entries(self) -> None:
        g = GlossaryDraft(
            entries=[GlossaryEntry(term="API", definition="Application Programming Interface")],
        )
        assert len(g.entries) == 1
        assert g.entries[0].term == "API"


class TestReferenceDraft:
    def test_defaults(self) -> None:
        r = ReferenceDraft()
        assert r.entries == []
        assert r.content == ""

    def test_with_entries(self) -> None:
        r = ReferenceDraft(
            entries=[ReferenceEntry(title="Ref1", content="details")],
        )
        assert r.entries[0].title == "Ref1"


class TestValidationMessage:
    def test_default_severity(self) -> None:
        m = ValidationMessage(message="test")
        assert m.severity == "warning"


class TestWritingConfig:
    def test_defaults(self) -> None:
        c = WritingConfig()
        assert c.temperature == 0.7
        assert c.max_tokens == 4096
        assert c.target_word_count == 800

    def test_default_classmethod(self) -> None:
        c = WritingConfig.default()
        assert isinstance(c, WritingConfig)
