from bookforge.writer.chapter_writer import ChapterWriter
from bookforge.writer.models import ContentGenerator, DraftBook, DraftChapter, WritingConfig


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "## Chapter Content\n\nGenerated content for the chapter."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestChapterWriter:
    def setup_method(self) -> None:
        self.writer = ChapterWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=200)

    async def test_write_chapter(self) -> None:
        draft = DraftBook(title="Book", topic="Python")
        chapter = DraftChapter(title="Functions", goal="Explain functions")
        result = await self.writer.write_chapter(chapter, draft, self.generator, self.config)
        assert result.title == "Functions"
        assert len(result.content) > 0
        assert result.word_count > 0

    async def test_write_all_chapters(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[
                DraftChapter(title="Intro"),
                DraftChapter(title="Basics"),
            ],
        )
        result = await self.writer.write_all_chapters(draft, self.generator, self.config)
        assert len(result.chapters) == 2
        assert all(c.word_count > 0 for c in result.chapters)
