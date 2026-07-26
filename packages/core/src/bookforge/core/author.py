from __future__ import annotations

from datetime import datetime

from bookforge.core.enums import Difficulty
from bookforge.core.value_objects import URL, EmailAddress, PersonName
from pydantic import BaseModel, Field, field_validator


class Author(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    name: PersonName
    display_name: str = Field(min_length=1, max_length=200)
    email: EmailAddress | None = None
    bio: str | None = Field(default=None, max_length=5000)
    avatar_url: URL | None = None
    website_url: URL | None = None
    github_handle: str | None = Field(default=None, max_length=100)
    twitter_handle: str | None = Field(default=None, max_length=100)
    linkedin_url: URL | None = None
    specialties: list[str] = Field(default_factory=list)
    expertise_level: Difficulty = Difficulty.INTERMEDIATE
    orcid: str | None = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    @field_validator("display_name")
    @classmethod
    def _display_name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("display_name must not be empty")
        return stripped

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("author id must not be empty")
        return stripped

    def full_name(self) -> str:
        return f"{self.name.first} {self.name.last}"
