# Interceptors

Interceptors let you execute code before requests reach your route handlers. They're perfect for logging, data transformation, validation, and adding cross-cutting concerns without cluttering your handlers.

## What You'll Learn

- What interceptors are and when to use them
- Creating interceptors with RavynInterceptor
- Applying interceptors at different levels
- Using interceptors for logging and validation

## Quick Start

```python
from ravyn import Ravyn, Gateway, get, RavynInterceptor

class LoggingInterceptor(RavynInterceptor):
    async def intercept(self, request):
        print(f"Request to: {request.url.path}")
        # Request continues to handler after this

@get("/users")
def list_users() -> dict:
    return {"users": ["Alice", "Bob"]}

app = Ravyn(
    routes=[Gateway("/users", handler=list_users)],
    interceptors=[LoggingInterceptor]
)
```

Every request to `/users` logs the path before the handler executes.

---

## What Are Interceptors?

Interceptors capture requests **before** they reach handlers. They're inspired by Aspect-Oriented Programming (AOP) and let you:

- Add logging before requests
- Transform request data
- Validate authentication tokens
- Throw exceptions early
- Add caching logic
- Measure request timing

![Interceptors Flow](https://res.cloudinary.com/dymmond/image/upload/v1673451429/ravyn/resources/interceptors_tyohjr.png)

!!! warning
    Interceptors only work **before** handlers execute. They don't intercept responses. Use [middleware](./middleware/index.md) for request/response processing.

---

## Creating Interceptors

### Basic Interceptor

All interceptors should inherit from `RavynInterceptor` and implement `intercept()`:

```python
from ravyn import RavynInterceptor

class SimpleInterceptor(RavynInterceptor):
    async def intercept(self, request):
        # Your logic here
        print(f"Intercepted: {request.method} {request.url.path}")
```

### Import

```python
from ravyn import RavynInterceptor

# Or
from ravyn.core.interceptors.interceptor import RavynInterceptor
```

---

## Practical Examples

### Example 1: Request Logging

```python
from ravyn import RavynInterceptor
import logging

logger = logging.getLogger(__name__)

class RequestLogInterceptor(RavynInterceptor):
    async def intercept(self, request):
        logger.info(
            f"{request.method} {request.url.path} "
            f"from {request.client.host}"
        )
```

### Example 2: Header Validation

```python
from ravyn import RavynInterceptor
from ravyn.exceptions import NotAuthorized

class APIKeyInterceptor(RavynInterceptor):
    async def intercept(self, request):
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            raise NotAuthorized("API key required")
        
        if not self.validate_api_key(api_key):
            raise NotAuthorized("Invalid API key")
    
    def validate_api_key(self, key: str) -> bool:
        # Your validation logic
        return key in ["valid-key-1", "valid-key-2"]
```

### Example 3: Request Timing

```python
from ravyn import RavynInterceptor
import time

class TimingInterceptor(RavynInterceptor):
    async def intercept(self, request):
        request.state.start_time = time.time()
        # Handler executes after this
        # Note: Can't measure total time here (no response interception)
```

### Example 4: Data Transformation

```python
from ravyn import RavynInterceptor

class NormalizeDataInterceptor(RavynInterceptor):
    async def intercept(self, request):
        # Modify request before handler
        if hasattr(request.state, "user_input"):
            request.state.user_input = request.state.user_input.strip().lower()
```

---

## Applying Interceptors at Different Levels

Interceptors work at multiple levels in Ravyn's hierarchy.

### Application Level

Apply to all routes:

```python
from ravyn import Ravyn

app = Ravyn(
    routes=[...],
    interceptors=[LoggingInterceptor, APIKeyInterceptor]
)
```

### Gateway Level

Apply to specific routes:

```python
from ravyn import Gateway, get

@get()
def protected_route() -> dict:
    return {"data": "sensitive"}

app = Ravyn(routes=[
    Gateway(
        "/protected",
        handler=protected_route,
        interceptors=[APIKeyInterceptor]
    )
])
```

### Include Level

Apply to groups of routes:

```python
from ravyn import Include

app = Ravyn(routes=[
    Include(
        "/api",
        namespace="myapp.api.urls",
        interceptors=[LoggingInterceptor, APIKeyInterceptor]
    )
])
```

### Multiple Levels

Interceptors execute from parent to child:

```python
from ravyn import Ravyn, Include, Gateway

# Execution order: App → Include → Gateway → Handler
app = Ravyn(
    routes=[
        Include(
            "/api",
            interceptors=[LoggingInterceptor],
            routes=[
                Gateway(
                    "/users",
                    handler=list_users,
                    interceptors=[APIKeyInterceptor]
                )
            ]
        )
    ],
    interceptors=[TimingInterceptor]
)

# Order: TimingInterceptor → LoggingInterceptor → APIKeyInterceptor → Handler
```

---

## Interceptors with ChildRavyn

ChildRavyn applications have isolated interceptors:

```python
from ravyn import Ravyn, ChildRavyn, Include

class ParentInterceptor(RavynInterceptor):
    async def intercept(self, request):
        print("Parent interceptor")

class ChildInterceptor(RavynInterceptor):
    async def intercept(self, request):
        print("Child interceptor")

child_app = ChildRavyn(
    routes=[...],
    interceptors=[ChildInterceptor]
)

app = Ravyn(
    routes=[Include("/child", app=child_app)],
    interceptors=[ParentInterceptor]
)

# Requests to /child/* run: ParentInterceptor → ChildInterceptor → Handler
```

---

## Interceptors in Settings

Keep your code clean by defining interceptors in settings:

```python
# settings.py
from ravyn import RavynSettings

class AppSettings(RavynSettings):
    @property
    def interceptors(self):
        return [
            "myapp.interceptors.LoggingInterceptor",
            "myapp.interceptors.APIKeyInterceptor"
        ]
```

```python
# app.py
from ravyn import Ravyn

app = Ravyn()  # Interceptors loaded from settings
```

Run with settings:

```shell
# MacOS/Linux
RAVYN_SETTINGS_MODULE='settings.AppSettings' uvicorn app:app

# Windows
$env:RAVYN_SETTINGS_MODULE="settings.AppSettings"; uvicorn app:app
```

---

## Custom Interceptor (Without RavynInterceptor)

You can create interceptors without inheriting from `RavynInterceptor`, but it's **not recommended**:

```python
class CustomInterceptor:
    async def intercept(self, request):
        print("Custom interceptor")
```

!!! tip
    Always use `RavynInterceptor` as it implements the `InterceptorProtocol` correctly and provides better type safety.

---

## Common Pitfalls & Fixes

### Pitfall 1: Trying to Intercept Responses

**Problem:** Interceptors only work on requests, not responses.

```python
# Won't work - can't intercept response
class ResponseInterceptor(RavynInterceptor):
    async def intercept(self, request):
        # Can't access response here!
        pass
```

**Solution:** Use middleware for response processing:

```python
# Use middleware instead
from lilya.middleware import DefineMiddleware

class ResponseMiddleware:
    async def __call__(self, request, call_next):
        response = await call_next(request)
        # Process response here
        return response

app = Ravyn(
    middleware=[DefineMiddleware(ResponseMiddleware)]
)
```

### Pitfall 2: Using Interceptors on Handlers

**Problem:** Interceptors don't work directly on handler decorators.

```python
# Won't work
@get("/users", interceptors=[LoggingInterceptor])  # Not supported
def list_users() -> dict:
    return {"users": []}
```

**Solution:** Use Gateway, Include, or application level:

```python
# Use Gateway
app = Ravyn(routes=[
    Gateway(
        "/users",
        handler=list_users,
        interceptors=[LoggingInterceptor]
    )
])
```

### Pitfall 3: Forgetting Async

**Problem:** Interceptor method is not async.

```python
# Missing async
class MyInterceptor(RavynInterceptor):
    def intercept(self, request):  # Should be async!
        print("Intercepted")
```

**Solution:** Always use `async def`:

```python
# Correct
class MyInterceptor(RavynInterceptor):
    async def intercept(self, request):
        print("Intercepted")
```

### Pitfall 4: Modifying Request Incorrectly

**Problem:** Trying to modify immutable request properties.

```python
# Can't modify request.url directly
class BadInterceptor(RavynInterceptor):
    async def intercept(self, request):
        request.url.path = "/new-path"  # Won't work!
```

**Solution:** Use `request.state` for custom data:

```python
# Use request.state
class GoodInterceptor(RavynInterceptor):
    async def intercept(self, request):
        request.state.custom_data = "value"
        # Access in handler via request.state.custom_data
```

---

## When to Use Interceptors vs Middleware

| Feature | Interceptors | Middleware |
|---------|-------------|------------|
| **Timing** | Before handler only | Before & after handler |
| **Scope** | Specific routes/levels | All requests |
| **Response Access** | No | Yes |
| **Granular Control** | Yes (per route) | No (global) |
| **Use Case** | Route-specific logic | Cross-cutting concerns |

**Use Interceptors for:**
- Route-specific validation
- Logging specific endpoints
- Pre-processing for certain routes

**Use Middleware for:**
- Authentication (all routes)
- Response modification
- CORS headers
- Request/response logging

---

## Next Steps

Now that you understand interceptors, explore:

- [Middleware](./middleware/index.md) - Request/response processing
- [Exception Handlers](./exception-handlers.md) - Handle errors
- [Permissions](./permissions/index.md) - Access control
- [Application Levels](./application/levels.md) - Understand hierarchy
- [API Reference](./references/interceptors.md) - Complete interceptor reference
