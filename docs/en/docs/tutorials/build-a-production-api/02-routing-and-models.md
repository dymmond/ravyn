# Step 2: Routing and Models

Add modular routing and validated data models.

## Define schemas

```python
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
```

## Define a route module

```python
from ravyn import get, post
from .schemas import UserCreate, UserOut


@get("/")
def list_users() -> list[UserOut]:
    return [UserOut(id=1, email="alice@example.com")]


@post("/")
def create_user(payload: UserCreate) -> UserOut:
    return UserOut(id=2, email=payload.email)
```

## Compose routes with Include

```python
from ravyn import Include, Ravyn


app = Ravyn(
    routes=[Include("/users", namespace="app.users.routes")],
)
```

## Checkpoint

- `GET /users/` returns typed output
- `POST /users/` validates payload

## Next step

Continue with [Auth and Permissions](./03-auth-and-permissions.md).
