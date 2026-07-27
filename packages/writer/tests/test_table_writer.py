from bookforge.writer.models import ContentGenerator, DraftBook, WritingConfig
from bookforge.writer.table_writer import TableWriter


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "| Name | Type |\n|------|------|\n| x | int |"

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestTableWriter:
    def setup_method(self) -> None:
        self.writer = TableWriter()
        self.generator = FakeGenerator()
        self.config = WritingConfig(target_word_count=100)

    async def test_write_table(self) -> None:
        draft = DraftBook(title="Guide", topic="Python")
        result = await self.writer.write_table(
            draft, self.generator, "Name, Type", "Data types", self.config,
        )
        assert "|" in result
