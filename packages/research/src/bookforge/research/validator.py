from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from bookforge.research.models import ResearchDocument, ResearchSource


class ValidationError:
    """Represents a single validation error found during research validation."""

    def __init__(self, message: str, field: str = "", item_id: str = "") -> None:
        self.message = message
        self.field = field
        self.item_id = item_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValidationError):
            return NotImplemented
        return self.message == other.message and self.field == other.field and self.item_id == other.item_id

    def __repr__(self) -> str:
        return f"ValidationError(message={self.message!r}, field={self.field!r}, item_id={self.item_id!r})"


class ResearchValidator:
    """Validates research sources, documents, and results.

    Checks for duplicate sources, missing metadata, invalid URLs,
    duplicate references, and empty summaries.
    """

    _URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)

    def validate_sources(self, sources: Sequence[ResearchSource]) -> list[ValidationError]:
        errors: list[ValidationError] = []
        seen_urls: set[str] = set()
        seen_ids: set[str] = set()

        for source in sources:
            if source.id in seen_ids:
                errors.append(ValidationError("Duplicate source ID", "id", source.id))
            seen_ids.add(source.id)

            if not source.title.strip():
                errors.append(ValidationError("Source has empty title", "title", source.id))

            if source.url and not self._URL_PATTERN.match(source.url):
                errors.append(ValidationError("Source has invalid URL", "url", source.id))

            if source.url:
                normalized_url = source.url.rstrip("/").lower()
                if normalized_url in seen_urls:
                    errors.append(ValidationError("Duplicate source URL", "url", source.id))
                seen_urls.add(normalized_url)

            if not source.content.strip():
                errors.append(ValidationError("Source has empty content", "content", source.id))

        return errors

    def validate_documents(self, documents: Sequence[ResearchDocument]) -> list[ValidationError]:
        errors: list[ValidationError] = []
        seen_titles: set[str] = set()

        for doc in documents:
            if not doc.title.strip():
                errors.append(ValidationError("Document has empty title", "title", doc.id))

            if doc.title.lower().strip() in seen_titles:
                errors.append(ValidationError("Duplicate document title", "title", doc.id))
            seen_titles.add(doc.title.lower().strip())

            if not doc.content.strip() and not doc.sections:
                errors.append(ValidationError("Document has no content or sections", "content", doc.id))

            if not doc.source_id.strip():
                errors.append(ValidationError("Document missing source_id", "source_id", doc.id))

        return errors

    def validate_url(self, url: str | None) -> bool:
        if url is None:
            return True
        return bool(self._URL_PATTERN.match(url))

    def has_duplicate_sources(
        self,
        sources: Sequence[ResearchSource],
    ) -> bool:
        errors = self.validate_sources(sources)
        return any("Duplicate" in e.message for e in errors)

    def has_empty_summary(self, summary: str | None) -> bool:
        return summary is None or not summary.strip()

    @staticmethod
    def format_errors(errors: list[ValidationError]) -> list[dict[str, Any]]:
        return [
            {"message": e.message, "field": e.field, "item_id": e.item_id} for e in errors
        ]
