"""Tests for ResearchPipeline."""

from datetime import datetime

from bookforge.research.enums import ResearchStatus
from bookforge.research.models import ResearchJob
from bookforge.research.pipeline import ResearchPipeline


class TestResearchPipeline:
    def test_pipeline_has_stages(self) -> None:
        pipeline = ResearchPipeline()
        stages = pipeline.stages
        assert len(stages) == 6
        expected = [
            ResearchStatus.PLANNING,
            ResearchStatus.NORMALIZING,
            ResearchStatus.DEDUPLICATING,
            ResearchStatus.RANKING,
            ResearchStatus.VALIDATING,
            ResearchStatus.EXPORTING,
        ]
        for (status, _), expected_status in zip(stages, expected):
            assert status == expected_status

    def test_run_empty_job(self) -> None:
        pipeline = ResearchPipeline()
        job = ResearchJob(id="j1", topic="Kubernetes", created_at=datetime.now(), updated_at=datetime.now())
        result = pipeline.run(job)
        assert result.status == ResearchStatus.COMPLETED
        assert result.plan is not None
        assert result.plan.topic == "Kubernetes"

    def test_run_job_with_sources(self) -> None:
        from bookforge.research.enums import SourceType
        from bookforge.research.models import ResearchSource

        pipeline = ResearchPipeline()
        job = ResearchJob(
            id="j2", topic="Docker",
            created_at=datetime.now(), updated_at=datetime.now(),
            sources=[
                ResearchSource(
                    id="s1", title="Docker Docs", source_type=SourceType.DOCUMENTATION, content="Content",
                ),
            ],
        )
        result = pipeline.run(job)
        assert result.status == ResearchStatus.COMPLETED
        assert result.statistics.documents_normalized == 1

    def test_run_from_mid_pipeline(self) -> None:
        pipeline = ResearchPipeline()
        job = ResearchJob(id="j3", topic="Rust", created_at=datetime.now(), updated_at=datetime.now())
        result = pipeline.run_from(job, ResearchStatus.VALIDATING)
        assert result.status == ResearchStatus.COMPLETED

    def test_run_with_duplicate_sources(self) -> None:
        from bookforge.research.enums import SourceType
        from bookforge.research.models import ResearchSource

        pipeline = ResearchPipeline()
        sources = [
            ResearchSource(id="s1", title="Same", source_type=SourceType.BLOG, content="Duplicate content here"),
            ResearchSource(id="s2", title="Same", source_type=SourceType.BLOG, content="Duplicate content here"),
        ]
        job = ResearchJob(
            id="j4", topic="Python",
            created_at=datetime.now(), updated_at=datetime.now(),
            sources=sources,
        )
        result = pipeline.run(job)
        assert result.statistics.duplicates_removed >= 1

    def test_result_has_summary(self) -> None:
        pipeline = ResearchPipeline()
        job = ResearchJob(id="j5", topic="AI Agents", created_at=datetime.now(), updated_at=datetime.now())
        result = pipeline.run(job)
        assert result.result is not None
        assert "AI Agents" in result.result.summary
