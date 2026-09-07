from __future__ import annotations

from typing import Any

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


class ResearchExporter:
    """Exports research results to structured formats.

    Produces dict, JSON, and structured summary representations
    of ResearchResult objects and intermediate pipeline data.
    """

    def export_result_to_dict(self, result: ResearchResult) -> dict[str, Any]:
        return result.model_dump()

    def export_result_to_json(self, result: ResearchResult, indent: int = 2) -> str:
        return result.model_dump_json(indent=indent)

    def export_sources_to_dict(self, sources: list[ResearchSource]) -> list[dict[str, Any]]:
        return [s.model_dump() for s in sources]

    def export_documents_to_dict(self, documents: list[ResearchDocument]) -> list[dict[str, Any]]:
        return [d.model_dump() for d in documents]

    def export_summary(self, result: ResearchResult) -> dict[str, Any]:
        return {
            "summary": result.summary,
            "concept_count": len(result.key_concepts),
            "term_count": len(result.terminology),
            "api_count": len(result.important_apis),
            "code_reference_count": len(result.code_references),
            "architecture_note_count": len(result.architecture_notes),
            "reference_count": len(result.references),
            "learning_objective_count": len(result.learning_objectives),
            "suggested_chapter_count": len(result.suggested_chapters),
        }

    def build_result(
        self,
        summary: str = "",
        key_concepts: list[KeyConcept] | None = None,
        terminology: list[Terminology] | None = None,
        important_apis: list[str] | None = None,
        code_references: list[CodeReference] | None = None,
        architecture_notes: list[ArchitectureNote] | None = None,
        references: list[Reference] | None = None,
        learning_objectives: list[str] | None = None,
        suggested_chapters: list[SuggestedChapter] | None = None,
    ) -> ResearchResult:
        return ResearchResult(
            summary=summary,
            key_concepts=key_concepts or [],
            terminology=terminology or [],
            important_apis=important_apis or [],
            code_references=code_references or [],
            architecture_notes=architecture_notes or [],
            references=references or [],
            learning_objectives=learning_objectives or [],
            suggested_chapters=suggested_chapters or [],
        )

    def merge_results(self, results: list[ResearchResult]) -> ResearchResult:
        merged = ResearchResult()
        for r in results:
            if r.summary:
                merged.summary += ("\n\n" if merged.summary else "") + r.summary
            merged.key_concepts.extend(r.key_concepts)
            merged.terminology.extend(r.terminology)
            merged.important_apis.extend(r.important_apis)
            merged.code_references.extend(r.code_references)
            merged.architecture_notes.extend(r.architecture_notes)
            merged.references.extend(r.references)
            merged.learning_objectives.extend(r.learning_objectives)
            merged.suggested_chapters.extend(r.suggested_chapters)
        return merged
