# Permissions

Control who can access what in your Ravyn application. Permissions let you restrict endpoints based on user roles, authentication status, or custom logic. Perfect for building secure APIs with fine-grained access control.

## What You'll Learn

- What permissions are and when to use them
- Authentication vs Authorization
- Using Ravyn's native permission system
- Using Lilya's permission protocol
- Applying permissions at different levels
- Creating custom permission classes

## Quick Start

```python
from ravyn import Ravyn, get
from ravyn.permissions import IsAuthenticated

@get("/profile", permissions=[IsAuthenticated])
def get_profile(request) -> dict:
    return {"user": request.user.username}

app = Ravyn(
    routes=[...],
    permissions=[IsAuthenticated]  # Apply globally
)
```

---

## Authentication vs Authorization

## Ravyn Native System

The Ravyn native system allows you to define permissions directly within your application. Here is an example:

```python
from ravyn.permissions import Permission

class ViewDashboardPermission(Permission):
    def has_permission(self, request, view):  # or async has_permission
        return request.user.is_authenticated and request.user.has_role('admin')
```

## Lilya Permissions

Lilya is the core of Ravyn that can be integrated to manage permissions. Here is an example of how to use Lilya with Ravyn:

```python
from typing import Any

from lilya.protocols.permissions import PermissionProtocol
from lilya.types import ASGIApp

from ravyn.exceptions import NotAuthorized

class EditProfilePermission(PermissionProtocol):
    def __init__(self, app: ASGIapp, *args: Any, **kwargs: Any):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotAuthorized()
```

Both systems offer flexibility and can be used based on your project's requirements and both **cannot be combined**. You
should either use one or the other but not both.

Its entirely up to you.
