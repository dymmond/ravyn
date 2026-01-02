# Exceptions

Exceptions let you handle errors consistently across your application. Ravyn provides built-in exceptions for common scenarios and makes it easy to create custom ones.

## What You'll Learn

- Built-in Ravyn exceptions and when to use them
- Creating custom exceptions
- Raising exceptions with helpful error messages
- Using ValidationError for clean error responses

## Quick Start

```python
from ravyn import Ravyn, get
from ravyn.exceptions import NotFound, PermissionDenied

@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    user = find_user(user_id)  # Your database lookup
    
    if not user:
        raise NotFound("User not found")
    
    if not user.is_active:
        raise PermissionDenied("User account is inactive")
    
    return {"user": user}

app = Ravyn()
app.add_route(get_user)
```

When raised, these exceptions automatically return proper HTTP status codes and JSON responses.

---

## Built-In Exceptions

All Ravyn exceptions inherit from `HTTPException` and return JSON error responses.

### Common Exceptions

| Exception | Status Code | Use Case |
|-----------|-------------|----------|
| `NotFound` | 404 | Resource doesn't exist |
| `NotAuthenticated` | 401 | User not logged in |
| `NotAuthorized` | 401 | Authentication failed |
| `PermissionDenied` | 403 | User lacks permission |
| `ValidationError` | 400 | Invalid input data |
| `MethodNotAllowed` | 405 | Wrong HTTP method |
| `InternalServerError` | 500 | Server error |
| `ServiceUnavailable` | 503 | Service down |
| `ImproperlyConfigured` | 500 | Configuration error |

### Import Exceptions

```python
from ravyn.exceptions import (
    NotFound,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
    HTTPException
)
```

---

## Exception Details

### NotFound (404)

Raise when a resource doesn't exist:

```python
from ravyn import get
from ravyn.exceptions import NotFound

@get("/posts/{post_id}")
def get_post(post_id: int) -> dict:
    post = database.get_post(post_id)
    
    if not post:
        raise NotFound(f"Post {post_id} not found")
    
    return {"post": post}
```

### NotAuthenticated (401)

Raise when user needs to log in:

```python
from ravyn import get, Request
from ravyn.exceptions import NotAuthenticated

@get("/profile")
def get_profile(request: Request) -> dict:
    user = request.user  # From authentication middleware
    
    if not user:
        raise NotAuthenticated("Please log in to view your profile")
    
    return {"user": user}
```

### PermissionDenied (403)

Raise when user lacks permission:

```python
from ravyn import delete
from ravyn.exceptions import PermissionDenied

@delete("/posts/{post_id}")
def delete_post(post_id: int, user: User) -> dict:
    post = database.get_post(post_id)
    
    if post.author_id != user.id:
        raise PermissionDenied("You can only delete your own posts")
    
    database.delete(post)
    return {"deleted": True}
```

### ValidationError (400)

Special exception for clean validation error responses:

```python
from ravyn import post
from ravyn.exceptions import ValidationError
from pydantic import BaseModel, model_validator

class PasswordChange(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValidationError({"confirm_password": "Passwords do not match"})
        return self

@post("/change-password")
def change_password(data: PasswordChange) -> dict:
    return {"success": True}
```

**Response when validation fails:**

```json
{
  "detail": {
    "confirm_password": "Passwords do not match"
  }
}
```

### ValidationError Formats

`ValidationError` accepts multiple formats:

```python
from ravyn.exceptions import ValidationError

# String
raise ValidationError("Invalid input")

# Dict (recommended for field-specific errors)
raise ValidationError({"email": "Email already exists"})

# List
raise ValidationError(["Error 1", "Error 2"])

# Tuple
raise ValidationError(("Error 1", "Error 2"))

# Custom status code
raise ValidationError("Unauthorized", status_code=401)
```

### InternalServerError (500)

Used for server errors. Shows detailed traceback if `debug=True`:

```python
from ravyn import get
from ravyn.exceptions import InternalServerError

@get("/risky")
def risky_operation() -> dict:
    try:
        result = perform_complex_operation()
        return {"result": result}
    except Exception as e:
        raise InternalServerError(f"Operation failed: {str(e)}")
```

### ImproperlyConfigured (500)

Raised when application is misconfigured:

```python
from ravyn.exceptions import ImproperlyConfigured

if not settings.secret_key:
    raise ImproperlyConfigured("SECRET_KEY must be set in settings")
```

---

## Creating Custom Exceptions

Create exceptions for your specific use cases:

```python
from ravyn import HTTPException

class PaymentRequired(HTTPException):
    status_code = 402
    detail = "Payment required to access this resource"

class RateLimitExceeded(HTTPException):
    status_code = 429
    detail = "Too many requests"

class InvalidAPIKey(HTTPException):
    status_code = 401
    detail = "Invalid API key provided"
```

### Using Custom Exceptions

```python
from ravyn import get

@get("/premium-content")
def premium_content(user: User) -> dict:
    if not user.has_subscription:
        raise PaymentRequired("Subscribe to access premium content")
    
    return {"content": "Premium data"}

@get("/api/data")
def api_endpoint(api_key: str) -> dict:
    if not validate_api_key(api_key):
        raise InvalidAPIKey()
    
    return {"data": "..."}
```

---

## Exception Handlers

Handle exceptions globally with custom handlers. See [Exception Handlers](./exception-handlers.md) for details.

### Quick Example

```python
from ravyn import Ravyn
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
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Not Providing Helpful Messages

**Problem:** Generic error messages aren't helpful.

```python
# Not helpful
@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    user = find_user(user_id)
    if not user:
        raise NotFound()  # Generic message
```

**Solution:** Provide specific, actionable messages:

```python
# Helpful
@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    user = find_user(user_id)
    if not user:
        raise NotFound(f"User with ID {user_id} does not exist")
```

### Pitfall 2: Using Wrong Exception Type

**Problem:** Using NotAuthenticated when PermissionDenied is more appropriate.

```python
# Wrong exception type
@delete("/posts/{post_id}")
def delete_post(post_id: int, user: User) -> dict:
    post = get_post(post_id)
    if post.author_id != user.id:
        raise NotAuthenticated()  # User IS authenticated, just not authorized
```

**Solution:** Use the correct exception:

```python
# Correct exception type
@delete("/posts/{post_id}")
def delete_post(post_id: int, user: User) -> dict:
    post = get_post(post_id)
    if post.author_id != user.id:
        raise PermissionDenied("You can only delete your own posts")
```

### Pitfall 3: Catching Exceptions Without Re-Raising

**Problem:** Swallowing exceptions silently.

```python
# Exception swallowed
@get("/data")
def get_data() -> dict:
    try:
        data = fetch_from_api()
        return {"data": data}
    except Exception:
        return {}  # Error hidden from user!
```

**Solution:** Re-raise or return proper error:

```python
# Proper error handling
@get("/data")
def get_data() -> dict:
    try:
        data = fetch_from_api()
        return {"data": data}
    except ConnectionError as e:
        raise ServiceUnavailable(f"External API unavailable: {str(e)}")
    except Exception as e:
        raise InternalServerError(f"Failed to fetch data: {str(e)}")
```

### Pitfall 4: ValidationError with Wrong Format

**Problem:** Using ValidationError incorrectly.

```python
# Not structured for easy parsing
raise ValidationError("Email is invalid and password is too short")
```

**Solution:** Use dict format for field-specific errors:

```python
# Structured and parseable
raise ValidationError({
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
})
```

---

## Exception Response Format

All Ravyn exceptions return JSON in this format:

```json
{
  "detail": "Error message here"
}
```

For `ValidationError` with dict:

```json
{
  "detail": {
    "field_name": "Error message",
    "another_field": "Another error"
  }
}
```

---

## Best Practices

### 1. Be Specific

```python
# Vague
raise NotFound("Not found")

# Specific
raise NotFound(f"Product with SKU '{sku}' not found")
```

### 2. Use Appropriate Status Codes

```python
# Wrong status code
raise ValidationError("Unauthorized", status_code=500)

# Correct status code
raise NotAuthorized("Invalid credentials")
```

### 3. Provide Actionable Information

```python
# Not actionable
raise PermissionDenied("Access denied")

# Actionable
raise PermissionDenied("You need 'admin' role to perform this action")
```

---

## Next Steps

Now that you understand exceptions, explore:

- [Exception Handlers](./exception-handlers.md) - Custom exception handling
- [Permissions](./permissions/index.md) - Permission-based access control
- [Middleware](./middleware/index.md) - Request/response processing
- [Responses](./responses.md) - Different response types
- [API Reference](./references/exceptions.md) - Complete exception reference
