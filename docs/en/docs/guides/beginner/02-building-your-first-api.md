# Building Your First API

In this guide, we’ll walk you through how to build a basic API using Ravyn. You’ll learn how to define routes,
use path and query parameters, and return structured responses.

## Prerequisites

- Ravyn installed: `pip install ravyn[standard]`
- Familiarity with basic Python and HTTP concepts

---

## Defining Your First Routes

In Ravyn, routes are created using decorators like `@get`, `@post`, etc., which map to HTTP methods.

```python
from ravyn import Ravyn, get

@get("/")
def home() -> dict:
    return {"message": "Welcome to your API!"}

app = Ravyn(routes=[home])
```

Start the server with:
```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/` to see your message.

---

## Path Parameters

Path parameters let you capture parts of the URL.

```python
from ravyn import get

@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"user_id": user_id, "name": f"User {user_id}"}
```

- `http://127.0.0.1:8000/users/42` → `{ "user_id": 42, "name": "User 42" }`

Path parameters are automatically converted to the specified type (`int` in this case).

---

## Query Parameters

Query parameters are passed using `?key=value` syntax.

```python
from ravyn import get, Query

@get("/search")
def search(term: str = Query(...), limit: int = Query(10)) -> dict:
    return {"term": term, "limit": limit}
```

- `http://127.0.0.1:8000/search?term=ravyn&limit=5`

You’ll get:
```json
{"term": "ravyn", "limit": 5}
```

---

## JSON Body (POST requests)

To handle JSON body data, just declare a parameter with a type.

```python
from pydantic import BaseModel
from ravyn import post

class User(BaseModel):
    name: str
    age: int

@post("/users")
def create_user(user: User) -> dict:
    return {"created": True, "user": user.model_dump()}
```

Curl test:
```bash
curl -X POST http://localhost:8000/users -H "Content-Type: application/json" \
     -d '{"name": "Alice", "age": 30}'
```

---

## Route Summary

| Decorator | HTTP Method |
|----------|-------------|
| `@get()` | GET         |
| `@post()`| POST        |
| `@put()` | PUT         |
| `@patch()`| PATCH      |
| `@delete()`| DELETE    |
| `@options()`| OPTIONS  |
| `@trace()` | TRACE     |

---

## What's Next?

Now that you know how to build basic routes, let’s move into **request validation, response models, and data schemas**.

👉 Continue to [the next section](03-request-and-response-models.md) to start defining schemas using Pydantic and working with structured input/output.

---

You're on your way to mastering Ravyn APIs! 💚
