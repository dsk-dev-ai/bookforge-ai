from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from uuid import uuid4

from bookforge.research.cache import MemoryCache, ResearchCache
from bookforge.research.enums import ResearchStatus, SupportedInput
from bookforge.research.models import (
    ResearchJob,
    ResearchResult,
    ResearchSource,
)
from bookforge.research.pipeline import ResearchPipeline


class JobNotFoundError(KeyError):
    """Raised when a requested job does not exist."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Job not found: {job_id}")


class ResearchManager:
    """Manages the lifecycle of research jobs.

    Creates jobs, submits them to the pipeline, tracks progress,
    and retrieves results. Uses dependency injection for all
    components — no global state.
    """

    def __init__(
        self,
        pipeline: ResearchPipeline | None = None,
        cache: ResearchCache | None = None,
    ) -> None:
        self._pipeline = pipeline or ResearchPipeline()
        self._cache = cache or MemoryCache(default_ttl=3600)
        self._jobs: dict[str, ResearchJob] = {}

    def create_job(
        self,
        topic: str,
        input_type: SupportedInput = SupportedInput.TECHNICAL_TOPIC,
    ) -> ResearchJob:
        job_id = uuid4().hex[:16]
        now = datetime.now()
        job = ResearchJob(
            id=job_id,
            topic=topic,
            input_type=input_type,
            status=ResearchStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._jobs[job_id] = job
        return job

    def start_job(
        self,
        job_id: str,
        start_stage: ResearchStatus | None = None,
    ) -> ResearchJob:
        """Run a job through the research pipeline.

        If *start_stage* is provided, the pipeline begins at that
        stage (skipping earlier stages).  This is useful for resuming
        a previously interrupted job.
        """
        job = self._get_job(job_id)
        job.updated_at = datetime.now()
        if start_stage is not None:
            job = self._pipeline.run_from(job, start_stage)
        else:
            job = self._pipeline.run(job)
        self._jobs[job_id] = job
        if job.status == ResearchStatus.COMPLETED:
            self._cache.set(f"job:{job_id}", job, ttl=3600)
        return job

    def get_job(self, job_id: str) -> ResearchJob | None:
        """Retrieve a job by its ID, or *None* if it does not exist."""
        return self._jobs.get(job_id)

    def get_result(self, job_id: str) -> ResearchResult | None:
        """Return the result of a completed job, or *None*."""
        job = self.get_job(job_id)
        if job is None:
            return None
        return job.result

    def list_jobs(self) -> list[ResearchJob]:
        """Return every known job."""
        return list(self._jobs.values())

    def cancel_job(self, job_id: str) -> ResearchJob | None:
        """Mark a job as failed (cancelled).  Returns *None* if unknown."""
        job = self._jobs.get(job_id)
        if job is None:
            return None
        job.status = ResearchStatus.FAILED
        job.updated_at = datetime.now()
        return job

    def add_source(self, job_id: str, source: ResearchSource) -> ResearchJob | None:
        """Append a single source to a job.  Returns *None* if unknown."""
        job = self._jobs.get(job_id)
        if job is None:
            return None
        job.sources.append(source)
        job.statistics.sources_collected = len(job.sources)
        job.updated_at = datetime.now()
        return job

    def add_sources(self, job_id: str, sources: Sequence[ResearchSource]) -> ResearchJob | None:
        """Append multiple sources to a job.  Returns *None* if unknown."""
        job = self._jobs.get(job_id)
        if job is None:
            return None
        job.sources.extend(sources)
        job.statistics.sources_collected = len(job.sources)
        job.updated_at = datetime.now()
        return job

    def job_status(self, job_id: str) -> ResearchStatus | None:
        """Return the current status of a job, or *None* if unknown."""
        job = self.get_job(job_id)
        if job is None:
            return None
        return job.status

    def _get_job(self, job_id: str) -> ResearchJob:
        """Fetch a job (from cache first, then in-memory store).

        Raises *JobNotFoundError* if the job does not exist.
        """
        cached = self._cache.get(f"job:{job_id}")
        if cached is not None:
            return cached
        job = self._jobs.get(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job
