# JWT Authentication Middleware

Imagine you're running a members-only club. Instead of checking IDs at every door, you give members a special wristband when they enter. This wristband proves they're allowed to be there, and staff can verify it instantly without checking the guest list every time.

JWT (JSON Web Tokens) work the same way. They're digital wristbands that prove a user is authenticated, eliminating the need to check credentials on every request.

## What You'll Learn

- How JWT authentication works with Mongoz
- Configuring the JWTAuthMiddleware
- Protecting routes with authentication
- Best practices for JWT security

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import JWTConfig
from ravyn.contrib.auth.mongoz.middleware import JWTAuthMiddleware
from accounts.documents import User

app = Ravyn(
    middleware=[
        JWTAuthMiddleware(
            config=JWTConfig(secret="your-secret-key"),
            user=User
        )
    ]
)
```

---

## JWTAuthMiddleware

This middleware extends the [BaseAuthMiddleware](../../middleware/index.md#baseauthmiddleware) and enables JWT-based authentication for your Mongoz documents.

```python
from ravyn.contrib.auth.mongoz.middleware import JWTAuthMiddleware
```

### How It Works

1. **User logs in** → Receives JWT token
2. **User makes request** → Includes token in `Authorization` header
3. **Middleware validates** → Checks token signature and expiration
4. **User injected** → `request.user` contains authenticated user
5. **Route handler** → Access user data directly

---

## Configuration

### Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `app` | ASGI | Any ASGI app instance (e.g., Ravyn) | Yes |
| `config` | JWTConfig | JWT configuration object | Yes |
| `user` | Type[Document] | User document class (not instance!) | Yes |

### JWTConfig

See [JWTConfig documentation](../../configurations/jwt.md) for complete configuration options.

---

## Usage Examples

### Via Settings (Recommended)

```python
{!> ../../../docs_src/databases/mongoz/jwt/settings.py!}
```

This approach centralizes configuration and makes it reusable across your application.

### Via Application Instantiation

```python
{!> ../../../docs_src/databases/mongoz/middleware/example1.py !}
```

Direct instantiation is useful for simple applications or testing.

### Via Custom Middleware

Override the middleware for advanced customization:

=== "Via app instance"

    ```python
    {!> ../../../docs_src/databases/mongoz/middleware/example2.py !}
    ```

=== "Via app settings"

    ```python
    {!> ../../../docs_src/databases/mongoz/middleware/example3.py !}
    ```

---

## Protecting Routes

### Automatic Protection

Once middleware is added, all routes under that middleware are protected:

```python
from ravyn import get, Request

@get("/profile")
async def get_profile(request: Request) -> dict:
    # request.user is automatically available
    return {
        "email": request.user.email,
        "name": request.user.first_name
    }
```

### Selective Protection

Apply middleware only to specific routes:

```python
from ravyn import Ravyn, Include, get
from ravyn.contrib.auth.mongoz.middleware import JWTAuthMiddleware

# Public routes (no auth)
@get("/")
async def home() -> dict:
    return {"message": "Welcome"}

# Protected routes
@get("/dashboard")
async def dashboard(request: Request) -> dict:
    return {"user": request.user.email}

app = Ravyn(routes=[
    Gateway(handler=home),  # No middleware
    Include(
        routes=[Gateway(handler=dashboard)],
        middleware=[JWTAuthMiddleware(...)]  # Auth required
    )
])
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Missing Authorization Header

**Problem:** Token not included in request headers.

```javascript
// Wrong - no token
fetch('/api/profile', {
    method: 'GET'
});
```

**Solution:** Include token in Authorization header:

```javascript
// Correct
fetch('/api/profile', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

### Pitfall 2: Using User Instance Instead of Class

**Problem:** Passing user instance instead of class.

```python
# Wrong
user = await User.query.get(id="507f1f77bcf86cd799439011")
JWTAuthMiddleware(config=config, user=user)  # Error!
```

**Solution:** Pass the class, not an instance:

```python
# Correct
JWTAuthMiddleware(config=config, user=User)
```

### Pitfall 3: Expired Tokens

**Problem:** Tokens expire and users get 401 errors.

**Solution:** Implement token refresh:

```python
# Check token expiration
# Refresh before expiry
# See JWT Config docs for refresh token implementation
```

[See refresh token example →](../../configurations/jwt.md#the-claims)

---

## Best Practices

### 1. Use Environment Variables for Secrets

```python
import os
from ravyn.config import JWTConfig

config = JWTConfig(
    secret=os.getenv("JWT_SECRET"),
    access_token_lifetime=3600  # 1 hour
)
```

### 2. Set Appropriate Token Lifetimes

```python
config = JWTConfig(
    secret="your-secret",
    access_token_lifetime=900,      # 15 minutes
    refresh_token_lifetime=604800   # 7 days
)
```

### 3. Use HTTPS in Production

JWT tokens should always be transmitted over HTTPS to prevent interception.

### 4. Implement Token Refresh

Provide a refresh endpoint to get new tokens without re-authentication:

[Token refresh implementation →](../../configurations/jwt.md#the-claims)

---

{!> ../../../docs_src/_shared/databases_important_note.md !}

---

## Learn More

- [JWTConfig Reference](../../configurations/jwt.md) - Complete JWT configuration
- [User Documents](./documents.md) - User document documentation
- [Complete Example](./example.md) - Full authentication tutorial
- [OWASP JWT Guide](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) - Security best practices

---

## Next Steps

- [User Documents](./documents.md) - Set up user authentication
- [Complete Example](./example.md) - Build a full auth system
- [JWTConfig](../../configurations/jwt.md) - Advanced JWT configuration
