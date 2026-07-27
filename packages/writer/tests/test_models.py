from bookforge.writer.enums import DraftQuality, WritingStatus
from bookforge.writer.models import (
    DraftBook,
    DraftChapter,
    DraftFrontMatter,
    DraftGlossary,
    DraftReferences,
    DraftSection,
    GlossaryEntry,
    ReferenceEntry,
    ValidationMessage,
    WritingConfig,
    WritingContext,
    WritingSession,
    WritingStatistics,
)


class TestDraftSection:
    def test_defaults(self) -> None:
        s = DraftSection(heading="Intro")
        assert s.content == ""
        assert s.word_count == 0
        assert s.total_word_count == 0

    def test_total_word_count_includes_subsections(self) -> None:
        sub = DraftSection(heading="Sub", content="words here", word_count=2)
        parent = DraftSection(heading="Parent", content="hello", word_count=1, subsections=[sub])
        assert parent.total_word_count == 3


class TestDraftChapter:
    def test_defaults(self) -> None:
        c = DraftChapter(title="Ch1")
        assert c.status == WritingStatus.PENDING
        assert c.word_count == 0

    def test_total_word_count(self) -> None:
        s = DraftSection(heading="Sec", content="some words", word_count=2)
        c = DraftChapter(title="Ch1", content="hello", word_count=1, sections=[s])
        assert c.total_word_count == 3


class TestDraftBook:
    def test_defaults(self) -> None:
        d = DraftBook(title="Test", topic="Testing")
        assert d.chapter_count == 0
        assert d.quality == DraftQuality.DRAFT
        assert d.status == WritingStatus.PENDING

    def test_total_word_count_aggregates(self) -> None:
        c1 = DraftChapter(title="Ch1", content="hello", word_count=1)
        fm = DraftFrontMatter(title="Preface", content="intro", word_count=2)
        d = DraftBook(title="Test", topic="T", chapters=[c1], front_matter=[fm])
        assert d.total_word_count == 3

    def test_chapter_count(self) -> None:
        d = DraftBook(
            title="Test", topic="T",
            chapters=[DraftChapter(title="A"), DraftChapter(title="B")],
        )
        assert d.chapter_count == 2


class TestDraftGlossary:
    def test_defaults(self) -> None:
        g = DraftGlossary()
        assert g.entries == []
        assert g.content == ""

    def test_with_entries(self) -> None:
        g = DraftGlossary(
            entries=[GlossaryEntry(term="API", definition="Application Programming Interface")],
        )
        assert len(g.entries) == 1
        assert g.entries[0].term == "API"


class TestDraftReferences:
    def test_defaults(self) -> None:
        r = DraftReferences()
        assert r.entries == []
        assert r.content == ""

    def test_with_entries(self) -> None:
        r = DraftReferences(
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


class TestWritingContext:
    def test_defaults(self) -> None:
        ctx = WritingContext(book_title="Test", book_topic="Python")
        assert ctx.target_audience == "developers"
        assert ctx.style_guidelines == "technical"

    def test_from_blueprint(self) -> None:
        class FakeBlueprint:
            title = "Book"
            topic = "Python"
            target_audience = "beginners"
            difficulty = 0.3

        bp = FakeBlueprint()
        ctx = WritingContext.from_blueprint(bp)
        assert ctx.book_title == "Book"
        assert ctx.book_topic == "Python"
        assert ctx.target_audience == "beginners"

    def test_from_blueprint_with_research(self) -> None:
        class FakeBlueprint:
            title = "Book"
            topic = "Python"
            target_audience = "devs"
            difficulty = 0.5

        kc = type("KC", (), {"name": "Python"})()
        class FakeResearch:
            summary = "Research summary"
            def __init__(self) -> None:
                self.key_concepts = [kc]
                self.learning_objectives = ["Learn X"]

        ctx = WritingContext.from_blueprint(FakeBlueprint(), FakeResearch())
        assert ctx.research_summary == "Research summary"
        assert "Python" in ctx.key_concepts
        assert "Learn X" in ctx.learning_objectives


class TestWritingSession:
    def test_defaults(self) -> None:
        ctx = WritingContext(book_title="T", book_topic="T")
        s = WritingSession(session_id="s1", context=ctx)
        assert s.status == WritingStatus.PENDING
        assert s.draft is None


class TestWritingStatistics:
    def test_from_draft(self) -> None:
        draft = DraftBook(
            title="T", topic="T",
            chapters=[DraftChapter(title="Ch1", content="Hi", word_count=2, status=WritingStatus.COMPLETED)],
        )
        stats = WritingStatistics.from_draft(draft)
        assert stats.total_chapters == 1
        assert stats.written_chapters == 1
        assert stats.total_word_count == 2
