# Lifespan Events

Lifespan events let you run code once when your application starts and once when it shuts down. Perfect for setting up database connections, loading models, or cleaning up resources.

## What You'll Learn

- Running code on application startup
- Running code on application shutdown  
- Using `on_startup` and `on_shutdown` events
- Using the modern `lifespan` context manager
- Request lifecycle hooks (before/after requests)

## Quick Start

### Using on_startup and on_shutdown

```python
from ravyn import Ravyn

async def startup():
    print("Application starting...")
    # Connect to database, load ML models, etc.

async def shutdown():
    print("Application shutting down...")
    # Close database connections, save state, etc.

app = Ravyn(
    on_startup=[startup],
    on_shutdown=[shutdown]
)
```

### Using Lifespan (Modern Approach)

```python
from ravyn import Ravyn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Startup: runs before accepting requests
    print("Starting up...")
    yield
    # Shutdown: runs after all requests handled
    print("Shutting down...")

app = Ravyn(lifespan=lifespan)
```

---

## Why Use Lifespan Events?

### Perfect For:

- **Database Connections** - Connect on startup, disconnect on shutdown

- **Resource Loading** - Load ML models, config files once

- **Cache Warming** - Pre-populate caches

- **Background Services** - Start/stop background workers

- **Cleanup** - Close connections, save state

### Example Use Cases

- Opening database connection pools
- Loading machine learning models into memory
- Starting background task queues
- Initializing external service clients
- Warming up caches

---

## on_startup and on_shutdown Events

The classic approach. simple and widely used.

### Database Connection Example

```python
from ravyn import Ravyn
import databases

database = databases.Database("postgresql://localhost/mydb")

async def connect_db():
    await database.connect()
    print("Database connected")

async def disconnect_db():
    await database.disconnect()
    print("Database disconnected")

app = Ravyn(
    on_startup=[connect_db],
    on_shutdown=[disconnect_db]
)
```

### Multiple Startup/Shutdown Functions

```python
async def load_ml_model():
    print("Loading ML model...")

async def connect_redis():
    print("Connecting to Redis...")

async def cleanup_temp_files():
    print("Cleaning up temp files...")

app = Ravyn(
    on_startup=[connect_redis, load_ml_model],
    on_shutdown=[cleanup_temp_files]
)

# Executes in order: connect_redis → load_ml_model
```

### Sync and Async Functions

Both `def` and `async def` work:

```python
def sync_startup():
    print("Sync startup")

async def async_startup():
    print("Async startup")

app = Ravyn(
    on_startup=[sync_startup, async_startup],
    on_shutdown=[]
)
```

---

## Lifespan Context Manager (Modern)

The modern approach using async context managers.

### Basic Example

```python
from ravyn import Ravyn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Code before yield runs on startup
    print("Application starting")
    database = await connect_database()
    
    yield  # Application runs here
    
    # Code after yield runs on shutdown
    await database.disconnect()
    print("Application stopped")

app = Ravyn(lifespan=lifespan)
```

### Database Connection Example

```python
from ravyn import Ravyn
from contextlib import asynccontextmanager
import databases

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Startup
    db = databases.Database("postgresql://localhost/mydb")
    await db.connect()
    app.state.db = db  # Store in app state
    print("Database connected")
    
    yield
    
    # Shutdown
    await app.state.db.disconnect()
    print("Database disconnected")

app = Ravyn(lifespan=lifespan)

# Access in handlers
from ravyn import get, Request

@get("/users")
async def list_users(request: Request) -> dict:
    db = request.app.state.db
    users = await db.fetch_all("SELECT * FROM users")
    return {"users": users}
```

### Why Use Lifespan?

**Advantages over on_startup/on_shutdown:**

- **Single place** - Startup and shutdown logic together

- **Context manager** - Automatic cleanup guaranteed

- **Cleaner code** - Less boilerplate

- **Modern standard** - Recommended by ASGI spec

---

## Storing Application State

Use `app.state` to share resources across your application:

```python
from ravyn import Ravyn, get, Request
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Store resources in app.state
    app.state.db = await connect_database()
    app.state.redis = await connect_redis()
    app.state.ml_model = load_ml_model()
    
    yield
    
    # Cleanup
    await app.state.db.disconnect()
    await app.state.redis.close()

app = Ravyn(lifespan=lifespan)

@get("/predict")
async def predict(request: Request, data: dict) -> dict:
    # Access from request.app.state
    model = request.app.state.ml_model
    result = model.predict(data)
    return {"prediction": result}
```

---

## Request Lifecycle Hooks

Run code before and after each request (different from lifespan events).

### before_request and after_request

```python
from ravyn import Ravyn
import time

async def log_request(scope, receive, send):
    print(f"Request: {scope['method']} {scope['path']}")

async def log_response(scope, receive, send):
    print(f"Response sent for: {scope['path']}")

app = Ravyn(
    before_request=[log_request],
    after_request=[log_response]
)
```

### Request Timing Example

```python
from ravyn import Ravyn, get
import time

async def start_timer(scope, receive, send):
    scope['start_time'] = time.time()

async def log_duration(scope, receive, send):
    duration = time.time() - scope.get('start_time', time.time())
    print(f"Request took {duration:.3f}s")

app = Ravyn(
    before_request=[start_timer],
    after_request=[log_duration]
)

@get("/slow")
async def slow_endpoint() -> dict:
    import asyncio
    await asyncio.sleep(1)
    return {"done": True}
```

### Execution Order

```
Ravyn before_request
  → Include before_request
    → Gateway before_request
      → Handler before_request
        → [Handler executes]
      → Handler after_request
    → Gateway after_request
  → Include after_request
→ Ravyn after_request
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Using Both lifespan and on_startup/on_shutdown

**Problem:** Can't use both at the same time.

```python
# Wrong - can't use both
app = Ravyn(
    lifespan=my_lifespan,
    on_startup=[startup_func]  # Error!
)
```

**Solution:** Choose one approach:

```python
# Option 1: Use lifespan
app = Ravyn(lifespan=my_lifespan)

# Option 2: Use on_startup/on_shutdown
app = Ravyn(
    on_startup=[startup_func],
    on_shutdown=[shutdown_func]
)
```

### Pitfall 2: Forgetting to Await Async Functions

**Problem:** Not awaiting async operations in startup/shutdown.

```python
# Wrong - not awaiting
async def startup():
    database.connect()  # Missing await!

app = Ravyn(on_startup=[startup])
```

**Solution:** Always await async operations:

```python
# Correct
async def startup():
    await database.connect()

app = Ravyn(on_startup=[startup])
```

### Pitfall 3: Not Storing Resources in app.state

**Problem:** Can't access startup resources in handlers.

```python
# Wrong - db is local variable
@asynccontextmanager
async def lifespan(app: Ravyn):
    db = await connect_database()
    yield
    await db.disconnect()

# Can't access db in handlers!
```

**Solution:** Store in `app.state`:

```python
# Correct
@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.db = await connect_database()
    yield
    await app.state.db.disconnect()

# Access via request.app.state.db
```

### Pitfall 4: Expensive Operations in Handlers

**Problem:** Loading resources on every request instead of once at startup.

```python
# Wrong - loads model on every request
@get("/predict")
async def predict(data: dict) -> dict:
    model = load_ml_model()  # Slow!
    return {"result": model.predict(data)}
```

**Solution:** Load once at startup:

```python
# Correct
@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.model = load_ml_model()  # Load once
    yield

@get("/predict")
async def predict(request: Request, data: dict) -> dict:
    model = request.app.state.model  # Fast!
    return {"result": model.predict(data)}
```

---

## Complete Example: Database + Redis + ML Model

```python
from ravyn import Ravyn, get, Request
from contextlib import asynccontextmanager
import databases
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Startup: Initialize all resources
    print("Starting application...")
    
    # Database
    app.state.db = databases.Database("postgresql://localhost/mydb")
    await app.state.db.connect()
    
    # Redis
    app.state.redis = await redis.from_url("redis://localhost")
    
    # ML Model
    app.state.model = load_ml_model()
    
    print("All resources initialized")
    
    yield  # Application runs
    
    # Shutdown: Cleanup all resources
    print("Shutting down...")
    await app.state.db.disconnect()
    await app.state.redis.close()
    print("Cleanup complete")

app = Ravyn(lifespan=lifespan)

@get("/users")
async def get_users(request: Request) -> dict:
    users = await request.app.state.db.fetch_all("SELECT * FROM users")
    return {"users": users}

@get("/cache/{key}")
async def get_cached(request: Request, key: str) -> dict:
    value = await request.app.state.redis.get(key)
    return {"key": key, "value": value}

@get("/predict")
async def predict(request: Request, data: dict) -> dict:
    result = request.app.state.model.predict(data)
    return {"prediction": result}
```

---

## Best Practices

### 1. Use Lifespan for New Code

```python
# Recommended - modern approach
@asynccontextmanager
async def lifespan(app: Ravyn):
    # Setup
    yield
    # Cleanup
```

### 2. Store Resources in app.state

```python
# Good
app.state.db = database
app.state.cache = cache

# Access in handlers
db = request.app.state.db
```

### 3. Handle Errors Gracefully

```python
@asynccontextmanager
async def lifespan(app: Ravyn):
    try:
        app.state.db = await connect_database()
        yield
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if hasattr(app.state, 'db'):
            await app.state.db.disconnect()
```

---

## Next Steps

Now that you understand lifespan events, explore:

- [Application Settings](./application/settings.md) - Configure your app
- [Dependencies](./dependencies.md) - Inject resources into handlers
- [Middleware](./middleware/index.md) - Process all requests
- [Background Tasks](./background-tasks.md) - Async processing
- [Context](./context.md) - Access app state in handlers
