"""Tests for the error hierarchy."""

from bookforge.llm.errors import (
    AuthenticationError,
    ConfigurationError,
    InvalidProvider,
    ProviderError,
    ProviderTimeout,
    ProviderUnavailable,
    RateLimitError,
)


class TestProviderError:
    def test_base_error(self) -> None:
        err = ProviderError("something went wrong", provider_name="test")
        assert str(err) == "test: something went wrong"
        assert err.provider_name == "test"

    def test_provider_unavailable(self) -> None:
        err = ProviderUnavailable("nvidia", reason="down for maintenance", retry_after=30.0)
        assert "nvidia" in str(err)
        assert "down for maintenance" in str(err)
        assert err.retry_after == 30.0
        assert err.provider_name == "nvidia"

    def test_authentication_error(self) -> None:
        err = AuthenticationError("nvidia", reason="invalid key")
        assert "nvidia" in str(err)
        assert "invalid key" in str(err)

    def test_rate_limit_error(self) -> None:
        err = RateLimitError("ollama", retry_after=60.0)
        assert "ollama" in str(err)
        assert err.retry_after == 60.0

    def test_provider_timeout(self) -> None:
        err = ProviderTimeout("nvidia", timeout_seconds=30.5, operation="chat")
        assert "nvidia" in str(err)
        assert "30.5" in str(err)
        assert "chat" in str(err)
        assert err.timeout_seconds == 30.5

    def test_configuration_error(self) -> None:
        err = ConfigurationError("missing API key", provider_name="nvidia")
        assert "missing API key" in str(err)
        assert err.provider_name == "nvidia"

    def test_invalid_provider(self) -> None:
        err = InvalidProvider("unknown")
        assert "unknown" in str(err)
        assert "not registered" in str(err)

    def test_error_inheritance(self) -> None:
        assert issubclass(ProviderUnavailable, ProviderError)
        assert issubclass(AuthenticationError, ProviderError)
        assert issubclass(RateLimitError, ProviderError)
        assert issubclass(ProviderTimeout, ProviderError)
        assert issubclass(ConfigurationError, ProviderError)
        assert issubclass(InvalidProvider, ProviderError)
