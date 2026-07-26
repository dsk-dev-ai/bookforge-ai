"""Tests for configuration loader."""

from bookforge.config.application import ApplicationSettings, EnvironmentSettings
from bookforge.config.features import FeatureFlags
from bookforge.config.loader import BookForgeConfig, load_config
from bookforge.config.logging_ import LoggingSettings
from bookforge.config.providers import NvidiaSettings, OllamaSettings, ProviderSettings
from bookforge.config.publishing import PublishingSettings
from bookforge.config.research import ResearchSettings
from bookforge.config.review import ReviewSettings
from bookforge.config.security import SecuritySettings
from bookforge.config.storage import StorageSettings
from bookforge.config.writer import WriterSettings


class TestBookForgeConfig:
    def test_all_settings_accessible(self) -> None:
        config = BookForgeConfig()
        assert isinstance(config.environment, EnvironmentSettings)
        assert isinstance(config.application, ApplicationSettings)
        assert isinstance(config.features, FeatureFlags)
        assert isinstance(config.provider, ProviderSettings)
        assert isinstance(config.nvidia, NvidiaSettings)
        assert isinstance(config.ollama, OllamaSettings)
        assert isinstance(config.research, ResearchSettings)
        assert isinstance(config.writer, WriterSettings)
        assert isinstance(config.review, ReviewSettings)
        assert isinstance(config.publishing, PublishingSettings)
        assert isinstance(config.logging, LoggingSettings)
        assert isinstance(config.storage, StorageSettings)
        assert isinstance(config.security, SecuritySettings)

    def test_settings_are_cached(self) -> None:
        config = BookForgeConfig()
        assert config.environment is config.environment

    def test_reload_resets_cache(self) -> None:
        config = BookForgeConfig()
        env1 = config.environment
        config.reload()
        env2 = config.environment
        assert env1 is not env2

    def test_reload_keeps_defaults(self) -> None:
        config = BookForgeConfig()
        config.reload()
        assert config.application.port == 8000


class TestLoadConfig:
    def test_returns_bookforge_config(self) -> None:
        config = load_config()
        assert isinstance(config, BookForgeConfig)

    def test_is_cached(self) -> None:
        assert load_config() is load_config()
