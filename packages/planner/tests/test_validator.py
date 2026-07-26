
from bookforge.planner.enums import ValidationSeverity
from bookforge.planner.models import BookBlueprint, BookOutline, ChapterPlan, SectionPlan
from bookforge.planner.validator import OutlineValidator, ValidationMessage


class TestValidationMessage:
    def test_default_severity(self) -> None:
        msg = ValidationMessage("Error")
        assert msg.severity == ValidationSeverity.ERROR

    def test_equality(self) -> None:
        a = ValidationMessage("Msg", ValidationSeverity.ERROR, "f", "1")
        b = ValidationMessage("Msg", ValidationSeverity.ERROR, "f", "1")
        assert a == b

    def test_inequality(self) -> None:
        a = ValidationMessage("A")
        b = ValidationMessage("B")
        assert a != b

    def test_not_equal_to_other_type(self) -> None:
        msg = ValidationMessage("Test")
        assert msg != "not a message"


class TestOutlineValidator:
    def test_no_outline(self) -> None:
        validator = OutlineValidator()
        bp = BookBlueprint(title="T", topic="T")
        errors = validator.validate_blueprint(bp)
        assert any("no outline" in e.message.lower() for e in errors)

    def test_empty_title(self) -> None:
        validator = OutlineValidator()
        outline = BookOutline(title="", chapters=[ChapterPlan(title="Ch1")])
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=1)
        errors = validator.validate_blueprint(bp)
        assert any("empty title" in e.message.lower() for e in errors)

    def test_no_chapters(self) -> None:
        validator = OutlineValidator()
        outline = BookOutline(title="Test")
        bp = BookBlueprint(title="T", topic="T", outline=outline)
        errors = validator.validate_blueprint(bp)
        assert any("no chapters" in e.message.lower() for e in errors)

    def test_duplicate_chapters(self) -> None:
        validator = OutlineValidator()
        chapters = [ChapterPlan(title="Same"), ChapterPlan(title="Same")]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=2)
        errors = validator.validate_blueprint(bp)
        assert any("duplicate" in e.message.lower() for e in errors)

    def test_duplicate_sections(self) -> None:
        validator = OutlineValidator()
        sections = [SectionPlan(heading="Intro"), SectionPlan(heading="Intro")]
        ch = ChapterPlan(title="Ch1", sections=sections)
        outline = BookOutline(title="T", chapters=[ch])
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=1)
        errors = validator.validate_blueprint(bp)
        assert any("duplicate section" in e.message.lower() for e in errors)

    def test_missing_prerequisites(self) -> None:
        validator = OutlineValidator()
        chapters = [ChapterPlan(title="Ch2", prerequisites=["Missing"])]
        outline = BookOutline(title="T", chapters=chapters)
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=1)
        errors = validator.validate_blueprint(bp)
        assert any("missing prerequisite" in e.message.lower() for e in errors)

    def test_no_learning_objectives_warning(self) -> None:
        validator = OutlineValidator()
        ch = ChapterPlan(title="Ch1", sections=[SectionPlan(heading="S1")])
        outline = BookOutline(title="T", chapters=[ch])
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=1)
        errors = validator.validate_blueprint(bp)
        assert any("learning objectives" in e.message.lower() for e in errors)

    def test_validate_chapter(self) -> None:
        validator = OutlineValidator()
        ch = ChapterPlan(title="Ch1", sections=[SectionPlan(heading="S1")])
        errors = validator.validate_chapter(ch)
        assert isinstance(errors, list)

    def test_valid_outline_no_errors(self) -> None:
        validator = OutlineValidator()
        ch = ChapterPlan(
            title="Ch1",
            goal="Understand X",
            learning_objectives=["Learn X"],
            sections=[SectionPlan(heading="S1", goal="Detail")],
        )
        outline = BookOutline(title="Valid Book", chapters=[ch])
        bp = BookBlueprint(title="T", topic="T", outline=outline, estimated_chapters=1, estimated_pages=100)
        errors = validator.validate_blueprint(bp)
        severe = [e for e in errors if e.severity == ValidationSeverity.ERROR]
        assert len(severe) == 0
