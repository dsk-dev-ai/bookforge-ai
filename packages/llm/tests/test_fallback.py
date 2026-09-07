"""Tests for fallback behaviour through the provider manager."""


from bookforge.llm.base import BaseProvider
from bookforge.llm.config_loader import RuntimeConfig
from bookforge.llm.manager import ProviderManager
from bookforge.llm.models import (
    ChatConfig,
    ChatResponse,
    HealthStatus,
    Message,
    MessageRole,
    TokenUsage,
)


class _AlwaysFailsProvider(BaseProvider):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def chat(self, messages: list[Message], config: ChatConfig | None = None) -> ChatResponse:
        from bookforge.llm.errors import ProviderUnavailable

        raise ProviderUnavailable(self.name, "simulated failure")

    async def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.name)


class _HealthyProvider(BaseProvider):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def chat(self, messages: list[Message], config: ChatConfig | None = None) -> ChatResponse:
        return ChatResponse(
            content=f"response from {self.name}",
            model=self.name,
            provider=self.name,
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        )

    async def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.name)


class TestFallback:
    async def test_fallback_to_healthy_provider(self) -> None:
        config = RuntimeConfig(
            provider="failing",
            fallback_provider="healthy",
            default_model="test",
            max_retries=0,
            retry_backoff_factor=1.0,
            retry_max_delay=1.0,
            retry_jitter=0,
            rate_limit_requests_per_minute=1000,
            rate_limit_tokens_per_minute=100000,
            health_check_interval_seconds=9999,
            health_check_timeout_seconds=5,
            circuit_breaker_threshold=100,
            circuit_breaker_cooldown_seconds=9999,
            fallback_enabled=True,
        )
        manager = ProviderManager(config=config)
        manager.register_provider(_AlwaysFailsProvider("failing"))
        manager.register_provider(_HealthyProvider("healthy"))
        manager.health.set_providers(manager.registry.providers())
        await manager.health.check_all()
        await manager.start()

        response = await manager.chat(
            [Message(role=MessageRole.USER, content="hello")],
            ChatConfig(model="test"),
        )
        assert "response from healthy" in response.content
        await manager.stop()
