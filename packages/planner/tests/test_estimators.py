from bookforge.planner.estimators import (
    AudienceAnalyzer,
    ChapterEstimator,
    DifficultyEstimator,
    PageEstimator,
    TimeEstimator,
)
from bookforge.planner.models import BookBlueprint, BookOutline, ChapterPlan


class TestAudienceAnalyzer:
    def test_beginners_at_low_difficulty(self) -> None:
        analyzer = AudienceAnalyzer()
        bp = BookBlueprint(title="T", topic="T", difficulty=0.1)
        scores = analyzer.analyze(bp)
        assert scores["beginners"] > scores["advanced"]

    def test_experts_at_high_difficulty(self) -> None:
        analyzer = AudienceAnalyzer()
        bp = BookBlueprint(title="T", topic="T", difficulty=0.9)
        scores = analyzer.analyze(bp)
        assert scores["experts"] > scores["beginners"]

    def test_scores_sum_to_one(self) -> None:
        analyzer = AudienceAnalyzer()
        bp = BookBlueprint(title="T", topic="T", difficulty=0.5)
        scores = analyzer.analyze(bp)
        total = sum(scores.values())
        assert abs(total - 1.0) < 0.01


class TestDifficultyEstimator:
    def test_estimate_chapter_difficulty_default(self) -> None:
        estimator = DifficultyEstimator()
        ch = ChapterPlan(title="Ch1")
        score = estimator.estimate_chapter_difficulty(ch)
        assert 0.0 <= score <= 1.0

    def test_estimate_chapter_difficulty_with_prereqs(self) -> None:
        estimator = DifficultyEstimator()
        ch = ChapterPlan(title="Ch1", prerequisites=["A", "B", "C"])
        score = estimator.estimate_chapter_difficulty(ch)
        base = ChapterPlan(title="Ch2")
        base_score = estimator.estimate_chapter_difficulty(base)
        assert score >= base_score

    def test_overall_difficulty_no_chapters(self) -> None:
        estimator = DifficultyEstimator()
        bp = BookBlueprint(title="T", topic="T", difficulty=0.5)
        score = estimator.estimate_overall_difficulty(bp)
        assert score == 0.5


class TestChapterEstimator:
    def test_estimate_count_custom(self) -> None:
        estimator = ChapterEstimator()
        assert estimator.estimate_count("T", chapter_count=5) == 5

    def test_estimate_count_from_pages(self) -> None:
        estimator = ChapterEstimator()
        count = estimator.estimate_count("T", page_count=300)
        assert 3 <= count <= 50

    def test_estimate_pages_per_chapter(self) -> None:
        estimator = ChapterEstimator()
        assert estimator.estimate_pages_per_chapter(100.0, 5) == 20.0


class TestPageEstimator:
    def test_estimate_from_words(self) -> None:
        estimator = PageEstimator()
        pages = estimator.estimate_from_words(700)
        assert pages == 2.0

    def test_estimate_total(self) -> None:
        estimator = PageEstimator()
        pages = estimator.estimate_total(chapter_count=5)
        assert pages > 0


class TestTimeEstimator:
    def test_reading_time_from_pages(self) -> None:
        estimator = TimeEstimator()
        minutes = estimator.estimate_reading_time_minutes(10.0)
        assert minutes == 50

    def test_reading_time_from_words(self) -> None:
        estimator = TimeEstimator()
        minutes = estimator.estimate_reading_time_from_words(1000)
        assert minutes == 5

    def test_chapter_time(self) -> None:
        estimator = TimeEstimator()
        ch = ChapterPlan(title="Ch1", estimated_minutes=45)
        assert estimator.estimate_chapter_time(ch) == 45

    def test_total_time_with_learning_path(self) -> None:
        estimator = TimeEstimator()
        from bookforge.planner.models import LearningPath, LearningStep
        lp = LearningPath(
            title="Path",
            steps=[LearningStep(chapter_title="Ch1", order=1, estimated_minutes=30)],
            total_estimated_minutes=30,
        )
        bp = BookBlueprint(title="T", topic="T", learning_path=lp)
        assert estimator.estimate_total_time(bp) == 30

    def test_total_time_with_outline(self) -> None:
        estimator = TimeEstimator()
        ch = ChapterPlan(title="Ch1", estimated_minutes=60)
        outline = BookOutline(title="T", chapters=[ch])
        bp = BookBlueprint(title="T", topic="T", outline=outline)
        assert estimator.estimate_total_time(bp) == 60
