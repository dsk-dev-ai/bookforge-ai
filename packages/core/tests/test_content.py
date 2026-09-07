"""Tests for content domain entities."""

import pytest
from pydantic import ValidationError

from bookforge.core.content import CodeExample, Diagram, ImageAsset, Paragraph, Table
from bookforge.core.enums import CodeLanguage, DiagramType
from bookforge.core.value_objects import URL, ImageDimension


class TestParagraph:
    def test_create(self) -> None:
        p = Paragraph(text="Hello world")
        assert p.text == "Hello world"
        assert p.is_code_block is False

    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValidationError):
            Paragraph(text="")

    def test_with_all_fields(self) -> None:
        p = Paragraph(
            id="p1",
            text="List item",
            style="bold",
            is_list_item=True,
            list_type="bullet",
            indent_level=1,
        )
        assert p.id == "p1"
        assert p.list_type == "bullet"
        assert p.indent_level == 1

    def test_invalid_list_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            Paragraph(text="test", list_type="invalid")


class TestCodeExample:
    def test_create(self) -> None:
        code = CodeExample(code="print('hello')", language=CodeLanguage.PYTHON)
        assert code.code == "print('hello')"
        assert code.language == CodeLanguage.PYTHON

    def test_empty_code_raises(self) -> None:
        with pytest.raises(ValidationError):
            CodeExample(code="")

    def test_with_explanation(self) -> None:
        code = CodeExample(
            code="x = 1",
            title="Assignment",
            explanation="Assigns 1 to x",
            filename="example.py",
            highlight_lines=[1],
            show_line_numbers=True,
        )
        assert code.title == "Assignment"
        assert code.filename == "example.py"
        assert code.highlight_lines == [1]
        assert code.show_line_numbers is True

    def test_default_language(self) -> None:
        code = CodeExample(code="print('hello')")
        assert code.language == CodeLanguage.PYTHON


class TestDiagram:
    def test_create_flowchart(self) -> None:
        diagram = Diagram(
            id="d1",
            diagram_type=DiagramType.FLOWCHART,
            title="Architecture Flow",
        )
        assert diagram.diagram_type == DiagramType.FLOWCHART
        assert diagram.title == "Architecture Flow"

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValidationError):
            Diagram(id="d1", diagram_type=DiagramType.SEQUENCE, title="")

    def test_with_mermaid_source(self) -> None:
        diagram = Diagram(
            id="d1",
            diagram_type=DiagramType.SEQUENCE,
            title="Sequence",
            source="A->>B: Hello",
            caption="A sequence diagram",
            alt_text="Sequence diagram example",
        )
        assert diagram.source == "A->>B: Hello"
        assert diagram.caption == "A sequence diagram"

    def test_minimal_diagram(self) -> None:
        diagram = Diagram(id="d1", diagram_type=DiagramType.ARCHITECTURE)
        assert diagram.title is None
        assert diagram.description is None


class TestImageAsset:
    def test_create(self) -> None:
        url = URL(url="https://example.com/image.png")
        img = ImageAsset(url=url, alt_text="Example image")
        assert img.url.url == "https://example.com/image.png"
        assert img.alt_text == "Example image"

    def test_empty_alt_text_raises(self) -> None:
        url = URL(url="https://example.com/image.png")
        with pytest.raises(ValidationError):
            ImageAsset(url=url, alt_text="")

    def test_with_dimensions(self) -> None:
        url = URL(url="https://example.com/img.png")
        dim = ImageDimension(width=800, height=600)
        img = ImageAsset(url=url, alt_text="test", dimensions=dim, caption="A photo")
        assert img.dimensions is not None
        assert img.dimensions.width == 800
        assert img.caption == "A photo"


class TestTable:
    def test_create(self) -> None:
        table = Table(
            headers=["Name", "Age"],
            rows=[["Alice", "30"], ["Bob", "25"]],
        )
        assert table.headers == ["Name", "Age"]
        assert len(table.rows) == 2

    def test_empty_headers_raises(self) -> None:
        with pytest.raises(ValidationError):
            Table(headers=[], rows=[["a"]])

    def test_empty_rows_raises(self) -> None:
        with pytest.raises(ValidationError):
            Table(headers=["A"], rows=[])

    def test_row_column_mismatch_raises(self) -> None:
        with pytest.raises(ValidationError, match="Row 0"):
            Table(headers=["A", "B"], rows=[["only one"]])

    def test_with_caption(self) -> None:
        table = Table(
            headers=["X"],
            rows=[["1"]],
            caption="Sample Table",
            sort_order=1,
        )
        assert table.caption == "Sample Table"
        assert table.sort_order == 1
