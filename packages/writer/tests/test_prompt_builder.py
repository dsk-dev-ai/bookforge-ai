from bookforge.writer.prompt_builder import PromptBuilder


class TestPromptBuilder:
    def setup_method(self) -> None:
        self.builder = PromptBuilder()

    def test_chapter_prompt(self) -> None:
        template = self.builder.chapter_prompt(
            topic="Python",
            title="Python Guide",
            chapter_title="Functions",
            chapter_goal="Explain functions",
            audience="beginners",
            research="Functions are reusable",
            target_words=500,
        )
        system, user = template.compose()
        assert "technical author" in system
        assert "Python" in user
        assert "Functions" in user
        assert "500" in user

    def test_section_prompt(self) -> None:
        template = self.builder.section_prompt(
            topic="Python",
            title="Python Guide",
            chapter_title="Functions",
            section_heading="Parameters",
            section_goal="Explain parameters",
            target_words=200,
        )
        _, user = template.compose()
        assert "Parameters" in user

    def test_glossary_prompt(self) -> None:
        template = self.builder.glossary_prompt(
            topic="Python",
            title="Python Guide",
            terms=[{"term": "Decorator", "context": "Functions"}],
        )
        _, user = template.compose()
        assert "Decorator" in user

    def test_reference_prompt(self) -> None:
        template = self.builder.reference_prompt(
            topic="Python",
            title="Python Guide",
            references=[{"title": "print()", "description": "Built-in function"}],
        )
        _, user = template.compose()
        assert "print()" in user

    def test_code_example_prompt(self) -> None:
        template = self.builder.code_example_prompt(
            topic="Python",
            title="Python Guide",
            language="python",
            description="List comprehension",
        )
        _, user = template.compose()
        assert "python" in user

    def test_table_prompt(self) -> None:
        template = self.builder.table_prompt(
            topic="Python",
            title="Python Guide",
            columns="Name, Type, Description",
            description="Data types",
        )
        _, user = template.compose()
        assert "Name, Type, Description" in user

    def test_introduction_prompt(self) -> None:
        template = self.builder.introduction_prompt(
            topic="Python",
            title="Python Guide",
            chapter_title="Intro",
            target_words=300,
        )
        _, user = template.compose()
        assert "engaging introduction" in user.lower()

    def test_conclusion_prompt(self) -> None:
        template = self.builder.conclusion_prompt(
            topic="Python",
            title="Python Guide",
            chapter_title="Intro",
        )
        _, user = template.compose()
        assert "conclusion" in user.lower()

    def test_compose_without_variables(self) -> None:
        template = self.builder.chapter_prompt(
            topic="T", title="T", chapter_title="Ch1",
        )
        _, user = template.compose()
        assert "T" in user
        assert "Ch1" in user
