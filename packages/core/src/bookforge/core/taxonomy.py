from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from bookforge.core.enums import BloomLevel, Difficulty


class Category(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    parent_id: str | None = Field(default=None, max_length=200)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def _name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("category name must not be empty")
        return stripped


class Tag(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=100)
    category_id: str | None = Field(default=None, max_length=200)

    @field_validator("name")
    @classmethod
    def _name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("tag name must not be empty")
        return stripped


class LearningObjective(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    bloom_level: BloomLevel = BloomLevel.APPLY
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    chapter_number: int | None = Field(default=None, ge=1)
    section_id: str | None = Field(default=None, max_length=200)

    @field_validator("description")
    @classmethod
    def _description_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("learning objective description must not be empty")
        return stripped
