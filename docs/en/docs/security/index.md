# Security

Implement secure authentication and authorization in your Ravyn application with built-in security tools.

## What You'll Learn

- Security fundamentals (OAuth2, JWT, etc.)
- Available security schemes
- Implementing authentication
- Authorization patterns
- Best practices

## Quick Start

```python
from ravyn import Ravyn, get, Inject
from ravyn.security.jwt import JWTAuth

@get("/protected", dependencies={"auth": Inject(JWTAuth())})
async def protected_route(auth: dict) -> dict:
    return {"user": auth["sub"], "message": "Authenticated!"}

app = Ravyn(routes=[Gateway(handler=protected_route)])
```

---

## In This Section

### Getting Started

- [Introduction](./introduction.md) - Security concepts and overview
- [Available Security](./available-security.md) - Built-in security schemes
- [Interaction](./interaction.md) - How security works in Ravyn

### Implementation Guides

- [OAuth2 + JWT](./oauth-jwt.md) - JWT-based OAuth2 authentication
- [Simple OAuth2](./simple-oauth2.md) - Basic OAuth2 implementation

### Advanced Topics

- [Basic Auth](./advanced/basic-auth.md) - HTTP Basic Authentication
- [OAuth2 Scopes](./advanced/oauth2-scopes.md) - Fine-grained permissions

---

## Security Concepts

### OAuth2

OAuth2 is a comprehensive specification for authentication and authorization. It enables:

- **Third-party login** - "Sign in with Google/Facebook/GitHub"

- **Token-based auth** - Stateless authentication

- **Scopes** - Fine-grained permissions

- **Multiple flows** - Password, client credentials, authorization code

### JWT (JSON Web Tokens)

JWTs are compact, URL-safe tokens for transmitting information:

- **Stateless** - No server-side session storage

- **Self-contained** - Contains all user information

- **Secure** - Cryptographically signed

- **Standard** - Widely supported

### OpenID Connect

Built on top of OAuth2, OpenID Connect adds:

- **Standardization** - Reduces OAuth2 ambiguities

- **User info** - Standard user profile endpoint

- **ID tokens** - JWT-based identity tokens

---

## Supported Security Schemes

Ravyn supports OpenAPI security schemes:

| Scheme | Type | Description |
|--------|------|-------------|
| **API Key** | apiKey | Custom keys in headers/cookies/query |
| **Bearer Token** | http (bearer) | JWT or opaque tokens |
| **Basic Auth** | http (basic) | Username/password |
| **OAuth2** | oauth2 | OAuth2 flows |
| **OpenID Connect** | openIdConnect | OIDC authentication |

---

## Quick Examples

### JWT Authentication

```python
from ravyn import Ravyn, get, Inject
from ravyn.security.jwt import JWTAuth

@get("/users/me", dependencies={"auth": Inject(JWTAuth())})
async def get_current_user(auth: dict) -> dict:
    return {"user_id": auth["sub"], "email": auth["email"]}
```

### API Key Authentication

```python
from ravyn import Ravyn, get, Security
from ravyn.security import APIKeyHeader

api_key_scheme = APIKeyHeader(name="X-API-Key")

@get("/data", security=[api_key_scheme])
async def get_data(api_key: str = Security(api_key_scheme)) -> dict:
    if api_key != "secret-key":
        raise HTTPException(status_code=401)
    return {"data": "sensitive"}
```

### OAuth2 with Scopes

```python
from ravyn import Ravyn, get
from ravyn.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={"read": "Read access", "write": "Write access"}
)

@get("/items", security=[oauth2_scheme])
async def read_items(token: str = Security(oauth2_scheme, scopes=["read"])):
    return {"items": []}
```

---

## Why Ravyn Security?

**Ravyn simplifies security implementation:**

- **Standards-based** - OAuth2, JWT, OpenAPI

- **Easy integration** - Built-in tools and decorators

- **Automatic docs** - Security schemes in OpenAPI

- **Flexible** - Multiple authentication methods

- **Production-ready** - Battle-tested patterns

---

## Common Patterns

### Pattern 1: JWT + Refresh Tokens

```python
# Login returns access + refresh tokens
@post("/login")
async def login(credentials: LoginRequest) -> dict:
    user = await authenticate(credentials)
    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
        "token_type": "bearer"
    }

# Protected route requires access token
@get("/protected", dependencies={"auth": Inject(JWTAuth())})
async def protected(auth: dict) -> dict:
    return {"user": auth["sub"]}
```

### Pattern 2: Role-Based Access

```python
from ravyn import get, Inject
from ravyn.permissions import IsAuthenticated, HasRole

@get(
    "/admin",
    permissions=[IsAuthenticated, HasRole("admin")]
)
async def admin_only() -> dict:
    return {"message": "Admin access granted"}
```

### Pattern 3: API Key + Rate Limiting

```python
from ravyn import get, Security
from ravyn.security import APIKeyHeader
from ravyn.middleware import RateLimitMiddleware

api_key = APIKeyHeader(name="X-API-Key")

@get(
    "/api/data",
    security=[api_key],
    middleware=[RateLimitMiddleware(max_requests=100)]
)
async def api_endpoint(key: str = Security(api_key)) -> dict:
    return {"data": "value"}
```

---

## Best Practices

### 1. Use HTTPS in Production

```python
# Good - enforce HTTPS
if not request.url.scheme == "https" and os.getenv("ENV") == "production":
    raise HTTPException(status_code=403, detail="HTTPS required")
```

### 2. Store Secrets Securely

```python
# Good - environment variables
import os

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
API_KEY = os.getenv("API_KEY")
```

### 3. Use Short-Lived Access Tokens

```python
# Good - 15 minute access tokens
access_token = create_jwt(
    user_id=user.id,
    expires_in=900  # 15 minutes
)
```

---

## Next Steps

Choose your authentication method:

- [OAuth2 + JWT](./oauth-jwt.md) - Most common pattern
- [Simple OAuth2](./simple-oauth2.md) - Basic implementation
- [Basic Auth](./advanced/basic-auth.md) - Simple username/password
- [Available Security](./available-security.md) - All security schemes
