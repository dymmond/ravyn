# How to Use Path Parameters in Ravyn (Advanced Guide)

Path parameters in Ravyn allow dynamic values to be captured directly from the URL path,
enabling highly flexible and descriptive routing. This guide is for advanced users who want full
control and understanding of how path parameters work, including usage with custom types, enums, and transformers.

---

## 📌 What Are Path Parameters?

Path parameters are dynamic segments in your route’s path, defined using either curly braces `{}`
or angle brackets `<>`. These values are passed to your controller/handler as arguments.

### Basic Example

```python
from ravyn import Ravyn, Gateway, JSONResponse, get

@get("/users/{user_id}")
async def read_user(user_id: str) -> JSONResponse:
    return JSONResponse({"user_id": user_id})

app = Ravyn(routes=[Gateway(handler=read_user)])
```

- The route `/users/{user_id}` declares `user_id` as a path parameter.
- Visiting `/users/1` returns `{ "user_id": "1" }`.
- If not explicitly typed, path parameters are treated as strings.

---

## 🔁 Syntax Variations: `{}` vs `<>`

Ravyn supports two syntaxes:

```python
@get("/items/{item_id}")
@get("/items/<item_id>")
```

Both styles are functionally equivalent and can be used based on your preference.

---

## 🔠 Parameter Typing and Conversion

Ravyn supports inline typing of parameters, ensuring automatic type conversion and validation.

### Example: Integer Parameter
```python
@get("/products/{product_id:int}")
async def get_product(product_id: int) -> JSONResponse:
    return JSONResponse({"product_id": product_id})
```

### Supported Built-in Transformers
- `str` – default
- `int`
- `float`
- `uuid`
- `path` – captures the full path, including slashes

### Example: UUID and Path
```python
from uuid import UUID

@get("/resources/{resource_id:uuid}")
async def get_resource(resource_id: UUID):
    ...

@get("/files/{filepath:path}")
async def get_file(filepath: str):
    ...
```

---

## 🧱 Creating Custom Transformers

Ravyn supports registering custom path transformers for complex scenarios.

### Custom DateTime Transformer
```python
from datetime import datetime
from lilya.transformers import Transformer, register_path_transformer

class DateTimeTransformer(Transformer):
    regex = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?"

    def transform(self, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")

    def normalise(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%S")

register_path_transformer("datetime", DateTimeTransformer())
```

### Usage
```python
@get("/events/{event_date:datetime}")
async def read_event(event_date: datetime):
    return JSONResponse({"event_date": event_date.isoformat()})
```

---

## 🧩 Using Enums for Validation

Python enums can be used to restrict path values to a predefined set.

### Example
```python
from enum import Enum

class UserType(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

@get("/users/{user_type}")
async def get_user_by_type(user_type: UserType):
    return JSONResponse({"type": user_type})
```

- This will raise a 422 error if an invalid enum value is used.
- `/users/admin` → - `/users/random` → ---

## Summary
- Use `{}` or `<>` to declare dynamic segments.
- Inline typing allows automatic validation and transformation.
- Custom transformers let you support advanced types (e.g., `datetime`).
- Enums are great for controlled, predictable values.

---

This guide gives you full control over how to implement and validate path parameters in Ravyn.
Whether you're building a large-scale API or finely tuned microservices, mastering path parameters will help you
write clean, reliable, and user-friendly endpoints.
