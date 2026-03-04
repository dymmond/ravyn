# Security

Implement authentication and authorization in Ravyn using built-in security dependencies and permission layers.

## What You'll Learn

- Available security schemes.
- How security dependencies are injected.
- How OpenAPI security metadata is generated.
- Common patterns for protected endpoints.

## Quick Start

```python
from typing import Any

from ravyn import Gateway, Inject, Injects, Ravyn, get
from ravyn.security.http import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer()


@get(
    "/me",
    dependencies={"credentials": Inject(bearer)},
    security=[bearer],
)
async def me(credentials: HTTPAuthorizationCredentials = Injects()) -> dict[str, Any]:
    return {
        "scheme": credentials.scheme,
        "token": credentials.credentials,
    }


app = Ravyn(routes=[Gateway(handler=me)])
```

## Available security schemes

### HTTP

Import from `ravyn.security.http`:

- `HTTPBasic`
- `HTTPBearer`
- `HTTPDigest`

### API Key

Import from `ravyn.security.api_key`:

- `APIKeyInHeader`
- `APIKeyInCookie`
- `APIKeyInQuery`

### OAuth2 and OpenID Connect

Import from:

- `ravyn.security.oauth2`:
  - `OAuth2`
  - `OAuth2PasswordBearer`
  - `OAuth2AuthorizationCodeBearer`
  - `OAuth2PasswordRequestForm`
  - `OAuth2PasswordRequestFormStrict`
- `ravyn.security.open_id`:
  - `OpenIdConnect`

## Security flow in Ravyn

1. Instantiate a security dependency (for example `HTTPBearer()`).
2. Register it in `dependencies` with `Inject(...)`.
3. Receive the resolved value in the handler with `Injects()`.
4. Add it to `security=[...]` so OpenAPI documents the requirement.

This keeps handler logic explicit and OpenAPI output accurate.

```text
request
  -> security dependency resolves credentials
  -> handler receives typed credentials
  -> optional permission checks run
  -> response
```

## Additional example: API key in header

```python
from ravyn import Inject, Injects, get
from ravyn.security.api_key import APIKeyInHeader

api_key_header = APIKeyInHeader(name="X-API-Key")


@get(
    "/internal",
    dependencies={"api_key": Inject(api_key_header)},
    security=[api_key_header],
)
def internal(api_key: str = Injects()) -> dict:
    return {"api_key_received": bool(api_key)}
```

## OpenAPI integration

Security dependencies that inherit from Ravyn security base classes are automatically represented in OpenAPI.

That means `/docs/swagger`, `/docs/redoc`, and `/docs/elements` show the right authorization UI for your endpoint.

## Next steps

- [Introduction](./introduction.md)
- [Interaction](./interaction.md)
- [Simple OAuth2](./simple-oauth2.md)
- [OAuth2 + JWT](./oauth-jwt.md)
- [Available Security](./available-security.md)
- [Permissions](../permissions/index.md)
