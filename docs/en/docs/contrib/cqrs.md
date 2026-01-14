# CQRS (Command Query Responsibility Segregation)

Ravyn inherits the CQRS implementation from Lilya with some minor changes since its agnostic
and makes it directly available via Ravyn API.

The documentation is the same but adapted to Ravyn needs and API.

## Overview

**CQRS (Command Query Responsibility Segregation)** is an architectural pattern that separates:

- **Commands** → operations that **change state**
- **Queries** → operations that **read state**

In CQRS, these two concerns are handled by **different execution paths**, often with different models,
validation rules, performance characteristics, and even storage mechanisms.

Ravyn provides a **lightweight, explicit, framework-native CQRS implementation** via `ravyn.contrib.cqrs`, designed to:

- integrate naturally with Ravyn endpoints
- remain async-first
- avoid hidden magic or global state
- work with Ravyn encoders and existing request/response patterns

This is **CQRS without ceremony**.

---

## Why CQRS exists

Traditional request handlers often mix responsibilities:

```
HTTP Request
 └── validate input
 └── fetch data
 └── mutate data
 └── apply business rules
 └── return response
```

As applications grow, this leads to:

- bloated endpoints
- unclear business boundaries
- difficult testing
- tight coupling between reads and writes
- poor scalability characteristics

!!! tip "CQRS addresses this by enforcing a simple rule"
    A command never returns data. A query never changes state.

---

## When CQRS makes sense

CQRS is **not mandatory** for every Ravyn application.

You should consider CQRS when:

- business logic becomes non-trivial
- writes and reads have different lifecycles
- multiple endpoints trigger the same write logic
- the same read logic is reused in many places
- you want explicit domain boundaries
- you want testable business logic outside HTTP

You probably **do not need CQRS** when:

- the app is CRUD-only
- logic is trivial
- performance and scale are not concerns
- endpoints are thin and unlikely to grow

CQRS is a **tool**, not a rule.

---

## CQRS in Ravyn

Ravyn's CQRS implementation lives in:

```shell
ravyn.contrib.cqrs
```

It provides:

- `CommandBus`
- `QueryBus`
- message envelopes
- handler registries
- optional middleware pipelines
- decorator-based registration (optional)

It **does not** introduce:

- background queues
- persistence layers
- event sourcing
- transport protocols

Those can be layered on later if needed.

---

## Core concepts

### Commands

A **Command** represents an **intent to change state**.

**Examples**:

- Create a user
- Update a password
- Delete an order
- Send an email

**Commands**:

- are explicit objects
- are validated before execution
- **do not return data**
- may fail

```python
class CreateUser:
    def __init__(self, user_id: str, email: str) -> None:
        self.user_id = user_id
        self.email = email
```

---

### Queries

A **Query** represents a **request for information**.

**Examples**:

- Get user profile
- List orders
- Check permissions

**Queries**:

- never mutate state
- return a value
- can be cached
- should be idempotent

```python
class GetUserEmail:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
```

---

### Handlers

Handlers contain **business logic**, not HTTP logic.

#### Command handler

```python
def handle_create_user(cmd: CreateUser) -> None:
    database.insert_user(cmd.user_id, cmd.email)
```

#### Query handler

```python
def handle_get_user_email(q: GetUserEmail) -> str | None:
    return database.get_email(q.user_id)
```

Handlers:

- are plain Python callables
- may be sync or async
- are easy to test
- can be reused across endpoints

---

## CommandBus and QueryBus

### CommandBus

Used to **dispatch commands**.

```python
from ravyn.contrib.cqrs import CommandBus

command_bus = CommandBus()
command_bus.register(CreateUser, handle_create_user)

await command_bus.dispatch(CreateUser("u1", "u1@example.com"))
```

- one handler per command type
- no return value
- exceptions bubble up

---

### QueryBus

Used to **execute queries**.

```python
from ravyn.contrib.cqrs import QueryBus

query_bus = QueryBus[str | None]()
query_bus.register(GetUserEmail, handle_get_user_email)

email = await query_bus.ask(GetUserEmail("u1"))
```

- returns a value
- supports sync and async handlers
- can be cached or optimized independently

---

## Using CQRS inside Ravyn endpoints

This is the **recommended usage pattern**.

### Example: Create and retrieve a user

```python
from ravyn import Ravyn, Gateway, JSONResponse, get, post, Request
from ravyn.contrib.cqrs import CommandBus, QueryBus
```

#### Setup buses and handlers

```python
store: dict[str, str] = {}

command_bus = CommandBus()
query_bus: QueryBus[str | None] = QueryBus()

def handle_create(cmd: CreateUser) -> None:
    store[cmd.user_id] = cmd.email

def handle_get(q: GetUserEmail) -> str | None:
    return store.get(q.user_id)

command_bus.register(CreateUser, handle_create)
query_bus.register(GetUserEmail, handle_get)
```

---

#### Write endpoint (Command)

```python
from ravyn import post, Request, JSONResponse

@post()
async def create_user(request: Request) -> JSONResponse:
    data = await request.json()

    await command_bus.dispatch(
        CreateUser(user_id=data["user_id"], email=data["email"])
    )
    return JSONResponse({"status": "created"}, status_code=201)
```

---

#### Read endpoint (Query)

```python
from ravyn import Request, JSONResponse, get

@get()
async def get_user(request: Request):
    user_id = request.path_params["user_id"]
    email = await query_bus.ask(GetUserEmail(user_id))

    if email is None:
        return JSONResponse({"detail": "not found"}, status_code=404)

    return JSONResponse({"user_id": user_id, "email": email})
```

---

#### Ravyn application

```python
from ravyn import Ravyn, Gateway

app = Ravyn(
    routes=[
        Gateway("/users", handler=create_user),
        Gateway("/users/{user_id}", handler=get_user),
    ]
)
```

---

## Why this is better than logic in endpoints

Without CQRS:

- logic is locked inside HTTP
- cannot be reused elsewhere
- hard to test without HTTP clients

With CQRS:

- handlers are pure business logic
- endpoints become thin orchestration layers
- logic can be reused by:
  - background jobs
  - admin panels
  - CLI commands
  - GraphQL resolvers
  - internal services

---

## Middleware in CQRS

CQRS buses support **middleware pipelines**, similar to HTTP middleware but scoped to domain logic.

### Example: auditing or validation

```python
from lilya.logging import logger
from ravyn.contrib.cqrs import CommandBus

async def logging_middleware(message, next):
    logger.info("Handling %s", type(message).__name__)
    return await next(message)

command_bus = CommandBus(middleware=[logging_middleware])
```

Middleware can:

- log
- mutate messages
- short-circuit execution
- add tracing
- enforce permissions

---

## Default buses and decorators (optional)

For small applications or quick prototypes, Ravyn provides **module-level default buses**.

```python
from ravyn.contrib.cqrs import command, query
```

```python
from ravyn.contrib.cqrs import command

@command(CreateUser)
def handle_create(cmd: CreateUser) -> None:
    ...
```

```python
from ravyn.contrib.cqrs import query

@query(GetUserEmail)
def handle_get(q: GetUserEmail) -> str | None:
    ...
```

This is convenient, but **explicit buses are recommended** for larger systems to avoid global coupling.

---

## Testing CQRS logic

CQRS handlers are **trivial to test**.

```python
def test_create_user():
    store = {}

    def handler(cmd: CreateUser):
        store[cmd.user_id] = cmd.email

    bus = CommandBus()
    bus.register(CreateUser, handler)

    bus.dispatch(CreateUser("u1", "x@y.com"))

    assert store["u1"] == "x@y.com"
```

No HTTP. No ASGI. No TestClient required.

---

## Summary

CQRS in Ravyn:

- is explicit, not magical
- keeps business logic out of endpoints
- scales with application complexity
- integrates naturally with Ravyn
- remains fully async-native
- is optional and composable

Use it when **your domain deserves structure**.

Avoid it when **simplicity is enough**.

---

## Next steps

- Combine CQRS with:
    - background tasks
    - caching
    - observables
- Introduce message envelopes for transport
- Add persistence or event sourcing if needed

CQRS is a foundation — not a constraint.
