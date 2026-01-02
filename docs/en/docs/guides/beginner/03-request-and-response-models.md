# Request and Response Models

In this section, you'll learn how to validate and structure input and output using Pydantic models in Ravyn.

## Why Use Models?

Pydantic models offer:

- **Automatic validation** of incoming request data
- **Auto-generated documentation**
- **Clear structure** for responses

---

## Request Model Example

Define a Pydantic model to validate incoming data:

```python
from pydantic import BaseModel
from ravyn import post

class CreateUserRequest(BaseModel):
    name: str
    age: int

@post("/users")
def create_user(data: CreateUserRequest) -> dict:
    return {"message": f"Created user {data.name} who is {data.age} years old"}
```

When a POST request is made to `/users`, Ravyn:

- Automatically parses the JSON
- Validates it against `CreateUserRequest`
- Injects the model instance into the handler

Invalid request? Ravyn returns a 422 with helpful details.

---

## Response Model Example

Define a model to **structure** the output:

```python
from pydantic import BaseModel
from ravyn import get

class UserResponse(BaseModel):
    id: int
    name: str

@get("/users/{user_id}")
def get_user(user_id: int) -> UserResponse:
    return UserResponse(id=user_id, name=f"User {user_id}")
```

- Ravyn converts the returned model into JSON automatically

---

## Nested Models

```python
class Address(BaseModel):
    city: str
    country: str

class UserProfile(BaseModel):
    name: str
    address: Address

@get("/profile")
def get_profile() -> UserProfile:
    return UserProfile(name="Alice", address=Address(city="Berlin", country="Germany"))
```

---

## List of Models

Returning a list? Just use `list[Model]` or `List[Model]`.

```python
@get("/users")
def list_users() -> list[UserResponse]:
    return [UserResponse(id=1, name="Alice"), UserResponse(id=2, name="Bob")]
```

---

## What's Next?

You've now learned how to:

- Use request models for validation
- Use response models for output structure
- Handle nesting and collections

👉 Continue to [the next section](04-handling-errors.md) to learn about custom error handling, exceptions, and status codes in Ravyn.
