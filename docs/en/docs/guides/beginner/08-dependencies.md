# Dependencies

In this section, you'll learn how to use dependency injection with Ravyn.

Dependencies let you share reusable logic across handlers without duplicating setup code.

## Basic dependency injection

Use `Inject` to register a dependency and `Injects` to receive it.

```python
from ravyn import Gateway, Inject, Injects, Ravyn, get


def get_token() -> str:
    return "super-secret-token"


@get()
def secure(token: str = Injects()) -> dict:
    return {"token": token}


app = Ravyn(
    routes=[Gateway("/secure", handler=secure)],
    dependencies={"token": Inject(get_token)},
)
```

## Class-based dependencies

For class construction, prefer `Factory`.

```python
from ravyn import Factory, Inject, Injects, get


class AuthService:
    def get_user(self) -> dict:
        return {"name": "John Doe"}


@get("/user", dependencies={"auth": Inject(Factory(AuthService))})
def user(auth: AuthService = Injects()) -> dict:
    return auth.get_user()
```

## Caching behavior (`use_cache`)

`Inject(..., use_cache=False)` is the default.

- `use_cache=False`: resolve dependency each time it is needed.
- `use_cache=True`: reuse the resolved value during the dependency lifecycle.

```python
from ravyn import Inject

# No cache (default)
no_cache = Inject(get_token)

# Cached
cached = Inject(get_token, use_cache=True)
```

## Nested dependencies

A dependency can depend on another dependency.

```python
from ravyn import Inject, Injects, get


def get_settings() -> dict:
    return {"env": "production"}


def get_config(settings: dict = Injects()) -> str:
    return f"Running in {settings['env']}"


@get(
    "/config",
    dependencies={
        "settings": Inject(get_settings),
        "config": Inject(get_config),
    },
)
def read_config(config: str = Injects()) -> dict:
    return {"config": config}
```

## Next step

Continue to [requests and responses](./09-requests-and-responses.md).
