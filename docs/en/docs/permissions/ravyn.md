# Ravyn Permissions

Ravyn's native permission system provides a clean, Django-inspired way to control access to your API endpoints. Define custom permissions, use built-in permissions, and apply them at any application level for fine-grained access control.

## What You'll Learn

- Creating custom permission classes
- Using built-in permissions (IsAuthenticated, IsAdminUser, etc.)
- Applying permissions at different levels
- Async permission support
- Permission inheritance and cascading
- Integrating with Edgy user models

## Quick Start

```python
from ravyn import Ravyn, get
from ravyn.permissions import BasePermission, IsAuthenticated

class IsOwner(BasePermission):
    async def has_permission(self, request, controller):
        # Custom logic to check if user owns the resource
        user_id = request.path_params.get("user_id")
        return request.user.id == user_id

@get("/users/{user_id}/profile", permissions=[IsAuthenticated, IsOwner])
def get_profile(user_id: int) -> dict:
    return {"user_id": user_id, "data": "..."}

app = Ravyn(
    routes=[...],
    permissions=[IsAuthenticated]  # Apply globally
)
```

---

## BasePermission and custom permissions

If you are used to Django Rest Framework, the way **Ravyn** designed was very much within the same lines and with
all the huge community of developer in mind to make a transition almost immediate and simple as possible.

All the permission classes **must derive** from `BasePermission`.

The permissions **must** implement the `has_permission` and return `True` or `False`.

The permissions can also be `async` in case you need to run awaitables.

**An example of a permission for an user admin**.

```python
{!> ../../../docs_src/permissions/permissions.py !}
```

**An example of a permission for an user admin with async**.

```python
{!> ../../../docs_src/permissions/async/permissions.py !}
```

**An example of a permission for a project**

```python
{!> ../../../docs_src/permissions/simple_permissions.py !}
```

**An example of a permission for a project with async**

```python
{!> ../../../docs_src/permissions/async/simple_permissions.py !}
```

## Ravyn and permissions

Ravyn giving support to [Edgy](../databases/edgy/motivation.md) also provides some default permissions
that can be linked to the models also provided by **Ravyn**.

### IsAdminUser and example of provided permissions

This is a simple permission that extends the `BaseAbstractUserPermission` and checks if a user is authenticated or not.
The functionality of verifying if a user might be or not authenticated was separated from the
[Edgy](../databases/edgy/motivation.md) and instead you must implement the `is_user_authenticated()`
function when inheriting from `BaseAbstractUserPermission` or `IsAdminUser`.

## Ravyn and provided permissions

Ravyn provides some default permissions that can be used in your projects but not too many as every project has
special needs and rules.

* **DenyAll** - As the name suggests, blocks access to anyone. Can be useful if an API is under maintenance.
* **AllowAny** - The opposite of DenyAll. Allows access to everyone. Useful as permission for the top Ravyn
application.
* **IsAdminUser** - Checks if a user is admin or not by inheriting the object and implementing `is_user_staff` function.
* **IsAuthenticated** - Checks if a user is authenticated by inheriting from the object and implementing the logic
for `is_user_authenticated` function.
* **IsAuthenticatedOrReadOnly** - Checks if a user is authenticated or a read only request. For the autenticated
part the `is_user_authenticated` needs to be implemented.

### How to use

To use the `IsAdminUser`, `IsAuthenticated` and `IsAuthenticatedOrReadOnly` is as simple as the example below.

```python
{!> ../../../docs_src/permissions/admin.py !}
```

1. The main app `Ravyn` has an `AllowAny` permission for the top level
2. The `UserAPIView` object has a `IsUserAuthenticated` allowing only authenticated users to access any
of the endpoints under the class (endpoints under `/users`).
3. The `/users/admin` has a permission `IsAdmin` allowing only admin users to access the specific endpoint

### More on permissions

The permissions internally are checked from top down which means you can place permissios at any
given part of the [level](../application/levels.md) making it more dynamic and allowing to narrow
it down to a granular level that is managenable.

Internally, Ravyn runs all the validations and checks and on an application level, the only
thing you need to make sure is to **implement the `has_permission`** on any derived class of
[BasePermission](#basepermission-and-custom-permissions).

## Permissions summary

1. All permissions must inherit from `BasePermission`.
2. `BasePermission` has the `has_permission(request Request, controller: "APIGateHandler") and it can
be `async` or not.
3. The [handlers](../routing/handlers.md), [Gateway](../routing/routes.md#gateway),
[WebSocketGateway](../routing/routes.md#websocketgateway), [Include](../routing/routes.md#include)
and [Ravyn](../application/applications.md) can have as many permissions as you want.

## API Reference

Check out the [API Reference for Permissions](../references/permissions.md) for more details.
