# Step 3: Auth and Permissions

Protect endpoints with JWT-based authentication and permission checks.

## Add JWT configuration

```python
from ravyn import Ravyn
from ravyn.core.config.jwt import JWTConfig

app = Ravyn(
    routes=[...],
    jwt_config=JWTConfig(secret_key="change-me", algorithm="HS256"),
)
```

## Add a security dependency

```python
from ravyn import Inject, Injects, get
from ravyn.security.http import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer()


@get("/me", dependencies={"credentials": Inject(bearer)}, security=[bearer])
def me(credentials: HTTPAuthorizationCredentials = Injects()) -> dict:
    return {"scheme": credentials.scheme}
```

## Add endpoint-level permissions

```python
from ravyn import Gateway


app = Ravyn(
    routes=[
        Gateway("/me", handler=me, permissions=[IsAuthenticated]),
    ],
)
```

## Checkpoint

- Unauthorized calls are rejected
- OpenAPI shows auth requirements

## Next step

Continue with [Testing and Deployment](./04-testing-and-deploy.md).

## Related pages

- [Security](../../security/index.md)
- [Permissions](../../permissions/index.md)
