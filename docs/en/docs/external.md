# External Packages

Ravyn makes it easy to integrate external packages and third-party tools into your application. Whether you need authentication, database ORMs, task queues, or monitoring tools, Ravyn's flexible architecture supports seamless integration.

## What You'll Learn

- Integrating popular Python packages
- Using middleware for third-party tools
- Configuring external services
- Best practices for package integration

## Quick Start

```python
from ravyn import Ravyn
from some_package import SomeMiddleware

app = Ravyn(
    middleware=[SomeMiddleware]
)

# External package is now integrated!
```

---

## Why Integrate External Packages?

### Benefits:

- **Leverage Existing Tools** - Use battle-tested libraries

- **Save Development Time** - Don't reinvent the wheel

- **Community Support** - Access to extensive documentation

- **Proven Solutions** - Production-ready implementations

### Common Use Cases:

- **Authentication** - OAuth, JWT, session management
- **Databases** - SQLAlchemy, Tortoise ORM, MongoDB
- **Caching** - Redis, Memcached
- **Task Queues** - Celery, RQ, Dramatiq
- **Monitoring** - Sentry, DataDog, Prometheus
- **Logging** - Loguru, structlog

---

## Integration Methods

### 1. Via Middleware

Most ASGI-compatible middleware works directly:

```python
from ravyn import Ravyn
from starlette.middleware.cors import CORSMiddleware

app = Ravyn(
    middleware=[
        CORSMiddleware,
        {
            "allow_origins": ["*"],
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }
    ]
)
```

### 2. Via Lifespan Events

Initialize external services on startup:

```python
from ravyn import Ravyn
from contextlib import asynccontextmanager
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Startup: Connect to Redis
    app.state.redis = await redis.from_url("redis://localhost")
    
    yield
    
    # Shutdown: Close connection
    await app.state.redis.close()

app = Ravyn(lifespan=lifespan)
```

### 3. Via Dependencies

Inject external services into handlers:

```python
from ravyn import Ravyn, get, Inject

def get_database():
    return {"db": "connection"}

@get("/users", dependencies={"db": Inject(get_database)})
def list_users(db: dict) -> dict:
    return {"users": ["Alice"], "db": db}

app = Ravyn()
app.add_route(list_users)
```

### 4. Via Extensions

Create reusable extensions:

```python
from ravyn import Ravyn
from ravyn.extensions import Extension

class MyServiceExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # Initialize your service
        app.state.my_service = MyService()

app = Ravyn(
    extensions={"my_service": MyServiceExtension()}
)
```

---

## Popular Integrations

### Authentication: JWT

```python
from ravyn import Ravyn, get, Request
from ravyn.exceptions import NotAuthorized
import jwt

SECRET_KEY = "your-secret-key"

def verify_token(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.user = payload
    except jwt.InvalidTokenError:
        raise NotAuthorized("Invalid token")

@get("/protected", dependencies={"auth": Inject(verify_token)})
def protected_route(request: Request) -> dict:
    return {"user": request.state.user}

app = Ravyn()
app.add_route(protected_route)
```

### Database: SQLAlchemy

```python
from ravyn import Ravyn, get
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Create engine
    engine = create_async_engine("postgresql+asyncpg://localhost/mydb")
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    app.state.db_session = SessionLocal
    
    yield
    
    await engine.dispose()

app = Ravyn(lifespan=lifespan)

@get("/users")
async def list_users(request: Request) -> dict:
    async with request.app.state.db_session() as session:
        # Query database
        result = await session.execute("SELECT * FROM users")
        return {"users": result.fetchall()}
```

### Caching: Redis

```python
from ravyn import Ravyn, get
from contextlib import asynccontextmanager
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.redis = await redis.from_url("redis://localhost")
    yield
    await app.state.redis.close()

app = Ravyn(lifespan=lifespan)

@get("/cache/{key}")
async def get_cached(request: Request, key: str) -> dict:
    value = await request.app.state.redis.get(key)
    return {"key": key, "value": value}

@post("/cache/{key}")
async def set_cached(request: Request, key: str, value: str) -> dict:
    await request.app.state.redis.set(key, value)
    return {"cached": True}
```

### Monitoring: Sentry

```python
from ravyn import Ravyn
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)

app = Ravyn()

# Sentry automatically captures errors
@get("/error")
def trigger_error() -> dict:
    raise Exception("This error will be sent to Sentry")
```

### Task Queue: Celery

```python
from ravyn import Ravyn, post
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def send_email(to: str, subject: str):
    # Send email logic
    pass

app = Ravyn()

@post("/send-email")
def queue_email(to: str, subject: str) -> dict:
    send_email.delay(to, subject)
    return {"queued": True}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Not Cleaning Up Resources

**Problem:** External connections not closed on shutdown.

```python
# Wrong - connection never closed
@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.db = await connect_database()
    yield
    # Missing cleanup!
```

**Solution:** Always clean up in lifespan:

```python
# Correct
@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.db = await connect_database()
    yield
    await app.state.db.disconnect()
```

### Pitfall 2: Blocking Operations in Async Context

**Problem:** Using sync libraries in async handlers.

```python
# Wrong - blocking call in async handler
@get("/users")
async def list_users() -> dict:
    users = sync_database.query("SELECT * FROM users")  # Blocks!
    return {"users": users}
```

**Solution:** Use async libraries or run in thread:

```python
# Option 1: Use async library
@get("/users")
async def list_users() -> dict:
    users = await async_database.query("SELECT * FROM users")
    return {"users": users}

# Option 2: Run sync code in thread
import asyncio

@get("/users")
async def list_users() -> dict:
    users = await asyncio.to_thread(sync_database.query, "SELECT * FROM users")
    return {"users": users}
```

### Pitfall 3: Missing Dependencies

**Problem:** Package not installed.

```python
# Error - package not installed
from some_package import SomeClass
```

**Solution:** Install required packages:

```shell
pip install some-package
```

### Pitfall 4: Incorrect Middleware Configuration

**Problem:** Middleware configured incorrectly.

```python
# Wrong - missing configuration
app = Ravyn(middleware=[CORSMiddleware])
```

**Solution:** Provide proper configuration:

```python
# Correct
app = Ravyn(
    middleware=[
        CORSMiddleware,
        {
            "allow_origins": ["https://example.com"],
            "allow_methods": ["GET", "POST"],
            "allow_headers": ["*"]
        }
    ]
)
```

---

## Best Practices

### 1. Use Lifespan for Connections

```python
# Good - proper resource management
@asynccontextmanager
async def lifespan(app: Ravyn):
    # Setup
    app.state.redis = await redis.from_url("redis://localhost")
    app.state.db = await database.connect()
    
    yield
    
    # Cleanup
    await app.state.redis.close()
    await app.state.db.disconnect()
```

### 2. Store in app.state

```python
# Good - accessible throughout app
app.state.service = MyService()

# Access in handlers
@get("/data")
def get_data(request: Request) -> dict:
    return request.app.state.service.get_data()
```

### 3. Use Environment Variables

```python
# Good - configuration from environment
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/mydb")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
```

### 4. Handle Errors Gracefully

```python
# Good - error handling
@asynccontextmanager
async def lifespan(app: Ravyn):
    try:
        app.state.db = await connect_database()
        yield
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        if hasattr(app.state, 'db'):
            await app.state.db.disconnect()
```

---

## Integration Checklist

When integrating external packages:

- [ ] Install package: `pip install package-name`
- [ ] Initialize in lifespan (if needed)
- [ ] Store in `app.state` for global access
- [ ] Clean up resources on shutdown
- [ ] Handle errors gracefully
- [ ] Use environment variables for configuration
- [ ] Test integration thoroughly
- [ ] Document usage for your team

---

## Next Steps

Now that you understand external package integration, explore:

- [Lifespan Events](./lifespan-events.md) - Startup/shutdown logic
- [Middleware](./middleware/index.md) - Request/response processing
- [Extensions](./extensions.md) - Create reusable extensions
- [Dependencies](./dependencies.md) - Dependency injection
- [Application Settings](./application/settings.md) - Configuration
