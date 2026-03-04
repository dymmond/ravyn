# Middlewares

In this section, you'll learn how middleware works in Ravyn and how to add your own.

## What is middleware?

Middleware is ASGI code that runs around request handling.

Common uses:

- Logging.
- Authentication.
- Compression.
- Security headers.
- Cross-cutting validation.

## Adding middleware

Use `DefineMiddleware` and pass middleware classes in `Ravyn(..., middleware=[...])`.

```python
from lilya.middleware import DefineMiddleware
from lilya.types import ASGIApp, Receive, Scope, Send
from ravyn import Gateway, Ravyn, get


class LogMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            print(f"{scope['method']} {scope['path']}")
        await self.app(scope, receive, send)


@get("/")
async def home() -> dict:
    return {"hello": "world"}


app = Ravyn(
    routes=[Gateway(handler=home)],
    middleware=[DefineMiddleware(LogMiddleware)],
)
```

## Built-in middleware examples

### CORS

```python
from ravyn import CORSConfig, Ravyn

app = Ravyn(
    routes=[],
    cors_config=CORSConfig(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    ),
)
```

### Trusted host

```python
from lilya.middleware import DefineMiddleware
from ravyn import Ravyn
from ravyn.middleware import TrustedHostMiddleware

app = Ravyn(
    routes=[],
    middleware=[DefineMiddleware(TrustedHostMiddleware, allowed_hosts=["example.com", "localhost"])],
)
```

## Middleware order

Middleware executes in declaration order from outermost to innermost.

```python
middleware=[DefineMiddleware(A), DefineMiddleware(B)]
```

Execution order:

1. `A` before request.
2. `B` before request.
3. Handler.
4. `B` after handler.
5. `A` after handler.

## Next step

Continue to [background tasks](07-background-tasks.md).
