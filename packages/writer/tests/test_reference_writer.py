from bookforge.writer.models import ContentGenerator, DraftBook, DraftChapter, DraftSection, WritingConfig
from bookforge.writer.reference_writer import ReferenceWriter


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "## print()\n\nPrints to stdout."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestReferenceWriter:
    def setup_method(self) -> None:
        self.writer = ReferenceWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=100)

    async def test_write_references(self) -> None:
        draft = DraftBook(title="Guide", topic="Python")
        result = await self.writer.write_references(
            draft, self.generator,
            references=[{"title": "print()", "description": "Built-in", "category": "functions"}],
            config=self.config,
        )
        assert result.references is not None
        assert len(result.references.entries) == 1

    async def test_write_references_no_refs_returns_unchanged(self) -> None:
        draft = DraftBook(title="Guide", topic="Python", chapters=[])
        result = await self.writer.write_references(draft, self.generator, references=[], config=self.config)
        assert result.references is None

    def test_extract_references(self) -> None:
        draft = DraftBook(
            title="Guide", topic="Python",
            chapters=[
                DraftChapter(
                    title="Intro",
                    sections=[
                        DraftSection(heading="Using Django REST Framework"),
                    ],
                ),
            ],
        )
        refs = self.writer._extract_references(draft)
        assert "Django" in [r["title"] for r in refs]
