"""Tests for reference domain entities."""

import pytest
from pydantic import ValidationError

from bookforge.core.enums import ReferenceType
from bookforge.core.reference import Bibliography, Citation, Reference
from bookforge.core.value_objects import URL


class TestReference:
    def test_create_minimal(self) -> None:
        ref = Reference(
            id="ref1",
            title="Learning Python",
            authors=["Mark Lutz"],
            year=2013,
        )
        assert ref.id == "ref1"
        assert ref.title == "Learning Python"
        assert ref.authors == ["Mark Lutz"]
        assert ref.year == 2013
        assert ref.reference_type == ReferenceType.BOOK

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValidationError):
            Reference(id="ref1", title="", authors=["A"], year=2024)

    def test_empty_authors_raises(self) -> None:
        with pytest.raises(ValidationError):
            Reference(id="ref1", title="Title", authors=[], year=2024)

    def test_full_reference(self) -> None:
        ref = Reference(
            id="ref1",
            reference_type=ReferenceType.ARTICLE,
            title="A Paper",
            authors=["Alice", "Bob"],
            year=2024,
            journal="Journal of Things",
            volume="12",
            issue="3",
            pages="45-67",
            doi="10.1234/example",
        )
        assert ref.reference_type == ReferenceType.ARTICLE
        assert ref.journal == "Journal of Things"
        assert ref.doi == "10.1234/example"

    def test_with_url(self) -> None:
        ref = Reference(
            id="ref1",
            title="Online Resource",
            authors=["Author"],
            year=2024,
            reference_type=ReferenceType.WEBSITE,
            url=URL(url="https://example.com"),
        )
        assert ref.url is not None
        assert ref.url.url == "https://example.com"


class TestCitation:
    def test_create_minimal(self) -> None:
        cit = Citation(id="cit1", reference_id="ref1")
        assert cit.id == "cit1"
        assert cit.reference_id == "ref1"

    def test_empty_id_raises(self) -> None:
        with pytest.raises(ValidationError):
            Citation(id="", reference_id="ref1")

    def test_empty_reference_id_raises(self) -> None:
        with pytest.raises(ValidationError):
            Citation(id="cit1", reference_id="")

    def test_with_context(self) -> None:
        cit = Citation(
            id="cit1",
            reference_id="ref1",
            context="As discussed in earlier work",
            page_range="42-45",
            chapter_number=3,
            quotation="Exact quote here",
        )
        assert cit.context is not None
        assert cit.page_range == "42-45"
        assert cit.chapter_number == 3


class TestBibliography:
    def test_create_default(self) -> None:
        bib = Bibliography(id="bib1")
        assert bib.title == "References"
        assert len(bib.references) == 0
        assert bib.style == "apa"

    def test_custom_style(self) -> None:
        bib = Bibliography(id="bib1", style="ieee")
        assert bib.style == "ieee"

    def test_invalid_style_raises(self) -> None:
        with pytest.raises(ValidationError):
            Bibliography(id="bib1", style="invalid")

    def test_add_reference(self) -> None:
        bib = Bibliography(id="bib1")
        ref = Reference(id="ref1", title="A Book", authors=["Author"], year=2024)
        bib.add_reference(ref)
        assert len(bib.references) == 1

    def test_add_duplicate_reference_raises(self) -> None:
        bib = Bibliography(id="bib1")
        ref = Reference(id="ref1", title="A Book", authors=["Author"], year=2024)
        bib.add_reference(ref)
        with pytest.raises(ValueError, match="already exists"):
            bib.add_reference(ref)

    def test_duplicate_reference_ids_at_construction(self) -> None:
        ref1 = Reference(id="ref1", title="A Book", authors=["Author"], year=2024)
        ref2 = Reference(id="ref1", title="Another Book", authors=["Author"], year=2025)
        with pytest.raises(ValidationError, match="Duplicate reference IDs"):
            Bibliography(id="bib1", references=[ref1, ref2])

    def test_remove_reference(self) -> None:
        bib = Bibliography(id="bib1")
        ref = Reference(id="ref1", title="A Book", authors=["Author"], year=2024)
        bib.add_reference(ref)
        bib.remove_reference("ref1")
        assert len(bib.references) == 0

    def test_get_reference(self) -> None:
        bib = Bibliography(id="bib1")
        ref = Reference(id="ref1", title="A Book", authors=["Author"], year=2024)
        bib.add_reference(ref)
        assert bib.get_reference("ref1") is ref
        assert bib.get_reference("nonexistent") is None
