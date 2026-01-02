# Dependency Injection

Ravyn supports a powerful and flexible dependency injection system inspired by Angular and other modern frameworks. You can declare dependencies in a clean and declarative way, enabling separation of concerns, easy testing, and better structure for your application.

This guide walks through how to use Ravyn's dependency injection using `Inject` and `Injects`.

---

## Basic Usage

Use `Inject` in the `dependencies` argument of the route decorator to define a dependency provider. Then, retrieve it with `Injects` inside your handler.

### Example

```python
from ravyn import get, Inject, Injects

# A service we want to inject
def get_token() -> str:
    return "my-secret-token"

@get("/token", dependencies={"token": Inject(get_token)})
def read_token(token: str = Injects()) -> dict:
    return {"token": token}
```

Note: Every route handler must include an explicit return type in Ravyn.

---

## Injecting Custom Services

Dependency injection is not limited to simple values. You can also inject classes or more complex services.

### Example

```python
from ravyn import get, Inject, Injects

class Database:
    def connect(self) -> str:
        return "Connected to DB"

def get_db() -> Database:
    return Database()

@get("/db", dependencies={"db": Inject(get_db)})
def read_db(db: Database = Injects()) -> dict:
    return {"status": db.connect()}
```

---

## Sharing Dependencies Across Routes

Define your dependencies once and reuse them across multiple routes using a dictionary or shared module.

```python
# dependencies.py
from ravyn import Inject
from .services import get_db

common_dependencies = {
    "db": Inject(get_db),
}

# routes.py
from ravyn import get, Injects
from .dependencies import common_dependencies

@get("/users", dependencies=common_dependencies)
def list_users(db=Injects()) -> dict:
    return {"db": str(db)}
```

---

## Using Dependency Injection with Classes

You can inject dependencies into class-based handlers or services.

```python
from ravyn import Inject, Injects, get

class MyService:
    def greet(self, name: str) -> str:
        return f"Hello {name}"

def get_service() -> MyService:
    return MyService()

@get("/greet", dependencies={"service": Inject(get_service)})
def greet(service: MyService = Injects()) -> dict:
    return {"message": service.greet("Ravyn")}
```

---

## Lifecycle of Dependencies

- Functions used with `Inject()` are called **once per request**.
- Dependencies can be composed: you can inject dependencies inside other dependency functions.

```python
from ravyn import Inject, Requires

def get_settings():
    return {"env": "production"}

def get_config(settings=Requires(get_settings)):
    return f"Running in {settings['env']} mode"
```

---

## Tips

- Always annotate injected parameters with their type for clarity and validation.
- Avoid injecting raw functions as values; prefer dependency providers.
- If using `Requires()` inside a function that isn't a route, make sure it's declared properly.

---

## What's Next?

You now understand how to use dependency injection in Ravyn, from simple values to complex services.
