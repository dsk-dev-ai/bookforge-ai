from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from bookforge.research.enums import SourceType, SupportedInput
from bookforge.research.models import ResearchPlan


class ResearchPlanner:
    """Generates a structured research plan from a topic.

    Operates without external LLM calls — uses heuristic rules to build
    a plan, identify relevant source types, and generate search queries.
    """

    _INPUT_SOURCE_MAP: ClassVar[dict[SupportedInput, list[SourceType]]] = {
        SupportedInput.TECHNICAL_TOPIC: [
            SourceType.DOCUMENTATION,
            SourceType.BLOG,
            SourceType.BOOK,
            SourceType.PAPER,
        ],
        SupportedInput.PROGRAMMING_LANGUAGE: [
            SourceType.DOCUMENTATION,
            SourceType.SPECIFICATION,
            SourceType.BOOK,
            SourceType.BLOG,
        ],
        SupportedInput.FRAMEWORK: [
            SourceType.DOCUMENTATION,
            SourceType.GITHUB,
            SourceType.BLOG,
            SourceType.API,
        ],
        SupportedInput.TECHNOLOGY: [
            SourceType.DOCUMENTATION,
            SourceType.RFC,
            SourceType.PAPER,
            SourceType.BLOG,
        ],
        SupportedInput.SOFTWARE_LIBRARY: [
            SourceType.DOCUMENTATION,
            SourceType.GITHUB,
            SourceType.API,
            SourceType.BLOG,
        ],
        SupportedInput.API: [
            SourceType.API,
            SourceType.DOCUMENTATION,
            SourceType.SPECIFICATION,
            SourceType.BLOG,
        ],
        SupportedInput.RFC: [
            SourceType.RFC,
            SourceType.DOCUMENTATION,
            SourceType.BLOG,
            SourceType.PAPER,
        ],
        SupportedInput.ARCHITECTURE: [
            SourceType.BOOK,
            SourceType.PAPER,
            SourceType.BLOG,
            SourceType.DOCUMENTATION,
        ],
    }

    _DEPTH_QUERY_MULTIPLIER: ClassVar[dict[int, int]] = {1: 3, 2: 5, 3: 8, 4: 12, 5: 16}

    def create_plan(
        self,
        topic: str,
        input_type: SupportedInput = SupportedInput.TECHNICAL_TOPIC,
        depth: int = 3,
    ) -> ResearchPlan:
        objective = self._generate_objective(topic, input_type)
        queries = self._generate_queries(topic, input_type, depth)
        sources = self._identify_sources(input_type)

        return ResearchPlan(
            topic=topic,
            input_type=input_type,
            objectives=[objective],
            search_queries=queries,
            target_sources=sources,
            depth=depth,
            created_at=datetime.now(),
        )

    def _generate_objective(self, topic: str, input_type: SupportedInput) -> str:
        type_label = input_type.value.replace("_", " ")
        return f"Research and analyze the {type_label}: {topic}"

    def _generate_queries(self, topic: str, input_type: SupportedInput, depth: int) -> list[str]:
        count = self._DEPTH_QUERY_MULTIPLIER.get(depth, 8)
        queries: list[str] = []

        base = {
            SupportedInput.PROGRAMMING_LANGUAGE: f"What is the {topic} programming language",
            SupportedInput.FRAMEWORK: f"How does the {topic} framework work",
            SupportedInput.TECHNOLOGY: f"What is the {topic} technology",
            SupportedInput.SOFTWARE_LIBRARY: f"How to use the {topic} library",
            SupportedInput.API: f"How to use the {topic} API",
            SupportedInput.RFC: f"What does the {topic} RFC specify",
            SupportedInput.ARCHITECTURE: f"What is the {topic} architecture pattern",
            SupportedInput.TECHNICAL_TOPIC: f"What is {topic}",
        }
        queries.append(base.get(input_type, f"What is {topic}"))

        facets = [
            f"core concepts of {topic}",
            f"best practices for {topic}",
            f"{topic} architecture and design",
            f"{topic} use cases and examples",
            f"{topic} common patterns",
            f"{topic} tools and ecosystem",
            f"{topic} getting started guide",
            f"{topic} advanced topics",
            f"{topic} performance considerations",
            f"{topic} security best practices",
            f"comparing {topic} with alternatives",
            f"{topic} production deployment",
            f"{topic} troubleshooting guide",
            f"{topic} community resources",
            f"{topic} future trends",
            f"{topic} case studies",
        ]
        queries.extend(facets[:count])
        return queries

    def _identify_sources(self, input_type: SupportedInput) -> list[SourceType]:
        return self._INPUT_SOURCE_MAP.get(input_type, [SourceType.DOCUMENTATION, SourceType.BLOG])
