"""Tests for configuration validation."""

import pytest
from bookforge.config.application import ApplicationSettings, EnvironmentSettings
from bookforge.config.enums import Environment
from bookforge.config.providers import NvidiaSettings, OllamaSettings, ProviderSettings
from bookforge.config.validator import assert_valid_config, validate_settings
from pydantic import ValidationError


class TestApplicationSettings:
    def test_defaults(self) -> None:
        settings = ApplicationSettings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.workers == 4

    def test_invalid_port_raises(self) -> None:
        with pytest.raises(ValidationError):
            ApplicationSettings(port=0)

    def test_invalid_port_too_high(self) -> None:
        with pytest.raises(ValidationError):
            ApplicationSettings(port=65536)

    def test_negative_workers_raises(self) -> None:
        with pytest.raises(ValidationError):
            ApplicationSettings(workers=0)

    def test_empty_host_raises(self) -> None:
        with pytest.raises(ValidationError):
            ApplicationSettings(host="")


class TestEnvironmentSettings:
    def test_defaults(self) -> None:
        settings = EnvironmentSettings()
        assert settings.env == Environment.DEVELOPMENT
        assert settings.debug is True

    def test_custom_env(self) -> None:
        settings = EnvironmentSettings(env=Environment.PRODUCTION, debug=False)
        assert settings.env == Environment.PRODUCTION
        assert settings.debug is False


class TestNvidiaSettings:
    def test_defaults(self) -> None:
        settings = NvidiaSettings()
        assert settings.nvidia_nim_base_url == "http://localhost:8000"
        assert settings.nvidia_nim_max_retries == 3

    def test_timeout_too_low_raises(self) -> None:
        with pytest.raises(ValidationError):
            NvidiaSettings(nvidia_nim_timeout_seconds=0.5)

    def test_timeout_too_high_raises(self) -> None:
        with pytest.raises(ValidationError):
            NvidiaSettings(nvidia_nim_timeout_seconds=700.0)

    def test_negative_max_retries_raises(self) -> None:
        with pytest.raises(ValidationError):
            NvidiaSettings(nvidia_nim_max_retries=-1)


class TestOllamaSettings:
    def test_defaults(self) -> None:
        settings = OllamaSettings()
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "llama3.1"

    def test_base_url_strips_trailing_slash(self) -> None:
        settings = OllamaSettings(ollama_base_url="http://localhost:11434/")
        assert settings.ollama_base_url == "http://localhost:11434"


class TestProviderSettings:
    def test_defaults(self) -> None:
        settings = ProviderSettings()
        assert settings.primary == "nvidia"
        assert settings.fallback == "ollama"
        assert settings.max_retries == 3

    def test_invalid_retry_backoff_raises(self) -> None:
        with pytest.raises(ValidationError):
            ProviderSettings(retry_backoff_factor=0.5)

    def test_invalid_jitter_raises(self) -> None:
        with pytest.raises(ValidationError):
            ProviderSettings(retry_jitter=1.5)

    def test_threshold_minimum(self) -> None:
        with pytest.raises(ValidationError):
            ProviderSettings(circuit_breaker_threshold=0)


class TestValidator:
    def test_validate_valid_settings(self) -> None:
        errors = validate_settings(EnvironmentSettings())
        assert errors == []

    def test_validate_invalid_settings(self) -> None:
        raw = ApplicationSettings.model_construct(port=99999)
        errors = validate_settings(raw)
        assert len(errors) >= 1

    def test_assert_valid_config_passes(self) -> None:
        assert_valid_config(EnvironmentSettings())

    def test_assert_valid_config_raises(self) -> None:
        from bookforge.config.validator import ConfigValidationError

        raw = ApplicationSettings.model_construct(port=0)
        with pytest.raises(ConfigValidationError):
            assert_valid_config(raw)
