# JWT

As part of the support, Ravyn developed an authentication middleware using pyjwt allowing JWT integration
with the current [supported models](./models.md#user).

## JWTAuthMiddleware

This simple but effective middleware extends the [AuthenticationMiddleware](../../middleware/index.md#authenticationmiddleware)
and enables the authentication via JWT.

```python
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware, JWTAuthBackend
```

### Parameters

* `app` - Any ASGI app instance. E.g.: Ravyn instance.
* `config` - An instance of [JWTConfig](../../configurations/jwt.md) object.
* `user` - The user class (not instance!) being used by the application.

## How to use it

There are different ways of calling this middleware in any Ravyn application.

### Via settings

```python
{!> ../../../docs_src/databases/edgy/jwt/settings.py!}
```

### Via application instantiation

```python
{!> ../../../docs_src/databases/edgy/middleware/example1.py !}
```

### Via overriding the JWTAuthMiddleware

=== "Via app instance"

    ```python
    {!> ../../../docs_src/databases/edgy/middleware/example2.py !}
    ```

=== "Via app settings"

    ```python
    {!> ../../../docs_src/databases/edgy/middleware/example3.py !}
    ```

{!> ../../../docs_src/_shared/databases_important_note.md !}
