from __future__ import annotations

import random
import time
from typing import Any

from ravyn import Gateway, Ravyn, get
from ravyn.conf import settings
from ravyn.core.caches.redis import RedisCache
from ravyn.testclient import RavynTestClient
from ravyn.utils.decorators import cache


def test_basic_caching_memory(memory_cache) -> None:
    @cache(backend=memory_cache, ttl=10)
    def slow_function(x: int) -> int:
        return x * 2

    assert slow_function(5) == 10
    assert slow_function(5) == 10  # Should return from cache

    # Ensure function was not called twice
    memory_cache.sync_delete("slow_function:5")
    assert slow_function(5) == 10  # Should recompute


def test_basic_caching_memory_redis(redis_cache) -> None:
    @cache(backend=redis_cache, ttl=10)
    def slow_function(x: int) -> int:
        return x * 2

    assert slow_function(5) == 10
    assert slow_function(5) == 10  # Should return from cache

    # Ensure function was not called twice
    redis_cache.sync_delete("slow_function:5")
    assert slow_function(5) == 10  # Should recompute


async def test_cache_expiry_memory(memory_cache):
    @cache(backend=memory_cache, ttl=1)
    async def short_lived_function() -> str:
        return "cached_value"

    assert await short_lived_function() == "cached_value"
    time.sleep(1.5)  # Wait for expiry
    assert await short_lived_function() == "cached_value"  # Should recompute


async def test_cache_expiry_redis(redis_cache):
    @cache(backend=redis_cache, ttl=1)
    async def short_lived_function() -> str:
        return "cached_value"

    assert await short_lived_function() == "cached_value"
    time.sleep(1.5)  # Wait for expiry
    assert await short_lived_function() == "cached_value"  # Should recompute


async def test_cache_key_generation_memory(memory_cache):
    @cache(backend=memory_cache, ttl=10)
    async def key_test(a: int, b: str) -> str:
        return f"{a}-{b}"

    assert await key_test(1, "hello") == "1-hello"
    assert await key_test(1, "hello") == "1-hello"  # Should return from cache

    # Ensure different arguments create different cache entries
    assert await key_test(2, "hello") == "2-hello"


async def test_cache_key_generation_redis(redis_cache):
    @cache(backend=redis_cache, ttl=10)
    async def key_test(a: int, b: str) -> str:
        return f"{a}-{b}"

    assert await key_test(1, "hello") == "1-hello"
    assert await key_test(1, "hello") == "1-hello"  # Should return from cache

    # Ensure different arguments create different cache entries
    assert await key_test(2, "hello") == "2-hello"


async def test_cache_invalidation_memory(memory_cache):
    """Ensure cache invalidation works properly in memory."""

    @cache(backend=memory_cache, ttl=10)
    async def cached_function(x: int) -> int:
        return x * 3

    assert await cached_function(3) == 9
    memory_cache.sync_delete("cached_function:3")  # Manually clear cache
    assert await cached_function(3) == 9  # Should recompute


async def test_cache_invalidation_redis(redis_cache):
    """Ensure cache invalidation works properly in redis."""

    @cache(backend=redis_cache, ttl=10)
    async def cached_function(x: int) -> int:
        return x * 3

    assert await cached_function(3) == 9
    redis_cache.sync_delete("cached_function:3")  # Manually clear cache
    assert await cached_function(3) == 9  # Should recompute


async def test_cache_backend_failure_redis(caplog):
    """Simulate a cache backend failure and ensure fallback behavior in redis."""

    class BrokenCache(RedisCache):
        def sync_get(self, key: str) -> Any | None:
            raise RuntimeError("Simulated backend failure")

    broken_backend = BrokenCache(redis_url="redis://localhost")

    @cache(backend=broken_backend, ttl=10)
    async def unstable_function() -> str:
        return "safe_value"

    assert await unstable_function() == "safe_value"  # Should not crash


async def test_ravyn_integration_in_memory(memory_cache):
    """Ensure the caching decorator works in an Ravyn application with in-memory caching."""

    @get("/cached/{value}")
    @cache(backend=memory_cache, ttl=1)
    async def endpoint(value: int) -> dict:
        return {"value": value * 2, "random": random.randint(1, 1000)}

    app = Ravyn(routes=[Gateway(handler=endpoint)])

    with RavynTestClient(app) as client:
        response1 = client.get("/cached/10")
        response2 = client.get("/cached/10")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()  # Cached response

        # Compute the exact cache key used
        cache_key = (
            "tests.caches.test_decorator.test_ravyn_integration_in_memory.cached_endpoint:10"
        )
        time.sleep(1)

        # Delete from cache using the correct key
        memory_cache.sync_delete(cache_key)

        # Now fetch again (should be different)
        response3 = client.get("/cached/10")

        assert response3.status_code == 200
        assert response3.json() != response1.json()  # Recomputed value


async def test_ravyn_integration_default():
    """Ensure the caching decorator works in an Ravyn application with default caching."""

    @get("/cached/{value}")
    @cache(ttl=1)
    async def endpoint(value: int) -> dict:
        return {"value": value * 2, "random": random.randint(1, 1000)}

    app = Ravyn(routes=[Gateway(handler=endpoint)])

    with RavynTestClient(app) as client:
        response1 = client.get("/cached/10")
        response2 = client.get("/cached/10")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()  # Cached response

        # Compute the exact cache key used
        cache_key = (
            "tests.caches.test_decorator.test_ravyn_integration_in_memory.cached_endpoint:10"
        )
        time.sleep(1)

        # Delete from cache using the correct key
        settings.cache_backend.sync_delete(cache_key)

        # Now fetch again (should be different)
        response3 = client.get("/cached/10")

        assert response3.status_code == 200
        assert response3.json() != response1.json()  # Recomputed value


async def test_ravyn_integration_in_redis(redis_cache):
    """Ensure the caching decorator works in an Ravyn application in redis."""

    @get("/cached/{value}")
    @cache(backend=redis_cache, ttl=1)
    async def cached_endpoint(value: int) -> dict:
        return {"value": value * 2, "random": random.randint(1, 1000)}

    app = Ravyn(routes=[Gateway(handler=cached_endpoint)])

    with RavynTestClient(app) as client:
        response1 = client.get("/cached/10")
        response2 = client.get("/cached/10")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()  # Cached response

        redis_cache.sync_delete("cached_endpoint:10")
        time.sleep(1)
        response3 = client.get("/cached/10")

        assert response3.status_code == 200
        assert response3.json() != response1.json()  # Recomputed value
