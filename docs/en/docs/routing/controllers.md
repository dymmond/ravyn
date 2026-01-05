# Controllers

Imagine a restaurant kitchen with different stations: one for appetizers, one for main courses, one for desserts. Each station has its own chef, tools, and recipes, but they all work together to serve the restaurant.

Controllers work the same way. Instead of scattering your user-related endpoints across multiple files, you group them into a `UserController` class. All user operations (create, read, update, delete) live in one organized place.

## What You'll Learn

- Creating class-based controllers
- Using generic controllers for common patterns
- Controller routing and path prefixes
- Best practices for organization

## Quick Start

```python
from ravyn import Ravyn, Controller, get, post

class UserController(Controller):
    path = "/users"
    
    @get("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Alice"}
    
    @post("/")
    async def create_user(self, data: dict) -> dict:
        return {"id": 1, **data}

app = Ravyn(routes=[Gateway(handler=UserController)])
```

---

## Why Controllers?

- **Organization** - Group related endpoints

- **Code Reuse** - Share logic across methods

- **OOP Style** - Class-based approach

- **Cleaner Code** - Less repetition

---

## Basic Controller

### Creating a Controller

```python
from ravyn import Controller, get, post, put, delete

class ProductController(Controller):
    path = "/products"
    
    @get("/")
    async def list_products(self) -> list:
        return [{"id": 1, "name": "Product 1"}]
    
    @get("/{product_id}")
    async def get_product(self, product_id: int) -> dict:
        return {"id": product_id, "name": "Product 1"}
    
    @post("/")
    async def create_product(self, data: dict) -> dict:
        return {"id": 1, **data}
    
    @put("/{product_id}")
    async def update_product(self, product_id: int, data: dict) -> dict:
        return {"id": product_id, **data}
    
    @delete("/{product_id}")
    async def delete_product(self, product_id: int) -> None:
        pass
```

### Registering Controllers

```python
from ravyn import Ravyn, Gateway

app = Ravyn(
    routes=[
        Gateway(handler=ProductController)
    ]
)
```

---

## Controller Features

### Shared Dependencies

```python
from ravyn import Controller, Inject, get

class UserController(Controller):
    path = "/users"
    dependencies = {"db": Inject(get_database)}
    
    @get("/")
    async def list_users(self, db) -> list:
        return await db.fetch_all("SELECT * FROM users")
```

### Shared Permissions

```python
from ravyn import Controller, get

class AdminController(Controller):
    path = "/admin"
    permissions = [IsAdmin]  # Applied to all methods
    
    @get("/users")
    async def list_users(self) -> list:
        return []
```

### WebSockets

```python
from ravyn import Controller, get, websocket
from ravyn.websockets import WebSocket

class ChatController(Controller):
    path = "/chat"
    
    @get("/")
    async def chat_page(self) -> dict:
        return {"message": "Chat room"}
    
    @websocket("/ws")
    async def chat_ws(self, socket: WebSocket) -> None:
        await socket.accept()
        while True:
            data = await socket.receive_text()
            await socket.send_text(f"Echo: {data}")
```

---

## Generic Controllers

### SimpleAPIView - All Methods

```python
from ravyn import SimpleAPIView, get, post

class UserAPI(SimpleAPIView):
    path = "/users"
    
    @get("/")
    async def get(self) -> list:  # Method name matches HTTP verb
        return []
    
    @post("/")
    async def post(self, data: dict) -> dict:  # Method name matches HTTP verb
        return data
```

!!! info
    Generic controllers enforce method name matching with HTTP verbs.

### ReadAPIController - GET Only

```python
from ravyn.routing.controllers.generics import ReadAPIController
from ravyn import get

class UserReadAPI(ReadAPIController):
    path = "/users"
    
    @get("/")
    async def get(self) -> list:
        return []
```

### CreateAPIController - POST/PUT/PATCH

```python
from ravyn.routing.controllers.generics import CreateAPIController
from ravyn import post, put

class UserCreateAPI(CreateAPIController):
    path = "/users"
    
    @post("/")
    async def post(self, data: dict) -> dict:
        return data
    
    @put("/{user_id}")
    async def put(self, user_id: int, data: dict) -> dict:
        return {"id": user_id, **data}
```

### DeleteAPIController - DELETE Only

```python
from ravyn.routing.controllers.generics import DeleteAPIController
from ravyn import delete

class UserDeleteAPI(DeleteAPIController):
    path = "/users"
    
    @delete("/{user_id}")
    async def delete(self, user_id: int) -> None:
        pass
```

---

## Generic Controller Comparison

| Generic | Allowed Methods | Use Case |
|---------|----------------|----------|
| `SimpleAPIView` | All | Full CRUD |
| `ReadAPIController` | GET | Read-only APIs |
| `CreateAPIController` | POST, PUT, PATCH | Create/Update |
| `DeleteAPIController` | DELETE | Delete operations |
| `ListAPIController` | All (returns lists) | List endpoints |

---

## Extra Methods

Add custom methods with `extra_allowed`:

```python
from ravyn import SimpleAPIView, get

class UserAPI(SimpleAPIView):
    path = "/users"
    extra_allowed = ["search_users"]  # Allow custom method
    
    @get("/")
    async def get(self) -> list:
        return []
    
    @get("/search")
    async def search_users(self, query: str) -> list:  # Custom method
        return []
```

---

## Best Practices

### 1. Use Controllers for Related Endpoints

```python
# Good - grouped by resource
class UserController(Controller):
    path = "/users"
    
    @get("/")
    async def list_users(self) -> list:
        return []
    
    @post("/")
    async def create_user(self, data: dict) -> dict:
        return data
```

### 2. Share Common Logic

```python
# Good - shared validation
class ProductController(Controller):
    path = "/products"
    
    def _validate_product(self, data: dict) -> None:
        if not data.get("name"):
            raise ValueError("Name required")
    
    @post("/")
    async def create_product(self, data: dict) -> dict:
        self._validate_product(data)
        return data
```

### 3. Use Generics for Restrictions

```python
# Good - enforce read-only
class PublicUserAPI(ReadAPIController):
    path = "/public/users"
    
    @get("/")
    async def get(self) -> list:
        return []
```

---

## Controller vs Handlers

| Feature | Controller | Handlers |
|---------|-----------|----------|
| **Style** | Class-based | Function-based |
| **Organization** | Grouped | Individual |
| **Code Reuse** | Easy | Manual |
| **Complexity** | Higher | Lower |

**Use controllers when:**
- Multiple related endpoints
- Shared logic needed
- OOP preferred

**Use handlers when:**
- Simple endpoints
- Functional style preferred
- Quick prototyping

---

## Next Steps

- [Handlers](./handlers.md) - Function-based routing
- [Routes](./routes.md) - Route organization
- [Dependencies](../dependencies.md) - Dependency injection
- [Permissions](../permissions/index.md) - Access control
