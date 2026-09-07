"""Tests for publishing domain entities."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from bookforge.core.enums import BookStatus, ExportFormat
from bookforge.core.publishing import ExportInfo, PublishingInfo, ReviewInfo
from bookforge.core.value_objects import ISBN, Version


class TestPublishingInfo:
    def test_create_minimal(self) -> None:
        info = PublishingInfo()
        assert info.edition == 1
        assert info.format == ExportFormat.PDF
        assert info.language == "en"
        assert info.rights == "All rights reserved"

    def test_with_isbn(self) -> None:
        isbn = ISBN(value="978-0-306-40615-7")
        info = PublishingInfo(
            isbn=isbn,
            publisher="O'Reilly",
            edition=2,
            format=ExportFormat.EPUB,
            list_price_usd=39.99,
        )
        assert info.isbn is not None
        assert info.publisher == "O'Reilly"
        assert info.list_price_usd == 39.99

    def test_negative_price_raises(self) -> None:
        with pytest.raises(ValidationError):
            PublishingInfo(list_price_usd=-1.0)

    def test_edition_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            PublishingInfo(edition=0)

    def test_full(self) -> None:
        info = PublishingInfo(
            publisher="Packt",
            copyright_year=2024,
            edition=1,
            format=ExportFormat.PDF,
            page_count=350,
            list_price_usd=49.99,
        )
        assert info.copyright_year == 2024
        assert info.page_count == 350


class TestReviewInfo:
    def test_create_minimal(self) -> None:
        review = ReviewInfo()
        assert review.status == BookStatus.DRAFT
        assert review.rating is None

    def test_with_rating(self) -> None:
        review = ReviewInfo(
            reviewer_name="Alice",
            status=BookStatus.REVIEWING,
            rating=4,
            comments="Good work",
            revision_notes=["Fix typo on page 10"],
        )
        assert review.reviewer_name == "Alice"
        assert review.rating == 4
        assert len(review.revision_notes) == 1

    def test_invalid_rating_low_raises(self) -> None:
        with pytest.raises(ValidationError):
            ReviewInfo(rating=0)

    def test_invalid_rating_high_raises(self) -> None:
        with pytest.raises(ValidationError):
            ReviewInfo(rating=6)

    def test_empty_reviewer_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            ReviewInfo(reviewer_name="")

    def test_with_dates(self) -> None:
        now = datetime.now(UTC)
        review = ReviewInfo(
            reviewer_name="Bob",
            status=BookStatus.REVIEWING,
            started_at=now,
            version_reviewed=Version(major=1, minor=0, patch=0),
        )
        assert review.started_at == now
        assert review.version_reviewed is not None
        assert str(review.version_reviewed) == "1.0.0"


class TestExportInfo:
    def test_create_minimal(self) -> None:
        info = ExportInfo(
            id="exp1",
            export_format=ExportFormat.PDF,
            file_path="/output/book.pdf",
        )
        assert info.export_format == ExportFormat.PDF
        assert info.file_path == "/output/book.pdf"
        assert info.status == "pending"

    def test_empty_file_path_raises(self) -> None:
        with pytest.raises(ValidationError):
            ExportInfo(id="exp1", export_format=ExportFormat.PDF, file_path="")

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValidationError):
            ExportInfo(
                id="exp1",
                export_format=ExportFormat.PDF,
                file_path="/out.pdf",
                status="unknown",
            )

    def test_completed_export(self) -> None:
        now = datetime.now(UTC)
        info = ExportInfo(
            id="exp1",
            export_format=ExportFormat.EPUB,
            file_path="/output/book.epub",
            file_size_bytes=1024000,
            status="completed",
            generated_at=now,
            version=Version(major=1, minor=0, patch=0),
        )
        assert info.file_size_bytes == 1024000
        assert info.generated_at == now
        assert info.status == "completed"

    def test_failed_export(self) -> None:
        info = ExportInfo(
            id="exp1",
            export_format=ExportFormat.PDF,
            file_path="/output/book.pdf",
            status="failed",
            error_message="Disk full",
        )
        assert info.error_message == "Disk full"
