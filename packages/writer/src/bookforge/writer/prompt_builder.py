from __future__ import annotations

SYSTEM_TEMPLATES: dict[str, str] = {
    "chapter": (
        "You are an expert technical author writing a book chapter. "
        "Write clear, well-structured content in markdown format. "
        "Use proper heading hierarchy (## for sections, ### for subsections). "
        "Include code blocks with language annotations where appropriate. "
        "Keep explanations practical and actionable."
    ),
    "section": (
        "You are an expert technical author writing a section of a book chapter. "
        "Write focused, detailed content in markdown format. "
        "Use ### for subsections if needed. "
        "Include examples and practical explanations."
    ),
    "glossary": (
        "You are an expert technical author creating glossary definitions. "
        "Provide clear, concise definitions for each term. "
        "Include context about how the term is used in the subject area."
    ),
    "reference": (
        "You are an expert technical author writing reference documentation. "
        "Provide precise technical details, usage examples, and important notes. "
        "Format in markdown with code blocks where applicable."
    ),
}

USER_TEMPLATES: dict[str, str] = {
    "chapter": (
        "Book topic: {topic}\n"
        "Chapter title: {title}\n"
        "Chapter goal: {goal}\n"
        "Target audience: {audience}\n"
        "Research context: {research}\n"
        "Target word count: {target_words}\n"
        "\n"
        "Write the full chapter content in markdown below:"
    ),
    "section": (
        "Book: {book_title}\n"
        "Chapter: {chapter_title}\n"
        "Section heading: {section_heading}\n"
        "Section goal: {section_goal}\n"
        "Research context: {research}\n"
        "Target word count: {target_words}\n"
        "\n"
        "Write the section content in markdown below:"
    ),
    "glossary": (
        "Book topic: {topic}\n"
        "\n"
        "Create glossary definitions for the following terms:\n"
        "{terms}\n"
        "\n"
        "Format each entry as:\n"
        "**term**  \n"
        "definition  \n"
        "*Context: where it appears*"
    ),
    "reference": (
        "Book topic: {topic}\n"
        "\n"
        "Write reference documentation for:\n"
        "{references}\n"
        "\n"
        "Include API signatures, usage examples, and notes."
    ),
}


class PromptBuilder:
    def build_chapter_prompt(
        self,
        topic: str,
        title: str,
        goal: str,
        audience: str = "developers",
        research: str = "",
        target_words: int = 800,
    ) -> tuple[str, str]:
        system = SYSTEM_TEMPLATES["chapter"]
        user = USER_TEMPLATES["chapter"].format(
            topic=topic,
            title=title,
            goal=goal,
            audience=audience,
            research=research,
            target_words=target_words,
        )
        return system, user

    def build_section_prompt(
        self,
        book_title: str,
        chapter_title: str,
        section_heading: str,
        section_goal: str,
        research: str = "",
        target_words: int = 300,
    ) -> tuple[str, str]:
        system = SYSTEM_TEMPLATES["section"]
        user = USER_TEMPLATES["section"].format(
            book_title=book_title,
            chapter_title=chapter_title,
            section_heading=section_heading,
            section_goal=section_goal,
            research=research,
            target_words=target_words,
        )
        return system, user

    def build_glossary_prompt(
        self,
        topic: str,
        terms: list[dict[str, str]],
    ) -> tuple[str, str]:
        system = SYSTEM_TEMPLATES["glossary"]
        terms_text = "\n".join(
            f"- {t.get('term', '')}: {t.get('context', '')}" for t in terms
        )
        user = USER_TEMPLATES["glossary"].format(topic=topic, terms=terms_text)
        return system, user

    def build_reference_prompt(
        self,
        topic: str,
        references: list[dict[str, str]],
    ) -> tuple[str, str]:
        system = SYSTEM_TEMPLATES["reference"]
        refs_text = "\n".join(
            f"- {r.get('title', '')}: {r.get('description', '')}" for r in references
        )
        user = USER_TEMPLATES["reference"].format(topic=topic, references=refs_text)
        return system, user
