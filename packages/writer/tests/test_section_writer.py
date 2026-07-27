from bookforge.writer.models import BookDraft, ChapterDraft, ContentGenerator, SectionDraft, WritingConfig
from bookforge.writer.section_writer import SectionWriter


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Generated section content with enough words for testing purposes here."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestSectionWriter:
    def setup_method(self) -> None:
        self.writer = SectionWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=100)

    async def test_write_section(self) -> None:
        draft = BookDraft(title="Book", topic="Python")
        section = SectionDraft(heading="Parameters")
        result = await self.writer.write_section(
            section, "Functions", draft, self.generator, self.config,
        )
        assert result.heading == "Parameters"
        assert len(result.content) > 0

    async def test_write_all_sections(self) -> None:
        draft = BookDraft(
            title="Book", topic="Python",
            chapters=[
                ChapterDraft(
                    title="Functions",
                    sections=[
                        SectionDraft(heading="Parameters"),
                        SectionDraft(heading="Return Values"),
                    ],
                ),
            ],
        )
        result = await self.writer.write_all_sections(draft, self.generator, self.config)
        assert len(result.chapters[0].sections) == 2
