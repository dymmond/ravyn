# Context

The `Context` object gives you access to handler metadata, request information, and application settings within your route handlers. It's a convenient way to access everything you need without passing multiple parameters.

## What You'll Learn

- What the Context object provides
- How to use Context in handlers
- Accessing request, settings, and handler information
- When to use Context vs Request

## Quick Start

```python
from ravyn import Ravyn, Context, get

@get("/users/{id}")
def get_user(context: Context, id: str) -> dict:
    # Access request information
    host = context.request.client.host
    
    # Access application settings
    app_name = context.settings.app_name
    
    # Add custom data to context
    context.add_to_context("user_id", id)
    
    # Get all context data
    data = context.get_context_data()
    
    return {
        "user_id": id,
        "host": host,
        "app_name": app_name,
        "context": data
    }

app = Ravyn()
app.add_route(get_user)
```

---

## What is Context?

`Context` is a special object available **only in handlers** that provides:

1. **Request object** - Access to the current HTTP request
2. **Application settings** - Your app's configuration
3. **Handler information** - Metadata about the current handler
4. **Custom context data** - Store and retrieve handler-specific data

### Importing Context

```python
from ravyn import Context
```

**API Reference:** See the [Context Reference](./references/context.md) for all available methods and properties.

---

## Using Context in Handlers

### Basic Usage

```python
from ravyn import Ravyn, Context, get

@get("/info")
def handler_info(context: Context) -> dict:
    return {
        "path": context.request.url.path,
        "method": context.request.method,
        "app_name": context.settings.app_name
    }

app = Ravyn()
app.add_route(handler_info)
```

### Context vs Request

You can use `Context` instead of `Request` since it includes the request:

```python
from ravyn import Context, Request, get

# Option 1: Using both (redundant)
@get("/users")
def with_both(request: Request, context: Context) -> dict:
    host1 = request.client.host  # Direct access
    host2 = context.request.client.host  # Via context
    return {"host": host1}

# Option 2: Using only Context (recommended)
@get("/users")
def with_context_only(context: Context) -> dict:
    host = context.request.client.host  # Access request via context
    return {"host": host}
```

!!! tip
    Use `Context` when you need request + settings + handler info. Use `Request` when you only need request data.

---

## Context Properties

### context.request

Access the current HTTP request:

```python
from ravyn import Context, get

@get("/request-info")
def request_info(context: Context) -> dict:
    return {
        "method": context.request.method,
        "path": context.request.url.path,
        "headers": dict(context.request.headers),
        "client_host": context.request.client.host
    }
```

### context.settings

Access application settings:

```python
from ravyn import Context, get

@get("/app-info")
def app_info(context: Context) -> dict:
    return {
        "app_name": context.settings.app_name,
        "debug": context.settings.debug,
        "environment": context.settings.environment
    }
```

### context.handler

Access handler metadata:

```python
from ravyn import Context, get

@get("/handler-info")
def handler_info(context: Context) -> dict:
    return {
        "handler_name": context.handler.fn.__name__,
        "path": context.handler.path,
        "methods": context.handler.methods
    }
```

---

## Managing Context Data

### Adding Data to Context

```python
from ravyn import Context, get

@get("/users/{user_id}")
def get_user(context: Context, user_id: str) -> dict:
    # Add data to context
    context.add_to_context("user_id", user_id)
    context.add_to_context("processed", True)
    
    # Retrieve all context data
    data = context.get_context_data()
    
    return data
```

### Getting Context Data

```python
from ravyn import Context, get

@get("/process")
def process_data(context: Context) -> dict:
    # Add multiple pieces of data
    context.add_to_context("step1", "complete")
    context.add_to_context("step2", "in_progress")
    context.add_to_context("timestamp", "2024-01-01T12:00:00")
    
    # Get all context data as dict
    all_data = context.get_context_data()
    
    return {
        "context_data": all_data,
        "total_items": len(all_data)
    }
```

---

## Practical Examples

### Example 1: Logging with Context

```python
from ravyn import Context, get
import logging

logger = logging.getLogger(__name__)

@get("/api/users/{user_id}")
def get_user(context: Context, user_id: str) -> dict:
    logger.info(
        f"Handler: {context.handler.fn.__name__}, "
        f"Path: {context.request.url.path}, "
        f"Client: {context.request.client.host}"
    )
    
    return {"user_id": user_id}
```

### Example 2: Conditional Logic Based on Settings

```python
from ravyn import Context, get

@get("/features")
def features(context: Context) -> dict:
    features_enabled = []
    
    if context.settings.debug:
        features_enabled.append("debug_mode")
    
    if hasattr(context.settings, 'feature_beta'):
        if context.settings.feature_beta:
            features_enabled.append("beta_features")
    
    return {"enabled_features": features_enabled}
```

### Example 3: Building Audit Trail

```python
from ravyn import Context, post
from datetime import datetime

@post("/api/actions")
async def track_action(context: Context, action: str) -> dict:
    audit_data = {
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "user_ip": context.request.client.host,
        "endpoint": context.request.url.path,
        "method": context.request.method,
        "handler": context.handler.fn.__name__
    }
    
    # Store in context for middleware to process
    context.add_to_context("audit", audit_data)
    
    return {"status": "tracked", "audit": audit_data}
```

---

## When to Use Context

### Use Context When:

You need access to **multiple** of these:

- Request information
- Application settings
- Handler metadata

You want to **store custom data** during request processing

You're building **middleware** that needs handler information

### Use Request When:

You **only** need request data (headers, body, params)

You want **simpler, more explicit** code

### Example Comparison

```python
from ravyn import Context, Request, get

# Use Request - simple and clear
@get("/simple")
def simple_handler(request: Request) -> dict:
    return {"path": request.url.path}

# Use Context - need multiple pieces of information
@get("/complex")
def complex_handler(context: Context) -> dict:
    return {
        "path": context.request.url.path,
        "app_name": context.settings.app_name,
        "handler": context.handler.fn.__name__
    }
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Using Context Outside Handlers

**Problem:** Context is only available in handlers.

```python
# Wrong - Context not available in dependencies
def get_database(context: Context):  # Won't work!
    return {"db": "connection"}
```

**Solution:** Use Context only in handlers, use Request in dependencies:

```python
# Correct
from ravyn import Request

def get_database(request: Request):
    return {"db": "connection"}
```

### Pitfall 2: Forgetting to Import Context

**Problem:** `NameError: name 'Context' is not defined`

```python
# Wrong
@get("/test")
def handler(context: Context):  # Context not imported
    return {}
```

**Solution:** Import Context from ravyn:

```python
# Correct
from ravyn import Context, get

@get("/test")
def handler(context: Context):
    return {}
```

### Pitfall 3: Passing Both Request and Context Unnecessarily

**Problem:** Redundant parameters.

```python
# Redundant - context already includes request
@get("/test")
def handler(request: Request, context: Context):
    host1 = request.client.host
    host2 = context.request.client.host  # Same thing!
    return {"host": host1}
```

**Solution:** Use only Context if you need both:

```python
# Correct
@get("/test")
def handler(context: Context):
    host = context.request.client.host
    app_name = context.settings.app_name
    return {"host": host, "app": app_name}
```

---

## Context Methods Reference

| Method | Description | Returns |
|--------|-------------|---------|
| `context.add_to_context(key, value)` | Add data to context | `None` |
| `context.get_context_data()` | Get all context data | `dict` |
| `context.request` | Access request object | `Request` |
| `context.settings` | Access app settings | `RavynSettings` |
| `context.handler` | Access handler metadata | `Handler` |

---

## Next Steps

Now that you understand Context, explore:

- [Requests](./requests.md) - Working with HTTP requests
- [Application Settings](./application/settings.md) - Configure your application
- [Handlers](./routing/handlers.md) - Different handler types
- [Middleware](./middleware/index.md) - Process requests with middleware
- [Context Reference](./references/context.md) - Full API documentation
