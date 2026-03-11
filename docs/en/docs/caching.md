# Caching

Imagine a busy coffee shop during morning rush. Every time someone orders a cappuccino, the barista could:

1. Grind fresh beans (2 minutes)
2. Pull a fresh espresso shot (30 seconds)
3. Steam new milk (1 minute)

Or, they could prepare espresso shots and steamed milk in advance. When orders come in, they just combine the pre-made components. Serve time drops from 3.5 minutes to 10 seconds.

That's caching. Store frequently-accessed data so you don't regenerate it every time. Your database query that takes 500ms? With caching, it's 5ms.

Caching stores frequently accessed data in fast memory, dramatically reducing response times and database load. Ravyn provides built-in caching with support for in-memory, Redis, and custom backends.

## What You'll Learn

- What caching is and when to use it
- Using the `@cache` decorator
- Configuring cache backends (in-memory, Redis)
- Setting cache TTL (time-to-live)
- Creating custom cache backends

## Quick Start

```python
from ravyn import Ravyn, get
from ravyn.utils.decorators import cache

@get("/expensive-data")
@cache(ttl=60)  # Cache for 60 seconds
async def get_expensive_data() -> dict:
    # Slow operation (database query, API call, etc.)
    import time
    time.sleep(2)

    return {"data": "This took 2 seconds to compute"}

app = Ravyn()
app.add_route(get_expensive_data)

# First request: Takes 2 seconds
# Subsequent requests (within 60s): Instant!
```

---

## What is Caching?

Caching temporarily stores computed results in fast memory. Instead of recalculating or reloading data repeatedly, your app fetches it from cache instantly.

### Real-World Analogy

Imagine a coffee shop. If a customer orders the same drink repeatedly, the barista might pre-make a batch and serve it instantly. That's caching. storing results for quick retrieval.

### Benefits

- **Faster Responses** - Serve cached data instantly

- **Reduced Database Load** - Fewer queries to your database

- **Lower API Costs** - Fewer calls to external APIs

- **Better Scalability** - Handle more users with same resources

---

## When to Use Caching

### Perfect For:

- **Expensive Computations** - Complex calculations

- **Database Queries** - Frequently accessed data

- **External API Calls** - Third-party data

- **Static Content** - Data that changes infrequently

### Not Suitable For:

- **User-Specific Data** - Personalized content

- **Real-Time Data** - Stock prices, live scores

- **Frequently Changing Data** - Data that updates every second

---

## Using the @cache Decorator

### Basic Usage

```python
from ravyn import get
from ravyn.utils.decorators import cache

@get("/users")
@cache(ttl=300)  # Cache for 5 minutes
async def list_users() -> dict:
    # Expensive database query
    users = await database.fetch_all_users()
    return {"users": users}
```

**First request:** Executes function, stores result in cache

**Subsequent requests (within 5 min):** Returns cached result instantly

### Without Caching vs With Caching

#### Without Caching (Slow)

```python
@get("/products")
async def get_products() -> dict:
    # Every request hits the database
    products = await database.query("SELECT * FROM products")
    return {"products": products}

# Every call takes 500ms
```

#### With Caching (Fast)

```python
@get("/products")
@cache(ttl=60)
async def get_products() -> dict:
    # First request hits database
    products = await database.query("SELECT * FROM products")
    return {"products": products}

# First call: 500ms
# Next calls (within 60s): <1ms
```

---

## Cache Backends

Ravyn supports multiple cache backends:

| Backend | Speed | Persistence | Use Case |
|---------|-------|-------------|----------|
| **In-Memory** | ⚡ Fastest | No | Single server, development |
| **Redis** | ⚡ Very Fast | Yes | Production, multiple servers |
| **Custom** | Varies | Varies | Special requirements |

### In-Memory Cache (Default)

```python
from ravyn import get
from ravyn.utils.decorators import cache

@get("/data")
@cache(ttl=60)  # Uses in-memory cache by default
async def get_data() -> dict:
    return {"data": "cached"}
```

!!! warning
    In-memory cache is lost when the server restarts. Use Redis for production.

### Redis Cache

```python
from ravyn import get
from ravyn.utils.decorators import cache
from ravyn.core.caches.redis import RedisCache

redis_backend = RedisCache("redis://localhost:6379")

@get("/data")
@cache(ttl=60, backend=redis_backend)
async def get_data() -> dict:
    return {"data": "cached in Redis"}
```

**Install Redis support:**

```shell
pip install redis
```

---

## Configuring Default Cache Backend

Set a global cache backend in settings:

```python
from ravyn import RavynSettings
from ravyn.core.caches.redis import RedisCache

class Settings(RavynSettings):
    @property
    def cache_backend(self):
        return RedisCache("redis://localhost:6379")
```

Now all `@cache` decorators use Redis by default:

```python
@get("/data")
@cache(ttl=60)  # Automatically uses Redis from settings
async def get_data() -> dict:
    return {"data": "cached"}
```

---

## Cache TTL (Time-To-Live)

TTL determines how long data stays in cache before expiring. When the TTL expires, the cache entry is automatically removed, and the next request will execute the function and cache the fresh result.

```python
from ravyn import get
from ravyn.utils.decorators import cache

# Cache for 1 minute
@get("/quick-data")
@cache(ttl=60)
async def get_quick_data() -> dict:
    return {"data": "expires in 60 seconds"}

# Cache for 1 hour
@get("/hourly-data")
@cache(ttl=3600)
async def get_hourly_data() -> dict:
    return {"data": "expires in 1 hour"}

# Cache for 1 day
@get("/daily-data")
@cache(ttl=86400)
async def get_daily_data() -> dict:
    return {"data": "expires in 24 hours"}

# Cache forever (no expiration)
@get("/permanent-data")
@cache(ttl=None)
async def get_permanent_data() -> dict:
    return {"data": "never expires automatically"}
```

### What Happens When Cache Expires?

1. **Before expiration:** Cached value is returned instantly (no function execution)
2. **After expiration:** Cache entry is deleted, function executes normally
3. **Result is cached again** with a fresh TTL

```python
from ravyn import get
from ravyn.utils.decorators import cache
import time

@get("/timestamp")
@cache(ttl=5)  # 5-second TTL
async def get_timestamp() -> dict:
    return {"timestamp": time.time()}

# First request: Executes function, returns timestamp=1234567890, caches result
# Requests within 5 seconds: Returns cached timestamp=1234567890
# After 5 seconds: Cache expired, function executes, returns new timestamp=1234567895
```

### Choosing TTL

| Data Type | Recommended TTL | Example |
|-----------|----------------|---------|
| **Static content** | Hours/Days | `ttl=86400` |
| **Frequently updated** | Minutes | `ttl=300` |
| **Expensive queries** | 5-15 minutes | `ttl=600` |
| **External API data** | 10-30 minutes | `ttl=1800` |
| **Never expires** | No TTL | `ttl=None` |

---

## Advanced Caching Patterns

### Conditional Caching

Cache only certain responses based on conditions:

```python
from ravyn import get
from ravyn.utils.decorators import cache
from ravyn.core.caches.memory import InMemoryCache

memory_cache = InMemoryCache()

@get("/user/{user_id}")
async def get_user(user_id: int) -> dict:
    # Fetch user data
    user = await fetch_user_from_db(user_id)

    # Only cache if user is not a premium member
    if not user.get("is_premium"):
        cache_key = f"user:{user_id}"
        await memory_cache.set(cache_key, user, ttl=300)

    return user
```

Another approach: Skip caching for specific request headers:

```python
from ravyn import get, Request

@get("/data")
async def get_data(request: Request) -> dict:
    # Check if client requested fresh data
    if request.headers.get("Cache-Control") == "no-cache":
        return {"data": await fetch_fresh_data()}

    # Use cached version
    return await get_cached_data()
```

### Manual Cache Control

Directly interact with cache backends for fine-grained control:

```python
from ravyn import get, post
from ravyn.core.caches.memory import InMemoryCache

cache_backend = InMemoryCache()

@get("/stats")
async def get_stats() -> dict:
    # Check cache first
    cached = await cache_backend.get("stats_key")
    if cached:
        return cached

    # Compute expensive stats
    stats = await compute_expensive_stats()

    # Cache with 10-minute TTL
    await cache_backend.set("stats_key", stats, ttl=600)

    return stats

@post("/clear-cache")
async def clear_cache() -> dict:
    # Manually delete cache entry
    await cache_backend.delete("stats_key")
    return {"message": "Cache cleared"}
```

### Cache Warming

Pre-populate cache on application startup:

```python
from ravyn import Ravyn, get
from ravyn.core.caches.memory import InMemoryCache

cache_backend = InMemoryCache()
app = Ravyn()

@app.on_event("startup")
async def warm_cache():
    """Populate cache with frequently accessed data before serving requests"""
    # Fetch and cache popular products
    popular_products = await fetch_popular_products()
    await cache_backend.set("popular_products", popular_products, ttl=3600)

    # Cache site configuration
    site_config = await fetch_site_config()
    await cache_backend.set("site_config", site_config, ttl=None)  # Never expires

@get("/popular")
async def get_popular() -> dict:
    # This will hit warm cache immediately
    products = await cache_backend.get("popular_products")
    return {"products": products}
```

---

## InMemoryCache vs External Backends

### InMemoryCache (Built-in)

**Advantages:**
- ⚡ **Fastest** - No network overhead
- **Zero dependencies** - No external services required
- **Simple setup** - Works out of the box

**Limitations:**
- ❌ **No persistence** - Lost on server restart
- ❌ **Single process only** - Not shared across multiple workers/servers
- ❌ **Memory bound** - Limited by server RAM

**When to use:**
- Development and testing
- Single-server deployments
- Small-scale applications
- Temporary/session caching

**Example:**

```python
from ravyn import get
from ravyn.utils.decorators import cache

# Uses InMemoryCache by default
@get("/data")
@cache(ttl=60)
async def get_data() -> dict:
    return {"data": "in-memory"}
```

### Redis (External Backend)

**Advantages:**
- ✅ **Persistent** - Survives server restarts
- ✅ **Distributed** - Shared across all workers and servers
- ✅ **Scalable** - Handles large datasets
- ✅ **Production-ready** - Battle-tested reliability

**Limitations:**
- Network latency (slightly slower than in-memory)
- Requires Redis server setup
- Additional dependency (`pip install redis`)

**When to use:**
- Production environments
- Multi-server deployments
- Applications with multiple workers (Gunicorn, Uvicorn)
- Need cache persistence

**Example:**

```python
from ravyn import get
from ravyn.utils.decorators import cache
from ravyn.core.caches.redis import RedisCache

redis_cache = RedisCache("redis://localhost:6379")

@get("/data")
@cache(ttl=60, backend=redis_cache)
async def get_data() -> dict:
    return {"data": "in-redis"}
```

### Comparison Table

| Feature | InMemoryCache | Redis |
|---------|--------------|-------|
| **Speed** | ⚡⚡⚡ Fastest | ⚡⚡ Very Fast |
| **Persistence** | ❌ No | ✅ Yes |
| **Multi-process** | ❌ No | ✅ Yes |
| **Scalability** | Limited | Excellent |
| **Setup** | None | Redis server required |
| **Use Case** | Development | Production |

---

## Creating Custom Cache Backends

Implement the `CacheBackend` protocol for custom storage:

```python
from ravyn.core.protocols.cache import CacheBackend
import json
from pathlib import Path

class FileCacheBackend(CacheBackend):
    def __init__(self, cache_dir: str = "/tmp/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    async def get(self, key: str):
        file_path = self.cache_dir / f"{key}.json"
        if file_path.exists():
            return json.loads(file_path.read_text())
        return None

    async def set(self, key: str, value, ttl: int = None):
        file_path = self.cache_dir / f"{key}.json"
        file_path.write_text(json.dumps(value))

    async def delete(self, key: str):
        file_path = self.cache_dir / f"{key}.json"
        if file_path.exists():
            file_path.unlink()

    async def clear(self):
        for file in self.cache_dir.glob("*.json"):
            file.unlink()
```

### Using Custom Backend

```python
from ravyn import get
from ravyn.utils.decorators import cache

file_cache = FileCacheBackend(cache_dir="/tmp/my_cache")

@get("/data")
@cache(ttl=60, backend=file_cache)
async def get_data() -> dict:
    return {"data": "cached in files"}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Caching User-Specific Data

**Problem:** All users see the same cached data.

```python
# Wrong - caches same data for all users
@get("/profile")
@cache(ttl=60)
async def get_profile(user_id: int) -> dict:
    return {"user": user_id, "data": "..."}

# User 1 requests /profile?user_id=1 (cached)
# User 2 requests /profile?user_id=2 (gets User 1's data!)
```

**Solution:** Don't cache user-specific data, or use cache keys:

```python
# Correct - don't cache personalized data
@get("/profile")
async def get_profile(user_id: int) -> dict:
    return {"user": user_id, "data": "..."}
```

### Pitfall 2: TTL Too Long for Changing Data

**Problem:** Stale data served to users.

```python
# Wrong - product prices cached for 1 day
@get("/products")
@cache(ttl=86400)  # 24 hours
async def get_products() -> dict:
    return {"products": fetch_products()}

# Prices change, but users see old prices for 24 hours!
```

**Solution:** Use appropriate TTL for data freshness:

```python
# Correct - shorter TTL for frequently changing data
@get("/products")
@cache(ttl=300)  # 5 minutes
async def get_products() -> dict:
    return {"products": fetch_products()}
```

### Pitfall 3: Forgetting Redis Dependency

**Problem:** `ModuleNotFoundError` when using Redis.

```python
# Error if redis not installed
from ravyn.core.caches.redis import RedisCache
```

**Solution:** Install Redis support:

```shell
pip install redis
```

### Pitfall 4: In-Memory Cache in Production

**Problem:** Cache lost on server restart or not shared across workers.

```python
# Not ideal for production
@cache(ttl=3600)  # In-memory cache
async def get_data() -> dict:
    return {"data": "..."}
```

**Solution:** Use Redis for production:

```python
# Correct for production
from ravyn.core.caches.redis import RedisCache

redis = RedisCache("redis://localhost:6379")

@cache(ttl=3600, backend=redis)
async def get_data() -> dict:
    return {"data": "..."}
```

---

## Cache Invalidation

Manually clear cache when data changes to ensure users see fresh content.

### Method 1: Using Cache Backend Directly

```python
from ravyn import post, get
from ravyn.utils.decorators import cache
from ravyn.core.caches.redis import RedisCache

redis = RedisCache("redis://localhost:6379")

@get("/products")
@cache(ttl=300, backend=redis)
async def get_products() -> dict:
    products = await fetch_products_from_db()
    return {"products": products}

@post("/products")
async def create_product(product: dict) -> dict:
    # Save new product to database
    await save_product(product)

    # Invalidate cache so next GET request fetches fresh data
    await redis.delete("products")

    return {"created": True, "product": product}
```

### Method 2: Using Cache Decorator's `invalidate()` Method

```python
from ravyn import post, get
from ravyn.utils.decorators import cache

cache_decorator = cache(ttl=300)

@get("/users")
@cache_decorator
async def get_users() -> dict:
    users = await fetch_users_from_db()
    return {"users": users}

@post("/users")
async def create_user(user: dict) -> dict:
    # Save user
    await save_user(user)

    # Invalidate the specific cache entry for get_users
    cache_decorator.invalidate(get_users)

    return {"created": True, "user": user}
```

### Method 3: Invalidating Specific Keys

For parameterized functions, invalidate cache for specific arguments:

```python
from ravyn import get, put
from ravyn.utils.decorators import cache

@get("/user/{user_id}")
@cache(ttl=600)
async def get_user(user_id: int) -> dict:
    user = await fetch_user(user_id)
    return {"user": user}

@put("/user/{user_id}")
async def update_user(user_id: int, data: dict) -> dict:
    # Update user
    await update_user_in_db(user_id, data)

    # Invalidate cache for this specific user
    from ravyn.core.caches.memory import InMemoryCache
    cache_backend = InMemoryCache()
    cache_key = f"get_user:{user_id}"
    await cache_backend.delete(cache_key)

    return {"updated": True}
```

### Method 4: Pattern-Based Invalidation (Redis)

Clear all caches matching a pattern:

```python
from ravyn import post
from ravyn.core.caches.redis import RedisCache

redis = RedisCache("redis://localhost:6379")

@post("/clear-user-caches")
async def clear_all_user_caches() -> dict:
    # Clear all keys matching pattern "user:*"
    # Note: This requires direct Redis client access
    import redis as redis_client
    r = redis_client.from_url("redis://localhost:6379")

    # Get all matching keys
    keys = r.keys("user:*")

    # Delete all matching keys
    if keys:
        r.delete(*keys)

    return {"cleared": len(keys)}
```

---

## Best Practices

### 1. Cache Expensive Operations Only

```python
# Good - expensive database query
@cache(ttl=300)
async def get_analytics() -> dict:
    return await complex_analytics_query()

# Unnecessary - simple operation
@cache(ttl=60)
async def add_numbers(a: int, b: int) -> int:
    return a + b
```

### 2. Use Appropriate TTL

```python
# Static content - long TTL
@cache(ttl=86400)  # 1 day
async def get_site_config() -> dict:
    return {"config": "..."}

# Dynamic content - short TTL
@cache(ttl=60)  # 1 minute
async def get_trending_posts() -> dict:
    return {"posts": "..."}
```

### 3. Monitor Cache Hit Rate

Track how often cache is used vs missed to optimize TTL.

---

## Next Steps

Now that you understand caching, explore:

- [Background Tasks](./background-tasks.md) - Async processing
- [Scheduler](./scheduler/index.md) - Scheduled jobs
- [Settings](./application/settings.md) - Configure cache backend
