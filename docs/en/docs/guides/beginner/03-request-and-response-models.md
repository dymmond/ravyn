# Request and Response Models

In this section, you'll learn how to validate input and shape output with Pydantic models in Ravyn.

## Why models matter

Models give you a clear contract between your API and its consumers:

- Request model: what clients are allowed to send.
- Response model: what your API guarantees to return.

That contract improves correctness, readability, and generated API docs.

---

## Request model: validate incoming JSON

```python
from pydantic import BaseModel, Field
from ravyn import post


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2)
    age: int = Field(ge=0)


@post("/users")
def create_user(data: CreateUserRequest) -> dict:
    return {"message": f"Created user {data.name} ({data.age})"}
```

What Ravyn does automatically:

1. Reads JSON body.
2. Validates against `CreateUserRequest`.
3. Injects a typed model instance into `data`.

If validation fails, the request is rejected before your handler logic runs.

---

## Response model: control output shape

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

Returning a Pydantic model keeps your response consistent and explicit.

---

## Nested models

```python
from pydantic import BaseModel
from ravyn import get


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

This pattern is useful when response objects have clear sub-structures.

---

## Lists of models

```python
from ravyn import get


@get("/users")
def list_users() -> list[UserResponse]:
    return [
        UserResponse(id=1, name="Alice"),
        UserResponse(id=2, name="Bob"),
    ]
```

---

## Input/output flow (conceptual)

```text
Client JSON
   -> Request Model (validation)
   -> Handler (business logic)
   -> Response Model (shape)
   -> JSON response
```

This is a good default for most endpoints.

---

## Practical pattern: split request and response models

```python
from pydantic import BaseModel
from ravyn import post


class CreatePostRequest(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    title: str


@post("/posts")
def create_post(data: CreatePostRequest) -> PostResponse:
    # Simulated persistence
    return PostResponse(id=1, title=data.title)
```

Use this pattern when internal fields should not be exposed in responses.

---

## Related pages

- [Handling Errors](./04-handling-errors.md)
- [Requests and Responses (overview)](./09-requests-and-responses.md)
- [Body Parameters](../../extras/body-fields.md)
- [Responses](../../responses.md)

## What's Next?

Continue to [Handling Errors](./04-handling-errors.md) to learn how validation and domain errors should be returned consistently.
