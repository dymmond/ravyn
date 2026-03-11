# How to Handle Errors with Custom Exception Handlers

This guide explains how to manage application errors by creating custom exception handlers and mapping them to specific status codes or exception classes.

## Problem Statement

When an application encounters an error, you often want to return a consistent, structured response to the client instead of a generic error page or a raw stack trace. You might also need to perform specific actions, such as logging the error or notifying an external service, whenever a particular exception occurs.

## Solution

Ravyn allows you to define custom exception handlers at the application level. These handlers are functions that take a `Request` and an `Exception` as arguments and return a `Response`.

### 1. Create a custom exception

First, define a custom exception class for your application logic.

```python
class ItemNotFoundException(Exception):
    def __init__(self, item_id: str):
        self.item_id = item_id
```

### 2. Define the exception handler

Create a function to handle this specific exception. It must return a Ravyn `Response` (or a subclass like `JSONResponse`).

```python
from ravyn import Request, JSONResponse, status

async def item_not_found_handler(request: Request, exc: ItemNotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Item Not Found",
            "message": f"Could not find item with ID: {exc.item_id}",
            "path": request.url.path,
        },
    )
```

### 3. Register the handler

Map the exception class to your handler in the `Ravyn` application instance.

```python
from ravyn import Ravyn, get

@get("/items/{item_id}")
def get_item(item_id: str) -> dict:
    if item_id == "unknown":
        raise ItemNotFoundException(item_id=item_id)
    return {"id": item_id, "name": "Sample Item"}

app = Ravyn(
    routes=[get_item],
    exception_handlers={
        ItemNotFoundException: item_not_found_handler
    }
)
```

### Handling status codes

You can also register handlers for specific HTTP status codes, regardless of which exception triggered them.

```python
async def custom_404_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "This is not the page you are looking for."}
    )

app = Ravyn(
    exception_handlers={
        404: custom_404_handler
    }
)
```

## Explanation

When an exception is raised during request processing:

1. Ravyn checks if there is a handler registered for that specific exception class.
2. If not found, it checks the classes in the exception's MRO (Method Resolution Order).
3. If the exception is a subclass of `HTTPException`, Ravyn checks for a handler registered for its `status_code`.
4. If no custom handler is found, Ravyn uses its default internal exception handling logic.

By using `async def`, your handlers can perform asynchronous operations like database lookups or API calls before returning the response.

## Common Pitfalls

- **Incorrect signature**: Ensure your handler accepts exactly two arguments: `(request: Request, exc: Exception)`.
- **Forgetting to return a Response**: Exception handlers must return a valid Ravyn `Response` object. Returning a `dict` or `None` will cause an internal error.
- **Handling built-in exceptions**: If you want to handle standard Python exceptions like `ValueError`, register them explicitly in the `exception_handlers` dictionary.
- **Middleware interference**: Some middleware might catch exceptions before they reach the application-level exception handlers. Ensure your middleware stack is ordered correctly.

## Related pages

- [Middleware](../middleware/index.md)
- [Responses](../responses.md)
- [HTTP Exceptions](../references/exceptions.md)
