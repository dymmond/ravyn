# Exception Handlers

Exception handlers let you control how your application responds to errors. Instead of default error messages, you can return custom responses, log errors, or transform exceptions into user-friendly formats.

## What You'll Learn

- Creating custom exception handlers
- Applying handlers at different levels
- Handler priority and precedence
- Using built-in handlers
- Transforming errors into JSON

## Quick Start

```python
from ravyn import Ravyn, get
from ravyn.exceptions import NotFound
from ravyn.responses import JSONResponse

def handle_not_found(request, exc):
    return JSONResponse(
        {"error": "Resource not found", "detail": str(exc)},
        status_code=404
    )

app = Ravyn(
    exception_handlers={
        NotFound: handle_not_found
    }
)

@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    raise NotFound(f"User {user_id} not found")
    # Returns: {"error": "Resource not found", "detail": "User 123 not found"}
```

---

## Why Use Exception Handlers?

### Perfect For:

- **Custom Error Formats** - Return consistent error structures

- **Error Logging** - Log errors before returning response

- **User-Friendly Messages** - Transform technical errors

- **Error Tracking** - Send errors to monitoring services

- **Validation Errors** - Format validation errors consistently

---

## Creating Exception Handlers

Exception handlers are functions that take `request` and `exc` parameters:

```python
def my_handler(request, exc):
    # request: The current request
    # exc: The exception that was raised
    return JSONResponse({"error": str(exc)}, status_code=500)
```

### Basic Example

```python
from ravyn import Ravyn
from ravyn.exceptions import ValidationError
from ravyn.responses import JSONResponse

def validation_handler(request, exc):
    return JSONResponse(
        {
            "error": "Validation failed",
            "details": exc.detail
        },
        status_code=400
    )

app = Ravyn(
    exception_handlers={
        ValidationError: validation_handler
    }
)
```

---

## Exception Handler Levels

Exception handlers can be applied at multiple levels with clear precedence rules.

### Application Level

Handles exceptions across the entire app:

```python
from ravyn import Ravyn
from ravyn.exceptions import NotFound

def app_not_found_handler(request, exc):
    return JSONResponse({"error": "Not found at app level"}, status_code=404)

app = Ravyn(
    exception_handlers={
        NotFound: app_not_found_handler
    }
)
```

### Gateway Level

Overrides application-level handlers for specific routes:

```python
from ravyn import Ravyn, Gateway, get
from ravyn.exceptions import ValidationError

def gateway_validation_handler(request, exc):
    return JSONResponse({"error": "Gateway validation error"}, status_code=400)

@get("/users")
def list_users() -> dict:
    raise ValidationError("Invalid request")

app = Ravyn(routes=[
    Gateway(
        "/users",
        handler=list_users,
        exception_handlers={
            ValidationError: gateway_validation_handler
        }
    )
])
```

### Handler Level

Most specific—overrides all other handlers:

```python
from ravyn import get
from ravyn.exceptions import ValidationError

def handler_validation_handler(request, exc):
    return JSONResponse({"error": "Handler-specific error"}, status_code=400)

@get(
    "/users",
    exception_handlers={
        ValidationError: handler_validation_handler
    }
)
def list_users() -> dict:
    raise ValidationError("Error")
```

---

## Handler Precedence

When the same exception is handled at multiple levels, **the most specific handler wins**:

```
Handler Level (highest priority)
  ↓
Gateway Level
  ↓
Include Level
  ↓
Application Level (lowest priority)
```

### Example

```python
from ravyn import Ravyn, Gateway, get
from ravyn.exceptions import NotFound

# Application level
def app_handler(request, exc):
    return JSONResponse({"level": "app"}, status_code=404)

# Gateway level
def gateway_handler(request, exc):
    return JSONResponse({"level": "gateway"}, status_code=404)

# Handler level
def handler_handler(request, exc):
    return JSONResponse({"level": "handler"}, status_code=404)

@get(
    "/users/{id}",
    exception_handlers={NotFound: handler_handler}
)
def get_user(id: int) -> dict:
    raise NotFound("User not found")

app = Ravyn(
    routes=[
        Gateway(
            "/users/{id}",
            handler=get_user,
            exception_handlers={NotFound: gateway_handler}
        )
    ],
    exception_handlers={NotFound: app_handler}
)

# Result: Uses handler_handler (most specific)
```

---

## Built-In Exception Handlers

Ravyn provides ready-to-use handlers:

### value_error_handler

Converts `ValueError` to JSON:

```python
from ravyn import Ravyn
from ravyn.exception_handlers import value_error_handler

app = Ravyn(
    exception_handlers={
        ValueError: value_error_handler
    }
)

@app.get("/divide")
def divide(a: int, b: int) -> dict:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return {"result": a / b}

# GET /divide?a=10&b=0
# Returns: {"detail": "Cannot divide by zero"}
```

---

## Practical Examples

### Example 1: Error Logging

```python
from ravyn import Ravyn
from ravyn.exceptions import HTTPException
from ravyn.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def log_and_return_error(request, exc):
    # Log the error
    logger.error(
        f"Error on {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    # Return user-friendly response
    return JSONResponse(
        {"error": "An error occurred", "message": str(exc)},
        status_code=exc.status_code if hasattr(exc, 'status_code') else 500
    )

app = Ravyn(
    exception_handlers={
        HTTPException: log_and_return_error
    }
)
```

### Example 2: Validation Error Formatting

```python
from ravyn import Ravyn, post
from ravyn.exceptions import ValidationError
from ravyn.responses import JSONResponse
from pydantic import BaseModel, ValidationError as PydanticValidationError

def format_validation_errors(request, exc):
    if isinstance(exc.detail, dict):
        # Already formatted
        errors = exc.detail
    else:
        # Convert to dict
        errors = {"message": str(exc.detail)}
    
    return JSONResponse(
        {
            "error": "Validation failed",
            "fields": errors
        },
        status_code=400
    )

app = Ravyn(
    exception_handlers={
        ValidationError: format_validation_errors
    }
)

class User(BaseModel):
    name: str
    email: str

@post("/users")
def create_user(user: User) -> dict:
    return {"created": user.dict()}
```

### Example 3: Error Tracking Integration

```python
from ravyn import Ravyn
from ravyn.exceptions import HTTPException
from ravyn.responses import JSONResponse
import sentry_sdk

def track_and_handle_error(request, exc):
    # Send to Sentry
    sentry_sdk.capture_exception(exc)
    
    # Return response
    return JSONResponse(
        {
            "error": "Internal server error",
            "message": "This error has been logged"
        },
        status_code=500
    )

app = Ravyn(
    exception_handlers={
        Exception: track_and_handle_error
    }
)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Handler Doesn't Return Response

**Problem:** Exception handler doesn't return a response object.

```python
# Wrong - no return
def bad_handler(request, exc):
    print(f"Error: {exc}")
    # Missing return!
```

**Solution:** Always return a Response:

```python
# Correct
def good_handler(request, exc):
    print(f"Error: {exc}")
    return JSONResponse({"error": str(exc)}, status_code=500)
```

### Pitfall 2: Wrong Exception Type

**Problem:** Handler registered for wrong exception class.

```python
# Wrong - ValidationError won't catch NotFound
app = Ravyn(
    exception_handlers={
        ValidationError: my_handler
    }
)

@app.get("/users/{id}")
def get_user(id: int) -> dict:
    raise NotFound("User not found")  # Not caught!
```

**Solution:** Register handler for correct exception:

```python
# Correct
app = Ravyn(
    exception_handlers={
        NotFound: my_handler
    }
)
```

### Pitfall 3: Forgetting Request Parameter

**Problem:** Handler signature is wrong.

```python
# Wrong - missing request parameter
def bad_handler(exc):
    return JSONResponse({"error": str(exc)})
```

**Solution:** Include both request and exc:

```python
# Correct
def good_handler(request, exc):
    return JSONResponse({"error": str(exc)})
```

### Pitfall 4: Not Understanding Precedence

**Problem:** Expecting app-level handler but gateway-level takes precedence.

```python
# Confusing - which handler runs?
app = Ravyn(
    routes=[
        Gateway(
            "/users",
            handler=get_users,
            exception_handlers={NotFound: gateway_handler}
        )
    ],
    exception_handlers={NotFound: app_handler}
)
# gateway_handler wins (more specific)
```

**Solution:** Understand precedence: Handler > Gateway > Include > App

---

## Exception Handler Patterns

### Pattern 1: Consistent Error Format

```python
def standard_error_handler(request, exc):
    return JSONResponse(
        {
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "path": request.url.path
            }
        },
        status_code=getattr(exc, 'status_code', 500)
    )
```

### Pattern 2: Development vs Production

```python
from ravyn import RavynSettings

class Settings(RavynSettings):
    debug: bool = False
    
    @property
    def exception_handlers(self):
        if self.debug:
            # Detailed errors in development
            return {Exception: detailed_error_handler}
        else:
            # Generic errors in production
            return {Exception: generic_error_handler}
```

### Pattern 3: Multiple Exception Types

```python
from ravyn.exceptions import NotFound, PermissionDenied, ValidationError

def not_found_handler(request, exc):
    return JSONResponse({"error": "Not found"}, status_code=404)

def permission_handler(request, exc):
    return JSONResponse({"error": "Access denied"}, status_code=403)

def validation_handler(request, exc):
    return JSONResponse({"error": "Invalid data"}, status_code=400)

app = Ravyn(
    exception_handlers={
        NotFound: not_found_handler,
        PermissionDenied: permission_handler,
        ValidationError: validation_handler
    }
)
```

---

## Next Steps

Now that you understand exception handlers, explore:

- [Exceptions](./exceptions.md) - Built-in exception types
- [Responses](./responses.md) - Different response types
- [Middleware](./middleware/index.md) - Request/response processing
- [Application Levels](./application/levels.md) - Understanding hierarchy
- [Logging](./configurations/logging.md) - Configure logging
