# Extensions

Extensions let you create reusable, pluggable components that can be hooked into any Ravyn application. Think of them as self-contained modules that add functionality without modifying your core application code.

## What You'll Learn

- What extensions are and why they're useful
- Creating custom extensions
- Using the Pluggable system
- Hooking extensions into your app
- Extension lifecycle management

## Quick Start

```python
from ravyn import Ravyn
from ravyn.extensions import Extension, Pluggable

# Create an extension
class DatabaseExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # This runs when the extension is loaded
        app.state.db = connect_database()
        print("Database extension loaded!")

# Use the extension
app = Ravyn(
    extensions={
        "database": Pluggable(DatabaseExtension)
    }
)

# Access in handlers
@app.get("/users")
async def get_users(request: Request) -> dict:
    db = request.app.state.db
    users = await db.fetch_all("SELECT * FROM users")
    return {"users": users}
```

---

## Why Use Extensions?

### Benefits:

- **Reusability** - Write once, use in multiple apps

- **Modularity** - Keep functionality isolated and organized

- **Maintainability** - Changes in one place

- **Shareability** - Distribute as packages

- **Clean Code** - Separate concerns from main app

### Perfect For:

- Database connections
- Authentication systems
- Logging configurations
- Monitoring integrations
- Custom middleware
- Third-party service integrations

---

## Extension vs ChildRavyn

| Feature | Extension | ChildRavyn |
|---------|-----------|------------|
| **Purpose** | Add functionality | Mount sub-application |
| **Use Case** | Database, auth, logging | API versioning, modules |
| **Lifecycle** | Runs on app startup | Independent ASGI app |
| **Access** | Via `app.state` | Via routing |

!!! info
    Extensions and ChildRavyn serve different purposes. Use extensions for shared functionality, ChildRavyn for sub-applications.

---

## Creating Extensions

### Basic Extension

```python
from ravyn import Ravyn
from ravyn.extensions import Extension

class MyExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        """
        This method is called when the extension is loaded.
        
        Args:
            app: The Ravyn application instance
            **kwargs: Additional parameters passed during registration
        """
        # Your initialization logic here
        app.state.my_service = MyService()
        print("MyExtension loaded!")
```

### Extension with Configuration

```python
class CacheExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # Get configuration from kwargs
        cache_url = kwargs.get("cache_url", "redis://localhost")
        ttl = kwargs.get("ttl", 3600)
        
        # Initialize cache
        app.state.cache = RedisCache(cache_url, ttl=ttl)
        print(f"Cache extension loaded with TTL={ttl}")
```

---

## The Pluggable System

`Pluggable` wraps your extension and manages its lifecycle.

### Using Pluggable

```python
from ravyn import Ravyn
from ravyn.extensions import Pluggable

app = Ravyn(
    extensions={
        "cache": Pluggable(CacheExtension, cache_url="redis://localhost", ttl=7200)
    }
)
```

### How It Works

1. **Registration** - Extension added to `extensions` dict
2. **Initialization** - Ravyn creates Pluggable wrapper
3. **Execution** - `extend()` method called on startup
4. **Access** - Extension available via `app.extensions`

---

## Hooking Extensions

### Method 1: Via Application Instance (Automatic)

```python
from ravyn import Ravyn
from ravyn.extensions import Pluggable

app = Ravyn(
    extensions={
        "database": Pluggable(DatabaseExtension),
        "cache": Pluggable(CacheExtension, ttl=3600),
        "auth": Pluggable(AuthExtension)
    }
)

# Extensions automatically loaded on startup
# Access via app.extensions
print(app.extensions["database"])
```

### Method 2: Via Settings

```python
from ravyn import RavynSettings

class Settings(RavynSettings):
    @property
    def extensions(self):
        return {
            "database": Pluggable(DatabaseExtension),
            "cache": Pluggable(CacheExtension, ttl=3600)
        }

app = Ravyn(settings_module=Settings)
```

### Method 3: Manual Registration

```python
from ravyn import Ravyn

app = Ravyn()

# Register extension manually
extension = MyExtension()
app.add_extension("my_ext", extension)

# Or with Pluggable
app.add_extension("my_ext", Pluggable(MyExtension))
```

---

## Practical Examples

### Example 1: Database Extension

```python
from ravyn import Ravyn
from ravyn.extensions import Extension
import databases

class DatabaseExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # Get database URL from kwargs or environment
        db_url = kwargs.get("database_url", "postgresql://localhost/mydb")
        
        # Create database connection
        database = databases.Database(db_url)
        
        # Store in app state
        app.state.db = database
        
        # Add startup/shutdown handlers
        async def connect():
            await app.state.db.connect()
            print("Database connected")
        
        async def disconnect():
            await app.state.db.disconnect()
            print("Database disconnected")
        
        app.on_startup.append(connect)
        app.on_shutdown.append(disconnect)

# Use the extension
app = Ravyn(
    extensions={
        "database": Pluggable(
            DatabaseExtension,
            database_url="postgresql://localhost/mydb"
        )
    }
)

# Access in handlers
@app.get("/users")
async def get_users(request: Request) -> dict:
    users = await request.app.state.db.fetch_all("SELECT * FROM users")
    return {"users": users}
```

### Example 2: Logging Extension

```python
from ravyn.extensions import Extension
import logging

class LoggingExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # Configure logging
        log_level = kwargs.get("log_level", "INFO")
        log_format = kwargs.get("log_format", "%(asctime)s - %(message)s")
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format
        )
        
        # Store logger in app state
        app.state.logger = logging.getLogger("ravyn_app")
        
        print(f"Logging configured at {log_level} level")

# Use it
app = Ravyn(
    extensions={
        "logging": Pluggable(LoggingExtension, log_level="DEBUG")
    }
)

@app.get("/test")
async def test(request: Request) -> dict:
    request.app.state.logger.info("Test endpoint called")
    return {"status": "ok"}
```

### Example 3: Authentication Extension

```python
from ravyn.extensions import Extension

class AuthExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # Get secret key
        secret_key = kwargs.get("secret_key", "default-secret")
        
        # Create auth service
        from myapp.auth import AuthService
        app.state.auth = AuthService(secret_key=secret_key)
        
        # Add authentication middleware
        from myapp.middleware import AuthMiddleware
        app.user_middleware.append(AuthMiddleware)
        
        print("Authentication extension loaded")

app = Ravyn(
    extensions={
        "auth": Pluggable(AuthExtension, secret_key="my-secret-key")
    }
)
```

---

## Extension Ordering

Sometimes extensions depend on each other. Use `ensure_extension()` to control order:

```python
class CacheExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # Ensure database extension is loaded first
        app.extensions.ensure_extension("database")
        
        # Now we can use the database
        db = app.state.db
        app.state.cache = Cache(db)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Not Implementing extend()

**Problem:** Missing required `extend()` method.

```python
# Wrong - missing extend method
class MyExtension(Extension):
    pass  # No extend() method!
```

**Solution:** Implement `extend()`:

```python
# Correct
class MyExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        # Your initialization logic
        pass
```

### Pitfall 2: Not Storing in app.state

**Problem:** Can't access extension resources in handlers.

```python
# Wrong - local variable
class DatabaseExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        db = connect_database()  # Local variable, lost after extend()
```

**Solution:** Store in `app.state`:

```python
# Correct
class DatabaseExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        app.state.db = connect_database()  # Accessible everywhere
```

### Pitfall 3: Using Both Extension and Pluggable

**Problem:** Confusing Extension with Pluggable.

```python
# Wrong - mixing both
app = Ravyn(
    extensions={
        "db": DatabaseExtension()  # Should use Pluggable
    }
)
```

**Solution:** Use Pluggable wrapper:

```python
# Correct
app = Ravyn(
    extensions={
        "db": Pluggable(DatabaseExtension)
    }
)
```

### Pitfall 4: Extension Order Issues

**Problem:** Extension depends on another that isn't loaded yet.

```python
# Wrong - cache needs database but database loads after
app = Ravyn(
    extensions={
        "cache": Pluggable(CacheExtension),  # Needs database
        "database": Pluggable(DatabaseExtension)
    }
)
```

**Solution:** Use `ensure_extension()`:

```python
# Correct
class CacheExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        app.extensions.ensure_extension("database")
        # Now database is guaranteed to be loaded
        app.state.cache = Cache(app.state.db)
```

---

## Best Practices

### 1. Use Descriptive Names

```python
# Good
extensions={
    "database": Pluggable(DatabaseExtension),
    "cache": Pluggable(CacheExtension),
    "auth": Pluggable(AuthExtension)
}

# Bad
extensions={
    "ext1": Pluggable(DatabaseExtension),
    "thing": Pluggable(CacheExtension)
}
```

### 2. Accept Configuration via kwargs

```python
# Good - configurable
class MyExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        url = kwargs.get("url", "default")
        timeout = kwargs.get("timeout", 30)
        # Use configuration
```

### 3. Clean Up Resources

```python
# Good - proper cleanup
class DatabaseExtension(Extension):
    def extend(self, app: Ravyn, **kwargs):
        app.state.db = connect_database()
        
        async def cleanup():
            await app.state.db.disconnect()
        
        app.on_shutdown.append(cleanup)
```

---

## Standalone Extensions

You can create extensions without inheriting from `Extension` by implementing the protocol:

```python
class MyStandaloneExtension:
    def extend(self, app: Ravyn, **kwargs):
        # Your logic
        app.state.my_service = MyService()

# Works the same way
app = Ravyn(
    extensions={
        "my_ext": Pluggable(MyStandaloneExtension)
    }
)
```

---

## Next Steps

Now that you understand extensions, explore:

- [Lifespan Events](./lifespan-events.md) - Application lifecycle
- [Dependencies](./dependencies.md) - Dependency injection
- [Middleware](./middleware/index.md) - Request processing
- [Application Settings](./application/settings.md) - Configuration
