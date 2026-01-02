# SessionConfig

Think of sessions like hotel key cards. When you check in (log in), the hotel gives you a key card programmed for your room. The card doesn't contain your personal information - it's just a reference number. The hotel's system knows which room that card number unlocks.

Sessions work the same way:

- **Client gets a session ID** (the key card)
- **Server stores session data** (the hotel's database)
- **Each request includes the session ID** (showing your key card)
- **Server looks up your data** (checking which room you have)

When you check out (log out), the key card stops working.

Configure session management for your Ravyn application to maintain user state across requests.

## What You'll Learn

- What HTTP sessions are
- Configuring sessions in Ravyn
- Using sessions in your app
- Security best practices

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import SessionConfig

app = Ravyn(
    session_config=SessionConfig(
        secret_key="your-secret-key-change-in-production"
    )
)
```

---

## What are Sessions?

**HTTP sessions** allow you to store user-specific data across multiple requests. Perfect for:

- **User Authentication** - Keep users logged in

- **Shopping Carts** - Store cart items

- **User Preferences** - Remember settings

- **Form Data** - Multi-step forms

---

## Basic Configuration

### Minimal Setup

```python
from ravyn import Ravyn
from ravyn.config import SessionConfig

app = Ravyn(
    session_config=SessionConfig(
        secret_key="your-secret-key"
    )
)
```

### Complete Configuration

```python
app = Ravyn(
    session_config=SessionConfig(
        secret_key="your-secret-key",
        session_cookie="session_id",
        max_age=3600,  # 1 hour
        same_site="lax",
        https_only=True
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `secret_key` | str | Secret for signing cookies | **Required** |
| `session_cookie` | str | Cookie name | `"session"` |
| `max_age` | int | Session lifetime (seconds) | `14400` (4h) |
| `same_site` | str | SameSite attribute | `"lax"` |
| `https_only` | bool | HTTPS only | `False` |

---

## Using Sessions

### Setting Session Data

```python
from ravyn import post, Request

@post("/login")
async def login(request: Request, email: str, password: str) -> dict:
    # Verify credentials
    user = await authenticate(email, password)
    
    # Store in session
    request.session["user_id"] = user.id
    request.session["email"] = user.email
    
    return {"message": "Logged in"}
```

### Reading Session Data

```python
from ravyn import get, Request

@get("/profile")
async def profile(request: Request) -> dict:
    # Get from session
    user_id = request.session.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await User.get(id=user_id)
    return {"user": user}
```

### Clearing Session

```python
@post("/logout")
async def logout(request: Request) -> dict:
    # Clear session
    request.session.clear()
    return {"message": "Logged out"}
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import SessionConfig

class AppSettings(RavynSettings):
    session_config: SessionConfig = SessionConfig(
        secret_key="your-secret-key",
        max_age=3600,
        https_only=True
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Best Practices

### 1. Use Strong Secret Keys

```python
# Good - strong random secret
import secrets
import os

session_config = SessionConfig(
    secret_key=os.getenv("SESSION_SECRET", secrets.token_urlsafe(32))
)
```

### 2. Enable HTTPS in Production

```python
# Good - secure in production
session_config = SessionConfig(
    secret_key=secret_key,
    https_only=True,  # HTTPS only
    same_site="strict"
)
```

### 3. Set Appropriate Timeouts

```python
# Good - reasonable timeout
session_config = SessionConfig(
    secret_key=secret_key,
    max_age=1800  # 30 minutes
)
```

---

## Advanced: Ravyn Sessions Package

For more advanced session management, use the official [Ravyn Sessions](https://ravyn-sessions.dymmond.com/) package:

- Redis backend
- Database backend
- Custom backends
- Advanced features

---

## Next Steps

- [CSRFConfig](./csrf.md) - CSRF protection
- [JWTConfig](./jwt.md) - JWT authentication
- [CORSConfig](./cors.md) - CORS configuration
