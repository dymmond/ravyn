# How to Add Observability and Logging

This guide provides a baseline observability setup for production APIs.

## 1. Configure structured logging

```python
import logging
from ravyn import LoggingConfig, Ravyn

logging_config = LoggingConfig(level="INFO")

app = Ravyn(
    routes=[...],
    logging_config=logging_config,
)
```

## 2. Add request-level logging middleware

```python
class RequestLogMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        method = scope.get("method")
        path = scope.get("path")
        logging.getLogger("api").info("request", extra={"method": method, "path": path})
        await self.app(scope, receive, send)
```

## 3. Add health and readiness endpoints

```python
from ravyn import get

@get("/healthz")
def health() -> dict:
    return {"status": "ok"}
```

## 4. Add error visibility

Use custom exception handlers to normalize application errors and route them to your monitoring stack.

## Related pages

- [Configurations: Logging](../configurations/logging.md)
- [Middleware](../middleware/index.md)
- [Exception Handlers](../exception-handlers.md)
