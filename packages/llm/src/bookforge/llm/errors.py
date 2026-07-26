"""Custom exception hierarchy for the LLM provider system."""


class ProviderError(Exception):
    """Base exception for all provider-related errors."""

    def __init__(self, message: str, provider_name: str | None = None) -> None:
        self.provider_name = provider_name
        super().__init__(message)

    def __str__(self) -> str:
        if self.provider_name:
            return f"{self.provider_name}: {self.args[0]}"
        return str(self.args[0])


class ProviderUnavailable(ProviderError):
    """Raised when a provider is unreachable or unhealthy."""

    def __init__(
        self,
        provider_name: str,
        reason: str = "Provider is unavailable",
        retry_after: float | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(f"{provider_name}: {reason}", provider_name=provider_name)


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""

    def __init__(self, provider_name: str, reason: str = "Authentication failed") -> None:
        super().__init__(f"{provider_name}: {reason}", provider_name=provider_name)


class RateLimitError(ProviderError):
    """Raised when a provider rate limit is exceeded."""

    def __init__(
        self,
        provider_name: str,
        retry_after: float | None = None,
        reason: str = "Rate limit exceeded",
    ) -> None:
        self.retry_after = retry_after
        super().__init__(f"{provider_name}: {reason}", provider_name=provider_name)


class ProviderTimeout(ProviderError):
    """Raised when a provider request times out."""

    def __init__(
        self,
        provider_name: str,
        timeout_seconds: float,
        operation: str = "request",
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        super().__init__(
            f"{provider_name}: {operation} timed out after {timeout_seconds}s",
            provider_name=provider_name,
        )


class ConfigurationError(ProviderError):
    """Raised when provider configuration is invalid or missing."""

    def __init__(self, message: str, provider_name: str | None = None) -> None:
        super().__init__(message, provider_name=provider_name)


class InvalidProvider(ProviderError):
    """Raised when a requested provider is not registered."""

    def __init__(self, provider_name: str) -> None:
        super().__init__(
            f"Provider '{provider_name}' is not registered",
            provider_name=provider_name,
        )
