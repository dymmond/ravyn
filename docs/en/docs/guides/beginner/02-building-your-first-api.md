# Building Your First API

In this guide, we’ll build a small API from scratch using Ravyn. You’ll define routes, accept path and query parameters, validate request bodies, and return structured responses.

## What you'll build

A tiny API with:

- `GET /` to confirm the app is running.
- `GET /users/{user_id}` using a path parameter.
- `GET /search` using query parameters.
- `POST /users` with request validation.

---

## Mental model first

A Ravyn request usually follows this flow:

```text
HTTP Request
   -> route match (@get/@post/...)
   -> parameter parsing (path/query/body)
   -> validation (type hints + Pydantic)
   -> handler execution
   -> response serialization
HTTP Response
```

If you keep this flow in mind, each feature in the next chapters will feel predictable.

---

## Step 1: Create and run a minimal app

```python
from ravyn import Ravyn, get


@get("/")
def home() -> dict:
    return {"message": "Welcome to your API!"}


app = Ravyn(routes=[home])
```

Run it:

```bash
palfrey main:app --reload
```

Open `http://127.0.0.1:8000/`.

---

## Step 2: Add path and query parameters

### Path parameter

```python
from ravyn import get


@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"user_id": user_id, "name": f"User {user_id}"}
```

- `GET /users/42` returns `{"user_id": 42, "name": "User 42"}`.
- `user_id` is converted to `int` automatically.

### Query parameters

```python
from ravyn import Query, get


@get("/search")
def search(term: str = Query(...), limit: int = Query(10)) -> dict:
    return {"term": term, "limit": limit}
```

Try:

- `GET /search?term=ravyn`
- `GET /search?term=ravyn&limit=5`

---

## Step 3: Accept and validate JSON body data

```python
from pydantic import BaseModel
from ravyn import post


class CreateUser(BaseModel):
    name: str
    age: int


@post("/users")
def create_user(user: CreateUser) -> dict:
    return {"created": True, "user": user.model_dump()}
```

Test with curl:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 30}'
```

Invalid data is rejected automatically with a structured error response.

---

## Step 4: Put everything together

```python
from pydantic import BaseModel
from ravyn import Query, Ravyn, get, post


class CreateUser(BaseModel):
    name: str
    age: int


@get("/")
def home() -> dict:
    return {"message": "Welcome to your API!"}


@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"user_id": user_id, "name": f"User {user_id}"}


@get("/search")
def search(term: str = Query(...), limit: int = Query(10)) -> dict:
    return {"term": term, "limit": limit}


@post("/users")
def create_user(user: CreateUser) -> dict:
    return {"created": True, "user": user.model_dump()}


app = Ravyn(routes=[home, get_user, search, create_user])
```

---

## Common mistakes at this stage

### 1. Missing return types

Always annotate handler return types (`-> dict`, `-> Model`, etc.).

### 2. Treating query/path values as untyped strings

Use type annotations (`int`, `bool`, `UUID`) so Ravyn validates and converts for you.

### 3. Mixing too many concepts at once

Keep each route focused while learning: one feature per endpoint.

---

## Related pages

- [Routing Basics](./05-routing.md)
- [Request and Response Models](./03-request-and-response-models.md)
- [Handling Errors](./04-handling-errors.md)
- [Application Basics](../../application/applications.md)

## What's Next?

Continue to [Request and Response Models](./03-request-and-response-models.md) to go deeper into schema design and validation behavior.
