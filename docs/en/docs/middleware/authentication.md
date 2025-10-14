# Authentication Middleware

This special middleware comes from **Lilya** and is used to authenticate users on every request but adapted for Ravyn.

These are a very special middlewares and helps with any authentication middleware that can be used within
a **Ravyn** application but like everything else, you can design your own.

`AuthenticationMiddleware` is an implementation using backends and most people will prefer it.
See [Authentication](#authentication) for more details.

Majority of the things here are from Lilya and we just added the ability to use it as a Ravyn middleware with almost no changes.

### Example of a JWT middleware class

```python title='/src/middleware/jwt.py'
{!> ../../../docs_src/middleware/auth/auth_middleware_example.py !}
```

1. Import the `AuthenticationMiddleware` from `ravyn.middleware.authentication`.
2. Implement the `authenticate` and return `tuple[AuthCredentials, UserInterface]` (AuthResult) or None or raise.

#### Import the middleware into a Lilya application

=== "From the application instance"

    ```python
    from ravyn import Ravyn
    from lilya.middleware import DefineMiddleware
    from .middleware.jwt import JWTAuthMiddleware


    app = Ravyn(routes=[...], middleware=[DefineMiddleware(JWTAuthMiddleware, ...)])
    ```

=== "From the settings"

    ```python
    from ravyn import Ravyn, RavynSettings
    from lilya.middleware import DefineMiddleware


    class AppSettings(RavynSettings):

        @property
        def middleware(self) -> list[DefineMiddleware]:
            return [
                # you can also use absolute import strings
                DefineMiddleware("project.middleware.jwt.JWTAuthMiddleware")
            ]

    # load the settings via RAVYN_SETTINGS_MODULE=src.configs.live.AppSettings
    app = Ravyn(routes=[...])
    ```

!!! Tip
    To know more about loading the settings and the available properties, have a look at the
    [settings](../application/settings.md) docs.

## Authentication

Ravyn provides a straightforward yet robust interface for managing authentication and permissions (from Lilya).
By installing `AuthenticationMiddleware` with a suitable authentication backend, you can access the `request.user` and `request.auth`
interfaces within your endpoints.

```python
{!> ../../../docs_src/authentication/basic_example.py !}
```

When not using an user management we can also do something like:

```python
{!> ../../../docs_src/authentication/static_pw_auth.py !}
```

## `authenticate()` from `AuthenticationMiddleware`

This is the main method that goes through the backends and tries to authenticate the user.

Sometimes you want to override this method to add some custom logic before or after the authentication.

```python title='project/middleware/jwt.py'
{!> ../../../docs_src/middleware/auth/auth_middleware_example.py !}
```

Here we passed extra information to the `authenticate` of the backend to be used for internal operations.

## Backends

For backends you need the `AuthenticationMiddleware` (not the BaseAuthMiddleware from Lilya). Only here you can provide them
via the `backend` parameter. This can be a sequence of AuthenticationBackend instances or also a single one.

If a backend doesn't find the user it can return None in `authenticate` to skip to the next Backend.

If a backend raises an error in `authenticate`, the whole chain is stopped.

Backends are retrievable on the middleware via the `backend` attribute. It is always a list.

## Users

Once you have installed `AuthenticationMiddleware`, the `request.user` interface becomes
available to your endpoints and other middleware.

The implementation should implement the interface `UserInterface`, which includes two properties and any additional information your user model requires.

* `.is_authenticated`
* `.display_name`

Ravyn provides two built-in user implementations: `AnonymousUser()` and `BasicUser(username)`.

## AuthCredentials

Authentication credentials should be considered distinct from user identities.
An authentication scheme must be capable of granting or restricting specific privileges independently of the user's identity.

The `AuthCredentials` class provides the basic interface that `request.auth`
exposes:

* `.scopes`

## Custom authentication error responses

You can customize the error response sent when an `AuthenticationError` is raised by an authentication backend:

```python
from lilya.middleware import DefineMiddleware

from ravyn import JSONResponse, Ravyn, Request
from ravyn.middleware.authentication import AuthenticationMiddleware


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)

app = Ravyn(
    middleware=[
        DefineMiddleware(AuthenticationMiddleware, backend=BasicAuthBackend(), on_error=on_auth_error),
    ],
)
```
