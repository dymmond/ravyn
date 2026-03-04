# Architecture Patterns

When Ravyn projects grow, architecture decisions start to matter more than syntax. This guide shows practical patterns and when to choose each one.

---

## A simple decision map

```text
Small API, single team, fast iteration
  -> Monolith with feature folders

Growing API, multiple domains, independent ownership
  -> Modular / feature-based with Includes and Routers

Complex business rules and long-lived domains
  -> Layered or DDD-inspired structure

Independent deploy/release cycles per domain
  -> Microservices (HTTP/gRPC between services)
```

---

## Baseline structure for most projects

For many production Ravyn apps, this is a strong default:

```text
app/
  main.py
  settings.py
  users/
    routes.py
    service.py
    schemas.py
  billing/
    routes.py
    service.py
    schemas.py
```

Use `Include` in `main.py` to keep composition explicit.

```python
from ravyn import Include, Ravyn


app = Ravyn(
    routes=[
        Include("/users", namespace="app.users.routes"),
        Include("/billing", namespace="app.billing.routes"),
    ]
)
```

---

## Pattern 1: Monolith (clean and simple)

All code ships as one service.

### When it fits

- Team is small.
- Domains are tightly coupled.
- Operational simplicity matters most.

### Example

```python
from ravyn import Ravyn, get


@get("/")
def home() -> dict:
    return {"message": "Welcome"}


app = Ravyn(routes=[home])
```

---

## Pattern 2: Modular feature-based architecture

Split code by domain (`users`, `orders`, `payments`).

### Why this is often the best middle ground

- Better ownership by feature.
- Lower merge conflicts.
- Easier onboarding for new developers.

### Example module

```python
# app/users/routes.py
from ravyn import get


@get("/")
def list_users() -> dict:
    return {"users": ["Alice", "Bob"]}
```

```python
# app/main.py
from ravyn import Include, Ravyn


app = Ravyn(routes=[Include("/users", namespace="app.users.routes")])
```

---

## Pattern 3: Layered / DDD-inspired approach

Separate transport, business, and persistence concerns.

```text
HTTP layer (routes/controllers)
    -> Application/service layer
        -> Repository/DAO layer
            -> Database or external systems
```

### Ravyn mapping

- HTTP layer: `Gateway`, `Router`, `Controller`
- Service/repository wiring: `Inject`, `Injects`, `Factory`
- Policies: `permissions`, middleware, interceptors

### Example

```python
from ravyn import Inject, Injects, Ravyn, get


class UserService:
    async def list(self) -> list[str]:
        return ["Alice", "Bob"]


def get_user_service() -> UserService:
    return UserService()


@get("/users", dependencies={"service": Inject(get_user_service)})
async def list_users(service: UserService = Injects()) -> dict:
    return {"users": await service.list()}


app = Ravyn(routes=[list_users])
```

---

## Pattern 4: Microservices

Split domains into independently deployable services.

### Use this when

- Teams release independently.
- Different scalability profiles are required.
- Service boundaries are stable and intentional.

Ravyn supports this model with normal HTTP boundaries and experimental gRPC integration.

---

## Common pitfalls

### 1. Premature microservices

Start modular inside one service first. Extract later when boundaries are proven.

### 2. Domain logic in handlers

Keep handlers thin; move business rules into services/DAOs.

### 3. Inconsistent route composition

Use a single composition style (`Include` by namespace or explicit route lists) to keep route trees predictable.

---

## Related pages

- [Dependency Injection](./06-dependency-injection.md)
- [Advanced Concepts](./07-advanced-concepts.md)
- [Routing](../../routing/index.md)
- [Extensions](../../extensions.md)
- [Experimental gRPC](../../experimental/grpc.md)

## What's Next?

Continue to [Dependency Injection](./06-dependency-injection.md) to formalize service wiring and keep architecture boundaries clean.
