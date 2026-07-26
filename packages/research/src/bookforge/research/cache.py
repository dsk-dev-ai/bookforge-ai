from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ResearchCache(ABC):
    @abstractmethod
    def get(self, key: str) -> Any | None: ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...


class MemoryCache(ResearchCache):
    def __init__(self, default_ttl: int = 3600) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None
        value, expiry = self._store[key]
        if time.monotonic() > expiry:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        t = ttl if ttl is not None else self._default_ttl
        self._store[key] = (value, time.monotonic() + t)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class DiskCache(ResearchCache):
    """Persistent cache backed by the local filesystem.

    Values are serialised as JSON and stored under a two-level
    directory tree derived from a SHA-256 hash of the cache key.
    Pydantic models are automatically serialised/deserialised via
    ``model_dump`` / ``model_validate``.
    """

    def __init__(self, cache_dir: str, default_ttl: int = 3600) -> None:
        self._cache_dir = Path(cache_dir)
        self._default_ttl = default_ttl
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        """Return the filesystem path for *key* using a nested hash layout."""
        safe = hashlib.sha256(key.encode()).hexdigest()
        subdir = self._cache_dir / safe[:2]
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / safe[2:]

    def _serialize(self, value: Any) -> Any:
        """Wrap Pydantic models with type metadata for round-trip safety."""
        if hasattr(value, "model_dump"):
            data = value.model_dump(mode="json")
            data["__module__"] = type(value).__module__
            data["__type__"] = type(value).__name__
            return {"__pydantic__": True, "data": data}
        return value

    def _deserialize(self, data: Any) -> Any:
        """Restore a Pydantic model from serialised form, if applicable."""
        if isinstance(data, dict) and data.get("__pydantic__"):
            raw = data["data"]
            module_name = raw.get("__module__", "")
            class_name = raw.get("__type__", "")
            if module_name and class_name:
                import importlib
                try:
                    mod = importlib.import_module(module_name)
                    cls = getattr(mod, class_name, None)
                    if cls is not None and hasattr(cls, "model_validate"):
                        return cls.model_validate(raw)
                except Exception:
                    pass
            return raw.get("data", raw)
        return data

    def get(self, key: str) -> Any | None:
        """Retrieve a value by key.  Returns *None* on miss or expiry."""
        path = self._path(key)
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text())
            if raw.get("key") != key:
                return None
            if time.time() > raw["expiry"]:
                path.unlink(missing_ok=True)
                return None
            return self._deserialize(raw["value"])
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store *value* under *key* with an optional *ttl* (seconds)."""
        t = ttl if ttl is not None else self._default_ttl
        serialized = self._serialize(value)
        data = {"key": key, "value": serialized, "expiry": time.time() + t}
        self._path(key).write_text(json.dumps(data))

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)

    def clear(self) -> None:
        for p in self._cache_dir.rglob("*"):
            if p.is_file():
                p.unlink()
        for p in self._cache_dir.iterdir():
            if p.is_dir():
                p.rmdir()
