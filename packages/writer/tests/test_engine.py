import pytest

from bookforge.writer.engine import WriterEngine
from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    DraftChapter,
    DraftSection,
    WritingContext,
)


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Generated content for testing."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestWriterEngine:
    def setup_method(self) -> None:
        self.engine = WriterEngine()
        self.generator = FakeGenerator()

    async def test_write(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[DraftChapter(title="Intro")],
        )
        result = await self.engine.write(draft, self.generator)
        assert result.success

    async def test_write_with_context(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[DraftChapter(title="Intro")],
        )
        ctx = WritingContext(book_title="Book", book_topic="Python", research_summary="Test research")
        result = await self.engine.write(draft, self.generator, context=ctx)
        assert result.success

    async def test_write_from_blueprint(self) -> None:
        class FakeBlueprint:
            title = "Book"
            topic = "Python"
            target_audience = "devs"
            difficulty = 0.5
            subtitle = "Sub"
            estimated_chapters = 1
            outline = None

        result = await self.engine.write_from_blueprint(FakeBlueprint(), self.generator)
        assert result.success

    async def test_write_chapter(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[DraftChapter(title="Intro", goal="Introduce")],
        )
        result = await self.engine.write_chapter(draft, "Intro", self.generator)
        assert result.title == "Intro"
        assert len(result.content) > 0

    async def test_write_chapter_not_found(self) -> None:
        draft = DraftBook(title="Book", topic="Python")
        with pytest.raises(ValueError, match="not found"):
            await self.engine.write_chapter(draft, "Nonexistent", self.generator)

    async def test_write_section(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[
                DraftChapter(
                    title="Intro",
                    sections=[DraftSection(heading="Welcome")],
                ),
            ],
        )
        result = await self.engine.write_section(draft, "Intro", "Welcome", self.generator)
        assert result.heading == "Welcome"

    async def test_write_section_not_found(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[DraftChapter(title="Intro")],
        )
        with pytest.raises(ValueError, match="not found"):
            await self.engine.write_section(draft, "Intro", "Nonexistent", self.generator)

    def test_create_draft(self) -> None:
        draft = self.engine.create_draft(
            title="Guide", topic="Python",
            chapter_titles=["Intro", "Basics"],
            subtitle="A Python Guide",
        )
        assert draft.title == "Guide"
        assert draft.subtitle == "A Python Guide"
        assert draft.chapter_count == 2

    def test_compute_statistics(self) -> None:
        draft = DraftBook(
            title="T", topic="T",
            chapters=[DraftChapter(title="Ch1", content="Hi", word_count=2)],
        )
        stats = self.engine.compute_statistics(draft)
        assert stats.total_chapters == 1
