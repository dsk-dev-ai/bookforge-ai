from bookforge.writer.introduction_writer import IntroductionWriter
from bookforge.writer.models import ContentGenerator, DraftBook, DraftChapter, WritingConfig


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "This chapter introduces the key concepts."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestIntroductionWriter:
    def setup_method(self) -> None:
        self.writer = IntroductionWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=200)

    async def test_write_introduction(self) -> None:
        draft = DraftBook(title="Book", topic="Python")
        chapter = DraftChapter(title="Intro", goal="Introduce Python")
        result = await self.writer.write_introduction(chapter, draft, self.generator, self.config)
        assert "introduces" in result.content.lower()

    async def test_write_introduction_existing_content(self) -> None:
        draft = DraftBook(title="Book", topic="Python")
        chapter = DraftChapter(title="Intro", goal="Introduce", content="Existing content.")
        result = await self.writer.write_introduction(chapter, draft, self.generator, self.config)
        assert "Existing" in result.content
