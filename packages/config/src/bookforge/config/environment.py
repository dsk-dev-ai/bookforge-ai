from __future__ import annotations

import os
from functools import lru_cache
from typing import ClassVar

from dotenv import dotenv_values

from bookforge.config.enums import Environment


class EnvironmentDetector:
    """Detects the current runtime environment from OS environment variables."""

    DETECTION_VARS: ClassVar[list[str]] = [
        "BOOKFORGE_ENV",
        "APP_ENV",
        "ENVIRONMENT",
    ]

    def detect(self) -> Environment:
        """Detect the environment.

        Checks ``BOOKFORGE_ENV``, then ``APP_ENV``, then ``ENVIRONMENT``.
        Falls back to ``development``.
        """
        _env = dotenv_values(".env")
        for var in self.DETECTION_VARS:
            raw = os.environ.get(var) or _env.get(var)
            if raw is not None:
                try:
                    return Environment(raw.lower())
                except ValueError:
                    continue
        return Environment.DEVELOPMENT

    def is_development(self) -> bool:
        return self.detect() is Environment.DEVELOPMENT

    def is_testing(self) -> bool:
        return self.detect() is Environment.TESTING

    def is_staging(self) -> bool:
        return self.detect() is Environment.STAGING

    def is_production(self) -> bool:
        return self.detect() is Environment.PRODUCTION


@lru_cache(maxsize=1)
def get_environment() -> Environment:
    """Get the cached environment detection result."""
    return EnvironmentDetector().detect()
