from bookforge.writer.assembler import MarkdownAssembler
from bookforge.writer.models import (
    DraftBackMatter,
    DraftBook,
    DraftChapter,
    DraftFrontMatter,
    DraftGlossary,
    DraftSection,
)


class TestMarkdownAssembler:
    def setup_method(self) -> None:
        self.assembler = MarkdownAssembler()

    def test_assemble_empty_draft(self) -> None:
        draft = DraftBook(title="Test", topic="T")
        result = self.assembler.assemble(draft)
        assert result == "# Test"

    def test_assemble_with_chapter_content(self) -> None:
        draft = DraftBook(
            title="Guide", topic="T",
            chapters=[DraftChapter(title="Ch1", content="## Ch1\n\nContent here")],
        )
        result = self.assembler.assemble(draft)
        assert "# Guide" in result
        assert "## Ch1" in result

    def test_assemble_with_sections(self) -> None:
        draft = DraftBook(
            title="Guide", topic="T",
            chapters=[
                DraftChapter(
                    title="Ch1",
                    sections=[DraftSection(heading="Sec1", content="Section content")],
                )
            ],
        )
        result = self.assembler.assemble(draft)
        assert "Sec1" in result

    def test_assemble_with_front_back_matter(self) -> None:
        draft = DraftBook(
            title="Guide", topic="T",
            front_matter=[DraftFrontMatter(title="Preface", content="Preface content")],
            back_matter=[DraftBackMatter(title="Index", content="Index content")],
        )
        result = self.assembler.assemble(draft)
        assert "Preface" in result
        assert "Index" in result

    def test_assemble_with_glossary(self) -> None:
        draft = DraftBook(
            title="Guide", topic="T",
            glossary=DraftGlossary(content="**API**: Application Interface"),
        )
        result = self.assembler.assemble(draft)
        assert "Glossary" in result

    def test_assemble_chapter_markdown(self) -> None:
        chapter = DraftChapter(title="Ch1", content="## Ch1\n\nBody")
        result = self.assembler.assemble_chapter_markdown(chapter)
        assert "Ch1" in result

    def test_extract_headings(self) -> None:
        md = "# Title\n## Section\n### Subsection\nParagraph"
        headings = self.assembler.extract_headings(md)
        assert headings == [(1, "Title"), (2, "Section"), (3, "Subsection")]

    def test_validate_markdown_structure(self) -> None:
        md = "# Good\n## Also good\ninvalid heading"
        issues = self.assembler.validate_markdown_structure(md)
        assert len(issues) == 0

    def test_validate_markdown_structure_bad_heading(self) -> None:
        md = "#NoSpace"
        issues = self.assembler.validate_markdown_structure(md)
        assert len(issues) >= 1
