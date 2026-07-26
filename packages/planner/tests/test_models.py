from bookforge.planner.models import (
    BookBlueprint,
    BookOutline,
    ChapterPlan,
    ConceptGraph,
    ConceptNode,
    DependencyEdge,
    DependencyGraph,
    LearningPath,
    LearningStep,
    PrerequisiteGraph,
    Relationship,
    SectionPlan,
    TopicCluster,
)


class TestSectionPlan:
    def test_defaults(self) -> None:
        s = SectionPlan(heading="Introduction")
        assert s.goal == ""
        assert s.subsections == []
        assert s.estimated_pages == 0.0
        assert s.estimated_minutes == 0

    def test_with_subsections(self) -> None:
        sub = SectionPlan(heading="Sub", goal="Detail", estimated_pages=2.0)
        s = SectionPlan(heading="Main", subsections=[sub])
        assert len(s.subsections) == 1
        assert s.subsections[0].heading == "Sub"


class TestChapterPlan:
    def test_defaults(self) -> None:
        ch = ChapterPlan(title="Chapter 1")
        assert ch.goal == ""
        assert ch.prerequisites == []
        assert ch.difficulty == 0.5

    def test_total_pages_includes_sections(self) -> None:
        ch = ChapterPlan(
            title="Ch1",
            estimated_pages=5.0,
            sections=[SectionPlan(heading="S1", estimated_pages=3.0)],
        )
        assert ch.total_pages == 8.0

    def test_total_minutes_includes_sections(self) -> None:
        ch = ChapterPlan(
            title="Ch1",
            estimated_minutes=30,
            sections=[SectionPlan(heading="S1", estimated_minutes=15)],
        )
        assert ch.total_minutes == 45


class TestBookOutline:
    def test_empty_outline(self) -> None:
        o = BookOutline(title="Test")
        assert o.chapter_count == 0
        assert o.total_pages == 0.0
        assert o.total_minutes == 0

    def test_with_chapters(self) -> None:
        ch = ChapterPlan(title="Ch1", estimated_pages=10.0, estimated_minutes=60)
        o = BookOutline(title="Test", chapters=[ch])
        assert o.chapter_count == 1
        assert o.total_pages == 10.0

    def test_with_front_back_matter(self) -> None:
        fm = SectionPlan(heading="Preface", estimated_pages=2.0, estimated_minutes=10)
        bm = SectionPlan(heading="Index", estimated_pages=3.0, estimated_minutes=5)
        o = BookOutline(title="Test", front_matter=[fm], back_matter=[bm])
        assert o.total_pages == 5.0


class TestTopicCluster:
    def test_default_relevance(self) -> None:
        tc = TopicCluster(name="Core", topics=["A", "B"])
        assert tc.relevance_score == 0.5

    def test_relevance_clamped(self) -> None:
        import pydantic
        import pytest
        with pytest.raises(pydantic.ValidationError):
            TopicCluster(name="Bad", topics=[], relevance_score=1.5)


class TestDependencyGraph:
    def test_no_cycle(self) -> None:
        g = DependencyGraph(
            edges=[
                DependencyEdge(from_chapter="Ch1", to_chapter="Ch2", reason="foundation"),
                DependencyEdge(from_chapter="Ch2", to_chapter="Ch3", reason="builds upon"),
            ],
            chapter_titles=["Ch1", "Ch2", "Ch3"],
        )
        assert not g.has_cycle()

    def test_has_cycle(self) -> None:
        g = DependencyGraph(
            edges=[
                DependencyEdge(from_chapter="Ch1", to_chapter="Ch2"),
                DependencyEdge(from_chapter="Ch2", to_chapter="Ch3"),
                DependencyEdge(from_chapter="Ch3", to_chapter="Ch1"),
            ],
            chapter_titles=["Ch1", "Ch2", "Ch3"],
        )
        assert g.has_cycle()

    def test_topological_sort_ignores_unknown_edges(self) -> None:
        g = DependencyGraph(
            edges=[
                DependencyEdge(from_chapter="Ch1", to_chapter="Ch2"),
                DependencyEdge(from_chapter="Unknown", to_chapter="Ch1"),
                DependencyEdge(from_chapter="Ch2", to_chapter="Missing"),
            ],
            chapter_titles=["Ch1", "Ch2"],
        )
        ordered = g.topological_sort()
        assert "Ch1" in ordered
        assert "Ch2" in ordered

    def test_topological_sort_no_crash_empty(self) -> None:
        g = DependencyGraph(edges=[], chapter_titles=[])
        assert g.topological_sort() == []

    def test_topological_sort(self) -> None:
        g = DependencyGraph(
            edges=[
                DependencyEdge(from_chapter="Ch1", to_chapter="Ch2"),
                DependencyEdge(from_chapter="Ch1", to_chapter="Ch3"),
                DependencyEdge(from_chapter="Ch2", to_chapter="Ch4"),
            ],
            chapter_titles=["Ch1", "Ch2", "Ch3", "Ch4"],
        )
        ordered = g.topological_sort()
        assert ordered.index("Ch1") < ordered.index("Ch2")
        assert ordered.index("Ch1") < ordered.index("Ch3")
        assert ordered.index("Ch2") < ordered.index("Ch4")

    def test_dependencies_for(self) -> None:
        g = DependencyGraph(
            edges=[DependencyEdge(from_chapter="Ch1", to_chapter="Ch2")],
            chapter_titles=["Ch1", "Ch2"],
        )
        assert g.dependencies_for("Ch2") == ["Ch1"]
        assert g.dependencies_for("Ch1") == []

    def test_dependents_of(self) -> None:
        g = DependencyGraph(
            edges=[DependencyEdge(from_chapter="Ch1", to_chapter="Ch2")],
            chapter_titles=["Ch1", "Ch2"],
        )
        assert g.dependents_of("Ch1") == ["Ch2"]
        assert g.dependents_of("Ch2") == []


class TestConceptGraph:
    def test_add_concept(self) -> None:
        g = ConceptGraph()
        c = ConceptNode(name="Python", definition="A language")
        g.add_concept(c)
        assert "Python" in g.concepts

    def test_add_relationship(self) -> None:
        g = ConceptGraph()
        g.add_concept(ConceptNode(name="A"))
        g.add_concept(ConceptNode(name="B"))
        g.add_relationship(Relationship(source="A", target="B", relationship_type="prerequisite"))
        assert g.prerequisites_for("B") == ["A"]

    def test_prerequisites_for_empty(self) -> None:
        g = ConceptGraph()
        assert g.prerequisites_for("X") == []


class TestPrerequisiteGraph:
    def test_level_for(self) -> None:
        g = PrerequisiteGraph(levels=[["Ch1", "Ch2"], ["Ch3"], ["Ch4"]])
        assert g.level_for("Ch1") == 0
        assert g.level_for("Ch3") == 1
        assert g.level_for("Ch4") == 2
        assert g.level_for("Unknown") == -1

    def test_max_depth(self) -> None:
        g = PrerequisiteGraph(levels=[["A"], ["B"], ["C"], ["D"]])
        assert g.max_depth() == 4


class TestLearningPath:
    def test_step_count(self) -> None:
        steps = [LearningStep(chapter_title="Ch1", order=1), LearningStep(chapter_title="Ch2", order=2)]
        lp = LearningPath(title="Path", steps=steps)
        assert lp.step_count == 2

    def test_defaults(self) -> None:
        lp = LearningPath(title="Empty")
        assert lp.steps == []
        assert lp.total_estimated_pages == 0.0
        assert lp.total_estimated_minutes == 0


class TestBookBlueprint:
    def test_defaults(self) -> None:
        bp = BookBlueprint(title="Test Book", topic="Testing")
        assert bp.subtitle is None
        assert bp.difficulty == 0.5
        assert bp.created_at is not None

    def test_is_complete_false_no_outline(self) -> None:
        bp = BookBlueprint(title="Test", topic="Test")
        assert not bp.is_complete

    def test_is_complete_true(self) -> None:
        outline = BookOutline(title="Test", chapters=[ChapterPlan(title="Ch1")])
        bp = BookBlueprint(title="Test", topic="Test", outline=outline, estimated_chapters=1)
        assert bp.is_complete
