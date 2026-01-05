# MsgSpec

MsgSpec is a fast serialization and validation library that integrates seamlessly with Ravyn. If you need maximum performance for JSON serialization, MsgSpec is an excellent alternative to Pydantic.

## What You'll Learn

- Using MsgSpec Structs in Ravyn
- MsgSpec vs Pydantic performance
- Integrating with OpenAPI documentation
- Mixing MsgSpec with Pydantic
- Validation with MsgSpec

## Quick Start

```python
from ravyn import Ravyn, get, post
from ravyn.datastructures.msgspec import Struct

class User(Struct):
    name: str
    email: str
    age: int = 0

@get("/user")
def get_user() -> User:
    return User(name="Alice", email="alice@example.com", age=30)

@post("/user")
def create_user(user: User) -> User:
    # Validation happens automatically
    return user

app = Ravyn()
app.add_route(get_user)
app.add_route(create_user)
```

!!! info
    Always import from `ravyn.datastructures.msgspec import Struct` for full Ravyn integration, not directly from `msgspec`.

---

## Why Use MsgSpec?

### Performance Benefits:

- **Faster Serialization** - 5-10x faster than Pydantic for JSON

- **Lower Memory Usage** - More efficient than Pydantic

- **Fast Validation** - High-performance data validation

- **Multiple Formats** - JSON, MessagePack, YAML, TOML support

### When to Use MsgSpec:

- High-throughput APIs
- Performance-critical endpoints
- Large data payloads
- Microservices with tight latency requirements

### When to Use Pydantic:

- Complex validation logic
- Rich ecosystem of validators
- Extensive field customization
- ORM integration (SQLAlchemy, etc.)

---

## MsgSpec vs Pydantic

| Feature | MsgSpec | Pydantic |
|---------|---------|----------|
| **Speed** | ⚡⚡⚡ Very Fast | ⚡⚡ Fast |
| **Memory** | Low | Higher |
| **Validation** | Built-in types | Extensive validators |
| **Ecosystem** | Smaller | Very Large |
| **Learning Curve** | Simple | Moderate |

---

## Using MsgSpec Structs

### Basic Struct

```python
from ravyn.datastructures.msgspec import Struct

class Product(Struct):
    name: str
    price: float
    in_stock: bool = True
```

### With Validation

```python
from ravyn.datastructures.msgspec import Struct
from ravyn import post
from ravyn.exceptions import ValidationError

class CreateUser(Struct):
    username: str
    email: str
    age: int
    
    def __post_init__(self):
        if self.age < 18:
            raise ValidationError("Must be 18 or older")
        if "@" not in self.email:
            raise ValidationError("Invalid email format")

@post("/users")
def create_user(data: CreateUser) -> dict:
    return {"created": data.username}
```

### Nested Structs

```python
from ravyn.datastructures.msgspec import Struct

class Address(Struct):
    street: str
    city: str
    zip_code: str

class User(Struct):
    name: str
    email: str
    address: Address

# Usage
user = User(
    name="Alice",
    email="alice@example.com",
    address=Address(
        street="123 Main St",
        city="Springfield",
        zip_code="12345"
    )
)
```

---

## Ravyn Integration

### Import from Ravyn

```python
# Correct - Full Ravyn integration
from ravyn.datastructures.msgspec import Struct

# Wrong - Missing OpenAPI support
from msgspec import Struct
```

!!! warning
    Using `msgspec.Struct` directly will cause errors with OpenAPI documentation. Always use `ravyn.datastructures.msgspec.Struct`.

### As Request Body

```python
from ravyn import post
from ravyn.datastructures.msgspec import Struct

class LoginRequest(Struct):
    username: str
    password: str

@post("/login")
def login(credentials: LoginRequest) -> dict:
    # MsgSpec validates automatically
    return {"token": "abc123"}
```

### As Response

```python
from ravyn import get
from ravyn.datastructures.msgspec import Struct

class UserResponse(Struct):
    id: int
    name: str
    email: str

@get("/users/{user_id}")
def get_user(user_id: int) -> UserResponse:
    return UserResponse(
        id=user_id,
        name="Alice",
        email="alice@example.com"
    )
```

---

## OpenAPI Documentation

MsgSpec Structs work seamlessly with OpenAPI:

### Single Response

```python
from ravyn import get
from ravyn.datastructures.msgspec import Struct
from ravyn.openapi.datastructures import OpenAPIResponse

class User(Struct):
    name: str
    email: str

@get(
    "/user",
    responses={
        200: OpenAPIResponse(model=User, description="User details")
    }
)
def get_user() -> User:
    return User(name="Alice", email="alice@example.com")
```

### List Response

```python
@get(
    "/users",
    responses={
        200: OpenAPIResponse(model=[User], description="List of users")
    }
)
def list_users() -> list[User]:
    return [
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com")
    ]
```

---

## Mixing MsgSpec with Pydantic

You can use MsgSpec Structs inside Pydantic models (but not vice versa):

```python
from ravyn.datastructures.msgspec import Struct
from pydantic import BaseModel

class Address(Struct):
    street: str
    city: str

class User(BaseModel):
    name: str
    email: str
    address: Address  # MsgSpec Struct inside Pydantic model

# This works!
user = User(
    name="Alice",
    email="alice@example.com",
    address=Address(street="123 Main St", city="Springfield")
)
```

> [!INFO]
> Each type is validated by its own library: MsgSpec validates `Address`, Pydantic validates `User`.

---

## Common Pitfalls & Fixes

### Pitfall 1: Using msgspec.Struct Directly

**Problem:** OpenAPI documentation fails.

```python
# Wrong - breaks OpenAPI
from msgspec import Struct

class User(Struct):
    name: str
```

**Solution:** Import from Ravyn:

```python
# Correct
from ravyn.datastructures.msgspec import Struct

class User(Struct):
    name: str
```

### Pitfall 2: Pydantic Inside MsgSpec

**Problem:** Trying to nest Pydantic in MsgSpec.

```python
# Won't work
from pydantic import BaseModel
from ravyn.datastructures.msgspec import Struct

class Address(BaseModel):
    street: str

class User(Struct):
    name: str
    address: Address  # Pydantic inside MsgSpec - not supported
```

**Solution:** Use MsgSpec for nested types or use Pydantic for everything:

```python
# Option 1: All MsgSpec
class Address(Struct):
    street: str

class User(Struct):
    name: str
    address: Address

# Option 2: All Pydantic
class Address(BaseModel):
    street: str

class User(BaseModel):
    name: str
    address: Address
```

### Pitfall 3: Missing Validation

**Problem:** No validation on struct fields.

```python
# No validation
class User(Struct):
    age: int  # Accepts any int, even negative
```

**Solution:** Add validation in `__post_init__`:

```python
# With validation
class User(Struct):
    age: int
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age must be positive")
```

### Pitfall 4: Forgetting Default Values

**Problem:** Required fields not provided.

```python
# Error if in_stock not provided
class Product(Struct):
    name: str
    price: float
    in_stock: bool  # Required!
```

**Solution:** Provide defaults for optional fields:

```python
# Correct
class Product(Struct):
    name: str
    price: float
    in_stock: bool = True  # Optional with default
```

---

## Performance Comparison

### Serialization Speed

```python
# MsgSpec: ~5-10x faster than Pydantic
import msgspec
import time

class User(Struct):
    name: str
    email: str

user = User(name="Alice", email="alice@example.com")

# Serialize 100,000 times
start = time.time()
for _ in range(100000):
    msgspec.json.encode(user)
print(f"MsgSpec: {time.time() - start:.2f}s")

# Compare with Pydantic for same operation
# Pydantic typically takes 5-10x longer
```

---

## Best Practices

### 1. Use for High-Performance Endpoints

```python
# Good - high-throughput endpoint
@get("/api/data")
def get_data() -> DataStruct:
    return DataStruct(...)  # Fast serialization
```

### 2. Keep Validation Simple

```python
# Good - simple validation
class User(Struct):
    age: int
    
    def __post_init__(self):
        if not 0 <= self.age <= 150:
            raise ValueError("Invalid age")
```

### 3. Use Type Hints

```python
# Good - clear types
class Product(Struct):
    name: str
    price: float
    tags: list[str]
    metadata: dict[str, str]
```

---

## Next Steps

Now that you understand MsgSpec, explore:

- [Encoders](./encoders.md) - Custom data type support
- [Responses](./responses.md) - Response types
- [Requests](./requests.md) - Request handling
- [OpenAPI](./openapi.md) - API documentation
- [MsgSpec Documentation](https://jcristharif.com/msgspec/) - Official docs
