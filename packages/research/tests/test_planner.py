"""Tests for ResearchPlanner."""

from bookforge.research.enums import SourceType, SupportedInput
from bookforge.research.planner import ResearchPlanner


class TestResearchPlanner:
    def test_create_plan_defaults(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("Kubernetes")
        assert plan.topic == "Kubernetes"
        assert plan.input_type == SupportedInput.TECHNICAL_TOPIC
        assert plan.depth == 3
        assert len(plan.search_queries) > 0

    def test_create_plan_programming_language(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("Rust", input_type=SupportedInput.PROGRAMMING_LANGUAGE)
        assert "Rust" in plan.search_queries[0]

    def test_create_plan_framework(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("React", input_type=SupportedInput.FRAMEWORK)
        assert plan.input_type == SupportedInput.FRAMEWORK

    def test_target_sources_for_technical_topic(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("Machine Learning")
        assert SourceType.DOCUMENTATION in plan.target_sources
        assert SourceType.BOOK in plan.target_sources

    def test_target_sources_for_rfc(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("HTTP/3", input_type=SupportedInput.RFC)
        assert SourceType.RFC in plan.target_sources
        assert SourceType.BOOK not in plan.target_sources

    def test_target_sources_for_api(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("REST", input_type=SupportedInput.API)
        assert SourceType.API in plan.target_sources
        assert SourceType.DOCUMENTATION in plan.target_sources

    def test_depth_affects_query_count(self) -> None:
        planner = ResearchPlanner()
        shallow = planner.create_plan("Kubernetes", depth=1)
        deep = planner.create_plan("Kubernetes", depth=5)
        assert len(shallow.search_queries) < len(deep.search_queries)

    def test_objective_generated(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("Docker")
        assert len(plan.objectives) == 1
        assert "Docker" in plan.objectives[0]

    def test_all_input_types_have_sources(self) -> None:
        planner = ResearchPlanner()
        for it in SupportedInput:
            plan = planner.create_plan("test", input_type=it)
            assert len(plan.target_sources) > 0

    def test_generate_objective_contains_type_label(self) -> None:
        planner = ResearchPlanner()
        plan = planner.create_plan("C++", input_type=SupportedInput.PROGRAMMING_LANGUAGE)
        assert "programming language" in plan.objectives[0].lower()
