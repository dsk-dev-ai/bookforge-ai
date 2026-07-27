from bookforge.writer.assembler import MarkdownAssembler
from bookforge.writer.models import BookDraft, ChapterDraft, SectionDraft


class TestMarkdownAssembler:
    def setup_method(self) -> None:
        self.assembler = MarkdownAssembler()

    def test_assemble_empty_draft(self) -> None:
        draft = BookDraft(title="Test", topic="T")
        result = self.assembler.assemble(draft)
        assert result == "# Test"

    def test_assemble_with_chapter_content(self) -> None:
        draft = BookDraft(
            title="Guide",
            topic="T",
            chapters=[ChapterDraft(title="Ch1", content="## Ch1\n\nContent here")],
        )
        result = self.assembler.assemble(draft)
        assert "# Guide" in result
        assert "## Ch1" in result
        assert "Content here" in result

    def test_assemble_with_sections(self) -> None:
        draft = BookDraft(
            title="Guide",
            topic="T",
            chapters=[
                ChapterDraft(
                    title="Ch1",
                    sections=[SectionDraft(heading="Sec1", content="Section content")],
                )
            ],
        )
        result = self.assembler.assemble(draft)
        assert "Sec1" in result
        assert "Section content" in result

    def test_assemble_with_front_back_matter(self) -> None:
        from bookforge.writer.models import BackMatterDraft, FrontMatterDraft
        draft = BookDraft(
            title="Guide",
            topic="T",
            front_matter=[FrontMatterDraft(title="Preface", content="Preface content")],
            back_matter=[BackMatterDraft(title="Index", content="Index content")],
        )
        result = self.assembler.assemble(draft)
        assert "Preface" in result
        assert "Index" in result
        assert "Preface content" in result

    def test_assemble_with_glossary(self) -> None:
        from bookforge.writer.models import GlossaryDraft
        draft = BookDraft(
            title="Guide",
            topic="T",
            glossary=GlossaryDraft(content="**API**: Application Interface"),
        )
        result = self.assembler.assemble(draft)
        assert "Glossary" in result
        assert "API" in result

    def test_assemble_chapter_markdown(self) -> None:
        chapter = ChapterDraft(title="Ch1", content="## Ch1\n\nBody")
        result = self.assembler.assemble_chapter_markdown(chapter)
        assert "Ch1" in result
