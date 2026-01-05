# Handling Body Fields in Ravyn

In Ravyn, body fields are used to parse and validate incoming request bodies. The `Body` class in Ravyn allows you to define structured data within the body of a request. This guide will cover how to handle and validate body fields using Ravyn.

## 📂 Using the `Body` Class

The `Body` class in Ravyn is used to define fields in the body of an HTTP request. These fields can be validated and documented using Pydantic models. You can also specify the media type of the body content, such as `application/json`, `application/x-www-form-urlencoded`, or `multipart/form-data`.

### Example: Simple Body Field

```python
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, JSONResponse, post, Body

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(data: User = Body(...)) -> JSONResponse:
    """
    Creates a new user based on the request body.
    """
    return JSONResponse({"message": "User created", "user": data.model_dump()})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `User` Pydantic model defines the structure of the incoming data.
- The `data` parameter is annotated with `Body(...)`, indicating that the body of the request should be parsed into the `User` model.
- The `create_user` endpoint accepts the user data in JSON format and returns the same data in the response.

---

## 🌐 Setting the `media_type` for Body Fields

Ravyn allows you to define the `media_type` for body fields, specifying the format of the data being sent.

### Available Media Types:

- `application/json` (default)
- `application/x-www-form-urlencoded`
- `multipart/form-data`

You can define the `media_type` when using the `Body` decorator to specify how Ravyn should parse the incoming request body.

### Example: Body with `media_type`

```python
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, JSONResponse, post, Body
from ravyn.utils.enums import EncodingType

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(
        data: User = Body(..., media_type=EncodingType.URL_ENCODED)
) -> JSONResponse:
    """
    Creates a user with the body sent as x-www-form-urlencoded.
    """
    return JSONResponse({"message": "User created", "user": data.model_dump()})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `media_type=EncodingType.URL_ENCODED` specifies that the body content should be parsed as `application/x-www-form-urlencoded`, commonly used in forms.
- This allows you to work with URL-encoded form data instead of JSON.

---

## 🧩 Using `Body` with Pydantic Models

Ravyn leverages Pydantic for automatic data validation and serialization. You can define more complex data structures using Pydantic models and use them as body fields.

### Example: Using `Body` with Nested Pydantic Models

```python
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, JSONResponse, post, Body

class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    email: str
    address: Address

@post("/create")
async def create_user(data: User = Body(...)) -> JSONResponse:
    """
    Creates a user with a nested address.
    """
    return JSONResponse({"message": "User created", "user": data.model_dump()})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `User` model contains a nested `Address` model. The `data` parameter in the `create_user` function is annotated as `Body(...)`, which will automatically parse the incoming request body into the nested `User` and `Address` models.
- This allows you to work with complex, nested data structures while keeping the validation and parsing automatic.

---

## 📝 Optional and Default Fields in `Body`

In Ravyn, body fields can be optional or have default values. You can use Python's typing and Pydantic features to define whether a field is required or optional.

### Example: Optional Fields in Body

```python
from typing import Optional
from pydantic import BaseModel
from ravyn import Ravyn, Gateway, JSONResponse, post, Body

class User(BaseModel):
    name: str
    email: Optional[str] = None  # Optional field

@post("/create")
async def create_user(data: User = Body(...)) -> JSONResponse:
    """
    Creates a user, with an optional email.
    """
    return JSONResponse({"message": "User created", "user": data.model_dump()})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `email` field is marked as `Optional[str]`, meaning it is not required in the request body. If the email is not provided, it will default to `None`.
- This allows you to handle flexible form submissions where some fields may be omitted.

---

## ⚙️ Advanced Field Validation in `Body`

You can apply advanced validation to body fields using Pydantic's `Field` class, which provides attributes like `min_length`, `max_length`, and custom validation.

### Example: Using `Field` for Validation

```python
from pydantic import BaseModel, Field
from ravyn import Ravyn, Gateway, JSONResponse, post, Body

class User(BaseModel):
    name: str = Field(..., min_length=3)  # Ensures the name has at least 3 characters
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w{2,3}$")  # Email validation

@post("/create")
async def create_user(data: User = Body(...)) -> JSONResponse:
    """
    Creates a user with field validation.
    """
    return JSONResponse({"message": "User created", "user": data.model_dump()})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `Field(..., min_length=3)` ensures that the `name` field has at least three characters.
- The `Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w{2,3}$")` validates that the `email` field is in a correct email format.
- These validations ensure that the request data meets specific requirements before reaching your handler logic.

---

## 📂 Summary

- **`Body`** allows you to handle and validate request bodies in Ravyn, using Pydantic models or simple Python data structures.
- You can customize the body content using `media_type`, choosing between `application/json`, `application/x-www-form-urlencoded`, and `multipart/form-data`.
- Ravyn makes it easy to handle complex, nested models and apply custom validations using Pydantic’s powerful features.
- **Optional** fields and **default values** allow you to create flexible API endpoints that can handle a variety of input scenarios.
