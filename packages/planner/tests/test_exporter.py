import json
from typing import Any

from bookforge.planner.exporter import OutlineExporter
from bookforge.planner.models import (
    BookBlueprint,
    BookOutline,
    ChapterPlan,
    DependencyEdge,
    DependencyGraph,
    LearningPath,
    LearningStep,
    SectionPlan,
    TopicCluster,
)


class TestOutlineExporter:
    def _make_blueprint(self) -> BookBlueprint:
        chapters = [
            ChapterPlan(
                title="Ch1",
                goal="Intro",
                estimated_pages=10.0,
                estimated_minutes=60,
                sections=[SectionPlan(heading="S1", goal="Detail", estimated_pages=3.0)],
            ),
        ]
        outline = BookOutline(title="Test Book", chapters=chapters)
        return BookBlueprint(
            title="Test Book",
            topic="Testing",
            outline=outline,
            estimated_chapters=1,
            estimated_pages=13.0,
            estimated_reading_minutes=60,
            difficulty=0.5,
            dependency_graph=DependencyGraph(
                edges=[DependencyEdge(from_chapter="Ch1", to_chapter="Ch2", reason="builds upon")],
                chapter_titles=["Ch1", "Ch2"],
            ),
            learning_path=LearningPath(
                title="Path",
                steps=[LearningStep(chapter_title="Ch1", order=1, estimated_minutes=60)],
                total_estimated_minutes=60,
            ),
            topic_clusters=[TopicCluster(name="Core", topics=["Ch1"], relevance_score=1.0)],
        )

    def test_to_dict(self) -> None:
        exporter = OutlineExporter()
        bp = self._make_blueprint()
        data = exporter.to_dict(bp)
        assert data["title"] == "Test Book"
        assert data["estimated_chapters"] == 1
        assert "outline" in data
        assert "dependency_graph" in data
        assert "learning_path" in data
        assert "topic_clusters" in data

    def test_to_dict_without_optional(self) -> None:
        exporter = OutlineExporter()
        bp = BookBlueprint(title="Minimal", topic="Test")
        data = exporter.to_dict(bp)
        assert data["title"] == "Minimal"
        assert "outline" not in data

    def test_to_json(self) -> None:
        exporter = OutlineExporter()
        bp = self._make_blueprint()
        result = exporter.to_json(bp)
        parsed: dict[str, Any] = json.loads(result)
        assert parsed["title"] == "Test Book"

    def test_to_yaml(self) -> None:
        exporter = OutlineExporter()
        bp = self._make_blueprint()
        result = exporter.to_yaml(bp)
        assert "Test Book" in result
        assert "Ch1" in result

    def test_round_trip_json(self) -> None:
        exporter = OutlineExporter()
        bp = self._make_blueprint()
        json_str = exporter.to_json(bp)
        parsed = json.loads(json_str)
        assert parsed["estimated_chapters"] == 1
        assert parsed["estimated_pages"] == 13.0
