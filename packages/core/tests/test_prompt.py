"""Tests for prompt template entity."""

import pytest
from bookforge.core.enums import Difficulty
from bookforge.core.prompt import PromptTemplate
from pydantic import ValidationError


class TestPromptTemplate:
    def test_create_minimal(self) -> None:
        pt = PromptTemplate(
            id="pt1",
            name="Write Chapter",
            template="Write a chapter about {{topic}}",
        )
        assert pt.id == "pt1"
        assert pt.name == "Write Chapter"
        assert pt.template == "Write a chapter about {{topic}}"
        assert pt.is_active is True
        assert pt.difficulty == Difficulty.INTERMEDIATE

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            PromptTemplate(id="pt1", name="", template="content")

    def test_empty_template_raises(self) -> None:
        with pytest.raises(ValidationError):
            PromptTemplate(id="pt1", name="Test", template="")

    def test_with_all_fields(self) -> None:
        pt = PromptTemplate(
            id="pt1",
            name="Full Template",
            description="A comprehensive template",
            template="Hello {{name}}",
            variables=["name"],
            category="greeting",
            tags=["simple"],
            difficulty=Difficulty.BEGINNER,
            model_hint="gpt-4",
            temperature=0.5,
            max_tokens=500,
            system_prompt="You are helpful",
        )
        assert len(pt.variables) == 1
        assert pt.variables[0] == "name"
        assert pt.model_hint == "gpt-4"
        assert pt.temperature == 0.5

    def test_temperature_out_of_range_raises(self) -> None:
        with pytest.raises(ValidationError):
            PromptTemplate(
                id="pt1",
                name="Test",
                template="content",
                temperature=3.0,
            )
