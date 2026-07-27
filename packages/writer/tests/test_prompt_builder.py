from bookforge.writer.prompt_builder import PromptBuilder


class TestPromptBuilder:
    def setup_method(self) -> None:
        self.builder = PromptBuilder()

    def test_build_chapter_prompt(self) -> None:
        system, user = self.builder.build_chapter_prompt(
            topic="Python",
            title="Functions",
            goal="Explain functions",
            audience="beginners",
            research="Functions are reusable",
            target_words=500,
        )
        assert "technical author" in system
        assert "Python" in user
        assert "Functions" in user
        assert "500" in user

    def test_build_section_prompt(self) -> None:
        system, user = self.builder.build_section_prompt(
            book_title="Python Guide",
            chapter_title="Functions",
            section_heading="Parameters",
            section_goal="Explain parameters",
            target_words=200,
        )
        assert "technical author" in system
        assert "Parameters" in user
        assert "Python Guide" in user

    def test_build_glossary_prompt(self) -> None:
        system, user = self.builder.build_glossary_prompt(
            topic="Python",
            terms=[{"term": "Decorator", "context": "Functions"}],
        )
        assert "glossary definitions" in system
        assert "Decorator" in user

    def test_build_reference_prompt(self) -> None:
        system, user = self.builder.build_reference_prompt(
            topic="Python",
            references=[{"title": "print()", "description": "Built-in function"}],
        )
        assert "reference documentation" in system
        assert "print()" in user
