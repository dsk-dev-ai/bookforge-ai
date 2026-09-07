from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from bookforge.core.enums import Difficulty
from bookforge.core.value_objects import Version


class PromptTemplate(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=2000)
    template: str = Field(min_length=1, max_length=100000)
    variables: list[str] = Field(default_factory=list)
    version: Version = Version(major=0, minor=1, patch=0)
    category: str = Field(default="general", min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    model_hint: str | None = Field(default=None, max_length=200)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=1000000)
    system_prompt: str | None = Field(default=None, max_length=10000)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def _name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("prompt template name must not be empty")
        return stripped

    @field_validator("template")
    @classmethod
    def _template_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("prompt template must not be empty")
        return stripped

    @field_validator("id")
    @classmethod
    def _id_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("prompt template id must not be empty")
        return stripped
