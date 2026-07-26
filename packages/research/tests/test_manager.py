"""Tests for ResearchManager."""

from bookforge.research.cache import MemoryCache
from bookforge.research.enums import ResearchStatus, SourceType
from bookforge.research.manager import ResearchManager
from bookforge.research.models import ResearchSource
from bookforge.research.pipeline import ResearchPipeline


class TestResearchManager:
    def test_create_job(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("Kubernetes")
        assert job.topic == "Kubernetes"
        assert job.status == ResearchStatus.PENDING
        assert job.id is not None

    def test_start_job(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("Docker")
        result = manager.start_job(job.id)
        assert result.status == ResearchStatus.COMPLETED

    def test_get_job(self) -> None:
        manager = ResearchManager()
        created = manager.create_job("Rust")
        fetched = manager.get_job(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_job_not_found(self) -> None:
        manager = ResearchManager()
        assert manager.get_job("nonexistent") is None

    def test_get_result(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("Python async")
        manager.start_job(job.id)
        result = manager.get_result(job.id)
        assert result is not None

    def test_get_result_not_found(self) -> None:
        manager = ResearchManager()
        assert manager.get_result("nonexistent") is None

    def test_list_jobs(self) -> None:
        manager = ResearchManager()
        manager.create_job("Job A")
        manager.create_job("Job B")
        assert len(manager.list_jobs()) == 2

    def test_cancel_job(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("To cancel")
        cancelled = manager.cancel_job(job.id)
        assert cancelled is not None
        assert cancelled.status == ResearchStatus.FAILED

    def test_cancel_nonexistent_job(self) -> None:
        manager = ResearchManager()
        assert manager.cancel_job("nonexistent") is None

    def test_add_source(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("Topic")
        source = ResearchSource(id="s1", title="Src", source_type=SourceType.GITHUB, content="C")
        updated = manager.add_source(job.id, source)
        assert updated is not None
        assert len(updated.sources) == 1

    def test_add_sources(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("Topic")
        sources = [
            ResearchSource(id="s1", title="A", source_type=SourceType.BLOG, content="C1"),
            ResearchSource(id="s2", title="B", source_type=SourceType.BOOK, content="C2"),
        ]
        manager.add_sources(job.id, sources)
        assert len(manager.get_job(job.id).sources) == 2

    def test_add_source_to_nonexistent_job(self) -> None:
        manager = ResearchManager()
        source = ResearchSource(id="s1", title="Src", source_type=SourceType.API, content="C")
        assert manager.add_source("nonexistent", source) is None

    def test_job_status(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("Status Test")
        assert manager.job_status(job.id) == ResearchStatus.PENDING
        manager.start_job(job.id)
        assert manager.job_status(job.id) == ResearchStatus.COMPLETED

    def test_job_status_not_found(self) -> None:
        manager = ResearchManager()
        assert manager.job_status("nonexistent") is None

    def test_start_job_caches_result(self) -> None:
        cache = MemoryCache()
        manager = ResearchManager(cache=cache)
        job = manager.create_job("Cached job")
        manager.start_job(job.id)
        cached = cache.get(f"job:{job.id}")
        assert cached is not None

    def test_start_job_raises_for_nonexistent(self) -> None:
        import pytest

        from bookforge.research.manager import JobNotFoundError
        manager = ResearchManager()
        with pytest.raises(JobNotFoundError, match="not found"):
            manager.start_job("nonexistent")

    def test_start_job_with_start_stage(self) -> None:
        manager = ResearchManager()
        job = manager.create_job("Skip ahead")
        result = manager.start_job(job.id, start_stage=ResearchStatus.VALIDATING)
        assert result.status == ResearchStatus.COMPLETED

    def test_pipeline_injection(self) -> None:
        pipeline = ResearchPipeline()
        manager = ResearchManager(pipeline=pipeline)
        assert manager._pipeline is pipeline
