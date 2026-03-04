# How to Add JWT Authentication

This guide shows a practical JWT setup with security dependencies and protected endpoints.

## 1. Configure JWT

```python
from ravyn import Ravyn
from ravyn.core.config.jwt import JWTConfig

app = Ravyn(
    routes=[...],
    jwt_config=JWTConfig(
        secret_key="change-me",
        algorithm="HS256",
    ),
)
```

## 2. Add bearer security dependency

```python
from ravyn import Inject, Injects, get
from ravyn.security.http import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer()

@get("/me", dependencies={"auth": Inject(bearer)}, security=[bearer])
def me(credentials: HTTPAuthorizationCredentials = Injects()) -> dict:
    return {"token_present": bool(credentials.credentials)}
```

## 3. Enforce permission policy

Attach permission classes at app/router/gateway level based on your boundary needs.

```python
from ravyn import Gateway, Ravyn

app = Ravyn(
    routes=[Gateway("/me", handler=me, permissions=[IsAuthenticated])],
)
```

## 4. Validate behavior

1. Call endpoint without token and assert failure status.
2. Call with token and assert success.
3. Confirm OpenAPI security metadata appears in docs UI.

## Related pages

- [Security](../security/index.md)
- [Permissions](../permissions/index.md)
- [JWT Configuration](../configurations/jwt.md)
