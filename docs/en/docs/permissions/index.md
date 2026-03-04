# Permissions

Control who can access what in your Ravyn application.

Permissions are authorization rules evaluated before the handler runs. They are ideal for role checks, access policies, and endpoint-level protection.

## What You'll Learn

- Ravyn native permission classes.
- Where to apply permissions (app, include, gateway, handler).
- How to create custom permissions.
- How to combine permissions with logical operators.

## Quick Start

```python
from ravyn import Ravyn, Gateway, get
from ravyn.permissions import IsAuthenticated

@get()
async def profile() -> dict:
    return {"ok": True}

app = Ravyn(
    routes=[Gateway("/profile", handler=profile)],
    permissions=[IsAuthenticated],
)
```

## Built-in Ravyn permissions

Ravyn provides these built-ins:

- `AllowAny`
- `DenyAll`
- `IsAuthenticated`
- `IsAdminUser`
- `IsAuthenticatedOrReadOnly`

Import from:

```python
from ravyn.permissions import (
    AllowAny,
    DenyAll,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
```

## Creating a custom permission

Subclass `BasePermission` and implement `has_permission(request, controller)`.

```python
from ravyn.permissions import BasePermission
from ravyn.requests import Request


class HasAPIKey(BasePermission):
    async def has_permission(self, request: Request, controller) -> bool:
        return request.headers.get("x-api-key") == "secret"
```

You can also implement `has_permission` as a sync method.

## Applying permissions

Permissions can be declared at multiple levels.

- Application level: applies globally.
- Include level: applies to grouped routes.
- Gateway/handler level: applies to a specific endpoint.

```python
from ravyn import Ravyn, Include, Gateway, get
from ravyn.permissions import IsAuthenticated

@get()
async def me() -> dict:
    return {"user": "ok"}

app = Ravyn(
    routes=[
        Include(
            "/api",
            routes=[Gateway("/me", handler=me)],
            permissions=[IsAuthenticated],
        )
    ]
)
```

## Permission composition (AND, OR, NOT, XOR, NOR)

Ravyn supports composing permissions using operators in `BasePermission`.

- `A & B` -> both must pass
- `A | B` -> either one passes
- `~A` -> inverse of `A`
- `A ^ B` -> exactly one passes
- `A - B` -> NOR (`not (A or B)`)

```python
from ravyn.permissions import BasePermission, IsAuthenticated


class HasVerifiedEmail(BasePermission):
    async def has_permission(self, request, controller) -> bool:
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_verified", False))


Combined = IsAuthenticated & HasVerifiedEmail
```

Then use `Combined` anywhere permissions are accepted.

## Ravyn vs Lilya permissions

Ravyn supports both Ravyn-native and Lilya-style permissions.

Important: do not mix both styles on the same Gateway definition.

If you use Ravyn-native permissions, stay consistent in that route tree.

## Best practices

- Keep permissions focused on authorization only.
- Reuse permission classes instead of inline checks in handlers.
- Compose small permission classes for complex access rules.
- Prefer explicit denial messages in your exception handlers when needed.
