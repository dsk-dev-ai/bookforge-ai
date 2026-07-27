from bookforge.writer.code_example_writer import CodeExampleWriter
from bookforge.writer.models import ContentGenerator, DraftBook, WritingConfig


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "```python\nprint('hello')\n```"

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestCodeExampleWriter:
    def setup_method(self) -> None:
        self.writer = CodeExampleWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=100)

    async def test_write_code_example(self) -> None:
        draft = DraftBook(title="Guide", topic="Python")
        result = await self.writer.write_code_example(
            draft, self.generator, "python", "Print function", self.config,
        )
        assert "python" in result.lower()
