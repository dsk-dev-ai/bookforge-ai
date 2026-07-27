import pytest

from bookforge.writer.enums import WritingStatus
from bookforge.writer.manager import WriterManager
from bookforge.writer.models import ContentGenerator


class FakeGenerator(ContentGenerator):
    async def generate(self, prompt: str, **kwargs) -> str:
        return "Generated content for testing."

    async def generate_stream(self, prompt: str, **kwargs):
        yield "streamed"

    @property
    def name(self) -> str:
        return "fake"


class TestWriterManager:
    def setup_method(self) -> None:
        self.manager = WriterManager()
        self.generator = FakeGenerator()

    def test_create_job(self) -> None:
        job = self.manager.create_job("Python Guide", "Python", ["Intro", "Basics"])
        assert job.id.startswith("job_")
        assert job.draft.title == "Python Guide"
        assert len(job.draft.chapters) == 2
        assert job.status == WritingStatus.PENDING

    def test_create_job_with_subtitle(self) -> None:
        job = self.manager.create_job("Guide", "Python", ["Ch1"], subtitle="Sub")
        assert job.draft.subtitle == "Sub"

    async def test_run_job(self) -> None:
        job = self.manager.create_job("Guide", "Python", ["Intro"])
        result = await self.manager.run_job(job.id, self.generator)
        assert result.success
        updated = self.manager.get_job(job.id)
        assert updated is not None
        assert updated.status == WritingStatus.COMPLETED

    async def test_run_job_not_found(self) -> None:
        with pytest.raises(ValueError, match="not found"):
            await self.manager.run_job("nonexistent", self.generator)

    def test_get_job(self) -> None:
        job = self.manager.create_job("Guide", "T", ["Ch1"])
        fetched = self.manager.get_job(job.id)
        assert fetched is not None
        assert fetched.id == job.id

    def test_get_job_not_found(self) -> None:
        assert self.manager.get_job("nonexistent") is None

    def test_list_jobs(self) -> None:
        self.manager.create_job("A", "T", ["Ch1"])
        self.manager.create_job("B", "T", ["Ch1"])
        assert len(self.manager.list_jobs()) == 2

    def test_delete_job(self) -> None:
        job = self.manager.create_job("Guide", "T", ["Ch1"])
        assert self.manager.delete_job(job.id) is True
        assert self.manager.get_job(job.id) is None

    def test_delete_nonexistent(self) -> None:
        assert self.manager.delete_job("nonexistent") is False

    def test_get_draft(self) -> None:
        job = self.manager.create_job("Guide", "Python", ["Intro"])
        draft = self.manager.get_draft(job.id)
        assert draft is not None
        assert draft.title == "Guide"

    def test_get_draft_not_found(self) -> None:
        assert self.manager.get_draft("nonexistent") is None
