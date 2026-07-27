from bookforge.writer.conclusion_writer import ConclusionWriter
from bookforge.writer.models import ContentGenerator, DraftBook, DraftChapter, WritingConfig


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "In conclusion, we covered the main topics."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestConclusionWriter:
    def setup_method(self) -> None:
        self.writer = ConclusionWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=200)

    async def test_write_conclusion(self) -> None:
        draft = DraftBook(title="Book", topic="Python")
        chapter = DraftChapter(title="Intro", content="Chapter body here.")
        result = await self.writer.write_conclusion(chapter, draft, self.generator, self.config)
        assert "conclusion" in result.content.lower()

    async def test_write_conclusion_no_content(self) -> None:
        draft = DraftBook(title="Book", topic="Python")
        chapter = DraftChapter(title="Intro")
        result = await self.writer.write_conclusion(chapter, draft, self.generator, self.config)
        assert result.content
