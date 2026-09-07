"""Tests for request/response models."""

from bookforge.llm.models import (
    ChatResponse,
    Embedding,
    HealthStatus,
    Message,
    MessageRole,
    TokenUsage,
)


class TestMessage:
    def test_create_system_message(self) -> None:
        msg = Message(role=MessageRole.SYSTEM, content="You are a helpful assistant")
        assert msg.role == MessageRole.SYSTEM
        assert msg.content == "You are a helpful assistant"
        assert msg.name is None

    def test_create_user_message_with_name(self) -> None:
        msg = Message(role=MessageRole.USER, content="Hello", name="alice")
        assert msg.role == MessageRole.USER
        assert msg.name == "alice"

    def test_immutable(self) -> None:
        msg = Message(role=MessageRole.USER, content="test")
        try:
            msg.content = "changed"
            assert False, "should be frozen"
        except AttributeError:
            pass


class TestChatResponse:
    def test_create_response(self) -> None:
        usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        response = ChatResponse(
            content="Hello!",
            model="gpt-4o",
            provider="nvidia",
            finish_reason="stop",
            usage=usage,
            latency_ms=1500.0,
        )
        assert response.content == "Hello!"
        assert response.model == "gpt-4o"
        assert response.usage is not None
        assert response.usage.total_tokens == 30
        assert response.latency_ms == 1500.0


class TestHealthStatus:
    def test_healthy(self) -> None:
        status = HealthStatus(healthy=True, provider="nvidia", model="llama-3.1")
        assert status.healthy is True
        assert status.provider == "nvidia"
        assert status.model == "llama-3.1"
        assert status.error is None

    def test_unhealthy(self) -> None:
        status = HealthStatus(healthy=False, provider="nvidia", error="timeout")
        assert status.healthy is False
        assert status.error == "timeout"


class TestEmbedding:
    def test_create_embedding(self) -> None:
        emb = Embedding(vector=[0.1, 0.2, 0.3], index=5)
        assert emb.vector == [0.1, 0.2, 0.3]
        assert emb.index == 5
