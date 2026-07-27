from bookforge.writer.models import ContentGenerator, DraftBook, DraftChapter, WritingConfig
from bookforge.writer.pipeline import WriterPipeline


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Generated content for testing purposes here."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestWriterPipeline:
    def setup_method(self) -> None:
        self.pipeline = WriterPipeline()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=100)

    async def test_run_pipeline(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[DraftChapter(title="Intro", goal="Introduce Python")],
        )
        result = await self.pipeline.run(draft, self.generator, self.config)
        assert result.success
        assert result.draft is not None
        assert len(result.markdown) > 0

    async def test_run_pipeline_multiple_chapters(self) -> None:
        draft = DraftBook(
            title="Guide", topic="Python",
            chapters=[
                DraftChapter(title="Basics"),
                DraftChapter(title="Advanced"),
            ],
        )
        result = await self.pipeline.run(draft, self.generator, self.config)
        assert result.success
        assert len(result.draft.chapters) == 2

    async def test_run_pipeline_validates(self) -> None:
        draft = DraftBook(
            title="Book", topic="T",
            chapters=[DraftChapter(title="Ch1")],
        )
        result = await self.pipeline.run(draft, self.generator, self.config)
        assert len(result.validation_messages) > 0

    async def test_run_pipeline_metrics(self) -> None:
        draft = DraftBook(
            title="Book", topic="Python",
            chapters=[DraftChapter(title="Ch1", goal="Test")],
        )
        result = await self.pipeline.run(draft, self.generator, self.config)
        assert result.metrics is not None
