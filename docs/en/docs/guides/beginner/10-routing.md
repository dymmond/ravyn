# A bit more about Routing

In this section, you’ll move from single-file routing to a structure that scales.

By the end, you’ll know when to use:

- Route decorators (`@get`, `@post`, ...)
- `Router` for grouping handlers
- `Include` for route-tree composition
- `Controller` for class-based endpoints

---

## Route organization mental model

```text
Ravyn app
  -> Include('/api', ...)
      -> Router / route list
          -> Gateway / handler
```

As your API grows, this layered approach helps keep files small and navigation predictable.

---

## Step 1: Start with simple handlers

```python
from ravyn import Ravyn, get


@get("/hello")
def say_hello() -> dict:
    return {"message": "Hello, world!"}


app = Ravyn(routes=[say_hello])
```

This is great for small APIs or early prototypes.

---

## Step 2: Group routes with `Router`

```python
from ravyn import Ravyn, Router


user_router = Router()


@user_router.get("/users")
def list_users() -> list[str]:
    return ["user1", "user2"]


@user_router.post("/users")
def create_user() -> dict:
    return {"status": "created"}


app = Ravyn(routes=[user_router])
```

Use this when a feature has multiple endpoints that belong together.

---

## Step 3: Compose larger apps with `Include`

```python
from ravyn import Include, Ravyn, Router


api_router = Router()


@api_router.get("/status")
def status() -> dict:
    return {"status": "ok"}


app = Ravyn(
    routes=[
        Include("/api", routes=[api_router]),
    ]
)
```

Now your endpoint is available at `/api/status`.

---

## Step 4: Use class-based routing with `Controller`

```python
from ravyn import Controller, Ravyn, get


class HealthController(Controller):
    @get("/health")
    def health(self) -> dict:
        return {"ok": True}


app = Ravyn(routes=[HealthController])
```

Use controllers when multiple endpoints share class-level concerns.

---

## Choosing the right tool

| Need | Best Fit |
|------|----------|
| One or two endpoints | Decorated handlers |
| A feature module with many endpoints | `Router` |
| Prefix/group subtrees (`/api`, `/v1`) | `Include` |
| Shared class behavior | `Controller` |

---

## Practical file layout

```text
app/
  main.py
  users/
    routes.py
  billing/
    routes.py
```

`main.py`:

```python
from ravyn import Include, Ravyn


app = Ravyn(
    routes=[
        Include("/users", namespace="app.users.routes"),
        Include("/billing", namespace="app.billing.routes"),
    ]
)
```

This keeps each feature isolated while maintaining a clean top-level app file.

---

## Related pages

- [Routing (core docs)](../../routing/index.md)
- [Routes](../../routing/routes.md)
- [Router](../../routing/router.md)
- [Controllers](../../routing/controllers.md)
- [Webhooks](../../routing/webhooks.md)

## What's Next?

You completed the beginner path. Next, continue with [Security](../more-advanced/01-security.md) in the advanced section.
