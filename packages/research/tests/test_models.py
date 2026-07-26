"""Tests for research domain models."""


import pytest

from bookforge.research.enums import SourceType, SupportedInput
from bookforge.research.models import (
    ArchitectureNote,
    CodeReference,
    KeyConcept,
    Reference,
    ResearchDocument,
    ResearchJob,
    ResearchPlan,
    ResearchResult,
    ResearchSection,
    ResearchSource,
    ResearchStatistics,
    ResearchTask,
    SuggestedChapter,
    Terminology,
)


class TestKeyConcept:
    def test_default_relevance(self) -> None:
        c = KeyConcept(name="test", definition="a concept")
        assert c.relevance == 0.5

    def test_relevance_clamped(self) -> None:
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            KeyConcept(name="test", definition="a concept", relevance=1.5)


class TestTerminology:
    def test_minimal(self) -> None:
        t = Terminology(term="TCP", definition="Transmission Control Protocol")
        assert t.context is None

    def test_with_context(self) -> None:
        t = Terminology(term="REST", definition="Representational State Transfer", context="APIs")
        assert t.context == "APIs"


class TestCodeReference:
    def test_defaults(self) -> None:
        ref = CodeReference(language="python", code="print('hello')", description="hello world")
        assert ref.source_url is None


class TestArchitectureNote:
    def test_default_relevance(self) -> None:
        n = ArchitectureNote(title="Note", content="Content")
        assert n.relevance == 0.5


class TestReference:
    def test_minimal(self) -> None:
        r = Reference(title="Doc", source_type=SourceType.DOCUMENTATION)
        assert r.authors == []
        assert r.year is None

    def test_with_all_fields(self) -> None:
        r = Reference(
            title="Paper",
            url="https://example.com/paper",
            source_type=SourceType.PAPER,
            authors=["Alice", "Bob"],
            year=2024,
        )
        assert r.url == "https://example.com/paper"
        assert len(r.authors) == 2
        assert r.year == 2024


class TestSuggestedChapter:
    def test_order_ge_one(self) -> None:
        c = SuggestedChapter(title="Intro", description="Start here", order=1)
        assert c.order == 1


class TestResearchResult:
    def test_defaults(self) -> None:
        r = ResearchResult()
        assert r.summary == ""
        assert r.key_concepts == []
        assert r.terminology == []
        assert r.important_apis == []
        assert r.code_references == []
        assert r.architecture_notes == []
        assert r.references == []
        assert r.learning_objectives == []
        assert r.suggested_chapters == []

    def test_is_empty_true(self) -> None:
        r = ResearchResult()
        assert r.is_empty is True

    def test_is_empty_false_with_summary(self) -> None:
        r = ResearchResult(summary="Some research done")
        assert r.is_empty is False

    def test_is_empty_false_with_concepts(self) -> None:
        r = ResearchResult(key_concepts=[KeyConcept(name="X", definition="X is Y")])
        assert r.is_empty is False

    def test_is_empty_false_with_references(self) -> None:
        r = ResearchResult(references=[Reference(title="Ref", source_type=SourceType.BOOK)])
        assert r.is_empty is False


class TestResearchStatistics:
    def test_defaults(self) -> None:
        s = ResearchStatistics()
        assert s.sources_collected == 0
        assert s.documents_normalized == 0
        assert s.duplicates_removed == 0
        assert s.total_ranked == 0
        assert s.validation_errors == 0
        assert s.elapsed_seconds == 0.0


class TestResearchPlan:
    def test_defaults(self) -> None:
        p = ResearchPlan(topic="Kubernetes")
        assert p.input_type == SupportedInput.TECHNICAL_TOPIC
        assert p.depth == 3
        assert p.created_at is not None

    def test_custom_input_type(self) -> None:
        p = ResearchPlan(topic="Rust", input_type=SupportedInput.PROGRAMMING_LANGUAGE)
        assert p.input_type == SupportedInput.PROGRAMMING_LANGUAGE


class TestResearchSource:
    def test_defaults(self) -> None:
        s = ResearchSource(id="src1", title="Source 1", source_type=SourceType.DOCUMENTATION)
        assert s.url is None
        assert s.content == ""
        assert s.score == 0.0
        assert s.collected_at is not None


class TestResearchSection:
    def test_defaults(self) -> None:
        sec = ResearchSection(heading="Intro")
        assert sec.content == ""
        assert sec.subsections == []

    def test_nested_sections(self) -> None:
        sub = ResearchSection(heading="Sub", content="Deep")
        sec = ResearchSection(heading="Main", content="Top", subsections=[sub])
        assert len(sec.subsections) == 1
        assert sec.subsections[0].heading == "Sub"


class TestResearchDocument:
    def test_defaults(self) -> None:
        doc = ResearchDocument(id="doc1", source_id="src1", title="Document")
        assert doc.content == ""
        assert doc.sections == []
        assert doc.normalized_at is not None

    def test_with_sections(self) -> None:
        sec = ResearchSection(heading="Intro", content="Hello")
        doc = ResearchDocument(id="doc1", source_id="src1", title="Doc", sections=[sec])
        assert len(doc.sections) == 1


class TestResearchTask:
    def test_defaults(self) -> None:
        t = ResearchTask(id="t1", job_id="j1", source_type=SourceType.DOCUMENTATION)
        assert t.status.value == "pending"
        assert t.priority == 0
        assert t.completed_at is None


class TestResearchJob:
    def test_defaults(self) -> None:
        j = ResearchJob(id="j1", topic="Kubernetes")
        assert j.status.value == "pending"
        assert j.tasks == []
        assert j.sources == []
        assert j.documents == []
        assert j.result is None
        assert j.statistics is not None

    def test_with_tasks(self) -> None:
        task = ResearchTask(id="t1", job_id="j1", source_type=SourceType.GITHUB)
        j = ResearchJob(id="j1", topic="Kubernetes", tasks=[task])
        assert len(j.tasks) == 1

    def test_with_result(self) -> None:
        result = ResearchResult(summary="Done")
        j = ResearchJob(id="j1", topic="Kubernetes", result=result)
        assert j.result is not None
        assert j.result.summary == "Done"
