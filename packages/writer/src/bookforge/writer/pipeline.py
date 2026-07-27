from __future__ import annotations

from pydantic import BaseModel, Field

from bookforge.writer.assembler import MarkdownAssembler
from bookforge.writer.chapter_writer import ChapterWriter
from bookforge.writer.code_example_writer import CodeExampleWriter
from bookforge.writer.conclusion_writer import ConclusionWriter
from bookforge.writer.enums import WritingStatus
from bookforge.writer.exporter import WritingExporter
from bookforge.writer.glossary_writer import GlossaryWriter
from bookforge.writer.introduction_writer import IntroductionWriter
from bookforge.writer.models import (
    ContentGenerator,
    DraftBook,
    ValidationMessage,
    WritingConfig,
    WritingContext,
    WritingMetrics,
)
from bookforge.writer.reference_writer import ReferenceWriter
from bookforge.writer.section_writer import SectionWriter
from bookforge.writer.table_writer import TableWriter
from bookforge.writer.validator import ContentValidator


class WriterPipelineResult(BaseModel):
    draft: DraftBook = Field(description="Final book draft")
    markdown: str = Field(default="", description="Assembled markdown")
    validation_messages: list[ValidationMessage] = Field(default_factory=list, description="Validation results")
    success: bool = Field(default=True, description="Whether pipeline completed successfully")
    metrics: WritingMetrics = Field(default_factory=WritingMetrics, description="Writing metrics")


class WriterPipeline:
    def __init__(
        self,
        chapter_writer: ChapterWriter | None = None,
        section_writer: SectionWriter | None = None,
        introduction_writer: IntroductionWriter | None = None,
        conclusion_writer: ConclusionWriter | None = None,
        glossary_writer: GlossaryWriter | None = None,
        reference_writer: ReferenceWriter | None = None,
        code_example_writer: CodeExampleWriter | None = None,
        table_writer: TableWriter | None = None,
        assembler: MarkdownAssembler | None = None,
        validator: ContentValidator | None = None,
        exporter: WritingExporter | None = None,
    ) -> None:
        self._chapter_writer = chapter_writer or ChapterWriter()
        self._section_writer = section_writer or SectionWriter()
        self._introduction_writer = introduction_writer or IntroductionWriter()
        self._conclusion_writer = conclusion_writer or ConclusionWriter()
        self._glossary_writer = glossary_writer or GlossaryWriter()
        self._reference_writer = reference_writer or ReferenceWriter()
        self._code_example_writer = code_example_writer or CodeExampleWriter()
        self._table_writer = table_writer or TableWriter()
        self._assembler = assembler or MarkdownAssembler()
        self._validator = validator or ContentValidator()
        self._exporter = exporter or WritingExporter()

    async def run(
        self,
        draft: DraftBook,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
        context: WritingContext | None = None,
    ) -> WriterPipelineResult:
        cfg = config or WritingConfig.default()
        draft = draft.model_copy(update={"status": WritingStatus.GENERATING})

        if context:
            draft = draft.model_copy(update={"research_summary": context.research_summary})

        draft = await self._chapter_writer.write_all_chapters(draft, generator, cfg)

        for i, ch in enumerate(draft.chapters):
            intro_ch = await self._introduction_writer.write_introduction(ch, draft, generator, cfg)
            draft.chapters[i] = intro_ch

        draft = await self._section_writer.write_all_sections(draft, generator, cfg)

        for i, ch in enumerate(draft.chapters):
            concl_ch = await self._conclusion_writer.write_conclusion(ch, draft, generator, cfg)
            draft.chapters[i] = concl_ch

        draft = await self._glossary_writer.write_glossary(draft, generator, config=cfg)

        draft = await self._reference_writer.write_references(draft, generator, config=cfg)

        draft = draft.model_copy(update={"status": WritingStatus.VALIDATING})
        validation_messages = self._validator.validate(draft)

        has_errors = any(
            getattr(m, "severity", "warning") == "error" for m in validation_messages
        )
        status = WritingStatus.FAILED if has_errors else WritingStatus.COMPLETED

        markdown = self._assembler.assemble(draft)
        total_wc = len(markdown.split())
        draft = draft.model_copy(update={"status": status, "word_count": total_wc})

        return WriterPipelineResult(
            draft=draft,
            markdown=markdown,
            validation_messages=validation_messages,
            success=not has_errors,
        )
