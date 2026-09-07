"""Tests for taxonomy entities."""

import pytest
from pydantic import ValidationError

from bookforge.core.enums import BloomLevel, Difficulty
from bookforge.core.taxonomy import Category, LearningObjective, Tag


class TestCategory:
    def test_create(self) -> None:
        cat = Category(id="cat1", name="Python")
        assert cat.id == "cat1"
        assert cat.name == "Python"
        assert cat.description is None

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            Category(id="cat1", name="")

    def test_with_parent(self) -> None:
        Category(id="cat1", name="Programming")
        child = Category(id="cat2", name="Python", parent_id="cat1")
        assert child.parent_id == "cat1"


class TestTag:
    def test_create(self) -> None:
        tag = Tag(id="tag1", name="async")
        assert tag.id == "tag1"
        assert tag.name == "async"

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            Tag(id="tag1", name="")

    def test_with_category(self) -> None:
        tag = Tag(id="tag1", name="fastapi", category_id="cat1")
        assert tag.category_id == "cat1"


class TestLearningObjective:
    def test_create(self) -> None:
        obj = LearningObjective(
            id="lo1",
            description="Understand async programming",
        )
        assert obj.bloom_level == BloomLevel.APPLY
        assert obj.difficulty == Difficulty.INTERMEDIATE

    def test_empty_description_raises(self) -> None:
        with pytest.raises(ValidationError):
            LearningObjective(id="lo1", description="")

    def test_full(self) -> None:
        obj = LearningObjective(
            id="lo1",
            description="Design a distributed system",
            bloom_level=BloomLevel.CREATE,
            difficulty=Difficulty.EXPERT,
            chapter_number=5,
            section_id="sec1",
        )
        assert obj.bloom_level == BloomLevel.CREATE
        assert obj.difficulty == Difficulty.EXPERT
        assert obj.chapter_number == 5
