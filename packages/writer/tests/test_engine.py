import pytest

from bookforge.writer.engine import WriterEngine
from bookforge.writer.models import BookDraft, ChapterDraft, ContentGenerator, SectionDraft


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
        draft = BookDraft(
            title="Book", topic="Python",
            chapters=[ChapterDraft(title="Intro")],
        )
        result = await self.engine.write(draft, self.generator)
        assert result.success

    async def test_write_chapter(self) -> None:
        draft = BookDraft(
            title="Book", topic="Python",
            chapters=[ChapterDraft(title="Intro", goal="Introduce")],
        )
        result = await self.engine.write_chapter(draft, "Intro", self.generator)
        assert result.title == "Intro"
        assert len(result.content) > 0

    async def test_write_chapter_not_found(self) -> None:
        draft = BookDraft(title="Book", topic="Python")
        with pytest.raises(ValueError, match="not found"):
            await self.engine.write_chapter(draft, "Nonexistent", self.generator)

    async def test_write_section(self) -> None:
        draft = BookDraft(
            title="Book", topic="Python",
            chapters=[
                ChapterDraft(
                    title="Intro",
                    sections=[SectionDraft(heading="Welcome")],
                ),
            ],
        )
        result = await self.engine.write_section(draft, "Intro", "Welcome", self.generator)
        assert result.heading == "Welcome"

    async def test_write_section_not_found(self) -> None:
        draft = BookDraft(
            title="Book", topic="Python",
            chapters=[ChapterDraft(title="Intro")],
        )
        with pytest.raises(ValueError, match="not found"):
            await self.engine.write_section(draft, "Intro", "Nonexistent", self.generator)

    def test_create_draft(self) -> None:
        draft = self.engine.create_draft(
            title="Guide",
            topic="Python",
            chapter_titles=["Intro", "Basics"],
            subtitle="A Python Guide",
        )
        assert draft.title == "Guide"
        assert draft.subtitle == "A Python Guide"
        assert draft.chapter_count == 2
        assert draft.chapters[0].title == "Intro"
