# Handling Header Fields in Ravyn

In modern web applications, HTTP headers are frequently used to pass metadata, authorization tokens,
and content-related information between clients and servers. Ravyn provides a simple and intuitive way to
work with request and response headers, allowing you to capture and validate headers efficiently.

## 🌐 Accessing Request Headers with `Header`

Ravyn makes it easy to capture headers in incoming requests using the `Header` class.
This class is part of Ravyn's request parameter system and allows you to specify headers that should be
included in the request.

### Example: Accessing Headers in the Request

```python
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, Header, JSONResponse, post

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(
        data: User,
        token: str = Header(value="X-API-TOKEN")
) -> JSONResponse:
    """
    Creates a user and requires the 'X-API-TOKEN' header.
    """
    return JSONResponse({"message": "User created", "user": data.model_dump(), "token": token})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `token` parameter is captured using the `Header` class, which corresponds to the `X-API-TOKEN` header.
- If the `X-API-TOKEN` header is not provided, Ravyn will raise a `422` validation error.
- The `alias` parameter is used to define the actual header name, allowing for flexibility and clarity.

---

## 🌐 Optional Headers with Default Values

Sometimes headers are optional, and you may want to provide default values if they are not included in the request.

### Example: Optional Header

```python
from ravyn import Ravyn, Gateway, Header, JSONResponse, post

@post("/create")
async def create_user(
        data: dict,
        user_agent: Optional[str] = Header(value=None)  # Optional header
) -> JSONResponse:
    """
    Creates a user and optionally receives the 'User-Agent' header.
    """
    return JSONResponse({"message": "User created", "data": data, "user_agent": user_agent})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `user_agent` header is optional, and the default value is `None`.
- If the `User-Agent` header is not provided, the `user_agent` variable will be set to `None`.

---

## 🌐 Using `Header` with Custom Validation

You can also apply validation to header fields using Pydantic’s `Field` or Ravyn’s `Header`
functionality. This allows you to ensure that the value of the header matches specific patterns or constraints.

### Example: Validating the Header

```python
from typing import Optional
from pydantic import BaseModel, Field
from ravyn import Ravyn, Gateway, Header, JSONResponse, post

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(
        data: User,
        authorization: str = Header(..., min_length=10)  # Validating minimum length for the header
) -> JSONResponse:
    """
    Creates a user, requiring a valid 'Authorization' header with at least 10 characters.
    """
    return JSONResponse({"message": "User created", "user": data.model_dump(), "authorization": authorization})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `authorization` header is validated to ensure its length is at least 10 characters.
- If the header doesn't meet the validation constraints, Ravyn will raise a `422` validation error.

---

## 🌐 Combining Header Fields with Body Data

You can combine header fields with other request parameters, such as data sent in the request body, by using multiple parameters in your endpoint handler.

### Example: Using Header and Body Data Together

```python
from typing import Optional
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, Header, JSONResponse, post

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(
        data: User,
        token: str = Header(value="X-API-TOKEN"),  # Header field
        user_agent: Optional[str] = Header(None)  # Optional header field
) -> JSONResponse:
    """
    Creates a user and requires an 'X-API-TOKEN' header, and optionally a 'User-Agent' header.
    """
    return JSONResponse({
        "message": "User created",
        "user": data.model_dump(),
        "token": token,
        "user_agent": user_agent
    })

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `token` header is mandatory and captured using the `Header` class with the `alias="X-API-TOKEN"`.
- The `user_agent` header is optional and will be `None` if not provided.
- Both the body data (`data` from `User`) and headers are processed in the same handler function.

---

## ⚙️ Setting Custom Response Headers

Ravyn also allows you to set custom headers in the response. This can be useful for setting things like
`X-Rate-Limit` or custom API keys.

### Example: Adding Custom Response Headers

```python
from ravyn import Ravyn, Gateway, JSONResponse, post

@post("/create")
async def create_user() -> JSONResponse:
    """
    Creates a user and adds custom headers to the response.
    """
    response = JSONResponse({"message": "User created"})
    response.headers["X-API-KEY"] = "some-api-key"  # Setting custom header
    return response

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- In this example, we set a custom `X-API-KEY` header in the response.
- This shows how you can add custom headers to the response as needed.

---

## 📑 Summary

- **Accessing Request Headers:** You can capture request headers using the `Header` class in Ravyn, with options to specify required or optional headers.
- **Header Validation:** Headers can be validated with Pydantic’s `Field`, allowing you to enforce constraints like minimum length, regex patterns, and more.
- **Combining Headers with Body Data:** Ravyn makes it easy to combine headers and body fields in the same handler function.
- **Custom Response Headers:** You can easily add custom headers to responses using the `headers` attribute of the `JSONResponse` object.
