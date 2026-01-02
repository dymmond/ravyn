# A bit more about Routing

In this section, you’ll learn how to structure and organize your API with routes and routers in Ravyn.

---

## Basic Routes

A route maps a URL path and HTTP method to a Python function:

```python
from ravyn import get

@get("/hello")
def say_hello():
    return {"message": "Hello, world!"}
```

---

## Dynamic Routes

You can use parameters in your path:

```python
@get("/items/{item_id}")
def read_item(item_id: int):
    return {"id": item_id}
```

---

## Routers

Group related routes into a `Router`:

```python
from ravyn import Router

user_router = Router()

@user_router.get("/users")
def list_users():
    return ["user1", "user2"]

@user_router.post("/users")
def create_user():
    return {"status": "created"}
```

Include the router in your app:

```python
from ravyn import Ravyn

app = Ravyn(routes=[user_router])
```

---

## Nested Routes

You can nest routers with prefixes:

```python
api_router = Router(path="/api")

app = Ravyn(routes=[...])
app.add_router(user_router)
```

---

## Tags and Summaries

Add metadata for documentation:

```python
@get("/status", tags=["Health"], summary="Check API status")
def status():
    return {"status": "ok"}
```

---

## Conditional Routing

Routes can depend on headers, query parameters, or even environment flags.

You can also dynamically register routes at runtime (e.g. based on settings).

---

## What's Next?

Now that you know how to build routes and organize them into routers, it's time to look at security.

👉 Continue to [security](../more-advanced/01-security.md) to implement auth and secure your endpoints.
