from __future__ import annotations

from functools import lru_cache
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class SettingsCache(Generic[T]):
    """Thread-safe cache for settings instances.

    Provides a simple cache-aside pattern for settings objects.
    """

    def __init__(self) -> None:
        self._value: T | None = None

    def get(self) -> T | None:
        return self._value

    def set(self, value: T) -> None:
        self._value = value

    def invalidate(self) -> None:
        self._value = None

    @property
    def is_cached(self) -> bool:
        return self._value is not None


@lru_cache(maxsize=1)
def _get_settings_cache() -> SettingsCache[Any]:
    return SettingsCache()


def get_settings_cache() -> SettingsCache[Any]:
    """Get the global settings cache singleton."""
    return _get_settings_cache()
