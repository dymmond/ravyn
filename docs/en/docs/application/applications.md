# Ravyn

The `Ravyn` class is the core of your application. It handles routing, middleware, settings, and ties everything together.

## What You'll Learn

- Creating a Ravyn application
- Configuration options
- Application state management
- Accessing settings
- Lifecycle management

## Quick Start

```python
from ravyn import Ravyn, get

@get("/")
def homepage() -> dict:
    return {"message": "Hello, Ravyn!"}

app = Ravyn(
    routes=[Gateway(handler=homepage)],
    debug=True
)
```

---

## Creating an Application

### Minimal Application

```python
from ravyn import Ravyn

app = Ravyn()
```

!!! warning "Route Requirement"
    While the code above assumes a valid application, a `Ravyn` application **requires at least one route** to be useful. Without routes, it will return 404 for every request.
    
    Also, ensure your route handlers have **explicit return types** (e.g., `def handler() -> dict:`). This is crucial for data serialization and automatic documentation.

### With Routes

```python
from ravyn import Ravyn, Gateway, get

@get("/users")
def list_users() -> dict:
    return {"users": []}

app = Ravyn(
    routes=[Gateway(handler=list_users)]
)
```

### With Configuration

```python
from ravyn import Ravyn

app = Ravyn(
    title="My API",
    version="1.0.0",
    debug=True,
    routes=[...]
)
```

---

## Configuration Parameters

### Essential Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `routes` | list | List of Gateway, WebSocketGateway, Include |
| `debug` | bool | Enable debug mode (default: False) |
| `title` | str | API title for OpenAPI docs |
| `version` | str | API version for OpenAPI docs |

### OpenAPI Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | str | API description |
| `contact` | dict | Admin contact info |
| `license` | dict | License information |
| `servers` | list | Server configurations |
| `tags` | list | OpenAPI tags |

### Security & Middleware

| Parameter | Type | Description |
|-----------|------|-------------|
| `allowed_hosts` | list | Allowed host names |
| `cors_config` | CORSConfig | CORS configuration |
| `csrf_config` | CSRFConfig | CSRF protection |
| `session_config` | SessionConfig | Session management |
| `middleware` | list | Custom middleware |

### Advanced Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dependencies` | dict | Application-level dependencies |
| `interceptors` | list | Request interceptors |
| `permissions` | list | Permission classes |
| `exception_handlers` | dict | Custom exception handlers |
| `lifespan` | callable | Lifespan context manager |

---

## Complete Example

```python
from ravyn import Ravyn, Gateway, Include, get
from ravyn.config import CORSConfig

@get("/health")
def health_check() -> dict:
    return {"status": "healthy"}

@get("/users")
def list_users() -> dict:
    return {"users": []}

app = Ravyn(
    title="My API",
    version="1.0.0",
    description="A powerful API built with Ravyn",
    debug=True,
    
    # Routes
    routes=[
        Gateway(handler=health_check),
        Include("/api", routes=[
            Gateway(handler=list_users)
        ])
    ],
    
    # CORS
    cors_config=CORSConfig(
        allow_origins=["*"],
        allow_methods=["*"]
    ),
    
    # Security
    allowed_hosts=["localhost", "api.example.com"]
)
```

---

## Application State

Store arbitrary data on the application instance:

### Setting State

```python
from ravyn import Ravyn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Startup
    app.state.db = await connect_database()
    app.state.cache = RedisCache()
    
    yield
    
    # Shutdown
    await app.state.db.disconnect()
    await app.state.cache.close()

app = Ravyn(lifespan=lifespan)
```

### Accessing State

```python
from ravyn import get, Request

@get("/users")
async def get_users(request: Request) -> dict:
    # Access database from state
    db = request.app.state.db
    users = await db.fetch_all("SELECT * FROM users")
    return {"users": users}
```

---

## Accessing Settings

### From Request

```python
from ravyn import get, Request

@get("/config")
def get_config(request: Request) -> dict:
    settings = request.app.settings
    return {
        "debug": settings.debug,
        "title": settings.title
    }
```

### From Global Settings

```python
from ravyn.conf import settings

# Access anywhere
print(settings.debug)
print(settings.title)
```

### From conf Module

```python
from ravyn.conf.global_settings import RavynSettings

settings = RavynSettings()
print(settings.debug)
```

---

## Lifecycle Management

### Startup and Shutdown

```python
async def startup():
    print("Application starting...")
    # Initialize resources

async def shutdown():
    print("Application shutting down...")
    # Cleanup resources

app = Ravyn(
    on_startup=[startup],
    on_shutdown=[shutdown]
)
```

### Lifespan Context (Recommended)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: Ravyn):
    # Startup
    print("Starting up...")
    app.state.db = await connect_database()
    
    yield  # Application runs
    
    # Shutdown
    print("Shutting down...")
    await app.state.db.disconnect()

app = Ravyn(lifespan=lifespan)
```

!!! tip
    Use `lifespan` instead of `on_startup`/`on_shutdown` for better resource management.

---

## Common Patterns

### Pattern 1: API with Database

```python
from ravyn import Ravyn, get
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.db = await connect_database()
    yield
    await app.state.db.disconnect()

@get("/users")
async def get_users(request: Request) -> list:
    return await request.app.state.db.fetch_all("SELECT * FROM users")

app = Ravyn(
    routes=[Gateway(handler=get_users)],
    lifespan=lifespan
)
```

### Pattern 2: Microservice

```python
from ravyn import Ravyn, Include

app = Ravyn(
    title="User Service",
    version="1.0.0",
    routes=[
        Include("/api/v1", routes=v1_routes),
        Include("/api/v2", routes=v2_routes)
    ],
    cors_config=CORSConfig(allow_origins=["*"])
)
```

### Pattern 3: With Settings

```python
from ravyn import Ravyn, RavynSettings

class AppSettings(RavynSettings):
    title: str = "My API"
    debug: bool = True
    database_url: str = "postgresql://..."

app = Ravyn(settings_module=AppSettings)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Forgetting to Add Routes

**Problem:** No routes defined.

```python
# Wrong - no routes
app = Ravyn()
```

**Solution:** Add routes:

```python
# Correct
app = Ravyn(
    routes=[Gateway(handler=homepage)]
)
```

### Pitfall 2: Using Both Lifespan and on_startup

**Problem:** Mixing lifecycle approaches.

```python
# Wrong - using both
app = Ravyn(
    lifespan=lifespan,
    on_startup=[startup]  # Don't mix!
)
```

**Solution:** Use one or the other:

```python
# Correct
app = Ravyn(lifespan=lifespan)
```

### Pitfall 3: Accessing State Before Initialization

**Problem:** State not set up yet.

```python
# Wrong - state not initialized
app = Ravyn()
print(app.state.db)  # Error!
```

**Solution:** Initialize in lifespan:

```python
# Correct
@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.db = await connect_database()
    yield

app = Ravyn(lifespan=lifespan)
```

---

## Best Practices

### 1. Use Settings for Configuration

```python
# Good - settings-based
class AppSettings(RavynSettings):
    title: str = "My API"
    debug: bool = False

app = Ravyn(settings_module=AppSettings)
```

### 2. Organize Routes with Include

```python
# Good - organized routes
app = Ravyn(
    routes=[
        Include("/api/users", routes=user_routes),
        Include("/api/products", routes=product_routes)
    ]
)
```

### 3. Use Lifespan for Resources

```python
# Good - proper resource management
@asynccontextmanager
async def lifespan(app: Ravyn):
    app.state.db = await connect_database()
    yield
    await app.state.db.disconnect()

app = Ravyn(lifespan=lifespan)
```

---

## Next Steps

Now that you understand the Ravyn application class, explore:

- [Settings](./settings.md) - Application configuration
- [Routing](../routing/routes.md) - Route configuration
- [Middleware](../middleware/index.md) - Request processing
- [Lifespan Events](../lifespan-events.md) - Application lifecycle
