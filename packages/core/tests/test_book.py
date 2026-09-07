"""Tests for book domain entities."""

import pytest
from pydantic import ValidationError

from bookforge.core.book import (
    Book,
    BookConfiguration,
    BookMetadata,
    BookSettings,
    BookSpecification,
    Chapter,
    Project,
    Section,
)
from bookforge.core.content import Paragraph
from bookforge.core.enums import (
    Audience,
    BloomLevel,
    BookStatus,
    Difficulty,
    GenerationStage,
    Language,
)
from bookforge.core.serialization import from_yaml, to_yaml
from bookforge.core.value_objects import Version


class TestBookMetadata:
    def test_create_minimal(self) -> None:
        meta = BookMetadata(title="Test Book")
        assert meta.title == "Test Book"
        assert meta.language == Language.ENGLISH
        assert meta.edition == 1

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValidationError):
            BookMetadata(title="")

    def test_whitespace_title_raises(self) -> None:
        with pytest.raises(ValidationError):
            BookMetadata(title="   ")

    def test_full_metadata(self) -> None:
        meta = BookMetadata(
            title="Advanced Python",
            subtitle="A Deep Dive",
            description="An advanced book",
            language=Language.GERMAN,
            tags=["python", "advanced"],
            edition=2,
        )
        assert meta.subtitle == "A Deep Dive"
        assert meta.language == Language.GERMAN
        assert len(meta.tags) == 2


class TestBookSpecification:
    def test_defaults(self) -> None:
        spec = BookSpecification()
        assert spec.target_audience == Audience.DEVELOPERS
        assert spec.difficulty == Difficulty.INTERMEDIATE
        assert spec.code_first is True

    def test_custom(self) -> None:
        spec = BookSpecification(
            target_audience=Audience.STUDENTS,
            difficulty=Difficulty.BEGINNER,
            estimated_page_count=200,
            bloom_level=BloomLevel.REMEMBER,
        )
        assert spec.target_audience == Audience.STUDENTS
        assert spec.estimated_page_count == 200

    def test_negative_page_count_raises(self) -> None:
        with pytest.raises(ValidationError):
            BookSpecification(estimated_page_count=-1)


class TestBookSettings:
    def test_defaults(self) -> None:
        settings = BookSettings()
        assert settings.temperature == 0.7
        assert settings.verbosity == "balanced"
        assert settings.use_active_voice is True

    def test_temperature_out_of_range_raises(self) -> None:
        with pytest.raises(ValidationError):
            BookSettings(temperature=3.0)

    def test_invalid_verbosity_raises(self) -> None:
        with pytest.raises(ValidationError):
            BookSettings(verbosity="extreme")


class TestBookConfiguration:
    def test_defaults(self) -> None:
        config = BookConfiguration()
        assert config.status == BookStatus.DRAFT
        assert config.stage == GenerationStage.CREATED
        assert config.is_locked is False

    def test_custom(self) -> None:
        config = BookConfiguration(
            status=BookStatus.PUBLISHED,
            stage=GenerationStage.EXPORTED,
            is_locked=True,
            version=Version(major=1, minor=0, patch=0),
        )
        assert config.status == BookStatus.PUBLISHED
        assert config.is_locked is True


class TestSection:
    def test_create_minimal(self) -> None:
        section = Section(id="sec1", heading="Introduction")
        assert section.id == "sec1"
        assert section.heading == "Introduction"
        assert section.heading_level == 2

    def test_empty_heading_raises(self) -> None:
        with pytest.raises(ValidationError):
            Section(id="sec1", heading="")

    def test_with_paragraphs(self) -> None:
        para = Paragraph(id="p1", text="Hello world")
        section = Section(id="sec1", heading="Intro", paragraphs=[para])
        assert len(section.paragraphs) == 1
        assert section.paragraphs[0].text == "Hello world"

    def test_nested_subsections(self) -> None:
        sub = Section(id="sub1", heading="Sub Section", heading_level=3)
        parent = Section(id="parent", heading="Parent", subsections=[sub])
        assert len(parent.subsections) == 1
        assert parent.subsections[0].heading_level == 3


class TestChapter:
    def test_create_minimal(self) -> None:
        chapter = Chapter(id="ch1", number=1, title="Getting Started")
        assert chapter.number == 1
        assert chapter.title == "Getting Started"

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValidationError):
            Chapter(id="ch1", number=1, title="")

    def test_zero_number_raises(self) -> None:
        with pytest.raises(ValidationError):
            Chapter(id="ch1", number=0, title="Intro")

    def test_with_sections(self) -> None:
        section = Section(id="sec1", heading="Overview")
        chapter = Chapter(
            id="ch1",
            number=1,
            title="Intro",
            sections=[section],
            estimated_page_count=15,
        )
        assert len(chapter.sections) == 1
        assert chapter.estimated_page_count == 15


class TestBook:
    def test_create_minimal(self) -> None:
        meta = BookMetadata(title="Test Book")
        book = Book(id="book1", metadata=meta)
        assert book.id == "book1"
        assert book.metadata.title == "Test Book"
        assert len(book.chapters) == 0

    def test_empty_id_raises(self) -> None:
        meta = BookMetadata(title="Test")
        with pytest.raises(ValidationError):
            Book(id="", metadata=meta)

    def test_add_chapter(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta)
        chapter = Chapter(id="ch1", number=1, title="Intro")
        book.add_chapter(chapter)
        assert len(book.chapters) == 1

    def test_add_duplicate_chapter_number_raises(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta)
        ch1 = Chapter(id="ch1", number=1, title="Intro")
        ch2 = Chapter(id="ch2", number=1, title="Intro 2")
        book.add_chapter(ch1)
        with pytest.raises(ValueError, match="already exists"):
            book.add_chapter(ch2)

    def test_duplicate_chapter_number_at_validation(self) -> None:
        meta = BookMetadata(title="Test")
        ch1 = Chapter(id="ch1", number=1, title="Intro")
        ch2 = Chapter(id="ch2", number=1, title="Intro 2")
        with pytest.raises(ValidationError, match="Duplicate chapter numbers"):
            Book(id="book1", metadata=meta, chapters=[ch1, ch2])

    def test_duplicate_chapter_id_at_validation(self) -> None:
        meta = BookMetadata(title="Test")
        ch1 = Chapter(id="ch1", number=1, title="Intro")
        ch2 = Chapter(id="ch1", number=2, title="Intro 2")
        with pytest.raises(ValidationError, match="Duplicate chapter IDs"):
            Book(id="book1", metadata=meta, chapters=[ch1, ch2])

    def test_remove_chapter(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta)
        ch1 = Chapter(id="ch1", number=1, title="Intro")
        book.add_chapter(ch1)
        book.remove_chapter("ch1")
        assert len(book.chapters) == 0

    def test_get_chapter_by_number(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta)
        ch = Chapter(id="ch1", number=1, title="Intro")
        book.add_chapter(ch)
        assert book.get_chapter_by_number(1) is ch
        assert book.get_chapter_by_number(99) is None

    def test_total_estimated_pages(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta)
        book.add_chapter(Chapter(id="ch1", number=1, title="Ch1", estimated_page_count=10))
        book.add_chapter(Chapter(id="ch2", number=2, title="Ch2", estimated_page_count=20))
        assert book.total_estimated_pages() == 30

    def test_with_references(self) -> None:
        from bookforge.core.reference import Reference

        meta = BookMetadata(title="Test")
        ref = Reference(id="ref1", title="A Book", authors=["Smith"], year=2024)
        book = Book(id="book1", metadata=meta, references=[ref])
        assert len(book.references) == 1
        assert book.references[0].title == "A Book"

    def test_duplicate_reference_ids_at_validation(self) -> None:
        from bookforge.core.reference import Reference

        meta = BookMetadata(title="Test")
        ref1 = Reference(id="ref1", title="Book A", authors=["A"], year=2024)
        ref2 = Reference(id="ref1", title="Book B", authors=["B"], year=2024)
        with pytest.raises(ValidationError, match="Duplicate reference IDs"):
            Book(id="book1", metadata=meta, references=[ref1, ref2])

    def test_with_glossary(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta, glossary_terms={"API": "Application Programming Interface"})
        assert book.glossary_terms["API"] == "Application Programming Interface"
        assert len(book.glossary_terms) == 1


class TestProject:
    def test_create_minimal(self) -> None:
        project = Project(id="proj1", name="My Book Project")
        assert project.id == "proj1"
        assert project.name == "My Book Project"
        assert len(project.books) == 0

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            Project(id="proj1", name="")

    def test_add_book(self) -> None:
        project = Project(id="proj1", name="Test Project")
        meta = BookMetadata(title="Book 1")
        book = Book(id="book1", metadata=meta)
        project.add_book(book)
        assert len(project.books) == 1

    def test_add_duplicate_book_raises(self) -> None:
        project = Project(id="proj1", name="Test Project")
        meta = BookMetadata(title="Book 1")
        book = Book(id="book1", metadata=meta)
        project.add_book(book)
        with pytest.raises(ValueError, match="already exists"):
            project.add_book(Book(id="book1", metadata=BookMetadata(title="Book 2")))

    def test_duplicate_book_ids_at_validation(self) -> None:
        meta1 = BookMetadata(title="Book 1")
        meta2 = BookMetadata(title="Book 2")
        with pytest.raises(ValidationError, match="Duplicate book IDs"):
            Project(
                id="proj1",
                name="Test",
                books=[Book(id="book1", metadata=meta1), Book(id="book1", metadata=meta2)],
            )

    def test_get_book(self) -> None:
        project = Project(id="proj1", name="Test")
        meta = BookMetadata(title="Book 1")
        book = Book(id="book1", metadata=meta)
        project.add_book(book)
        assert project.get_book("book1") is book
        assert project.get_book("nonexistent") is None

    def test_remove_book(self) -> None:
        project = Project(id="proj1", name="Test")
        meta = BookMetadata(title="Book 1")
        book = Book(id="book1", metadata=meta)
        project.add_book(book)
        project.remove_book("book1")
        assert len(project.books) == 0

    def test_full_project(self) -> None:
        project = Project(id="proj1", name="Full Project", description="A description")
        meta = BookMetadata(
            title="Advanced Python",
            language=Language.ENGLISH,
            tags=["python"],
        )
        spec = BookSpecification(difficulty=Difficulty.ADVANCED)
        book = Book(id="book1", metadata=meta, specification=spec)
        chapter = Chapter(id="ch1", number=1, title="Deep Dives")
        section = Section(id="sec1", heading="Meta Classes")
        section.paragraphs.append(Paragraph(text="Content here"))
        chapter.sections.append(section)
        book.add_chapter(chapter)
        project.add_book(book)
        assert project.get_book("book1") is book
        assert book.get_chapter("ch1") is chapter
        assert chapter.sections[0].paragraphs[0].text == "Content here"


class TestSerialization:
    def test_book_to_dict(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta)
        d = book.model_dump()
        assert d["id"] == "book1"
        assert d["metadata"]["title"] == "Test"
        assert "chapters" in d

    def test_book_from_dict(self) -> None:
        d = {"id": "book1", "metadata": {"title": "Test"}}
        book = Book.model_validate(d)
        assert book.id == "book1"
        assert book.metadata.title == "Test"

    def test_book_to_json(self) -> None:
        meta = BookMetadata(title="Test")
        book = Book(id="book1", metadata=meta)
        json_str = book.model_dump_json()
        assert '"id"' in json_str
        assert '"title"' in json_str

    def test_project_to_dict(self) -> None:
        project = Project(id="proj1", name="Test")
        d = project.model_dump()
        assert d["id"] == "proj1"
        assert d["name"] == "Test"

    def test_complex_roundtrip(self) -> None:
        para = Paragraph(text="Hello")
        section = Section(id="sec1", heading="Intro", paragraphs=[para])
        chapter = Chapter(id="ch1", number=1, title="Start", sections=[section])
        meta = BookMetadata(title="Test Book", tags=["tag1"])
        book = Book(id="book1", metadata=meta, chapters=[chapter])
        d = book.model_dump()
        restored = Book.model_validate(d)
        assert restored.id == "book1"
        assert restored.metadata.title == "Test Book"
        assert restored.chapters[0].title == "Start"
        assert restored.chapters[0].sections[0].paragraphs[0].text == "Hello"

    def test_yaml_roundtrip(self) -> None:
        meta = BookMetadata(title="YAML Test", language=Language.FRENCH)
        chapter = Chapter(id="ch1", number=1, title="Chapter One")
        book = Book(id="book1", metadata=meta, chapters=[chapter])
        yaml_str = to_yaml(book)
        restored = from_yaml(Book, yaml_str)
        assert restored.id == "book1"
        assert restored.metadata.title == "YAML Test"
        assert restored.metadata.language == Language.FRENCH
        assert restored.chapters[0].title == "Chapter One"

    def test_yaml_roundtrip_with_all_fields(self) -> None:
        para = Paragraph(text="Content")
        section = Section(id="sec1", heading="Intro", paragraphs=[para])
        chapter = Chapter(id="ch1", number=1, title="Start", sections=[section])
        meta = BookMetadata(title="Full Book", tags=["a", "b"])
        book = Book(id="book1", metadata=meta, chapters=[chapter])
        yaml_str = to_yaml(book)
        restored = from_yaml(Book, yaml_str)
        assert restored.id == "book1"
        assert restored.chapters[0].sections[0].paragraphs[0].text == "Content"
        assert restored.metadata.tags == ["a", "b"]
