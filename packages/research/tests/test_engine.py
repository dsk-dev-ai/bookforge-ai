"""Tests for ResearchEngine."""

from bookforge.research.cache import MemoryCache
from bookforge.research.engine import ResearchEngine
from bookforge.research.enums import SourceType
from bookforge.research.models import ResearchSource


class TestResearchEngine:
    def test_research_returns_result(self) -> None:
        engine = ResearchEngine()
        result = engine.research("Kubernetes networking")
        assert result is not None
        assert "Kubernetes networking" in result.summary

    def test_research_caches_result(self) -> None:
        cache = MemoryCache()
        engine = ResearchEngine(cache=cache)
        engine.research("Docker compose")
        cached = cache.get("research:Docker compose:technical_topic")
        assert cached is not None

    def test_research_with_sources(self) -> None:
        engine = ResearchEngine()
        sources = [
            ResearchSource(id="s1", title="K8s Doc", source_type=SourceType.DOCUMENTATION, content="Kubernetes networking overview content here"),
        ]
        result = engine.research_with_sources("Kubernetes", sources)
        assert result is not None

    def test_research_with_sources_updates_stats(self) -> None:
        engine = ResearchEngine()
        sources = [
            ResearchSource(id="s1", title="A", source_type=SourceType.BLOG, content="Content A"),
            ResearchSource(id="s2", title="B", source_type=SourceType.BOOK, content="Content B"),
        ]
        result = engine.research_with_sources("Topic", sources)
        assert result is not None

    def test_manager_property(self) -> None:
        engine = ResearchEngine()
        assert engine.manager is not None

    def test_planner_property(self) -> None:
        engine = ResearchEngine()
        plan = engine.planner.create_plan("Rust")
        assert plan.topic == "Rust"

    def test_normalizer_property(self) -> None:
        engine = ResearchEngine()
        source = ResearchSource(id="s1", title="Test", source_type=SourceType.API, content="Body")
        doc = engine.normalizer.normalize(source)
        assert doc.title == "Test"

    def test_deduplicator_property(self) -> None:
        engine = ResearchEngine()
        assert engine.deduplicator is not None

    def test_ranker_property(self) -> None:
        engine = ResearchEngine()
        assert engine.ranker is not None

    def test_validator_property(self) -> None:
        engine = ResearchEngine()
        assert engine.validator is not None

    def test_exporter_property(self) -> None:
        engine = ResearchEngine()
        assert engine.exporter is not None

    def test_cache_property(self) -> None:
        engine = ResearchEngine()
        assert engine.cache is not None

    def test_dependency_injection(self) -> None:
        cache = MemoryCache()
        engine = ResearchEngine(cache=cache)
        assert engine.cache is cache
