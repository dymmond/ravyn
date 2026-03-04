# Troubleshooting

Common issues and quick fixes when working with Ravyn.

## Routing issues

### Route returns 404

Check the basics first:

1. Path starts with `/`.
2. Handler is registered in `routes=[...]`.
3. Include namespace/module exists.
4. More specific routes are declared before generic ones.

```python
# Wrong: generic route first
app = Ravyn(routes=[
    Gateway("/{id}", handler=get_item),
    Gateway("/special", handler=special_item),
])

# Correct: specific first
app = Ravyn(routes=[
    Gateway("/special", handler=special_item),
    Gateway("/{id}", handler=get_item),
])
```

### Include does not load routes

If using `Include(..., namespace="...")`, confirm the module exists and exposes the expected pattern variable (default: `route_patterns`).

## Settings issues

### Custom settings not loading

Set `RAVYN_SETTINGS_MODULE` before starting the app:

```shell
RAVYN_SETTINGS_MODULE='myapp.settings.DevelopmentSettings' palfrey app:app --reload
```

You can also pass `settings_module=YourSettingsClass` directly into `Ravyn(...)`.

## Dependency injection issues

### Injected value is missing

- Register dependency with `Inject(...)`.
- Receive value with `Injects()`.
- Ensure dependency key names match.

```python
# Good
@get("/items", dependencies={"db": Inject(get_db)})
def items(db = Injects()):
    ...
```

### Factory dependency fails to import

If using a string provider path in `Factory("...")`, verify the module path and symbol are importable.

## Middleware issues

### Middleware class does not execute

Confirm middleware is ASGI-compatible and receives `(scope, receive, send)`.

```python
class MyMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
```

Also make sure it is wrapped with `DefineMiddleware(...)` where required.

## Security issues

### Security shows in docs but handler gets no credentials

For security dependencies, use both:

- `dependencies={"x": Inject(security_dependency)}`
- `security=[security_dependency]`

`security=[...]` documents OpenAPI requirements; `dependencies=...` resolves runtime values.

## OpenAPI issues

### Endpoint missing from docs

Check for `include_in_schema=False` at route, gateway, include, or app level.

### Wrong response schema in docs

Make sure handler return annotations are explicit and aligned with actual return types.

## CLI/directives issues

### `ravyn runserver` cannot find app

Use one of:

- `ravyn --app myproject.main:app runserver`
- `export RAVYN_DEFAULT_APP=myproject.main:app`

If using auto-discovery, confirm one of the discovery files (`main.py`, `app.py`, `application.py`, `asgi.py`) exists in the expected location.

## Still stuck?

- Check the [API Reference](./references/index.md) for exact signatures.
- Compare with examples in `docs_src/` to verify usage.
- Open a discussion or issue in the Ravyn repository with a minimal reproducible example.
