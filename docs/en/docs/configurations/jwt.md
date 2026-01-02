# JWTConfig

Think of a JWT like a security badge at a tech company. When you arrive (log in), security gives you a badge with your photo, name, and access level encoded on it. Throughout the day, you show this badge to enter different areas - no need to go back to security each time.

The badge is:

- **Self-contained** - Has all your info encoded in it
- **Tamper-proof** - Security can tell if someone modified it
- **Time-limited** - Expires at end of day

JWTs work the same way. After login, the server gives you a token containing your user info and permissions. You include this token with each request, and the server verifies it without checking the database every time.

Configure JWT authentication in your Ravyn application for secure, stateless authentication.

## What You'll Learn

- What JWT is and how it works
- Configuring JWT in Ravyn
- Generating and validating tokens
- Access and refresh token patterns
- Best practices for JWT security

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import JWTConfig
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware

app = Ravyn(
    middleware=[JWTAuthMiddleware],
    jwt_config=JWTConfig(
        signing_key="your-secret-key-change-in-production",
        algorithm="HS256"
    )
)
```

!!! info
    Install JWT support: `pip install ravyn[jwt]`

---

## What is JWT?

**JWT** (JSON Web Token) is a compact, URL-safe token format for transmitting information between parties. Perfect for stateless authentication.

### JWT Structure

```
header.payload.signature
eyJhbGc...  .  eyJzdWI...  .  SflKxw...
```

- **Header** - Algorithm and token type
- **Payload** - Claims (user data, expiration, etc.)
- **Signature** - Cryptographic signature

### Why Use JWT?

- **Stateless** - No server-side session storage

- **Scalable** - Works across multiple servers

- **Mobile-Friendly** - Easy to use in mobile apps

- **Flexible** - Include custom claims

---

## Basic Configuration

### Minimal Setup

```python
from ravyn import Ravyn
from ravyn.config import JWTConfig

app = Ravyn(
    jwt_config=JWTConfig(
        signing_key="your-secret-key",
        algorithm="HS256"
    )
)
```

### Complete Configuration

```python
app = Ravyn(
    jwt_config=JWTConfig(
        signing_key="your-secret-key",
        algorithm="HS256",
        access_token_lifetime=3600,      # 1 hour
        refresh_token_lifetime=86400,    # 24 hours
        issuer="https://api.example.com",
        audience="https://example.com"
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `signing_key` | str | Secret key for signing tokens | **Required** |
| `algorithm` | str | Signing algorithm | `"HS256"` |
| `access_token_lifetime` | int | Access token TTL (seconds) | `3600` |
| `refresh_token_lifetime` | int | Refresh token TTL (seconds) | `86400` |
| `issuer` | str | Token issuer | `None` |
| `audience` | str | Token audience | `None` |

---

## Generating Tokens

### Using Token Class

```python
from ravyn.security.jwt.token import Token
from ravyn.conf import settings
from datetime import datetime, timedelta

# Create token with claims
token = Token(
    sub="user123",  # Subject (user ID)
    exp=datetime.utcnow() + timedelta(hours=1),  # Expiration
    iat=datetime.utcnow()  # Issued at
)

# Encode to JWT string
jwt_string = token.encode(
    key=settings.secret_key,
    algorithm="HS256"
)
```

### Custom Claims

```python
# Add custom claims
token = Token(
    sub="user123",
    exp=datetime.utcnow() + timedelta(hours=1),
    iat=datetime.utcnow(),
    email="user@example.com",  # Custom claim
    role="admin"  # Custom claim
)

jwt_string = token.encode(
    key=settings.secret_key,
    algorithm="HS256"
)
```

---

## Validating Tokens

### Decode Token

```python
from ravyn.security.jwt.token import Token
from ravyn.conf import settings

# Decode JWT string
token = Token.decode(
    token=jwt_string,
    key=settings.secret_key,
    algorithms=["HS256"]
)

# Access claims
user_id = token.sub
email = token.email
```

### With Validation

```python
try:
    token = Token.decode(
        token=jwt_string,
        key=settings.secret_key,
        algorithms=["HS256"],
        audience="https://example.com",
        issuer="https://api.example.com"
    )
except Exception as e:
    # Token invalid or expired
    print(f"Token validation failed: {e}")
```

---

## Access & Refresh Tokens

### Custom Token Class

```python
from ravyn.security.jwt.token import Token
from typing import Literal

class AppToken(Token):
    token_type: Literal["access", "refresh"]
    
    def is_access_token(self) -> bool:
        return self.token_type == "access"
    
    def is_refresh_token(self) -> bool:
        return self.token_type == "refresh"
```

### Generate Both Tokens

```python
from datetime import datetime, timedelta

def create_tokens(user_id: str) -> dict:
    # Access token (short-lived)
    access_token = AppToken(
        sub=user_id,
        token_type="access",
        exp=datetime.utcnow() + timedelta(hours=1),
        iat=datetime.utcnow()
    )
    
    # Refresh token (long-lived)
    refresh_token = AppToken(
        sub=user_id,
        token_type="refresh",
        exp=datetime.utcnow() + timedelta(days=7),
        iat=datetime.utcnow()
    )
    
    return {
        "access_token": access_token.encode(key=settings.secret_key, algorithm="HS256"),
        "refresh_token": refresh_token.encode(key=settings.secret_key, algorithm="HS256")
    }
```

---

## Authentication Middleware

### Using Built-in Middleware

```python
from ravyn import Ravyn
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware
from ravyn.config import JWTConfig

app = Ravyn(
    middleware=[JWTAuthMiddleware],
    jwt_config=JWTConfig(
        signing_key="your-secret-key",
        algorithm="HS256"
    )
)
```

### Protected Endpoints

```python
from ravyn import get, Request

@get("/protected")
async def protected_route(request: Request) -> dict:
    # User automatically authenticated by middleware
    user = request.user
    return {"user_id": user.id, "email": user.email}
```

---

## Complete Example

### Login Endpoint

```python
from ravyn import post
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

@post("/auth/login")
async def login(data: LoginRequest) -> dict:
    # Verify credentials (example)
    user = await User.get(email=data.email)
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate tokens
    tokens = create_tokens(str(user.id))
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer"
    }
```

### Refresh Endpoint

```python
@post("/auth/refresh")
async def refresh_token(refresh_token: str) -> dict:
    try:
        # Decode refresh token
        token = AppToken.decode(
            token=refresh_token,
            key=settings.secret_key,
            algorithms=["HS256"]
        )
        
        # Verify it's a refresh token
        if not token.is_refresh_token():
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Generate new access token
        new_access_token = AppToken(
            sub=token.sub,
            token_type="access",
            exp=datetime.utcnow() + timedelta(hours=1),
            iat=datetime.utcnow()
        ).encode(key=settings.secret_key, algorithm="HS256")
        
        return {"access_token": new_access_token}
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import JWTConfig

class AppSettings(RavynSettings):
    jwt_config: JWTConfig = JWTConfig(
        signing_key="your-secret-key",
        algorithm="HS256",
        access_token_lifetime=3600,
        refresh_token_lifetime=604800  # 7 days
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Weak Secret Key

**Problem:** Using a weak or hardcoded secret.

```python
# Wrong - weak secret
jwt_config = JWTConfig(
    signing_key="secret"  # Too simple!
)
```

**Solution:** Use strong, random secrets:

```python
# Correct
import secrets
import os

jwt_config = JWTConfig(
    signing_key=os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
)
```

### Pitfall 2: Long-Lived Access Tokens

**Problem:** Access tokens that don't expire.

```python
# Wrong - never expires
token = Token(
    sub="user123",
    # No exp claim!
)
```

**Solution:** Always set expiration:

```python
# Correct
from datetime import datetime, timedelta

token = Token(
    sub="user123",
    exp=datetime.utcnow() + timedelta(hours=1),
    iat=datetime.utcnow()
)
```

### Pitfall 3: Storing Tokens in LocalStorage

**Problem:** XSS vulnerability.

```javascript
// Wrong - vulnerable to XSS
localStorage.setItem('token', accessToken);
```

**Solution:** Use httpOnly cookies or secure storage:

```python
# Correct - set httpOnly cookie
from ravyn import Response

response = Response({"message": "Logged in"})
response.set_cookie(
    "access_token",
    access_token,
    httponly=True,
    secure=True,
    samesite="strict"
)
```

---

## Best Practices

### 1. Use Environment Variables

```python
# Good - configurable secrets
import os

jwt_config = JWTConfig(
    signing_key=os.getenv("JWT_SECRET_KEY"),
    algorithm="HS256"
)
```

### 2. Short Access Token Lifetime

```python
# Good - short-lived access tokens
jwt_config = JWTConfig(
    signing_key=secret_key,
    access_token_lifetime=900,  # 15 minutes
    refresh_token_lifetime=604800  # 7 days
)
```

### 3. Validate All Claims

```python
# Good - validate issuer and audience
token = Token.decode(
    token=jwt_string,
    key=settings.secret_key,
    algorithms=["HS256"],
    issuer="https://api.example.com",
    audience="https://example.com"
)
```

---

## Learn More

- [JWT.io Introduction](https://jwt.io/introduction)
- [JWTConfig Reference](../references/configurations/jwt.md)
- [Security Best Practices](../security/index.md)
- [Edgy Middleware](../databases/edgy/middleware.md)

---

## Next Steps

- [SessionConfig](./session.md) - Session management
- [CORSConfig](./cors.md) - CORS configuration
- [Security](../security/index.md) - Authentication & authorization
