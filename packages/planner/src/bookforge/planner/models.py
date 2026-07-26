from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SectionPlan(BaseModel):
    heading: str = Field(description="Section heading")
    goal: str = Field(default="", description="What this section teaches")
    subsections: list[SectionPlan] = Field(default_factory=list, description="Nested subsections")
    estimated_pages: float = Field(default=0.0, ge=0.0, description="Estimated page count")
    estimated_minutes: int = Field(default=0, ge=0, description="Estimated reading time in minutes")
    required_diagrams: list[str] = Field(default_factory=list, description="Required diagram descriptions")
    required_code_examples: list[str] = Field(default_factory=list, description="Required code example descriptions")
    required_tables: list[str] = Field(default_factory=list, description="Required table descriptions")


class ChapterPlan(BaseModel):
    title: str = Field(description="Chapter title")
    goal: str = Field(default="", description="Chapter goal or purpose")
    prerequisites: list[str] = Field(default_factory=list, description="Prerequisite chapter titles or concepts")
    learning_objectives: list[str] = Field(default_factory=list, description="Learning objectives")
    estimated_pages: float = Field(default=0.0, ge=0.0, description="Estimated page count")
    estimated_minutes: int = Field(default=0, ge=0, description="Estimated reading time in minutes")
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0, description="Difficulty score 0-1")
    required_diagrams: list[str] = Field(default_factory=list, description="Required diagram descriptions")
    required_code_examples: list[str] = Field(default_factory=list, description="Required code example descriptions")
    required_tables: list[str] = Field(default_factory=list, description="Required table descriptions")
    sections: list[SectionPlan] = Field(default_factory=list, description="Chapter sections")

    @property
    def total_pages(self) -> float:
        return self.estimated_pages + sum(s.estimated_pages for s in self.sections)

    @property
    def total_minutes(self) -> int:
        return self.estimated_minutes + sum(s.estimated_minutes for s in self.sections)


class BookOutline(BaseModel):
    title: str = Field(description="Book title")
    subtitle: str | None = Field(default=None, description="Book subtitle")
    chapters: list[ChapterPlan] = Field(default_factory=list, description="Ordered chapter plans")
    front_matter: list[SectionPlan] = Field(default_factory=list, description="Front matter sections")
    back_matter: list[SectionPlan] = Field(default_factory=list, description="Back matter sections")

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    @property
    def total_pages(self) -> float:
        fm = sum(s.estimated_pages for s in self.front_matter)
        ch = sum(c.total_pages for c in self.chapters)
        bm = sum(s.estimated_pages for s in self.back_matter)
        return fm + ch + bm

    @property
    def total_minutes(self) -> int:
        fm = sum(s.estimated_minutes for s in self.front_matter)
        ch = sum(c.total_minutes for c in self.chapters)
        bm = sum(s.estimated_minutes for s in self.back_matter)
        return fm + ch + bm


class TopicCluster(BaseModel):
    name: str = Field(description="Cluster name")
    topics: list[str] = Field(default_factory=list, description="Topics in this cluster")
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance of this cluster")


class DependencyEdge(BaseModel):
    from_chapter: str = Field(description="Source chapter title")
    to_chapter: str = Field(description="Target chapter title that depends on source")
    reason: str = Field(default="", description="Why this dependency exists")


class DependencyGraph(BaseModel):
    edges: list[DependencyEdge] = Field(default_factory=list, description="Dependency edges")
    chapter_titles: list[str] = Field(default_factory=list, description="All chapter titles in the graph")

    def has_cycle(self) -> bool:
        adj: dict[str, list[str]] = {t: [] for t in self.chapter_titles}
        for e in self.edges:
            if e.from_chapter not in adj:
                adj[e.from_chapter] = []
            adj[e.from_chapter].append(e.to_chapter)

        visited: set[str] = set()
        recursion_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)
            for neighbour in adj.get(node, []):
                if neighbour not in visited:
                    if dfs(neighbour):
                        return True
                elif neighbour in recursion_stack:
                    return True
            recursion_stack.discard(node)
            return False

        for node in self.chapter_titles:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> list[str]:
        adj: dict[str, list[str]] = {t: [] for t in self.chapter_titles}
        in_degree: dict[str, int] = {t: 0 for t in self.chapter_titles}
        for e in self.edges:
            adj[e.from_chapter].append(e.to_chapter)
            in_degree[e.to_chapter] += 1

        queue: list[str] = [t for t, d in in_degree.items() if d == 0]
        result: list[str] = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            for neighbour in adj.get(node, []):
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)

        return result

    def dependencies_for(self, chapter_title: str) -> list[str]:
        return [e.from_chapter for e in self.edges if e.to_chapter == chapter_title]

    def dependents_of(self, chapter_title: str) -> list[str]:
        return [e.to_chapter for e in self.edges if e.from_chapter == chapter_title]


class ConceptNode(BaseModel):
    name: str = Field(description="Concept name")
    definition: str = Field(default="", description="Concept definition")
    chapter: str | None = Field(default=None, description="Associated chapter title")
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0, description="Concept difficulty")


class Relationship(BaseModel):
    source: str = Field(description="Source concept name")
    target: str = Field(description="Target concept name")
    relationship_type: str = Field(default="prerequisite", description="Type of relationship")


class ConceptGraph(BaseModel):
    concepts: dict[str, ConceptNode] = Field(default_factory=dict, description="Concept map keyed by name")
    relationships: list[Relationship] = Field(default_factory=list, description="Concept relationships")

    def add_concept(self, concept: ConceptNode) -> None:
        self.concepts[concept.name] = concept

    def add_relationship(self, rel: Relationship) -> None:
        self.relationships.append(rel)

    def prerequisites_for(self, concept_name: str) -> list[str]:
        return [r.source for r in self.relationships if r.target == concept_name and r.relationship_type == "prerequisite"]


class PrerequisiteGraph(BaseModel):
    levels: list[list[str]] = Field(default_factory=list, description="Topologically ordered prerequisite levels")
    all_prerequisites: dict[str, list[str]] = Field(default_factory=dict, description="Map of chapter to prerequisites")

    def level_for(self, chapter_title: str) -> int:
        for i, level in enumerate(self.levels):
            if chapter_title in level:
                return i
        return -1

    def max_depth(self) -> int:
        return len(self.levels)


class LearningStep(BaseModel):
    chapter_title: str = Field(description="Chapter to study")
    order: int = Field(ge=1, description="Step order")
    estimated_minutes: int = Field(default=0, ge=0, description="Time estimate")
    prerequisites_met: list[str] = Field(default_factory=list, description="Prerequisites satisfied at this step")


class LearningPath(BaseModel):
    title: str = Field(description="Learning path title")
    steps: list[LearningStep] = Field(default_factory=list, description="Ordered learning steps")
    total_estimated_pages: float = Field(default=0.0, ge=0.0, description="Total pages")
    total_estimated_minutes: int = Field(default=0, ge=0, description="Total reading time")

    @property
    def step_count(self) -> int:
        return len(self.steps)


class BookBlueprint(BaseModel):
    title: str = Field(description="Book title")
    subtitle: str | None = Field(default=None, description="Book subtitle")
    topic: str = Field(description="Book topic")
    summary: str = Field(default="", description="Book summary")
    target_audience: str = Field(default="developers", description="Target audience description")
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0, description="Overall difficulty score")
    estimated_pages: float = Field(default=0.0, ge=0.0, description="Total estimated pages")
    estimated_chapters: int = Field(default=0, ge=0, description="Number of chapters")
    estimated_reading_minutes: int = Field(default=0, ge=0, description="Total reading time")
    outline: BookOutline | None = Field(default=None, description="Book outline")
    dependency_graph: DependencyGraph | None = Field(default=None, description="Chapter dependency graph")
    prerequisite_graph: PrerequisiteGraph | None = Field(default=None, description="Prerequisite graph")
    learning_path: LearningPath | None = Field(default=None, description="Optimized learning path")
    topic_clusters: list[TopicCluster] = Field(default_factory=list, description="Topic clusters")
    created_at: datetime = Field(default_factory=datetime.now, description="When this blueprint was created")

    @property
    def is_complete(self) -> bool:
        return self.outline is not None and self.estimated_chapters > 0
