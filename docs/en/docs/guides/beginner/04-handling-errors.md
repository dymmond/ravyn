# Handling Errors

In this section, you'll learn how to handle errors and exceptions in Ravyn.

Ravyn provides robust error-handling capabilities out of the box, and also allows you to define your own.

---

## Raising HTTP Exceptions

Use `HTTPException` to raise an error with a specific status code and optional detail message:

```python
from ravyn import get, HTTPException

@get("/items/{item_id}")
def get_item(item_id: int) -> dict:
    if item_id != 1:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

This returns a response like:

```json
{
  "detail": "Item not found"
}
```

---

## Built-in Error Responses

Ravyn automatically returns helpful responses for:

- Validation errors (status code `422`)
- Missing routes (`404`)
- Internal server errors (`500`)

Example: Sending an invalid body to a route expecting a `Pydantic` model returns:

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Custom Exception Handlers

You can define a custom exception handler for your own exception classes:

```python
from ravyn import Ravyn, Request, HTTPException, ExceptionHandler

class MyCustomError(Exception):
    pass

def my_custom_handler(request: Request, exc: MyCustomError):
    return {"detail": "Something custom went wrong!"}

app = Ravyn(
    routes=[],
    exception_handlers={MyCustomError: my_custom_handler}
)
```

Raise it like so:

```python
@get("/fail")
def fail():
    raise MyCustomError()
```

---

## Returning Custom Status Codes

Just set `status_code` when raising `HTTPException`:

```python
from ravyn import post, HTTPException

@post("/login")
def login() -> None:
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

---

## Returning Custom Error Structures

You can return custom error payloads using a response directly:

```python
from ravyn.responses import JSONResponse

@get("/custom-error")
def custom_error() -> None:
    return JSONResponse({"error": "custom"}, status_code=400)
```

---

## What's Next?

You now know how to:

- Raise HTTP exceptions
- Customize error messages and handlers
- Return proper status codes

👉 Continue to [the next section](05-routing.md) to learn how to organize your routes, include routers, and build modular APIs.
