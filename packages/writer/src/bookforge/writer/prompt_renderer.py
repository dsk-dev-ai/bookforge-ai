from __future__ import annotations


class PromptRenderer:
    def render(self, system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def render_with_history(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            *messages,
        ]

    def format_messages_for_provider(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        lines: list[str] = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            lines.append(f"<{role}>\n{content}\n</{role}>")
        return "\n".join(lines)
