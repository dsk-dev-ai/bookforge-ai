from __future__ import annotations

from pydantic import BaseModel, Field

from bookforge.writer.assembler import MarkdownAssembler
from bookforge.writer.chapter_writer import ChapterWriter
from bookforge.writer.enums import WritingStatus
from bookforge.writer.exporter import WritingExporter
from bookforge.writer.glossary_writer import GlossaryWriter
from bookforge.writer.models import BookDraft, ContentGenerator, ValidationMessage, WritingConfig
from bookforge.writer.reference_writer import ReferenceWriter
from bookforge.writer.section_writer import SectionWriter
from bookforge.writer.validator import ContentValidator


class WriterPipelineResult(BaseModel):
    draft: BookDraft = Field(description="Final book draft")
    markdown: str = Field(default="", description="Assembled markdown")
    validation_messages: list[ValidationMessage] = Field(default_factory=list, description="Validation results")
    success: bool = Field(default=True, description="Whether pipeline completed successfully")


class WriterPipeline:
    def __init__(
        self,
        chapter_writer: ChapterWriter | None = None,
        section_writer: SectionWriter | None = None,
        glossary_writer: GlossaryWriter | None = None,
        reference_writer: ReferenceWriter | None = None,
        assembler: MarkdownAssembler | None = None,
        validator: ContentValidator | None = None,
        exporter: WritingExporter | None = None,
    ) -> None:
        self._chapter_writer = chapter_writer or ChapterWriter()
        self._section_writer = section_writer or SectionWriter()
        self._glossary_writer = glossary_writer or GlossaryWriter()
        self._reference_writer = reference_writer or ReferenceWriter()
        self._assembler = assembler or MarkdownAssembler()
        self._validator = validator or ContentValidator()
        self._exporter = exporter or WritingExporter()

    async def run(
        self,
        draft: BookDraft,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> WriterPipelineResult:
        cfg = config or WritingConfig.default()

        draft = draft.model_copy(update={"status": WritingStatus.GENERATING})

        draft = await self._chapter_writer.write_all_chapters(draft, generator, cfg)

        draft = await self._section_writer.write_all_sections(draft, generator, cfg)

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
