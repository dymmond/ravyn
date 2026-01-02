# WSGI

Mount WSGI applications (Flask, Django, etc.) inside your Ravyn app. Perfect for gradual migrations or integrating legacy systems.

## What You'll Learn

- What WSGI is and when to use it
- Mounting WSGI apps in Ravyn
- Migrating from WSGI to ASGI
- Common integration patterns
- Performance considerations

## Quick Start

```python
from ravyn import Ravyn
from flask import Flask

# Your existing Flask app
flask_app = Flask(__name__)

@flask_app.route("/hello")
def hello():
    return {"message": "Hello from Flask!"}

# Mount in Ravyn
from ravyn.middleware.wsgi import WSGIMiddleware

app = Ravyn(
    routes=[
        Mount("/legacy", app=WSGIMiddleware(flask_app))
    ]
)

# /legacy/hello → Flask handles it
# Other routes → Ravyn handles them
```

---

## Why Mount WSGI Apps?

### Use Cases:

- **Gradual Migration** - Migrate from Flask/Django to Ravyn incrementally

- **Legacy Integration** - Keep old WSGI apps running alongside new code

- **Third-Party Apps** - Integrate existing WSGI applications

- **Backwards Compatibility** - Support legacy endpoints during transition

### When to Use:

- Migrating from Flask, Django, or other WSGI frameworks
- Need to maintain legacy endpoints
- Integrating third-party WSGI applications
- Gradual modernization of codebase

---

## WSGI vs ASGI

| Feature | WSGI | ASGI |
|---------|------|------|
| **Concurrency** | Synchronous | Async/await |
| **WebSockets** | No | Yes |
| **HTTP/2** | No | Yes |
| **Performance** | Good | Excellent |
| **Frameworks** | Flask, Django | Ravyn, FastAPI |

!!! info
    WSGI apps run in a thread pool, which can impact performance. Consider migrating to ASGI for better concurrency.

---

## Mounting WSGI Applications

### Basic Mount

```python
from ravyn import Ravyn, Mount
from ravyn.middleware.wsgi import WSGIMiddleware
from flask import Flask

# Flask app
flask_app = Flask(__name__)

@flask_app.route("/api/users")
def users():
    return {"users": []}

# Mount in Ravyn
app = Ravyn(
    routes=[
        Mount("/flask", app=WSGIMiddleware(flask_app))
    ]
)

# /flask/api/users → Flask handles it
```

### Multiple WSGI Apps

```python
from ravyn import Ravyn, Mount
from ravyn.middleware.wsgi import WSGIMiddleware
from flask import Flask
from django.core.wsgi import get_wsgi_application

# Flask app
flask_app = Flask(__name__)

# Django app
django_app = get_wsgi_application()

# Mount both
app = Ravyn(
    routes=[
        Mount("/flask", app=WSGIMiddleware(flask_app)),
        Mount("/django", app=WSGIMiddleware(django_app))
    ]
)
```

---

## Flask Integration

### Complete Example

```python
from ravyn import Ravyn, Mount, get
from ravyn.middleware.wsgi import WSGIMiddleware
from flask import Flask, jsonify

# Existing Flask app
flask_app = Flask(__name__)

@flask_app.route("/legacy/users")
def get_users():
    return jsonify({"users": ["Alice", "Bob"]})

@flask_app.route("/legacy/products")
def get_products():
    return jsonify({"products": ["Product 1", "Product 2"]})

# New Ravyn endpoints
@get("/api/health")
def health() -> dict:
    return {"status": "healthy"}

# Combine them
app = Ravyn(
    routes=[
        Mount("/", app=WSGIMiddleware(flask_app)),  # Flask handles /legacy/*
        Gateway(handler=health)  # Ravyn handles /api/health
    ]
)
```

---

## Django Integration

### Basic Setup

```python
from ravyn import Ravyn, Mount
from ravyn.middleware.wsgi import WSGIMiddleware
import os
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# Get Django WSGI app
from django.core.wsgi import get_wsgi_application
django_app = get_wsgi_application()

# Mount in Ravyn
app = Ravyn(
    routes=[
        Mount("/admin", app=WSGIMiddleware(django_app))
    ]
)

# /admin/* → Django handles it
```

---

## Migration Strategies

### Strategy 1: Gradual Route Migration

```python
from ravyn import Ravyn, Mount, get
from ravyn.middleware.wsgi import WSGIMiddleware
from flask import Flask

flask_app = Flask(__name__)

# Old Flask routes (being phased out)
@flask_app.route("/old/users")
def old_users():
    return {"users": []}

# New Ravyn routes
@get("/api/users")
def new_users() -> dict:
    return {"users": [], "version": "v2"}

app = Ravyn(
    routes=[
        Mount("/old", app=WSGIMiddleware(flask_app)),  # Legacy
        Gateway(handler=new_users)  # New
    ]
)
```

### Strategy 2: Feature Flags

```python
import os
from ravyn import Ravyn, Mount, get
from ravyn.middleware.wsgi import WSGIMiddleware

USE_LEGACY = os.getenv("USE_LEGACY_API", "false") == "true"

if USE_LEGACY:
    # Mount legacy app
    app = Ravyn(
        routes=[Mount("/", app=WSGIMiddleware(legacy_app))]
    )
else:
    # Use new Ravyn app
    app = Ravyn(routes=[Gateway(handler=new_endpoint)])
```

---

## Performance Considerations

### Thread Pool Configuration

```python
from ravyn.middleware.wsgi import WSGIMiddleware

# Configure thread pool size
wsgi_middleware = WSGIMiddleware(
    flask_app,
    workers=10  # Number of worker threads
)

app = Ravyn(
    routes=[Mount("/legacy", app=wsgi_middleware)]
)
```

### Performance Tips

1. **Minimize WSGI Usage** - Migrate critical paths to ASGI first
2. **Use Caching** - Cache WSGI responses when possible
3. **Monitor Performance** - Track response times
4. **Gradual Migration** - Move high-traffic routes first

---

## Common Pitfalls & Fixes

### Pitfall 1: Path Conflicts

**Problem:** WSGI and ASGI routes conflict.

```python
# Wrong - both handle /api/users
flask_app.route("/api/users")
@get("/api/users")
```

**Solution:** Use different path prefixes:

```python
# Correct
Mount("/legacy", app=WSGIMiddleware(flask_app))  # /legacy/api/users
@get("/api/users")  # /api/users
```

### Pitfall 2: Missing Django Setup

**Problem:** Django not configured before mounting.

```python
# Wrong - Django not set up
django_app = get_wsgi_application()  # Error!
```

**Solution:** Configure Django first:

```python
# Correct
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

django_app = get_wsgi_application()
```

### Pitfall 3: Blocking Operations

**Problem:** WSGI app blocks async operations.

```python
# Wrong - WSGI blocks event loop
@flask_app.route("/slow")
def slow():
    time.sleep(10)  # Blocks!
    return {"done": True}
```

**Solution:** Use thread pool or migrate to async:

```python
# Correct - migrate to Ravyn
@get("/slow")
async def slow() -> dict:
    await asyncio.sleep(10)  # Non-blocking
    return {"done": True}
```

---

## Best Practices

### 1. Isolate Legacy Code

```python
# Good - clear separation
app = Ravyn(
    routes=[
        Mount("/legacy", app=WSGIMiddleware(old_app)),  # Legacy
        Include("/api", routes=new_routes)  # New
    ]
)
```

### 2. Document Migration Plan

```python
# Good - clear comments
app = Ravyn(
    routes=[
        # TODO: Migrate to /api/v2/users by Q2 2026
        Mount("/legacy", app=WSGIMiddleware(flask_app)),
        
        # New endpoints
        Include("/api/v2", routes=new_routes)
    ]
)
```

### 3. Monitor Performance

```python
# Good - add logging
import logging

logger = logging.getLogger(__name__)

wsgi_middleware = WSGIMiddleware(flask_app)

@app.on_event("startup")
async def log_wsgi_mount():
    logger.info("WSGI app mounted at /legacy")
```

---

## Testing WSGI Mounts

```python
from ravyn import Ravyn, Mount
from ravyn.middleware.wsgi import WSGIMiddleware
from ravyn import RavynTestClient
from flask import Flask

# Flask app
flask_app = Flask(__name__)

@flask_app.route("/hello")
def hello():
    return {"message": "Hello"}

# Ravyn app
app = Ravyn(
    routes=[Mount("/flask", app=WSGIMiddleware(flask_app))]
)

# Test
def test_wsgi_mount():
    with RavynTestClient(app) as client:
        response = client.get("/flask/hello")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello"}
```

---

## Next Steps

Now that you understand WSGI integration, explore:

- [Routing](./routing/routes.md) - Route configuration
- [Middleware](./middleware/index.md) - Request processing
- [Migration Guide](./migration.md) - Migrating to Ravyn
- [Testing](./testclient.md) - Test your application
