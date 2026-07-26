import re
from typing import Any, ClassVar

from pydantic import BaseModel, Field, field_validator


class PersonName(BaseModel, frozen=True):
    first: str = Field(min_length=1, max_length=100)
    last: str = Field(min_length=1, max_length=100)


class EmailAddress(BaseModel, frozen=True):
    address: str = Field(min_length=1, max_length=320)

    _pattern: ClassVar[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @field_validator("address")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        if not cls._pattern.match(v):
            raise ValueError(f"Invalid email address: {v!r}")
        return v


class URL(BaseModel, frozen=True):
    url: str = Field(min_length=1, max_length=2048)

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE
    )

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        if not cls._pattern.match(v):
            raise ValueError(f"Invalid URL: {v!r}")
        return v


class ISBN(BaseModel, frozen=True):
    value: str = Field(min_length=10, max_length=17)

    _isbn10: ClassVar[re.Pattern[str]] = re.compile(r"^\d{9}[\dX]$")
    _isbn13: ClassVar[re.Pattern[str]] = re.compile(r"^\d{13}$")

    @field_validator("value")
    @classmethod
    def _validate_isbn(cls, v: str) -> str:
        cleaned = v.replace("-", "").replace(" ", "")
        if not (cls._isbn10.match(cleaned) or cls._isbn13.match(cleaned)):
            raise ValueError(f"Invalid ISBN: {v!r}")
        if len(cleaned) == 10:
            checksum = sum((i + 1) * (10 if c == "X" else int(c)) for i, c in enumerate(cleaned))
            if checksum % 11 != 0:
                raise ValueError(f"Invalid ISBN-10 checksum: {v!r}")
        if len(cleaned) == 13:
            checksum = sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(cleaned))
            if checksum % 10 != 0:
                raise ValueError(f"Invalid ISBN-13 checksum: {v!r}")
        return v

    def formatted(self) -> str:
        cleaned = self.value.replace("-", "").replace(" ", "")
        if len(cleaned) == 10:
            return f"{cleaned[:1]}-{cleaned[1:4]}-{cleaned[4:9]}-{cleaned[9:]}"
        return f"{cleaned[:3]}-{cleaned[3:4]}-{cleaned[4:7]}-{cleaned[7:12]}-{cleaned[12:]}"


class PageRange(BaseModel, frozen=True):
    start: int = Field(ge=1)
    end: int = Field(ge=1)

    @field_validator("end")
    @classmethod
    def _end_must_be_ge_start(cls, v: int, info: Any) -> int:
        if "start" in info.data and v < info.data["start"]:
            raise ValueError(f"End page ({v}) must be >= start page ({info.data['start']})")
        return v


class Version(BaseModel, frozen=True):
    major: int = Field(ge=0)
    minor: int = Field(ge=0)
    patch: int = Field(ge=0)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class Color(BaseModel, frozen=True):
    hex: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")


class ImageDimension(BaseModel, frozen=True):
    width: int = Field(ge=1, le=100000)
    height: int = Field(ge=1, le=100000)
