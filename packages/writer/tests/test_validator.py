from bookforge.writer.models import BookDraft, ChapterDraft, SectionDraft
from bookforge.writer.validator import ContentValidator


class TestContentValidator:
    def setup_method(self) -> None:
        self.validator = ContentValidator()

    def test_valid_draft_no_errors(self) -> None:
        draft = BookDraft(
            title="Test", topic="T",
            chapters=[ChapterDraft(title="Ch1", content="Content here", word_count=100)],
        )
        messages = self.validator.validate(draft)
        errors = [m for m in messages if m.severity == "error"]
        assert len(errors) == 0

    def test_empty_chapter_is_error(self) -> None:
        draft = BookDraft(
            title="Test", topic="T",
            chapters=[ChapterDraft(title="Ch1")],
        )
        messages = self.validator.validate(draft)
        errors = [m for m in messages if m.severity == "error"]
        assert len(errors) >= 1
        assert any("Ch1" in e.message for e in errors)

    def test_short_chapter_is_warning(self) -> None:
        draft = BookDraft(
            title="Test", topic="T",
            chapters=[ChapterDraft(title="Ch1", content="Hi", word_count=2)],
        )
        messages = self.validator.validate(draft)
        warnings = [m for m in messages if "short" in m.message.lower()]
        assert len(warnings) >= 1

    def test_empty_section_is_warning(self) -> None:
        draft = BookDraft(
            title="Test", topic="T",
            chapters=[
                ChapterDraft(
                    title="Ch1",
                    sections=[SectionDraft(heading="Sec1")],
                )
            ],
        )
        messages = self.validator.validate(draft)
        warnings = [m for m in messages if m.severity == "warning"]
        assert any("Sec1" in w.message for w in warnings)

    def test_h1_in_chapter_is_warning(self) -> None:
        draft = BookDraft(
            title="Test", topic="T",
            chapters=[ChapterDraft(title="Ch1", content="# H1 heading\n\nContent")],
        )
        messages = self.validator.validate(draft)
        warnings = [m for m in messages if "H1" in m.message]
        assert len(warnings) >= 1

    def test_empty_front_matter_is_warning(self) -> None:
        from bookforge.writer.models import FrontMatterDraft
        draft = BookDraft(
            title="Test", topic="T",
            front_matter=[FrontMatterDraft(title="Preface")],
        )
        messages = self.validator.validate(draft)
        warnings = [m for m in messages if "Preface" in m.message]
        assert len(warnings) >= 1
