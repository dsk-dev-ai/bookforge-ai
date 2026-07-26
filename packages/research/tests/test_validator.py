"""Tests for ResearchValidator."""

from bookforge.research.enums import SourceType
from bookforge.research.models import ResearchDocument, ResearchSource
from bookforge.research.validator import ResearchValidator, ValidationError


class TestResearchValidator:
    def test_validate_valid_source(self) -> None:
        validator = ResearchValidator()
        source = ResearchSource(
            id="s1",
            title="Valid Source",
            url="https://example.com/doc",
            source_type=SourceType.DOCUMENTATION,
            content="Some content",
        )
        errors = validator.validate_sources([source])
        assert errors == []

    def test_validate_empty_title(self) -> None:
        validator = ResearchValidator()
        source = ResearchSource(id="s1", title="", source_type=SourceType.BLOG, content="Body")
        errors = validator.validate_sources([source])
        assert any("empty title" in e.message for e in errors)

    def test_validate_invalid_url(self) -> None:
        validator = ResearchValidator()
        source = ResearchSource(
            id="s1", title="Title", url="not-a-url", source_type=SourceType.BLOG, content="Body",
        )
        errors = validator.validate_sources([source])
        assert any("invalid url" in e.message.lower() for e in errors)

    def test_validate_empty_content(self) -> None:
        validator = ResearchValidator()
        source = ResearchSource(id="s1", title="Title", source_type=SourceType.BLOG, content="")
        errors = validator.validate_sources([source])
        assert any("empty content" in e.message for e in errors)

    def test_validate_duplicate_url(self) -> None:
        validator = ResearchValidator()
        sources = [
            ResearchSource(id="s1", title="A", url="https://example.com/doc",
                           source_type=SourceType.BLOG, content="Content"),
            ResearchSource(id="s2", title="B", url="https://example.com/doc",
                           source_type=SourceType.BLOG, content="Other"),
        ]
        errors = validator.validate_sources(sources)
        assert any("Duplicate" in e.message and "url" in e.field for e in errors)

    def test_validate_duplicate_id(self) -> None:
        validator = ResearchValidator()
        sources = [
            ResearchSource(id="same", title="A", source_type=SourceType.BLOG, content="C1"),
            ResearchSource(id="same", title="B", source_type=SourceType.BLOG, content="C2"),
        ]
        errors = validator.validate_sources(sources)
        assert any("Duplicate source ID" in e.message for e in errors)

    def test_validate_document_empty_title(self) -> None:
        validator = ResearchValidator()
        doc = ResearchDocument(id="d1", source_id="s1", title="", content="Some content")
        errors = validator.validate_documents([doc])
        assert any("empty title" in e.message for e in errors)

    def test_validate_document_empty_content_and_sections(self) -> None:
        validator = ResearchValidator()
        doc = ResearchDocument(id="d1", source_id="s1", title="Title", content="")
        errors = validator.validate_documents([doc])
        assert any("no content or sections" in e.message for e in errors)

    def test_validate_document_missing_source_id(self) -> None:
        validator = ResearchValidator()
        doc = ResearchDocument(id="d1", source_id="", title="Title", content="Content")
        errors = validator.validate_documents([doc])
        assert any("missing source_id" in e.message for e in errors)

    def test_validate_document_duplicate_title(self) -> None:
        validator = ResearchValidator()
        docs = [
            ResearchDocument(id="d1", source_id="s1", title="Same Title", content="C1"),
            ResearchDocument(id="d2", source_id="s2", title="Same Title", content="C2"),
        ]
        errors = validator.validate_documents(docs)
        assert any("Duplicate" in e.message for e in errors)

    def test_validate_url_valid(self) -> None:
        validator = ResearchValidator()
        assert validator.validate_url("https://example.com") is True

    def test_validate_url_invalid(self) -> None:
        validator = ResearchValidator()
        assert validator.validate_url("not a url") is False

    def test_validate_url_none(self) -> None:
        validator = ResearchValidator()
        assert validator.validate_url(None) is True

    def test_has_empty_summary(self) -> None:
        validator = ResearchValidator()
        assert validator.has_empty_summary("") is True
        assert validator.has_empty_summary("   ") is True
        assert validator.has_empty_summary(None) is True
        assert validator.has_empty_summary("Summary text") is False

    def test_has_duplicate_sources(self) -> None:
        validator = ResearchValidator()
        sources = [
            ResearchSource(id="s1", title="A", url="https://ex.com/a",
                           source_type=SourceType.BLOG, content="C"),
            ResearchSource(id="s2", title="B", url="https://ex.com/a",
                           source_type=SourceType.BLOG, content="D"),
        ]
        assert validator.has_duplicate_sources(sources) is True

    def test_format_errors(self) -> None:
        errors = [ValidationError("Bad field", "title", "id1")]
        formatted = ResearchValidator.format_errors(errors)
        assert formatted == [{"message": "Bad field", "field": "title", "item_id": "id1"}]
