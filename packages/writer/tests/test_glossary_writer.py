from bookforge.writer.glossary_writer import GlossaryWriter
from bookforge.writer.models import BookDraft, ChapterDraft, ContentGenerator, WritingConfig


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "**API**: Application Programming Interface\n\n*Context: Web Development*"

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestGlossaryWriter:
    def setup_method(self) -> None:
        self.writer = GlossaryWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=100)

    async def test_write_glossary_with_terms(self) -> None:
        draft = BookDraft(title="Guide", topic="Web Dev")
        result = await self.writer.write_glossary(
            draft, self.generator,
            terms=[{"term": "API", "context": "Web"}],
            config=self.config,
        )
        assert result.glossary is not None
        assert len(result.glossary.entries) == 1

    async def test_write_glossary_no_terms_returns_unchanged(self) -> None:
        draft = BookDraft(title="Guide", topic="Web Dev", chapters=[])
        result = await self.writer.write_glossary(draft, self.generator, terms=[], config=self.config)
        assert result.glossary is None

    def test_extract_terms(self) -> None:
        draft = BookDraft(
            title="Guide", topic="Python",
            chapters=[
                ChapterDraft(title="Django Basics"),
                ChapterDraft(title="REST APIs"),
            ],
        )
        terms = self.writer._extract_terms(draft)
        assert "Django" in terms
        assert "REST" in terms
        assert "APIs" in terms
