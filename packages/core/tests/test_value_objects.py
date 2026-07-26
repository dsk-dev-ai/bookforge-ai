"""Tests for value objects."""


import pytest
from bookforge.core.value_objects import (
    ISBN,
    URL,
    Color,
    EmailAddress,
    ImageDimension,
    PageRange,
    PersonName,
    Version,
)
from pydantic import ValidationError


class TestPersonName:
    def test_create(self) -> None:
        name = PersonName(first="John", last="Doe")
        assert name.first == "John"
        assert name.last == "Doe"

    def test_immutable(self) -> None:
        name = PersonName(first="John", last="Doe")
        with pytest.raises(ValidationError):
            name.first = "Jane"

    def test_empty_first_raises(self) -> None:
        with pytest.raises(ValidationError):
            PersonName(first="", last="Doe")

    def test_empty_last_raises(self) -> None:
        with pytest.raises(ValidationError):
            PersonName(first="John", last="")


class TestEmailAddress:
    def test_valid_email(self) -> None:
        email = EmailAddress(address="user@example.com")
        assert email.address == "user@example.com"

    def test_valid_email_with_plus(self) -> None:
        email = EmailAddress(address="user+tag@example.co.uk")
        assert email.address == "user+tag@example.co.uk"

    def test_invalid_email(self) -> None:
        with pytest.raises(ValidationError):
            EmailAddress(address="not-an-email")

    def test_missing_at_sign(self) -> None:
        with pytest.raises(ValidationError):
            EmailAddress(address="userexample.com")

    def test_missing_domain(self) -> None:
        with pytest.raises(ValidationError):
            EmailAddress(address="user@.com")


class TestURL:
    def test_valid_http(self) -> None:
        url = URL(url="http://example.com")
        assert url.url == "http://example.com"

    def test_valid_https(self) -> None:
        url = URL(url="https://example.com/path?q=1")
        assert url.url == "https://example.com/path?q=1"

    def test_invalid_url(self) -> None:
        with pytest.raises(ValidationError):
            URL(url="not-a-url")

    def test_no_protocol(self) -> None:
        with pytest.raises(ValidationError):
            URL(url="example.com")


class TestISBN:
    def test_valid_isbn10(self) -> None:
        isbn = ISBN(value="0-306-40615-2")
        assert isbn.value == "0-306-40615-2"

    def test_valid_isbn13(self) -> None:
        isbn = ISBN(value="978-0-306-40615-7")
        assert isbn.value == "978-0-306-40615-7"

    def test_isbn10_without_dashes(self) -> None:
        isbn = ISBN(value="0306406152")
        assert isbn.value == "0306406152"

    def test_isbn13_without_dashes(self) -> None:
        isbn = ISBN(value="9780306406157")
        assert isbn.value == "9780306406157"

    def test_invalid_isbn(self) -> None:
        with pytest.raises(ValidationError):
            ISBN(value="1234567890")

    def test_invalid_isbn13(self) -> None:
        with pytest.raises(ValidationError):
            ISBN(value="9780306406158")

    def test_formatted_isbn10(self) -> None:
        isbn = ISBN(value="0306406152")
        assert isbn.formatted() == "0-306-40615-2"

    def test_formatted_isbn13(self) -> None:
        isbn = ISBN(value="9780306406157")
        assert isbn.formatted() == "978-0-306-40615-7"


class TestPageRange:
    def test_valid_range(self) -> None:
        pr = PageRange(start=1, end=100)
        assert pr.start == 1
        assert pr.end == 100

    def test_single_page(self) -> None:
        pr = PageRange(start=42, end=42)
        assert pr.start == 42

    def test_end_less_than_start_raises(self) -> None:
        with pytest.raises(ValidationError):
            PageRange(start=50, end=20)

    def test_zero_start_raises(self) -> None:
        with pytest.raises(ValidationError):
            PageRange(start=0, end=10)

    def test_immutable(self) -> None:
        pr = PageRange(start=1, end=10)
        with pytest.raises(ValidationError):
            pr.start = 5


class TestVersion:
    def test_create(self) -> None:
        v = Version(major=1, minor=2, patch=3)
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_str(self) -> None:
        v = Version(major=2, minor=0, patch=1)
        assert str(v) == "2.0.1"

    def test_defaults(self) -> None:
        v = Version(major=0, minor=1, patch=0)
        assert str(v) == "0.1.0"

    def test_negative_raises(self) -> None:
        with pytest.raises(ValidationError):
            Version(major=-1, minor=0, patch=0)


class TestColor:
    def test_valid_hex(self) -> None:
        c = Color(hex="#FF5733")
        assert c.hex == "#FF5733"

    def test_valid_lowercase(self) -> None:
        c = Color(hex="#aabbcc")
        assert c.hex == "#aabbcc"

    def test_missing_hash_raises(self) -> None:
        with pytest.raises(ValidationError):
            Color(hex="FF5733")

    def test_short_hex_raises(self) -> None:
        with pytest.raises(ValidationError):
            Color(hex="#FFF")

    def test_numeric_only_raises(self) -> None:
        with pytest.raises(ValidationError):
            Color(hex="#GGGGGG")


class TestImageDimension:
    def test_valid(self) -> None:
        dim = ImageDimension(width=1920, height=1080)
        assert dim.width == 1920
        assert dim.height == 1080

    def test_zero_width_raises(self) -> None:
        with pytest.raises(ValidationError):
            ImageDimension(width=0, height=100)

    def test_zero_height_raises(self) -> None:
        with pytest.raises(ValidationError):
            ImageDimension(width=100, height=0)
