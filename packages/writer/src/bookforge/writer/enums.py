from __future__ import annotations

import enum


class WritingStatus(enum.StrEnum):
    PENDING = "pending"
    GENERATING = "generating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class WritingStage(enum.StrEnum):
    CHAPTER_WRITING = "chapter_writing"
    SECTION_WRITING = "section_writing"
    GLOSSARY_WRITING = "glossary_writing"
    REFERENCE_WRITING = "reference_writing"
    ASSEMBLING = "assembling"
    VALIDATING = "validating"
    EXPORTING = "exporting"


class DraftQuality(enum.StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    POLISHED = "polished"
    FINAL = "final"


class ValidationSeverity(enum.StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
