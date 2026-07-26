from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from bookforge.research.enums import ResearchStatus, SourceType, SupportedInput


class KeyConcept(BaseModel):
    name: str = Field(description="Name of the concept")
    definition: str = Field(description="Definition of the concept")
    relevance: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance score")


class Terminology(BaseModel):
    term: str = Field(description="Technical term")
    definition: str = Field(description="Definition of the term")
    context: str | None = Field(default=None, description="Context or domain where term is used")


class CodeReference(BaseModel):
    language: str = Field(description="Programming language")
    code: str = Field(description="Code snippet")
    description: str = Field(description="Description of the code")
    source_url: str | None = Field(default=None, description="Original source URL")


class ArchitectureNote(BaseModel):
    title: str = Field(description="Note title")
    content: str = Field(description="Note content")
    relevance: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance score")


class Reference(BaseModel):
    title: str = Field(description="Reference title")
    url: str | None = Field(default=None, description="Reference URL")
    source_type: SourceType = Field(description="Type of source")
    authors: list[str] = Field(default_factory=list, description="List of authors")
    year: int | None = Field(default=None, ge=1900, le=2100, description="Publication year")


class SuggestedChapter(BaseModel):
    title: str = Field(description="Chapter title")
    description: str = Field(description="Chapter description")
    order: int = Field(ge=1, description="Chapter order number")


class ResearchResult(BaseModel):
    summary: str = Field(default="", description="Executive summary of the research")
    key_concepts: list[KeyConcept] = Field(default_factory=list, description="Key concepts discovered")
    terminology: list[Terminology] = Field(default_factory=list, description="Domain terminology")
    important_apis: list[str] = Field(default_factory=list, description="Important APIs")
    code_references: list[CodeReference] = Field(default_factory=list, description="Code references found")
    architecture_notes: list[ArchitectureNote] = Field(default_factory=list, description="Architecture notes")
    references: list[Reference] = Field(default_factory=list, description="References used")
    learning_objectives: list[str] = Field(default_factory=list, description="Learning objectives")
    suggested_chapters: list[SuggestedChapter] = Field(default_factory=list, description="Suggested chapter outline")

    @property
    def is_empty(self) -> bool:
        return not self.summary and not self.key_concepts and not self.references


class ResearchStatistics(BaseModel):
    sources_collected: int = Field(default=0, ge=0, description="Number of sources collected")
    documents_normalized: int = Field(default=0, ge=0, description="Number of documents normalized")
    duplicates_removed: int = Field(default=0, ge=0, description="Number of duplicates removed")
    total_ranked: int = Field(default=0, ge=0, description="Number of items ranked")
    validation_errors: int = Field(default=0, ge=0, description="Number of validation errors")
    elapsed_seconds: float = Field(default=0.0, ge=0.0, description="Total elapsed time in seconds")


class ResearchPlan(BaseModel):
    topic: str = Field(description="Research topic")
    input_type: SupportedInput = Field(default=SupportedInput.TECHNICAL_TOPIC, description="Type of input")
    objectives: list[str] = Field(default_factory=list, description="Research objectives")
    search_queries: list[str] = Field(default_factory=list, description="Generated search queries")
    target_sources: list[SourceType] = Field(default_factory=list, description="Target source types")
    depth: int = Field(default=3, ge=1, le=10, description="Research depth")
    created_at: datetime = Field(default_factory=datetime.now, description="When the plan was created")


class ResearchSource(BaseModel):
    id: str = Field(description="Unique source identifier")
    url: str | None = Field(default=None, description="Source URL")
    title: str = Field(description="Source title")
    source_type: SourceType = Field(description="Type of source")
    content: str = Field(default="", description="Raw source content")
    collected_at: datetime = Field(default_factory=datetime.now, description="When the source was collected")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Quality score")


class ResearchSection(BaseModel):
    heading: str = Field(description="Section heading")
    content: str = Field(default="", description="Section content")
    subsections: list[ResearchSection] = Field(default_factory=list, description="Nested subsections")


class ResearchDocument(BaseModel):
    id: str = Field(description="Unique document identifier")
    source_id: str = Field(description="Source identifier this document was derived from")
    title: str = Field(description="Document title")
    content: str = Field(default="", description="Normalized document content")
    sections: list[ResearchSection] = Field(default_factory=list, description="Document sections")
    normalized_at: datetime = Field(default_factory=datetime.now, description="When the document was normalized")


class ResearchTask(BaseModel):
    id: str = Field(description="Unique task identifier")
    job_id: str = Field(description="Parent job identifier")
    source_type: SourceType = Field(description="Type of source to research")
    status: ResearchStatus = Field(default=ResearchStatus.PENDING, description="Task status")
    priority: int = Field(default=0, ge=0, le=100, description="Task priority (higher = more important)")
    created_at: datetime = Field(default_factory=datetime.now, description="When the task was created")
    completed_at: datetime | None = Field(default=None, description="When the task was completed")


class ResearchJob(BaseModel):
    id: str = Field(description="Unique job identifier")
    topic: str = Field(description="Research topic")
    input_type: SupportedInput = Field(default=SupportedInput.TECHNICAL_TOPIC, description="Type of input")
    status: ResearchStatus = Field(default=ResearchStatus.PENDING, description="Job status")
    tasks: list[ResearchTask] = Field(default_factory=list, description="Research tasks")
    pipeline_stage: ResearchStatus = Field(default=ResearchStatus.PENDING, description="Current pipeline stage")
    plan: ResearchPlan | None = Field(default=None, description="Research plan")
    sources: list[ResearchSource] = Field(default_factory=list, description="Collected sources")
    documents: list[ResearchDocument] = Field(default_factory=list, description="Normalized documents")
    created_at: datetime = Field(default_factory=datetime.now, description="When the job was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the job was last updated")
    result: ResearchResult | None = Field(default=None, description="Final research result")
    statistics: ResearchStatistics = Field(default_factory=ResearchStatistics, description="Job statistics")
