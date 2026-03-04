# Dependency Injection

Ravyn's dependency system helps you keep handlers thin and business logic reusable.

This guide focuses on production patterns with `Inject`, `Injects`, and `Factory`.

---

## Why DI matters in larger apps

Without DI, handlers tend to accumulate infrastructure logic.

With DI, you separate concerns:

```text
HTTP handler
   -> injected service
       -> injected repository/client
```

This improves testability and keeps boundaries explicit.

---

## Core building blocks

- `Inject(provider)` registers how to build a dependency.
- `Injects()` receives the resolved dependency in the handler signature.
- `Factory(...)` creates dependency providers from classes/callables.

---

## Pattern 1: service injection

```python
from ravyn import Inject, Injects, Ravyn, get


class UserService:
    async def profile(self, user_id: int) -> dict:
        return {"id": user_id, "name": f"User {user_id}"}


def get_user_service() -> UserService:
    return UserService()


@get("/users/{user_id}", dependencies={"service": Inject(get_user_service)})
async def get_user(user_id: int, service: UserService = Injects()) -> dict:
    return await service.profile(user_id)


app = Ravyn(routes=[get_user])
```

---

## Pattern 2: compose dependencies

Providers can depend on other providers.

```python
from ravyn import Inject, Injects, Requires, get


def get_settings() -> dict:
    return {"region": "eu"}


def get_api_client(settings: dict = Requires(get_settings)) -> dict:
    return {"base_url": f"https://api.{settings['region']}.example.com"}


@get(
    "/client",
    dependencies={
        "client": Inject(get_api_client),
    },
)
def client_info(client: dict = Injects()) -> dict:
    return client
```

This keeps construction logic centralized and reusable.

---

## Pattern 3: class-based factories

```python
from ravyn import Factory, Inject, Injects, get


class TokenService:
    def issue(self) -> str:
        return "token-123"


def get_token_service() -> TokenService:
    return TokenService()


token_factory = Factory(get_token_service)


@get("/token", dependencies={"service": Inject(token_factory)})
def token(service: TokenService = Injects()) -> dict:
    return {"token": service.issue()}
```

Use `Factory` when you want explicit construction wrappers and reusable provider definitions.

---

## Request-level flow

```text
request arrives
  -> resolve dependency graph
  -> run handler with injected values
  -> serialize handler result
```

If a dependency fails, Ravyn stops before business logic executes.

---

## Practical recommendations

- Inject services, not ORM sessions or low-level objects directly into every handler.
- Keep provider functions small and deterministic.
- Use type hints on injected parameters for readability.
- Group shared providers in dedicated modules (`dependencies.py`, `providers.py`).

---

## Related pages

- [Beginner Dependencies](../beginner/08-dependencies.md)
- [Architecture Patterns](./05-architecture-patterns.md)
- [Protocols](../../protocols.md)
- [Testing](./02-testing.md)

## What's Next?

Continue to [Advanced Concepts](./07-advanced-concepts.md) to connect DI with larger application design patterns.
