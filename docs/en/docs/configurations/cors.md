# CORSConfig

Think of CORS like international travel rules. When you're in your home country (same origin), you can go anywhere freely. But when you try to cross borders (different origin), you need permission.

Your frontend at `app.example.com` trying to call your API at `api.example.com`? That's crossing borders. CORS is the passport control that decides who gets through.

Enable cross-origin requests in your Ravyn application with CORS configuration.

## What You'll Learn

- What CORS is and why you need it
- Configuring CORS in Ravyn
- Common CORS patterns
- Security best practices

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import CORSConfig

app = Ravyn(
    cors_config=CORSConfig(
        allow_origins=["https://example.com"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"]
    )
)
```

---

## What is CORS?

**CORS** (Cross-Origin Resource Sharing) allows your API to accept requests from different domains. Without CORS, browsers block requests from other origins for security.

### When You Need CORS

- **Frontend on different domain** - React app at `app.com` calling API at `api.com`

- **Mobile apps** - Native apps calling your API

- **Third-party integrations** - External services accessing your API

- **Development** - Frontend on `localhost:3000`, API on `localhost:8000`

---

## Basic Configuration

### Allow All Origins (Development)

```python
from ravyn import Ravyn
from ravyn.config import CORSConfig

app = Ravyn(
    cors_config=CORSConfig(
        allow_origins=["*"],  # Allow all origins
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"]   # Allow all headers
    )
)
```

!!! warning
    Don't use `allow_origins=["*"]` in production! Specify exact origins.

### Allow Specific Origins (Production)

```python
app = Ravyn(
    cors_config=CORSConfig(
        allow_origins=[
            "https://example.com",
            "https://app.example.com"
        ],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"]
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `allow_origins` | list[str] | Allowed origin URLs | `[]` |
| `allow_methods` | list[str] | Allowed HTTP methods | `["GET"]` |
| `allow_headers` | list[str] | Allowed request headers | `[]` |
| `allow_credentials` | bool | Allow cookies/auth | `False` |
| `expose_headers` | list[str] | Headers exposed to browser | `[]` |
| `max_age` | int | Preflight cache time (seconds) | `600` |

---

## Common Patterns

### Pattern 1: Frontend + API

```python
# API at api.example.com
# Frontend at app.example.com

app = Ravyn(
    cors_config=CORSConfig(
        allow_origins=["https://app.example.com"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=True  # Allow cookies
    )
)
```

### Pattern 2: Multiple Subdomains

```python
app = Ravyn(
    cors_config=CORSConfig(
        allow_origins=[
            "https://app.example.com",
            "https://admin.example.com",
            "https://dashboard.example.com"
        ],
        allow_methods=["*"],
        allow_headers=["*"]
    )
)
```

### Pattern 3: Development Setup

```python
import os

# Different config for dev vs prod
if os.getenv("ENV") == "development":
    cors_config = CORSConfig(
        allow_origins=["http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
else:
    cors_config = CORSConfig(
        allow_origins=["https://app.example.com"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"]
    )

app = Ravyn(cors_config=cors_config)
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import CORSConfig

class AppSettings(RavynSettings):
    cors_config: CORSConfig = CORSConfig(
        allow_origins=["https://example.com"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"]
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Wildcard with Credentials

**Problem:** Can't use `*` with credentials.

```python
# Wrong - can't combine * with credentials
cors_config = CORSConfig(
    allow_origins=["*"],
    allow_credentials=True  # Error!
)
```

**Solution:** Specify exact origins:

```python
# Correct
cors_config = CORSConfig(
    allow_origins=["https://example.com"],
    allow_credentials=True
)
```

### Pitfall 2: Missing Authorization Header

**Problem:** JWT tokens not allowed.

```python
# Wrong - Authorization header blocked
cors_config = CORSConfig(
    allow_origins=["https://example.com"],
    allow_headers=["Content-Type"]  # Missing Authorization!
)
```

**Solution:** Include Authorization:

```python
# Correct
cors_config = CORSConfig(
    allow_origins=["https://example.com"],
    allow_headers=["Content-Type", "Authorization"]
)
```

### Pitfall 3: Wrong Origin Format

**Problem:** Origin doesn't include protocol.

```python
# Wrong - missing https://
cors_config = CORSConfig(
    allow_origins=["example.com"]  # Wrong format!
)
```

**Solution:** Include full URL:

```python
# Correct
cors_config = CORSConfig(
    allow_origins=["https://example.com"]
)
```

---

## Best Practices

### 1. Be Specific in Production

```python
# Good - exact origins
cors_config = CORSConfig(
    allow_origins=["https://app.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"]
)
```

### 2. Use Environment Variables

```python
# Good - configurable
import os

cors_config = CORSConfig(
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_methods=["GET", "POST", "PUT", "DELETE"]
)
```

### 3. Enable Credentials Only When Needed

```python
# Good - credentials only if required
cors_config = CORSConfig(
    allow_origins=["https://example.com"],
    allow_credentials=True,  # Only if using cookies/auth
    allow_headers=["Content-Type", "Authorization"]
)
```

---

## Learn More

- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CORSConfig Reference](../references/configurations/cors.md)
- [Security Best Practices](../security/index.md)

---

## Next Steps

- [CSRFConfig](./csrf.md) - CSRF protection
- [JWTConfig](./jwt.md) - JWT authentication
- [SessionConfig](./session.md) - Session management
