# How to Structure a Large Ravyn Project

Use this guide when your API grows beyond a single file and needs stable module boundaries.

## Recommended structure

```text
app/
  main.py
  settings.py
  users/
    routes.py
    schemas.py
    service.py
  billing/
    routes.py
    schemas.py
    service.py
  shared/
    dependencies.py
    middleware.py
```

## Route composition

Keep top-level composition explicit in `main.py`:

```python
from ravyn import Include, Ravyn

app = Ravyn(
    routes=[
        Include("/users", namespace="app.users.routes"),
        Include("/billing", namespace="app.billing.routes"),
    ]
)
```

## Design rules

1. Keep handlers thin and move business logic to services.
2. Use one module per domain boundary.
3. Avoid cross-domain imports in route modules.
4. Share dependencies from a single `shared/dependencies.py`.

## Verification checklist

- route composition is centralized
- each domain module can be tested in isolation
- dependency registration has no import cycles

## Related pages

- [Architecture Patterns](../guides/more-advanced/05-architecture-patterns.md)
- [Routing](../routing/index.md)
- [Dependency Injection](../dependencies.md)
