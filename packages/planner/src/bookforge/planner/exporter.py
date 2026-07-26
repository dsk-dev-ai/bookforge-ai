from __future__ import annotations

import json
from typing import Any

from bookforge.planner.models import (
    BookBlueprint,
    ChapterPlan,
    SectionPlan,
)


class OutlineExporter:
    def to_dict(self, blueprint: BookBlueprint) -> dict[str, Any]:
        return self._blueprint_to_dict(blueprint)

    def to_json(self, blueprint: BookBlueprint, indent: int = 2) -> str:
        data = self.to_dict(blueprint)
        return json.dumps(data, indent=indent, default=str)

    def to_yaml(self, blueprint: BookBlueprint) -> str:
        import yaml
        data = self.to_dict(blueprint)
        return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)

    def _blueprint_to_dict(self, blueprint: BookBlueprint) -> dict[str, Any]:
        result: dict[str, Any] = {
            "title": blueprint.title,
            "subtitle": blueprint.subtitle,
            "topic": blueprint.topic,
            "summary": blueprint.summary,
            "target_audience": blueprint.target_audience,
            "difficulty": blueprint.difficulty,
            "estimated_pages": blueprint.estimated_pages,
            "estimated_chapters": blueprint.estimated_chapters,
            "estimated_reading_minutes": blueprint.estimated_reading_minutes,
            "created_at": blueprint.created_at.isoformat(),
        }

        if blueprint.outline:
            result["outline"] = self._outline_to_dict(blueprint.outline)

        if blueprint.dependency_graph:
            result["dependency_graph"] = {
                "edges": [
                    {
                        "from": e.from_chapter,
                        "to": e.to_chapter,
                        "reason": e.reason,
                    }
                    for e in blueprint.dependency_graph.edges
                ],
                "has_cycle": blueprint.dependency_graph.has_cycle(),
            }

        if blueprint.prerequisite_graph:
            result["prerequisite_graph"] = {
                "levels": [
                    {"level": i, "chapters": level}
                    for i, level in enumerate(blueprint.prerequisite_graph.levels)
                ],
            }

        if blueprint.learning_path:
            result["learning_path"] = {
                "title": blueprint.learning_path.title,
                "steps": [
                    {
                        "order": s.order,
                        "chapter_title": s.chapter_title,
                        "estimated_minutes": s.estimated_minutes,
                        "prerequisites_met": s.prerequisites_met,
                    }
                    for s in blueprint.learning_path.steps
                ],
                "total_estimated_pages": blueprint.learning_path.total_estimated_pages,
                "total_estimated_minutes": blueprint.learning_path.total_estimated_minutes,
            }

        if blueprint.topic_clusters:
            result["topic_clusters"] = [
                {
                    "name": c.name,
                    "topics": c.topics,
                    "relevance_score": c.relevance_score,
                }
                for c in blueprint.topic_clusters
            ]

        return result

    def _outline_to_dict(self, outline: Any) -> dict[str, Any]:
        return {
            "title": outline.title,
            "subtitle": outline.subtitle,
            "chapter_count": outline.chapter_count,
            "total_pages": outline.total_pages,
            "total_minutes": outline.total_minutes,
            "front_matter": [self._section_to_dict(s) for s in outline.front_matter],
            "chapters": [self._chapter_to_dict(c) for c in outline.chapters],
            "back_matter": [self._section_to_dict(s) for s in outline.back_matter],
        }

    def _chapter_to_dict(self, chapter: ChapterPlan) -> dict[str, Any]:
        return {
            "title": chapter.title,
            "goal": chapter.goal,
            "prerequisites": chapter.prerequisites,
            "learning_objectives": chapter.learning_objectives,
            "estimated_pages": chapter.estimated_pages,
            "estimated_minutes": chapter.estimated_minutes,
            "difficulty": chapter.difficulty,
            "required_diagrams": chapter.required_diagrams,
            "required_code_examples": chapter.required_code_examples,
            "required_tables": chapter.required_tables,
            "sections": [self._section_to_dict(s) for s in chapter.sections],
        }

    def _section_to_dict(self, section: SectionPlan) -> dict[str, Any]:
        return {
            "heading": section.heading,
            "goal": section.goal,
            "estimated_pages": section.estimated_pages,
            "estimated_minutes": section.estimated_minutes,
            "required_diagrams": section.required_diagrams,
            "required_code_examples": section.required_code_examples,
            "required_tables": section.required_tables,
            "subsections": [self._section_to_dict(s) for s in section.subsections],
        }
