from bookforge.core.enums import (
    AssetType,
    Audience,
    BloomLevel,
    BookStatus,
    CodeLanguage,
    DiagramType,
    Difficulty,
    ExportFormat,
    GenerationStage,
    Language,
    ReferenceType,
)


class TestDifficulty:
    def test_values(self) -> None:
        assert Difficulty.BEGINNER.value == "beginner"
        assert Difficulty.INTERMEDIATE.value == "intermediate"
        assert Difficulty.ADVANCED.value == "advanced"
        assert Difficulty.EXPERT.value == "expert"

    def test_all_members(self) -> None:
        assert len(Difficulty) == 4


class TestAudience:
    def test_values(self) -> None:
        assert Audience.DEVELOPERS.value == "developers"
        assert Audience.STUDENTS.value == "students"

    def test_all_members(self) -> None:
        assert len(Audience) == 8


class TestLanguage:
    def test_values(self) -> None:
        assert Language.ENGLISH.value == "en"
        assert Language.SPANISH.value == "es"

    def test_all_members(self) -> None:
        assert len(Language) == 20


class TestBookStatus:
    def test_values(self) -> None:
        assert BookStatus.DRAFT.value == "draft"
        assert BookStatus.PUBLISHED.value == "published"

    def test_all_members(self) -> None:
        assert len(BookStatus) == 9


class TestGenerationStage:
    def test_values(self) -> None:
        assert GenerationStage.CREATED.value == "created"
        assert GenerationStage.FAILED.value == "failed"

    def test_progression(self) -> None:
        stages = list(GenerationStage)
        assert stages.index(GenerationStage.CREATED) < stages.index(GenerationStage.OUTLINING)
        assert stages.index(GenerationStage.OUTLINING) < stages.index(GenerationStage.WRITING)


class TestExportFormat:
    def test_values(self) -> None:
        assert ExportFormat.PDF.value == "pdf"
        assert ExportFormat.EPUB.value == "epub"

    def test_all_members(self) -> None:
        assert len(ExportFormat) == 9


class TestDiagramType:
    def test_values(self) -> None:
        assert DiagramType.FLOWCHART.value == "flowchart"
        assert DiagramType.SEQUENCE.value == "sequence"

    def test_all_members(self) -> None:
        assert len(DiagramType) == 12


class TestReferenceType:
    def test_values(self) -> None:
        assert ReferenceType.BOOK.value == "book"
        assert ReferenceType.ARTICLE.value == "article"

    def test_all_members(self) -> None:
        assert len(ReferenceType) == 14


class TestAssetType:
    def test_values(self) -> None:
        assert AssetType.IMAGE.value == "image"
        assert AssetType.DIAGRAM.value == "diagram"

    def test_all_members(self) -> None:
        assert len(AssetType) == 10


class TestCodeLanguage:
    def test_values(self) -> None:
        assert CodeLanguage.PYTHON.value == "python"
        assert CodeLanguage.RUST.value == "rust"

    def test_all_members(self) -> None:
        assert len(CodeLanguage) == 32


class TestBloomLevel:
    def test_values(self) -> None:
        assert BloomLevel.REMEMBER.value == "remember"
        assert BloomLevel.CREATE.value == "create"

    def test_all_members(self) -> None:
        assert len(BloomLevel) == 6
