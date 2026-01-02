---
hide:

  - navigation
---

# OpenAPI: Interactive API Documentation

Ravyn automatically generates beautiful, interactive API documentation. Test your endpoints, authenticate, and explore your API—all from your browser.

## What You'll Learn

- Accessing built-in API documentation
- Documenting your endpoints
- Adding authentication to docs
- Using security schemes
- Testing APIs in the browser

## Quick Start

```python
from ravyn import Ravyn, get
from ravyn.openapi.datastructures import OpenAPIResponse

@get(
    "/users",
    tags=["Users"],
    summary="List all users",
    description="Returns a list of all users in the system",
    responses={
        200: OpenAPIResponse(model=list[dict], description="List of users"),
        404: OpenAPIResponse(model=dict, description="No users found")
    }
)
def list_users() -> list[dict]:
    return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

app = Ravyn()
app.add_route(list_users)

# Visit http://localhost:8000/docs/swagger to see your docs!
```

---

## Built-In Documentation UIs

Ravyn provides **four** interactive documentation interfaces out of the box:

| UI | URL | Best For |
|----|-----|----------|
| **Swagger** | `/docs/swagger` | Testing & exploration |
| **Redoc** | `/docs/redoc` | Clean, readable docs |
| **Stoplight** | `/docs/elements` | Modern design |
| **Rapidoc** | `/docs/rapidoc` | Customizable interface |

!!! tip
    See [OpenAPIConfig](./configurations/openapi/config.md) to customize URLs and settings.

---

## Documenting Endpoints

### Basic Documentation

```python
from ravyn import get

@get(
    "/products",
    tags=["Products"],
    summary="Get all products",
    description="Returns a list of all available products"
)
def get_products() -> list[dict]:
    return [{"id": 1, "name": "Product 1"}]
```

### With Response Models

```python
from ravyn import get
from ravyn.openapi.datastructures import OpenAPIResponse
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float

class Error(BaseModel):
    detail: str

@get(
    "/products/{product_id}",
    tags=["Products"],
    summary="Get product by ID",
    responses={
        200: OpenAPIResponse(model=Product, description="Product found"),
        404: OpenAPIResponse(model=Error, description="Product not found")
    }
)
def get_product(product_id: int) -> Product:
    return Product(id=product_id, name="Product 1", price=99.99)
```

### Complete Example

```python
from ravyn import get, post, put, delete
from ravyn.openapi.datastructures import OpenAPIResponse
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    id: int
    name: str
    email: str

@get(
    "/users",
    tags=["Users"],
    summary="List all users",
    description="Returns a paginated list of users",
    responses={
        200: OpenAPIResponse(model=list[User], description="List of users")
    }
)
def list_users() -> list[User]:
    return [User(id=1, name="Alice", email="alice@example.com")]

@post(
    "/users",
    tags=["Users"],
    summary="Create user",
    description="Creates a new user in the system",
    responses={
        201: OpenAPIResponse(model=User, description="User created"),
        400: OpenAPIResponse(model=dict, description="Invalid data")
    }
)
def create_user(data: UserCreate) -> User:
    return User(id=1, **data.dict())
```

---

## Authentication in Documentation

Add authentication to your docs so you can test protected endpoints.

### Supported Security Schemes

| Scheme | Use Case | Import |
|--------|----------|--------|
| `HTTPBasic` | Basic auth | `ravyn.security.http` |
| `HTTPBearer` | JWT tokens | `ravyn.security.http` |
| `HTTPDigest` | Digest auth | `ravyn.security.http` |
| `APIKeyInHeader` | API keys in headers | `ravyn.security.api_key` |
| `APIKeyInCookie` | API keys in cookies | `ravyn.security.api_key` |
| `APIKeyInQuery` | API keys in query params | `ravyn.security.api_key` |
| `OAuth2` | OAuth2 flow | `ravyn.security.oauth2` |
| `OpenIdConnect` | OpenID Connect | `ravyn.security.open_id` |

### Import Security Schemes

```python
from ravyn.security.http import HTTPBasic, HTTPBearer, HTTPDigest
from ravyn.security.api_key import APIKeyInCookie, APIKeyInHeader, APIKeyInQuery
from ravyn.security.oauth2 import OAuth2
from ravyn.security.open_id import OpenIdConnect
```

---

## Using Security Schemes

### HTTPBearer (JWT Tokens)

```python
from ravyn import get
from ravyn.security.http import HTTPBearer

@get(
    "/protected",
    summary="Protected endpoint",
    security=[HTTPBearer]
)
def protected_route() -> dict:
    return {"message": "You are authenticated!"}
```

When you visit the docs, you'll see an "Authorize" button where you can enter your token.

### HTTPBasic (Username/Password)

```python
from ravyn.security.http import HTTPBasic

@get(
    "/admin",
    summary="Admin endpoint",
    security=[HTTPBasic]
)
def admin_route() -> dict:
    return {"message": "Admin access"}
```

### APIKeyInHeader

```python
from ravyn.security.api_key import APIKeyInHeader

# Define the security scheme
api_key_header = APIKeyInHeader(
    name="X-API-Key",
    scheme_name="API Key (Header)",
    description="Enter your API key"
)

@get(
    "/api/data",
    summary="Get data",
    security=[api_key_header]
)
def get_data() -> dict:
    return {"data": "sensitive information"}
```

### APIKeyInQuery

```python
from ravyn.security.api_key import APIKeyInQuery

api_key_query = APIKeyInQuery(
    name="api_key",
    scheme_name="API Key (Query)",
    description="Pass API key as query parameter"
)

@get(
    "/api/users",
    summary="Get users",
    security=[api_key_query]
)
def get_users() -> dict:
    # Accessed as: /api/users?api_key=YOUR_KEY
    return {"users": []}
```

### APIKeyInCookie

```python
from ravyn.security.api_key import APIKeyInCookie

api_key_cookie = APIKeyInCookie(
    name="session_id",
    scheme_name="Session Cookie",
    description="Session cookie for authentication"
)

@get(
    "/dashboard",
    summary="User dashboard",
    security=[api_key_cookie]
)
def dashboard() -> dict:
    return {"dashboard": "data"}
```

---

## Multiple Security Schemes

You can use multiple security schemes on the same endpoint:

```python
from ravyn import get
from ravyn.security.http import HTTPBearer
from ravyn.security.api_key import APIKeyInHeader

bearer_auth = HTTPBearer(scheme_name="JWT Token")
api_key_auth = APIKeyInHeader(name="X-API-Key", scheme_name="API Key")

@get(
    "/secure",
    summary="Secure endpoint",
    security=[bearer_auth, api_key_auth]
)
def secure_endpoint() -> dict:
    return {"message": "Authenticated with multiple methods"}
```

---

## Application-Level Security

Apply security to all routes in an Include or the entire app:

### Include-Level

```python
from ravyn import Ravyn, Include, get
from ravyn.security.http import HTTPBearer

@get("/users")
def list_users() -> dict:
    return {"users": []}

@get("/products")
def list_products() -> dict:
    return {"products": []}

# All routes in this Include require authentication
api_routes = Include(
    "/api",
    routes=[
        Gateway(handler=list_users),
        Gateway(handler=list_products)
    ],
    security=[HTTPBearer]
)

app = Ravyn(routes=[api_routes])
```

### App-Level

```python
from ravyn import Ravyn
from ravyn.security.http import HTTPBearer

# All routes in the app require authentication
app = Ravyn(
    routes=[...],
    security=[HTTPBearer]
)
```

---

## OAuth2 Authentication

For complex OAuth2 flows, see the [Security section](./security/index.md) for detailed examples.

```python
from ravyn.security.oauth2 import OAuth2

oauth2_scheme = OAuth2(
    flows={
        "password": {
            "tokenUrl": "/token",
            "scopes": {
                "read": "Read access",
                "write": "Write access"
            }
        }
    }
)

@get("/protected", security=[oauth2_scheme])
def protected() -> dict:
    return {"message": "OAuth2 protected"}
```

---

## OpenID Connect

```python
from ravyn.security.open_id import OpenIdConnect

openid_scheme = OpenIdConnect(
    openIdConnectUrl="https://example.com/.well-known/openid-configuration",
    scheme_name="OpenID Connect"
)

@get("/sso", security=[openid_scheme])
def sso_endpoint() -> dict:
    return {"message": "SSO authenticated"}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Missing Response Models

**Problem:** Docs don't show response structure.

```python
# Wrong - no response documentation
@get("/users")
def list_users() -> dict:
    return {"users": []}
```

**Solution:** Add OpenAPIResponse:

```python
# Correct
from ravyn.openapi.datastructures import OpenAPIResponse

@get(
    "/users",
    responses={
        200: OpenAPIResponse(model=dict, description="List of users")
    }
)
def list_users() -> dict:
    return {"users": []}
```

### Pitfall 2: Security Not Showing in Docs

**Problem:** Authorize button doesn't appear.

```python
# Wrong - security not configured
@get("/protected")
def protected() -> dict:
    return {}
```

**Solution:** Add security parameter:

```python
# Correct
from ravyn.security.http import HTTPBearer

@get("/protected", security=[HTTPBearer])
def protected() -> dict:
    return {}
```

### Pitfall 3: Wrong Security Scheme Type

**Problem:** Using wrong scheme for your auth method.

```python
# Wrong - using HTTPBasic for JWT
from ravyn.security.http import HTTPBasic

@get("/jwt-protected", security=[HTTPBasic])
def protected() -> dict:
    return {}
```

**Solution:** Use HTTPBearer for JWT:

```python
# Correct
from ravyn.security.http import HTTPBearer

@get("/jwt-protected", security=[HTTPBearer])
def protected() -> dict:
    return {}
```

---

## Best Practices

### 1. Use Tags to Organize

```python
# Good - organized by tags
@get("/users", tags=["Users"])
def list_users() -> dict:
    pass

@get("/products", tags=["Products"])
def list_products() -> dict:
    pass
```

### 2. Add Descriptions

```python
# Good - clear descriptions
@get(
    "/users/{user_id}",
    summary="Get user by ID",
    description="Retrieves a single user by their unique identifier"
)
def get_user(user_id: int) -> dict:
    pass
```

### 3. Document All Responses

```python
# Good - all responses documented
@get(
    "/users/{user_id}",
    responses={
        200: OpenAPIResponse(model=User, description="User found"),
        404: OpenAPIResponse(model=Error, description="User not found"),
        500: OpenAPIResponse(model=Error, description="Server error")
    }
)
def get_user(user_id: int) -> User:
    pass
```

---

## Customizing OpenAPI

See [OpenAPIConfig](./configurations/openapi/config.md) for:

- Changing documentation URLs
- Customizing titles and descriptions
- Adding contact information
- Setting API version
- Configuring servers

---

## Next Steps

Now that you understand OpenAPI documentation, explore:

- [OpenAPIConfig](./configurations/openapi/config.md) - Customize docs
- [Security](./security/index.md) - Authentication & authorization
- [Responses](./responses.md) - Response types
- [Requests](./requests.md) - Request handling
