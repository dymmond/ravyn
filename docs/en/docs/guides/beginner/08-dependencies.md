# Dependencies

In this section, you'll learn how to use dependency injection with Ravyn.

Dependencies are reusable logic that can be injected into routes, services, and anywhere else in your application.

---

## Basic Dependency Injection

Use `Inject` to register a dependency and `Injects` to consume it:

```python
from ravyn import get, Inject, Injects

def get_token():
    return "super-secret-token"

@get("/secure", dependencies={"token": Inject(get_token)})
def secure(token: str = Injects()) -> dict:
    return {"token": token}
```

---

## Class-Based Dependencies

Dependencies can be classes too:

```python
class AuthService:
    def get_user(self):
        return {"name": "John Doe"}

@get("/user", dependencies={"auth": Inject(AuthService)})
def user(auth: AuthService = Injects()) -> Any:
    return auth.get_user()
```

---

## Dependency Lifetimes

Dependencies in Ravyn are singletons by default.
If you want a **new instance per request**, you can pass `use_cache=False`:

```python
@get("/random", dependencies={"service": Inject(SomeService, use_cache=False)})
def random(service: SomeService = Injects()) -> Any:
    return service.new_value()
```

---

## Nested Dependencies

Dependencies can depend on other dependencies:

```python
class Logger:
    def log(self, msg: str):
        print(f"Log: {msg}")

class Processor:
    def __init__(self, logger: Logger):
        self.logger = logger

    def run(self):
        self.logger.log("Running...")
        return "done"

@get("/run", dependencies={"logger": Inject(Logger), "proc": Inject(Processor)})
def run(proc: Processor = Injects()) -> None:
    return proc.run()
```

## What's Next?

Now that you’ve mastered dependencies, let’s explore how to use request and response models to validate and document your APIs.

👉 Continue to [requests and responses](./09-requests-and-responses.md).
