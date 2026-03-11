from __future__ import annotations

import asyncio
import time

import pytest  # type: ignore[import-not-found]

from ravyn.core.caches.memory import InMemoryCache


@pytest.mark.asyncio
async def test_inmemory_cache_set_and_get_roundtrip() -> None:
    cache = InMemoryCache()

    await cache.set("user", {"id": 1, "name": "ravyn"})

    assert await cache.get("user") == {"id": 1, "name": "ravyn"}


@pytest.mark.asyncio
async def test_inmemory_cache_get_missing_key_returns_none() -> None:
    cache = InMemoryCache()

    assert await cache.get("missing") is None


@pytest.mark.asyncio
async def test_inmemory_cache_delete_removes_key() -> None:
    cache = InMemoryCache()
    await cache.set("token", "abc")

    await cache.delete("token")

    assert await cache.get("token") is None


@pytest.mark.asyncio
async def test_inmemory_cache_ttl_expiration() -> None:
    cache = InMemoryCache()
    await cache.set("short_lived", "value", ttl=1)

    assert await cache.get("short_lived") == "value"
    await asyncio.sleep(1.2)

    assert await cache.get("short_lived") is None


@pytest.mark.asyncio
async def test_inmemory_cache_concurrent_access_last_write_wins() -> None:
    cache = InMemoryCache()
    key = "counter"

    async def writer(value: int) -> None:
        await cache.set(key, value)

    await asyncio.gather(*(writer(i) for i in range(50)))

    final_value = await cache.get(key)
    assert isinstance(final_value, int)
    assert 0 <= final_value <= 49


@pytest.mark.asyncio
async def test_inmemory_cache_concurrent_mixed_operations_safe() -> None:
    cache = InMemoryCache()

    async def worker(index: int) -> None:
        key = f"k-{index % 5}"
        await cache.set(key, {"v": index}, ttl=2)
        value = await cache.get(key)
        if index % 3 == 0:
            await cache.delete(key)
        assert value is None or isinstance(value, dict)

    await asyncio.gather(*(worker(i) for i in range(100)))


def test_inmemory_cache_sync_set_get_delete_and_manual_clear() -> None:
    cache = InMemoryCache()

    cache.sync_set("a", 1)
    cache.sync_set("b", 2)
    assert cache.sync_get("a") == 1
    assert cache.sync_get("b") == 2

    cache.sync_delete("a")
    assert cache.sync_get("a") is None

    cache._store.clear()
    assert cache.sync_get("b") is None


def test_inmemory_cache_sync_get_removes_expired_entries() -> None:
    cache = InMemoryCache()
    cache.sync_set("expiring", "soon", ttl=1)

    payload, _expiry = cache._store["expiring"]
    cache._store["expiring"] = (payload, time.time() - 10)

    assert cache.sync_get("expiring") is None
    assert "expiring" not in cache._store
