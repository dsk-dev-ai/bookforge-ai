"""Configuration loader — combines settings sources into provider configs."""

from __future__ import annotations

from dataclasses import dataclass, field

from bookforge.llm.config import LLMSettings, ProviderSettings


@dataclass(frozen=True)
class ProviderEndpointConfig:
    """Resolved configuration for a single provider endpoint."""

    api_key: str | None
    base_url: str
    model: str
    timeout_seconds: float


@dataclass(frozen=True)
class RuntimeConfig:
    """Complete runtime configuration assembled from all sources."""

    provider: str
    fallback_provider: str
    default_model: str | None
    max_retries: int
    retry_backoff_factor: float
    retry_max_delay: float
    retry_jitter: float
    rate_limit_requests_per_minute: int
    rate_limit_tokens_per_minute: int
    health_check_interval_seconds: float
    health_check_timeout_seconds: float
    circuit_breaker_threshold: int
    circuit_breaker_cooldown_seconds: float
    fallback_enabled: bool
    providers: dict[str, ProviderEndpointConfig] = field(default_factory=dict)


class ConfigLoader:
    """Loads and merges configuration from all sources.

    Priority order (highest first):
    1. Environment variables
    2. .env file
    3. Default values
    """

    def load(self) -> RuntimeConfig:
        """Load and assemble the full runtime configuration.

        Returns:
            A complete RuntimeConfig with all settings resolved.
        """
        llm = LLMSettings()
        provider = ProviderSettings()

        providers: dict[str, ProviderEndpointConfig] = {
            "nvidia": ProviderEndpointConfig(
                api_key=provider.nvidia_nim_api_key,
                base_url=provider.nvidia_nim_base_url,
                model=provider.nvidia_nim_model,
                timeout_seconds=provider.nvidia_nim_timeout_seconds,
            ),
            "ollama": ProviderEndpointConfig(
                api_key=None,
                base_url=provider.ollama_base_url,
                model=provider.ollama_model,
                timeout_seconds=provider.ollama_timeout_seconds,
            ),
        }

        return RuntimeConfig(
            provider=llm.provider,
            fallback_provider=llm.fallback_provider,
            default_model=llm.default_model,
            max_retries=llm.max_retries,
            retry_backoff_factor=llm.retry_backoff_factor,
            retry_max_delay=llm.retry_max_delay,
            retry_jitter=llm.retry_jitter,
            rate_limit_requests_per_minute=llm.rate_limit_requests_per_minute,
            rate_limit_tokens_per_minute=llm.rate_limit_tokens_per_minute,
            health_check_interval_seconds=llm.health_check_interval_seconds,
            health_check_timeout_seconds=llm.health_check_timeout_seconds,
            circuit_breaker_threshold=llm.circuit_breaker_threshold,
            circuit_breaker_cooldown_seconds=llm.circuit_breaker_cooldown_seconds,
            fallback_enabled=llm.fallback_enabled,
            providers=providers,
        )
