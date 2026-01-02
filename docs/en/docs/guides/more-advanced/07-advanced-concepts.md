# Advanced Concepts in Ravyn

This section provides a deep technical dive into advanced features of Ravyn. These go beyond simple route handling
and API development, showcasing core extensibility mechanisms built into the framework.

This guide is intended for developers building scalable, maintainable, and extensible systems.

---

## Permissions

Permissions in Ravyn allow fine-grained control over who can access certain routes.
Permissions are declared using `BasePermission` and can be globally or locally applied.

### Why use Permissions?
- Enforce role-based access control (RBAC)
- Protect endpoints without mixing authorization logic into handlers
- Reuse authorization logic across multiple routes or gateways

### Creating a Permission Class

```python
from ravyn.permissions import BasePermission
from ravyn import Request

class IsAdmin(BasePermission):
    def has_permission(self, request: Request) -> bool:  # or async def has_permission(...)
        return request.headers.get("X-ADMIN") == "true"
```

### Applying Permissions to a Route

```python
from ravyn import get, HTTPException

@get("/admin", permissions=[IsAdmin])
def admin_dashboard() -> dict:
    return {"message": "Welcome admin!"}
```

If `IsAdmin` fails, a `403 Forbidden` is returned.

---

## Observables

Observables provide an event-driven model in Ravyn to emit and listen for events between components.

### Why Observables?
- Decouple business logic
- Enable audit logs, metrics, triggers
- Improve maintainability by externalizing side effects

### Declaring an Observable

```python
from ravyn import observable

@observable(sender=["user_created"])
def handle_user_created(payload: dict) -> None: ...
```

### Emitting an Observable

When declaring the `sender` automatically will trigger the event for those `listening` to act.

```python
from ravyn import observable

@observable(listen=["user_created"])
def handle_user_created() -> None:
# do something here
```
---

## Interceptors

Interceptors allow manipulation of request/response flow before or after they are processed by the route handler.

### Why Interceptors?
- Reusable, non-invasive logic (e.g., logging, metrics, transformation)
- Avoid bloated middlewares or tightly-coupled decorators

### Creating an Interceptor

```python
from loguru import logger

from ravyn import RavynInterceptor
from lilya.types import Receive, Scope, Send

class LoggingInterceptor(RavynInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        # Log a message here
        logger.info("This is my interceptor being called before reaching the handler.")
```

### Applying an Interceptor

```python
from ravyn import Ravyn

app = Ravyn(
    routes=[],
    interceptors=[LoggingInterceptor]
)
```

---

## Decorators

Ravyn supports decorators to extend or modify the behavior of route handlers.

### Common Use Cases
- Caching
- Retry logic
- Custom validation
- Metrics collection

### Example: Timing Decorator
```python
import time
from functools import wraps

def timing(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await fn(*args, **kwargs)
        print(f"Executed {fn.__name__} in {time.time() - start}s")
        return result
    return wrapper
```

Apply it to any handler:
```python
@get("/ping")
@timing
def ping() -> dict:
    return {"pong": True}
```

---

## Encoders

In Ravyn, encoders enable the framework to understand, encode, and serialize custom objects seamlessly. This flexibility
allows developers to integrate various data types without being constrained to specific serialization libraries.

### Benefits of Encoders

* **Flexibility**: Integrate custom data types without relying solely on built-in serializers.
* **Extensibility**: Design and register your own encoders to handle specific serialization needs.
* **Future-Proofing**: Ensure compatibility with various libraries and frameworks by defining custom serialization logic.

### Example: Encoding a Custom Type

```python
from typing import Any
from ravyn.encoders import Encoder

class Money:
    def __init__(self, amount: float, currency: str):
        self.amount = amount
        self.currency = currency

class MoneyEncoder(Encoder):
    def is_type(self, value: any) -> bool:
        return isinstance(value, Money)

    def serialize(self, value: Money) -> dict:
        return {"amount": value.amount, "currency": value.currency}

    def encode(self, annotation: Any, value: Any) -> dict:
        return annotation(**value)
```

* **is_type**: Checks if the value is an instance of the Money class.
* **serialize**: Defines how to convert the Money object into a serializable dictionary.
* **encode**: Brings the data passed and creates a Money object.

### Register the Encoder

```python
from ravyn import Ravyn

app = Ravyn(
    routes=[],
    encoders=[MoneyEncoder]
)
```

Now, any handler returning a `Money` object will automatically be encoded.

---

## Extensions (Pluggables)

Extensions allow you to add new functionality or integrate third-party systems in a clean, pluggable way.

### Use Cases
- Database integrations
- Queues (e.g., RabbitMQ, Kafka)
- Third-party APIs (Stripe, Twilio)

### Creating an Extension

```python
from ravyn import Extension

class MyDBExtension(Extension):
    def extend(self, app):
        app.state.db = connect_to_database()
```

### Loading an Extension

```python
from ravyn import Ravyn, Pluggable

app = Ravyn(
    routes=[],
    extensions={'my-extension': Pluggable(MyDBExtension)}
)
```

Now `app.state.db` is accessible throughout the app.

More [details](../../extensions.md) can be found with a lot more examples to go through.

---

## Summary

This document covered:

Permissions for access control
Observables for event-driven communication
Interceptors to wrap request/response
Decorators for reusable logic
Encoders for custom serialization
Extensions for third-party integrations

These features together form a powerful advanced toolkit to build modular and maintainable Ravyn applications.

👉 Ready to supercharge your app with high-performance caching? Continue to [caching](./08-caching.md) to learn about Ravyn’s caching system with memory and Redis support.
