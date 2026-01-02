# Lilya Permissions

Use Lilya's Pure ASGI permission system in your Ravyn applications. These protocol-based permissions follow the ASGI specification and can be reused across any ASGI framework for maximum portability and flexibility.

## What You'll Learn

- What Lilya permissions are and how they differ from Ravyn permissions
- Using the PermissionProtocol
- Creating Pure ASGI permissions
- Applying permissions at different application levels
- Integrating with Ravyn settings
- When to use Lilya vs Ravyn permissions

## Quick Start

```python
from ravyn import Ravyn, get
from lilya.protocols.permissions import PermissionProtocol
from lilya.types import ASGIApp, Scope, Receive, Send
from ravyn.exceptions import NotAuthorized

class AdminOnlyPermission(PermissionProtocol):
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Check if user is admin
        if not scope.get("user", {}).get("is_admin"):
            raise NotAuthorized("Admin access required")
        await self.app(scope, receive, send)

@get("/admin/dashboard")
def admin_dashboard() -> dict:
    return {"data": "Admin dashboard"}

app = Ravyn(
    routes=[...],
    permissions=[AdminOnlyPermission]
)
```

!!! warning "Important"
    Do not mix Lilya permissions with Ravyn permissions. Both are independent systems and combining them can cause security issues.

---

## Lilya vs Ravyn Permissions

## How to use it

Literally in the **same way** you would use in [Lilya](https://www.lilya.dev/permissions). Yes,
that simple!

### PermissionProtocol

For those coming from a more enforced typed language like Java or C#, a protocol is the python equivalent to an
interface.

```python
{!> ../../../docs_src/permissions/lilya/sample.py !}
```

The `PermissionProtocol` is simply an interface to build permissions for **Ravyn/Lilya** by enforcing the implementation of the `__init__` and the `async def __call__`.

Enforcing this protocol also aligns with writing a [Pure ASGI Permission](https://www.lilya.dev/permissions#pure-asgi-permission).

## Permission and the application

Creating this type of permissions will make sure the protocols are followed and therefore reducing development errors
by removing common mistakes.

To add middlewares to the application is very simple. You can add it at any level of the application.
Those can be included in the `Lilya`/`ChildLilya`, `Include`, `Path` and `WebSocketPath`.

=== "Application level"

    ```python
    {!> ../../../docs_src/permissions/lilya/adding_permission.py !}
    ```

=== "Any other level"

    ```python
    {!> ../../../docs_src/permissions/lilya/any_other_level.py !}
    ```

## Pure ASGI permission

Lilya follows the [ASGI spec](https://asgi.readthedocs.io/en/latest/).
This capability allows for the implementation of ASGI permissions using the
ASGI interface directly. This involves creating a chain of ASGI applications that call into the next one.

**Example of the most common approach**

```python
from lilya.types import ASGIApp, Scope, Receive, Send

class MyPermission:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.app(scope, receive, send)
```

When implementing a Pure ASGI permission, it is like implementing an ASGI application, the first
parameter **should always be an app** and the `__call__` should **always return the app**.

## Permissions and the settings

One of the advantages of Lilya is leveraging the settings to make the codebase tidy, clean and easy to maintain.
As mentioned in the [settings](../application/settings.md) document, the permissions is one of the properties available
to use to start a Lilya application.

```python
{!> ../../../docs_src/permissions/lilya/settings.py !}
```

### Notes

What you should avoid doing?

You cannot mix Lilya permissions with Ravyn permissions. Both are independent and combined can cause security concerns.

Lilya permissions are called on the execution of the `__call__` of an ASGI app and Ravyn permissions
on a `handle_dispatch` level.
