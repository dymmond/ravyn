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

## Authorization flow

```text
request enters app
  -> global permissions (app/include)
  -> route-level permissions
  -> handler execution (if all checks pass)
```

Use higher levels (app/include) for broad policy and route-level permissions for endpoint-specific rules.

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

### Composition example on a route

```python
from ravyn import get
from ravyn.permissions import BasePermission, IsAuthenticated


class HasStaffFlag(BasePermission):
    async def has_permission(self, request, controller) -> bool:
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_staff", False))


@get("/admin", permissions=[IsAuthenticated & HasStaffFlag])
def admin_dashboard() -> dict:
    return {"ok": True}
```

## Ravyn vs Lilya permissions

Ravyn supports both Ravyn-native and Lilya-style permissions.

Important: do not mix both styles on the same Gateway definition.

If you use Ravyn-native permissions, stay consistent in that route tree.

## Practical Permission Examples

This section covers real-world permission patterns commonly used in production applications.

### Role-Based Permissions

Role-based permissions check if a user has a specific role (e.g., admin, editor, viewer). This is ideal for applications with hierarchical access control.

```python
from ravyn import Ravyn, get
from ravyn.permissions import BasePermission
from ravyn.requests import Request


class IsEditor(BasePermission):
    """
    Grants access only to users with the 'editor' role.
    """

    async def has_permission(self, request: Request, controller) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False
        # Assuming user has a 'role' attribute
        return getattr(user, "role", None) == "editor"


class IsAdmin(BasePermission):
    """
    Grants access only to users with the 'admin' role.
    """

    async def has_permission(self, request: Request, controller) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False
        return getattr(user, "role", None) == "admin"


@get("/api/admin/settings", permissions=[IsAdmin])
def admin_settings() -> dict:
    return {"settings": "admin-only"}


@get("/api/editor/posts", permissions=[IsEditor])
def editor_posts() -> dict:
    return {"posts": "editor-access"}


# You can also combine roles for "admin OR editor" access
@get("/api/content", permissions=[IsAdmin | IsEditor])
def content_management() -> dict:
    return {"access": "admin or editor"}
```

### Resource-Based Permissions

Resource-based permissions check if a user has access to a specific resource (e.g., ownership, team membership). This is ideal for multi-tenant applications.

```python
from ravyn import Ravyn, get, post
from ravyn.permissions import BasePermission, IsAuthenticated
from ravyn.requests import Request


class IsOwner(BasePermission):
    """
    Grants access only if the user owns the resource.
    Checks if the user_id from the URL matches the authenticated user's ID.
    """

    async def has_permission(self, request: Request, controller) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False

        # Extract user_id from path parameters
        resource_user_id = request.path_params.get("user_id")
        if not resource_user_id:
            return False

        # Check if the authenticated user owns the resource
        return str(getattr(user, "id", None)) == str(resource_user_id)


class IsTeamMember(BasePermission):
    """
    Grants access only if the user is a member of the team.
    """

    async def has_permission(self, request: Request, controller) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False

        # Extract team_id from path parameters
        team_id = request.path_params.get("team_id")
        if not team_id:
            return False

        # Assuming user has a 'teams' list attribute
        user_teams = getattr(user, "teams", [])
        return int(team_id) in user_teams


# Only the user can access their own profile
@get("/users/{user_id}/profile", permissions=[IsAuthenticated & IsOwner])
def get_user_profile(user_id: int) -> dict:
    return {"user_id": user_id, "profile": "private data"}


# Only the user can update their own settings
@post("/users/{user_id}/settings", permissions=[IsAuthenticated & IsOwner])
def update_user_settings(user_id: int, settings: dict) -> dict:
    return {"user_id": user_id, "updated": True}


# Only team members can access team resources
@get("/teams/{team_id}/projects", permissions=[IsAuthenticated & IsTeamMember])
def get_team_projects(team_id: int) -> dict:
    return {"team_id": team_id, "projects": []}
```

### Combining Permissions for Complex Rules

You can combine multiple permissions using logical operators for more complex access control scenarios:

```python
from ravyn import get
from ravyn.permissions import BasePermission, IsAuthenticated


class IsPremiumUser(BasePermission):
    """
    Grants access only to premium/paid users.
    """

    async def has_permission(self, request, controller) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False
        return getattr(user, "is_premium", False)


class HasFeatureAccess(BasePermission):
    """
    Grants access based on feature flag.
    """

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    async def has_permission(self, request, controller) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False
        enabled_features = getattr(user, "enabled_features", [])
        return self.feature_name in enabled_features


# Premium feature: requires authentication AND premium status
@get("/api/premium/analytics", permissions=[IsAuthenticated & IsPremiumUser])
def premium_analytics() -> dict:
    return {"analytics": "premium-only"}


# Admin OR premium users can access advanced features
@get("/api/advanced/reports", permissions=[IsAdmin | IsPremiumUser])
def advanced_reports() -> dict:
    return {"reports": "advanced"}
```

## Best practices

- Keep permissions focused on authorization only.
- Reuse permission classes instead of inline checks in handlers.
- Compose small permission classes for complex access rules.
- Prefer explicit denial messages in your exception handlers when needed.
- Pair permissions with [Security dependencies](../security/index.md) when credentials and authorization rules are both required.
