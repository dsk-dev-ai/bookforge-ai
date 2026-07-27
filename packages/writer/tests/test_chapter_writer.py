from bookforge.writer.chapter_writer import ChapterWriter
from bookforge.writer.models import BookDraft, ChapterDraft, ContentGenerator, WritingConfig


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return f"## {self._extract_title(prompt)}\n\nGenerated content for the chapter."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"

    def _extract_title(self, prompt: str) -> str:
        for line in prompt.split("\n"):
            if "Chapter title:" in line:
                return line.split("Chapter title:")[-1].strip()
        return "Chapter"


class TestChapterWriter:
    def setup_method(self) -> None:
        self.writer = ChapterWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=200)

    async def test_write_chapter(self) -> None:
        draft = BookDraft(title="Book", topic="Python")
        chapter = ChapterDraft(title="Functions", goal="Explain functions")
        result = await self.writer.write_chapter(chapter, draft, self.generator, self.config)
        assert result.title == "Functions"
        assert len(result.content) > 0
        assert result.word_count > 0

    async def test_write_all_chapters(self) -> None:
        draft = BookDraft(
            title="Book", topic="Python",
            chapters=[
                ChapterDraft(title="Intro"),
                ChapterDraft(title="Basics"),
            ],
        )
        result = await self.writer.write_all_chapters(draft, self.generator, self.config)
        assert len(result.chapters) == 2
        assert all(c.word_count > 0 for c in result.chapters)
