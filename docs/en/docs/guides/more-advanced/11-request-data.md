# Complex Request Data in Ravyn

Ravyn allows for highly flexible handling of request data. Since release 3.4+, Ravyn supports **multiple payloads**, letting you structure data more clearly. This feature makes your request data more organized and manageable, especially when dealing with multiple entities.

## 📦 Sending Multiple Payloads

Ravyn allows you to declare multiple payloads in a handler, enabling better organization of complex data. You can use the `data` or `payload` field to achieve this, with each one serving the same purpose.

### Example: Using `data` or `payload`

```python
from pydantic import BaseModel, EmailStr
from ravyn import Ravyn, Gateway, post

class User(BaseModel):
    name: str
    email: EmailStr
    hobbies: list[str]  # Pydantic model handles type validation

@post("/create")
async def create_user(data: User) -> None:
    pass

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Request Payload (for `data` or `payload`):**

```json
{
    "name": "John",
    "email": "john.doe@example.com",
    "hobbies": ["running", "swimming"]
}
```

---

## 🏠 Splitting Data by Responsibility

Sometimes, you might want to send data that represents different entities (like a `User` and an `Address`). Ravyn allows you to handle such cases by splitting the payload into separate parts.

### Example: User and Address

```python
from pydantic import BaseModel, EmailStr
from ravyn import Ravyn, Gateway, post

class User(BaseModel):
    name: str
    email: EmailStr

class Address(BaseModel):
    street_name: str
    post_code: str

@post("/create")
async def create_user(user: User, address: Address) -> None:
    pass

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Request Payload:**

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com"
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

In this case, Ravyn automatically maps the `user` and `address` parts of the request to their respective models.

---

## 🧩 Optional Fields in Payloads

You can also mark fields as optional, which makes them not required for validation.

### Example: Optional Address

```python
from pydantic import BaseModel, EmailStr
from typing import Union
from ravyn import Ravyn, Gateway, post

class User(BaseModel):
    name: str
    email: EmailStr

class Address(BaseModel):
    street_name: str
    post_code: str

@post("/create")
async def create_user(user: User, address: Union[Address, None] = None) -> None:
    pass

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Request Payload (Optional Address):**

1. **With Address:**

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com"
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

2. **Without Address:**

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com"
    }
}
```

In this example, the `address` is optional. If it's not provided, Ravyn will still process the `user` data.

---

## Using Different Encoders

Ravyn supports multiple encoders, such as **Pydantic** and **Msgspec**. This allows you to mix and match encoders based on your data needs.

### Example: Using Pydantic and Msgspec

```python
from pydantic import BaseModel, EmailStr
from msgspec import Struct
from typing import Union
from ravyn import Ravyn, Gateway, post

class User(BaseModel):
    name: str
    email: EmailStr

class Address(Struct):
    street_name: str
    post_code: str

@post("/create")
async def create_user(user: User, address: Union[Address, None] = None) -> None:
    pass

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Request Payload:**

```json
{
    "user": {
        "name": "John",
        "email": "john.doe@example.com"
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

Ravyn automatically handles the encoder types (`Pydantic` for `User` and `Msgspec` for `Address`), so you don't have to manually process the encoding and decoding of your data.

---

## Important Note on Complex Bodies

Once you add an extra body (like `address`), you must declare it explicitly in your handler.

**Example of Declaring Complex Request Data:**

```python
from pydantic import BaseModel, EmailStr
from typing import Union
from ravyn import Ravyn, Gateway, post

class User(BaseModel):
    name: str
    email: EmailStr

class Address(BaseModel):
    street_name: str
    post_code: str

@post("/create")
async def create_user(data: User, address: Union[Address, None] = None) -> None:
    ...

app = Ravyn(routes=[Gateway(handler=create_user)])
```

**Request Payload (Explicit Declaration):**

```json
{
    "data": {
        "name": "John",
        "email": "john.doe@example.com"
    },
    "address": {
        "street_name": "123 Queens Park",
        "post_code": "90241"
    }
}
```

Ravyn requires the explicit declaration of each part of the payload when working with complex bodies.

---

## 📌 Conclusion

With Ravyn, you can easily handle complex request data, split data into multiple parts,
and use advanced techniques like optional fields and different encoders. Whether you're handling a
single object or complex nested data, Ravyn's flexibility ensures you can build scalable,
well-structured APIs with ease.
