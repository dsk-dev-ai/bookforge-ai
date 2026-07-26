"""Tests for ResearchExporter."""

from bookforge.research.enums import SourceType
from bookforge.research.exporter import ResearchExporter
from bookforge.research.models import (
    ArchitectureNote,
    CodeReference,
    KeyConcept,
    Reference,
    ResearchDocument,
    ResearchResult,
    ResearchSource,
    SuggestedChapter,
    Terminology,
)


class TestResearchExporter:
    def test_export_result_to_dict(self) -> None:
        exporter = ResearchExporter()
        result = ResearchResult(summary="Test summary")
        d = exporter.export_result_to_dict(result)
        assert d["summary"] == "Test summary"

    def test_export_result_to_json(self) -> None:
        exporter = ResearchExporter()
        result = ResearchResult(summary="JSON test")
        j = exporter.export_result_to_json(result)
        assert '"summary": "JSON test"' in j

    def test_export_sources_to_dict(self) -> None:
        exporter = ResearchExporter()
        sources = [
            ResearchSource(id="s1", title="Src", source_type=SourceType.BOOK, content="Body"),
        ]
        d = exporter.export_sources_to_dict(sources)
        assert len(d) == 1
        assert d[0]["id"] == "s1"

    def test_export_documents_to_dict(self) -> None:
        exporter = ResearchExporter()
        docs = [ResearchDocument(id="d1", source_id="s1", title="Doc", content="Body")]
        d = exporter.export_documents_to_dict(docs)
        assert len(d) == 1
        assert d[0]["id"] == "d1"

    def test_export_summary(self) -> None:
        exporter = ResearchExporter()
        result = ResearchResult(
            summary="S",
            key_concepts=[KeyConcept(name="X", definition="Y")],
            terminology=[Terminology(term="T", definition="D")],
            important_apis=["API1"],
            code_references=[CodeReference(language="py", code="x", description="d")],
            architecture_notes=[ArchitectureNote(title="A", content="B")],
            references=[Reference(title="R", source_type=SourceType.BOOK)],
            learning_objectives=["LO1"],
            suggested_chapters=[SuggestedChapter(title="Ch1", description="D", order=1)],
        )
        s = exporter.export_summary(result)
        assert s["concept_count"] == 1
        assert s["term_count"] == 1
        assert s["api_count"] == 1
        assert s["reference_count"] == 1
        assert s["suggested_chapter_count"] == 1

    def test_build_result_empty(self) -> None:
        exporter = ResearchExporter()
        r = exporter.build_result()
        assert r.is_empty is True

    def test_build_result_with_data(self) -> None:
        exporter = ResearchExporter()
        r = exporter.build_result(
            summary="Test",
            key_concepts=[KeyConcept(name="X", definition="Y")],
        )
        assert r.summary == "Test"
        assert len(r.key_concepts) == 1

    def test_merge_results(self) -> None:
        exporter = ResearchExporter()
        r1 = ResearchResult(summary="Part 1", key_concepts=[KeyConcept(name="A", definition="A is B")])
        r2 = ResearchResult(summary="Part 2", key_concepts=[KeyConcept(name="B", definition="B is C")])
        merged = exporter.merge_results([r1, r2])
        assert "Part 1" in merged.summary
        assert "Part 2" in merged.summary
        assert len(merged.key_concepts) == 2

    def test_merge_empty_list(self) -> None:
        exporter = ResearchExporter()
        merged = exporter.merge_results([])
        assert merged.is_empty is True
