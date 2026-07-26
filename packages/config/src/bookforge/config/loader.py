from __future__ import annotations

from functools import lru_cache

from bookforge.config.application import ApplicationSettings, EnvironmentSettings
from bookforge.config.features import FeatureFlags
from bookforge.config.logging_ import LoggingSettings
from bookforge.config.providers import NvidiaSettings, OllamaSettings, ProviderSettings
from bookforge.config.publishing import PublishingSettings
from bookforge.config.research import ResearchSettings
from bookforge.config.review import ReviewSettings
from bookforge.config.security import SecuritySettings
from bookforge.config.storage import StorageSettings
from bookforge.config.writer import WriterSettings


class BookForgeConfig:
    """Aggregate configuration containing all settings groups.

    Each attribute is lazily loaded and cached.
    """

    def __init__(self) -> None:
        self._environment: EnvironmentSettings | None = None
        self._application: ApplicationSettings | None = None
        self._features: FeatureFlags | None = None
        self._provider: ProviderSettings | None = None
        self._nvidia: NvidiaSettings | None = None
        self._ollama: OllamaSettings | None = None
        self._research: ResearchSettings | None = None
        self._writer: WriterSettings | None = None
        self._review: ReviewSettings | None = None
        self._publishing: PublishingSettings | None = None
        self._logging: LoggingSettings | None = None
        self._storage: StorageSettings | None = None
        self._security: SecuritySettings | None = None

    @property
    def environment(self) -> EnvironmentSettings:
        if self._environment is None:
            self._environment = EnvironmentSettings()
        return self._environment

    @property
    def application(self) -> ApplicationSettings:
        if self._application is None:
            self._application = ApplicationSettings()
        return self._application

    @property
    def features(self) -> FeatureFlags:
        if self._features is None:
            self._features = FeatureFlags()
        return self._features

    @property
    def provider(self) -> ProviderSettings:
        if self._provider is None:
            self._provider = ProviderSettings()
        return self._provider

    @property
    def nvidia(self) -> NvidiaSettings:
        if self._nvidia is None:
            self._nvidia = NvidiaSettings()
        return self._nvidia

    @property
    def ollama(self) -> OllamaSettings:
        if self._ollama is None:
            self._ollama = OllamaSettings()
        return self._ollama

    @property
    def research(self) -> ResearchSettings:
        if self._research is None:
            self._research = ResearchSettings()
        return self._research

    @property
    def writer(self) -> WriterSettings:
        if self._writer is None:
            self._writer = WriterSettings()
        return self._writer

    @property
    def review(self) -> ReviewSettings:
        if self._review is None:
            self._review = ReviewSettings()
        return self._review

    @property
    def publishing(self) -> PublishingSettings:
        if self._publishing is None:
            self._publishing = PublishingSettings()
        return self._publishing

    @property
    def logging(self) -> LoggingSettings:
        if self._logging is None:
            self._logging = LoggingSettings()
        return self._logging

    @property
    def storage(self) -> StorageSettings:
        if self._storage is None:
            self._storage = StorageSettings()
        return self._storage

    @property
    def security(self) -> SecuritySettings:
        if self._security is None:
            self._security = SecuritySettings()
        return self._security

    def reload(self) -> None:
        """Force reload all settings from environment variables."""
        self._environment = None
        self._application = None
        self._features = None
        self._provider = None
        self._nvidia = None
        self._ollama = None
        self._research = None
        self._writer = None
        self._review = None
        self._publishing = None
        self._logging = None
        self._storage = None
        self._security = None


@lru_cache(maxsize=1)
def load_config() -> BookForgeConfig:
    """Load and cache the global application configuration."""
    return BookForgeConfig()
