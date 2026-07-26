from __future__ import annotations

from bookforge.planner.models import BookBlueprint, ChapterPlan


class AudienceAnalyzer:
    def analyze(self, blueprint: BookBlueprint) -> dict[str, float]:
        scores: dict[str, float] = {
            "beginners": 0.0,
            "intermediate": 0.0,
            "advanced": 0.0,
            "experts": 0.0,
        }
        diff = blueprint.difficulty
        if diff < 0.3:
            scores["beginners"] = 1.0 - diff
            scores["intermediate"] = diff * 2
            scores["advanced"] = 0.0
            scores["experts"] = 0.0
        elif diff < 0.6:
            scores["beginners"] = max(0.0, 1.0 - diff * 2)
            scores["intermediate"] = 1.0 - abs(diff - 0.45) * 3
            scores["advanced"] = max(0.0, diff - 0.3) * 2
            scores["experts"] = 0.0
        elif diff < 0.8:
            scores["beginners"] = 0.0
            scores["intermediate"] = max(0.0, 1.0 - (diff - 0.5) * 4)
            scores["advanced"] = 1.0 - abs(diff - 0.7) * 5
            scores["experts"] = max(0.0, diff - 0.6) * 3
        else:
            scores["beginners"] = 0.0
            scores["intermediate"] = 0.0
            scores["advanced"] = max(0.0, 1.0 - (diff - 0.8) * 5)
            scores["experts"] = diff

        total = sum(scores.values()) or 1.0
        return {k: v / total for k, v in scores.items()}


class DifficultyEstimator:
    def estimate_chapter_difficulty(
        self,
        chapter: ChapterPlan,
        blueprint: BookBlueprint | None = None,
    ) -> float:
        score = chapter.difficulty
        prereq_count = len(chapter.prerequisites)
        section_count = len(chapter.sections)
        objective_count = len(chapter.learning_objectives)

        score += min(prereq_count * 0.05, 0.3)
        score += min(section_count * 0.02, 0.2)
        score += min(objective_count * 0.03, 0.15)

        if chapter.required_code_examples:
            score += 0.05
        if chapter.required_diagrams:
            score += 0.03
        if chapter.required_tables:
            score += 0.02

        return min(max(score, 0.0), 1.0)

    def estimate_overall_difficulty(self, blueprint: BookBlueprint) -> float:
        if not blueprint.outline or not blueprint.outline.chapters:
            return blueprint.difficulty
        scores = [self.estimate_chapter_difficulty(c, blueprint) for c in blueprint.outline.chapters]
        return sum(scores) / len(scores)


class ChapterEstimator:
    suggested_chapter_count: int = 10

    def estimate_count(
        self,
        topic: str,
        page_count: int | None = None,
        chapter_count: int | None = None,
    ) -> int:
        if chapter_count is not None and chapter_count > 0:
            return chapter_count
        if page_count is not None and page_count > 0:
            count = max(3, page_count // 15)
            return min(count, 50)
        return self.suggested_chapter_count

    def estimate_pages_per_chapter(
        self,
        total_pages: float,
        chapter_count: int,
    ) -> float:
        if chapter_count == 0:
            return 0.0
        return total_pages / chapter_count


class PageEstimator:
    WORDS_PER_PAGE = 350

    def estimate_from_words(self, word_count: int) -> float:
        return max(1.0, word_count / self.WORDS_PER_PAGE)

    def estimate_total(
        self,
        chapter_count: int,
        sections_per_chapter: int = 5,
        words_per_section: int = 500,
        words_per_chapter_intro: int = 300,
        words_front_matter: int = 2000,
        words_back_matter: int = 3000,
    ) -> float:
        chapter_words = chapter_count * (words_per_chapter_intro + sections_per_chapter * words_per_section)
        total_words = chapter_words + words_front_matter + words_back_matter
        return self.estimate_from_words(total_words)


class TimeEstimator:
    WORDS_PER_MINUTE = 200
    MINUTES_PER_PAGE = 5.0

    def estimate_reading_time_minutes(self, page_count: float) -> int:
        return max(1, int(page_count * self.MINUTES_PER_PAGE))

    def estimate_reading_time_from_words(self, word_count: int) -> int:
        return max(1, word_count // self.WORDS_PER_MINUTE)

    def estimate_chapter_time(self, chapter: ChapterPlan) -> int:
        return chapter.estimated_minutes or self.estimate_reading_time_minutes(chapter.estimated_pages)

    def estimate_total_time(self, blueprint: BookBlueprint) -> int:
        if blueprint.learning_path:
            return blueprint.learning_path.total_estimated_minutes
        if blueprint.outline:
            return blueprint.outline.total_minutes
        return self.estimate_reading_time_minutes(blueprint.estimated_pages)
