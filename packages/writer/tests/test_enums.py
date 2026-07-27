from bookforge.writer.enums import DraftQuality, ValidationSeverity, WritingStage, WritingStatus


class TestWritingStatus:
    def test_values(self) -> None:
        assert WritingStatus.PENDING == "pending"
        assert WritingStatus.GENERATING == "generating"
        assert WritingStatus.VALIDATING == "validating"
        assert WritingStatus.COMPLETED == "completed"
        assert WritingStatus.FAILED == "failed"


class TestWritingStage:
    def test_values(self) -> None:
        assert WritingStage.CHAPTER_WRITING == "chapter_writing"
        assert WritingStage.SECTION_WRITING == "section_writing"
        assert WritingStage.GLOSSARY_WRITING == "glossary_writing"
        assert WritingStage.REFERENCE_WRITING == "reference_writing"
        assert WritingStage.ASSEMBLING == "assembling"
        assert WritingStage.VALIDATING == "validating"
        assert WritingStage.EXPORTING == "exporting"


class TestDraftQuality:
    def test_values(self) -> None:
        assert DraftQuality.DRAFT == "draft"
        assert DraftQuality.REVIEW == "review"
        assert DraftQuality.POLISHED == "polished"
        assert DraftQuality.FINAL == "final"


class TestValidationSeverity:
    def test_values(self) -> None:
        assert ValidationSeverity.ERROR == "error"
        assert ValidationSeverity.WARNING == "warning"
        assert ValidationSeverity.INFO == "info"
