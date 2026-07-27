from __future__ import annotations

from datetime import datetime

from bookforge.writer.enums import WritingStatus
from bookforge.writer.models import BookDraft, ChapterDraft, ContentGenerator, WritingConfig, WritingJob
from bookforge.writer.pipeline import WriterPipeline, WriterPipelineResult


class WriterManager:
    def __init__(
        self,
        pipeline: WriterPipeline | None = None,
        config: WritingConfig | None = None,
    ) -> None:
        self._pipeline = pipeline or WriterPipeline()
        self._config = config or WritingConfig.default()
        self._jobs: dict[str, WritingJob] = {}
        self._job_counter: int = 0

    def create_job(
        self,
        title: str,
        topic: str,
        chapter_titles: list[str],
        subtitle: str | None = None,
    ) -> WritingJob:
        self._job_counter += 1
        job_id = f"job_{self._job_counter}"
        chapters = [ChapterDraft(title=t) for t in chapter_titles]
        draft = BookDraft(title=title, subtitle=subtitle, topic=topic, chapters=chapters)
        now = datetime.now().isoformat()
        job = WritingJob(
            id=job_id,
            draft=draft,
            status=WritingStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._jobs[job_id] = job
        return job

    async def run_job(
        self,
        job_id: str,
        generator: ContentGenerator,
        config: WritingConfig | None = None,
    ) -> WriterPipelineResult:
        job = self._jobs.get(job_id)
        if job is None:
            raise ValueError(f"Writing job '{job_id}' not found")

        cfg = config or self._config
        result = await self._pipeline.run(job.draft, generator, cfg)

        updated_job = job.model_copy(update={
            "draft": result.draft,
            "status": WritingStatus.COMPLETED if result.success else WritingStatus.FAILED,
            "errors": [m.message for m in result.validation_messages if getattr(m, "severity", "warning") == "error"],
            "updated_at": datetime.now().isoformat(),
        })
        self._jobs[job_id] = updated_job

        return result

    def get_job(self, job_id: str) -> WritingJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[WritingJob]:
        return list(self._jobs.values())

    def delete_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False

    def get_draft(self, job_id: str) -> BookDraft | None:
        job = self._jobs.get(job_id)
        return job.draft if job else None
