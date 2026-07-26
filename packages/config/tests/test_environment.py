"""Tests for environment detection."""

import os

from bookforge.config.enums import Environment
from bookforge.config.environment import EnvironmentDetector, get_environment


class TestEnvironmentDetector:
    def test_default_is_development(self) -> None:
        detector = EnvironmentDetector()
        for var in ("BOOKFORGE_ENV", "APP_ENV", "ENVIRONMENT"):
            os.environ.pop(var, None)
        assert detector.detect() == Environment.DEVELOPMENT

    def test_bookforge_env(self) -> None:
        detector = EnvironmentDetector()
        os.environ["BOOKFORGE_ENV"] = "production"
        assert detector.detect() == Environment.PRODUCTION
        os.environ.pop("BOOKFORGE_ENV", None)

    def test_app_env_fallback(self) -> None:
        detector = EnvironmentDetector()
        os.environ["APP_ENV"] = "staging"
        assert detector.detect() == Environment.STAGING
        os.environ.pop("APP_ENV", None)

    def test_environment_variable(self) -> None:
        detector = EnvironmentDetector()
        os.environ["ENVIRONMENT"] = "testing"
        assert detector.detect() == Environment.TESTING
        os.environ.pop("ENVIRONMENT", None)

    def test_is_production(self) -> None:
        detector = EnvironmentDetector()
        os.environ["BOOKFORGE_ENV"] = "production"
        assert detector.is_production() is True
        assert detector.is_development() is False
        os.environ.pop("BOOKFORGE_ENV", None)

    def test_is_development(self) -> None:
        detector = EnvironmentDetector()
        assert detector.is_development() is True

    def test_invalid_env_falls_back(self) -> None:
        detector = EnvironmentDetector()
        os.environ["BOOKFORGE_ENV"] = "invalid"
        assert detector.detect() == Environment.DEVELOPMENT
        os.environ.pop("BOOKFORGE_ENV", None)

    def test_precedence_bookforge_env_wins(self) -> None:
        detector = EnvironmentDetector()
        os.environ["BOOKFORGE_ENV"] = "production"
        os.environ["ENVIRONMENT"] = "development"
        assert detector.detect() == Environment.PRODUCTION
        os.environ.pop("BOOKFORGE_ENV", None)
        os.environ.pop("ENVIRONMENT", None)


class TestGetEnvironment:
    def test_returns_environment(self) -> None:
        env = get_environment()
        assert isinstance(env, Environment)
