from __future__ import annotations

from typing import Any


class PromptTemplate:
    def __init__(self, system: str, user: str) -> None:
        self.system = system
        self.user = user

    def compose(self, **variables: Any) -> tuple[str, str]:
        return (
            self.system.format(**variables),
            self.user.format(**variables),
        )


SYSTEM_PARTS: dict[str, str] = {
    "role": "You are an expert technical author writing a {style} book.",
    "format": "Write clear, well-structured content in markdown format.",
    "headings": "Use proper heading hierarchy. Use ## for sections, ### for subsections.",
    "code": "Include code blocks with language annotations where appropriate.",
    "practical": "Keep explanations practical and actionable.",
    "glossary": "Provide clear, concise definitions for each term.",
    "reference": "Provide precise technical details, usage examples, and important notes.",
}

USER_PARTS: dict[str, str] = {
    "context": "Book topic: {topic}\nTitle: {title}",
    "audience": "Target audience: {audience}",
    "chapter_context": "Chapter title: {chapter_title}\nChapter goal: {chapter_goal}",
    "section_context": "Section heading: {section_heading}\nSection goal: {section_goal}",
    "research": "Research context: {research}",
    "word_count": "Target word count: {target_words}",
    "terms": "Create glossary definitions for the following terms:\n{terms}",
    "references": "Write reference documentation for:\n{references}",
    "code_info": "Language: {language}\nDescription: {description}",
    "table_info": "Create a table with the following columns: {columns}\nDescription: {description}",
}


class PromptBuilder:
    def build_prompt(
        self,
        system_keys: list[str],
        user_keys: list[str],
        **variables: Any,
    ) -> tuple[str, str]:
        system_parts = [SYSTEM_PARTS[k] for k in system_keys if k in SYSTEM_PARTS]
        system = " ".join(system_parts)

        user_parts = [USER_PARTS[k] for k in user_keys if k in USER_PARTS]
        user = "\n".join(user_parts)

        extra = variables.pop("extra_user_instructions", "")
        if extra:
            user = f"{user}\n{extra}"

        system = system.format(**variables)
        user = user.format(**variables)
        return system, user

    def chapter_prompt(
        self,
        topic: str,
        title: str,
        chapter_title: str,
        chapter_goal: str = "",
        audience: str = "developers",
        research: str = "",
        target_words: int = 800,
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "format", "headings", "code", "practical"]
        user_keys = ["context", "audience", "chapter_context", "research", "word_count"]
        system, user = self.build_prompt(
            system_keys, user_keys,
            style=style, topic=topic, title=title,
            chapter_title=chapter_title, chapter_goal=chapter_goal,
            audience=audience, research=research, target_words=target_words,
        )
        return PromptTemplate(system, user)

    def section_prompt(
        self,
        topic: str,
        title: str,
        chapter_title: str,
        section_heading: str,
        section_goal: str = "",
        research: str = "",
        target_words: int = 300,
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "format", "headings", "practical"]
        user_keys = ["context", "chapter_context", "section_context", "research", "word_count"]
        system, user = self.build_prompt(
            system_keys, user_keys,
            style=style, topic=topic, title=title,
            chapter_title=chapter_title, chapter_goal="",
            section_heading=section_heading, section_goal=section_goal,
            research=research, target_words=target_words,
        )
        return PromptTemplate(system, user)

    def glossary_prompt(
        self,
        topic: str,
        title: str,
        terms: list[dict[str, str]],
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "glossary"]
        terms_text = "\n".join(
            f"- {t.get('term', '')}: {t.get('context', '')}" for t in terms
        )
        system, user = self.build_prompt(
            system_keys, ["context", "terms"],
            style=style, topic=topic, title=title,
            terms=terms_text,
        )
        return PromptTemplate(system, user)

    def reference_prompt(
        self,
        topic: str,
        title: str,
        references: list[dict[str, str]],
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "reference"]
        refs_text = "\n".join(
            f"- {r.get('title', '')}: {r.get('description', '')}" for r in references
        )
        system, user = self.build_prompt(
            system_keys, ["context", "references"],
            style=style, topic=topic, title=title,
            references=refs_text,
        )
        return PromptTemplate(system, user)

    def code_example_prompt(
        self,
        topic: str,
        title: str,
        language: str,
        description: str,
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "format", "code", "practical"]
        user_keys = ["context", "code_info"]
        system, user = self.build_prompt(
            system_keys, user_keys,
            style=style, topic=topic, title=title,
            language=language, description=description,
        )
        return PromptTemplate(system, user)

    def table_prompt(
        self,
        topic: str,
        title: str,
        columns: str,
        description: str,
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "format", "practical"]
        user_keys = ["context", "table_info"]
        system, user = self.build_prompt(
            system_keys, user_keys,
            style=style, topic=topic, title=title,
            columns=columns, description=description,
        )
        return PromptTemplate(system, user)

    def introduction_prompt(
        self,
        topic: str,
        title: str,
        chapter_title: str,
        chapter_goal: str = "",
        research: str = "",
        target_words: int = 400,
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "format", "practical"]
        user_keys = ["context", "chapter_context", "research", "word_count"]
        system, user = self.build_prompt(
            system_keys, user_keys,
            style=style, topic=topic, title=title,
            chapter_title=chapter_title, chapter_goal=chapter_goal,
            research=research, target_words=target_words,
            extra_user_instructions="Write an engaging introduction that sets up the chapter.",
        )
        return PromptTemplate(system, user)

    def conclusion_prompt(
        self,
        topic: str,
        title: str,
        chapter_title: str,
        chapter_summary: str = "",
        style: str = "technical",
    ) -> PromptTemplate:
        system_keys = ["role", "format", "practical"]
        system, user = self.build_prompt(
            system_keys, ["context", "chapter_context"],
            style=style, topic=topic, title=title,
            chapter_title=chapter_title, chapter_goal="",
            extra_user_instructions=(
                f"Write a conclusion for the chapter '{chapter_title}'.\n"
                f"Chapter summary: {chapter_summary}\n"
                "Summarize key takeaways and preview what comes next."
            ),
        )
        return PromptTemplate(system, user)
