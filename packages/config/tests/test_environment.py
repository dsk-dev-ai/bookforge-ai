"""Tests for environment detection."""


import pytest
from bookforge.config.enums import Environment
from bookforge.config.environment import EnvironmentDetector, get_environment


def _clear_get_environment_cache() -> None:
    get_environment.cache_clear()


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    _clear_get_environment_cache()


class TestEnvironmentDetector:
    def test_default_is_development(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("BOOKFORGE_ENV", raising=False)
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        detector = EnvironmentDetector()
        assert detector.detect() == Environment.DEVELOPMENT

    def test_bookforge_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BOOKFORGE_ENV", "production")
        detector = EnvironmentDetector()
        assert detector.detect() == Environment.PRODUCTION

    def test_app_env_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APP_ENV", "staging")
        detector = EnvironmentDetector()
        assert detector.detect() == Environment.STAGING

    def test_environment_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ENVIRONMENT", "testing")
        detector = EnvironmentDetector()
        assert detector.detect() == Environment.TESTING

    def test_is_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BOOKFORGE_ENV", "production")
        detector = EnvironmentDetector()
        assert detector.is_production() is True
        assert detector.is_development() is False

    def test_is_development(self) -> None:
        detector = EnvironmentDetector()
        assert detector.is_development() is True

    def test_invalid_env_falls_back(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BOOKFORGE_ENV", "invalid")
        detector = EnvironmentDetector()
        assert detector.detect() == Environment.DEVELOPMENT

    def test_precedence_bookforge_env_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BOOKFORGE_ENV", "production")
        monkeypatch.setenv("ENVIRONMENT", "development")
        detector = EnvironmentDetector()
        assert detector.detect() == Environment.PRODUCTION


class TestGetEnvironment:
    def test_returns_environment(self) -> None:
        env = get_environment()
        assert isinstance(env, Environment)
