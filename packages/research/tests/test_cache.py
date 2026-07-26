"""Tests for research cache implementations."""

import time

from bookforge.research.cache import DiskCache, MemoryCache


class TestMemoryCache:
    def test_get_missing(self) -> None:
        cache = MemoryCache()
        assert cache.get("nonexistent") is None

    def test_set_and_get(self) -> None:
        cache = MemoryCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_ttl_expiry(self) -> None:
        cache = MemoryCache(default_ttl=1)
        cache.set("key", "value", ttl=0)
        time.sleep(0.01)
        assert cache.get("key") is None

    def test_delete(self) -> None:
        cache = MemoryCache()
        cache.set("key", "value")
        cache.delete("key")
        assert cache.get("key") is None

    def test_clear(self) -> None:
        cache = MemoryCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_overwrite(self) -> None:
        cache = MemoryCache()
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"

    def test_custom_ttl(self) -> None:
        cache = MemoryCache(default_ttl=3600)
        cache.set("key", "value", ttl=100)
        data = cache.get("key")
        assert data == "value"


class TestDiskCache:
    def test_get_missing(self, tmp_path: str) -> None:
        cache = DiskCache(str(tmp_path))
        assert cache.get("nonexistent") is None

    def test_set_and_get(self, tmp_path: str) -> None:
        cache = DiskCache(str(tmp_path))
        cache.set("key1", {"nested": "data"})
        assert cache.get("key1") == {"nested": "data"}

    def test_delete(self, tmp_path: str) -> None:
        cache = DiskCache(str(tmp_path))
        cache.set("key", "value")
        cache.delete("key")
        assert cache.get("key") is None

    def test_clear(self, tmp_path: str) -> None:
        cache = DiskCache(str(tmp_path))
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_ttl_expiry(self, tmp_path: str) -> None:
        cache = DiskCache(str(tmp_path), default_ttl=1)
        cache.set("key", "value", ttl=0)
        time.sleep(0.01)
        assert cache.get("key") is None

    def test_persists_across_instances(self, tmp_path: str) -> None:
        c1 = DiskCache(str(tmp_path))
        c1.set("persist", "data")
        c2 = DiskCache(str(tmp_path))
        assert c2.get("persist") == "data"

    def test_invalid_file_returns_none(self, tmp_path: str) -> None:
        cache = DiskCache(str(tmp_path))
        path = cache._path("bad")
        path.write_text("not valid json")
        assert cache.get("bad") is None
