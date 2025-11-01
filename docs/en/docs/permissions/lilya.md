# Lilya Permissions

Now if you are not familiar with [Lilya Permisions](https://www.lilya.dev/permissions) now it would
be a good time to get acquainted.

Historically speaking, [Ravyn Permissions](./ravyn.md) came first and offer a different design
and feel than the Lilya ones.

Lilya born after Ravyn to be the core and grew to be one of the most powerful frameworks out there,
also came with permissions but in the concept of "Pure ASGI Permission".

## Relation with Ravyn

Because Ravyn is built on top of Lilya and Lilya does in fact the heavy lifting of the core, it
would make sense to provide **also** the integration with the permissions and the reason for that
its because Lilya Pure ASGI Permissions can be reused in Ravyn or any other ASGI framework without
any incompatibilities since it follows the ASGI specification.

Now lets get into the good stuff and see how we can use it in Ravyn.

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
