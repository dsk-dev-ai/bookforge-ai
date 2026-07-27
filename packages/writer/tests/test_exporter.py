import json

from bookforge.writer.exporter import WritingExporter
from bookforge.writer.models import DraftBook, DraftChapter


class TestWritingExporter:
    def setup_method(self) -> None:
        self.exporter = WritingExporter()

    def test_to_markdown(self) -> None:
        draft = DraftBook(
            title="Guide", topic="T",
            chapters=[DraftChapter(title="Ch1", content="## Ch1\n\nContent")],
        )
        result = self.exporter.to_markdown(draft)
        assert "# Guide" in result

    def test_to_dict(self) -> None:
        draft = DraftBook(
            title="Guide", topic="Python",
            chapters=[DraftChapter(title="Intro", content="Hello")],
        )
        data = self.exporter.to_dict(draft)
        assert data["title"] == "Guide"
        assert data["chapter_count"] == 1

    def test_to_json(self) -> None:
        draft = DraftBook(title="Guide", topic="T")
        result = self.exporter.to_json(draft)
        parsed = json.loads(result)
        assert parsed["title"] == "Guide"

    def test_to_dict_optional_fields(self) -> None:
        draft = DraftBook(title="Minimal", topic="Test")
        data = self.exporter.to_dict(draft)
        assert data["has_glossary"] is False

    def test_to_file(self, tmp_path) -> None:
        draft = DraftBook(title="Guide", topic="T")
        path = str(tmp_path / "output.md")
        result = self.exporter.to_file(draft, path)
        assert result == path
        with open(path) as f:
            content = f.read()
        assert "# Guide" in content
