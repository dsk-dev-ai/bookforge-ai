"""Tests for author entity."""

import pytest
from pydantic import ValidationError

from bookforge.core.author import Author
from bookforge.core.enums import Difficulty
from bookforge.core.value_objects import EmailAddress, PersonName


class TestAuthor:
    def test_create_minimal(self) -> None:
        name = PersonName(first="John", last="Doe")
        author = Author(id="auth1", name=name, display_name="John Doe")
        assert author.id == "auth1"
        assert author.display_name == "John Doe"
        assert author.full_name() == "John Doe"
        assert author.is_active is True

    def test_empty_display_name_raises(self) -> None:
        name = PersonName(first="John", last="Doe")
        with pytest.raises(ValidationError):
            Author(id="auth1", name=name, display_name="")

    def test_with_email(self) -> None:
        name = PersonName(first="Jane", last="Smith")
        email = EmailAddress(address="jane@example.com")
        author = Author(
            id="auth2",
            name=name,
            display_name="Jane Smith",
            email=email,
            bio="A prolific author",
            specialties=["Python", "Architecture"],
            expertise_level=Difficulty.EXPERT,
        )
        assert author.email is not None
        assert author.email.address == "jane@example.com"
        assert len(author.specialties) == 2
        assert author.expertise_level == Difficulty.EXPERT

    def test_invalid_email_raises(self) -> None:
        name = PersonName(first="John", last="Doe")
        with pytest.raises(ValidationError):
            Author(
                id="auth1",
                name=name,
                display_name="John Doe",
                email=EmailAddress(address="not-valid"),
            )

    def test_empty_id_raises(self) -> None:
        name = PersonName(first="John", last="Doe")
        with pytest.raises(ValidationError):
            Author(id="", name=name, display_name="John")

    def test_full_name_method(self) -> None:
        name = PersonName(first="Alice", last="Johnson")
        author = Author(id="auth3", name=name, display_name="Alice J.")
        assert author.full_name() == "Alice Johnson"
