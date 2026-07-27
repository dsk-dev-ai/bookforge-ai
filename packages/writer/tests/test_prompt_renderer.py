from bookforge.writer.prompt_renderer import PromptRenderer


class TestPromptRenderer:
    def setup_method(self) -> None:
        self.renderer = PromptRenderer()

    def test_render(self) -> None:
        messages = self.renderer.render("System prompt", "User prompt")
        assert len(messages) == 2
        assert messages[0] == {"role": "system", "content": "System prompt"}
        assert messages[1] == {"role": "user", "content": "User prompt"}

    def test_render_with_history(self) -> None:
        history = [{"role": "user", "content": "Q1"}, {"role": "assistant", "content": "A1"}]
        messages = self.renderer.render_with_history("System prompt", history)
        assert len(messages) == 3
        assert messages[0] == {"role": "system", "content": "System prompt"}

    def test_format_messages_for_provider(self) -> None:
        messages = [
            {"role": "system", "content": "Be helpful"},
            {"role": "user", "content": "Hello"},
        ]
        result = self.renderer.format_messages_for_provider(messages)
        assert "<SYSTEM>" in result
        assert "<USER>" in result
        assert "Be helpful" in result
        assert "Hello" in result
