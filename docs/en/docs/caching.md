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
from ravyn.core.caching.backends import RedisCacheBackend

redis_backend = RedisCacheBackend(url="redis://localhost:6379")

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
from ravyn.core.caching.backends import RedisCacheBackend

class Settings(RavynSettings):
    @property
    def cache_backend(self):
        return RedisCacheBackend(url="redis://localhost:6379")
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

TTL determines how long data stays in cache:

```python
# Cache for 1 minute
@cache(ttl=60)

# Cache for 1 hour
@cache(ttl=3600)

# Cache for 1 day
@cache(ttl=86400)
```

### Choosing TTL

| Data Type | Recommended TTL | Example |
|-----------|----------------|---------|
| **Static content** | Hours/Days | `ttl=86400` |
| **Frequently updated** | Minutes | `ttl=300` |
| **Expensive queries** | 5-15 minutes | `ttl=600` |
| **External API data** | 10-30 minutes | `ttl=1800` |

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
from ravyn.core.caching.backends import RedisCacheBackend
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
from ravyn.core.caching.backends import RedisCacheBackend

redis = RedisCacheBackend(url="redis://localhost:6379")

@cache(ttl=3600, backend=redis)
async def get_data() -> dict:
    return {"data": "..."}
```

---

## Cache Invalidation

Manually clear cache when data changes:

```python
from ravyn import post, get
from ravyn.utils.decorators import cache

# Cache backend instance
from ravyn.core.caching.backends import RedisCacheBackend
redis = RedisCacheBackend(url="redis://localhost:6379")

@get("/products")
@cache(ttl=300, backend=redis)
async def get_products() -> dict:
    return {"products": fetch_products()}

@post("/products")
async def create_product(product: dict) -> dict:
    # Create product
    save_product(product)
    
    # Invalidate cache
    await redis.delete("products")
    
    return {"created": True}
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
