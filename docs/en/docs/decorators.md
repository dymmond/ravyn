# Decorators

The `@controller` decorator transforms a regular Python class into a Ravyn controller, providing a clean way to organize related routes without explicit subclassing.

## What You'll Learn

- What the `@controller` decorator does
- Creating controllers with decorators
- Configuring controller behavior
- When to use decorators vs subclassing

## Quick Start

```python
from ravyn import Ravyn, get, post
from ravyn.decorators import controller

@controller(path="/users")
class UserController:
    @get("/")
    def list_users(self) -> dict:
        return {"users": ["Alice", "Bob"]}
    
    @get("/{user_id}")
    def get_user(self, user_id: int) -> dict:
        return {"user_id": user_id}
    
    @post("/")
    def create_user(self, name: str) -> dict:
        return {"created": name}

app = Ravyn(routes=[UserController])
```

Routes created:

- `GET /users/` → list_users
- `GET /users/{user_id}` → get_user
- `POST /users/` → create_user

---

## What is the @controller Decorator?

The `@controller` decorator converts a class into a Controller automatically, giving you:

- **Organized Routes** - Group related endpoints in one class

- **No Subclassing** - No need to inherit from Controller

- **Clean Syntax** - Decorator-based configuration

- **Full Features** - All Controller capabilities available

### Without Decorator (Traditional)

```python
from ravyn.routing import Controller

class UserController(Controller):
    path = "/users"
    
    @get("/")
    def list_users(self) -> dict:
        return {"users": []}
```

### With Decorator (Modern)

```python
from ravyn.decorators import controller

@controller(path="/users")
class UserController:
    @get("/")
    def list_users(self) -> dict:
        return {"users": []}
```

Both work identically—use whichever you prefer!

---

## Controller Configuration

The `@controller` decorator accepts all Controller parameters:

```python
@controller(
    path="/api/users",
    dependencies={},
    exception_handlers={},
    permissions=[],
    interceptors=[],
    middleware=[],
    response_class=JSONResponse,
    response_cookies=[],
    response_headers={},
    before_request=[],
    after_request=[],
    tags=["users"],
    include_in_schema=True,
    security=[],
    deprecated=False
)
class UserController:
    pass
```

---

## Practical Examples

### Example 1: Basic CRUD Controller

```python
from ravyn.decorators import controller
from ravyn import get, post, put, delete

@controller(path="/products")
class ProductController:
    @get("/")
    def list_products(self) -> dict:
        return {"products": ["Laptop", "Phone"]}
    
    @get("/{product_id}")
    def get_product(self, product_id: int) -> dict:
        return {"id": product_id, "name": "Product"}
    
    @post("/")
    def create_product(self, name: str, price: float) -> dict:
        return {"created": name, "price": price}
    
    @put("/{product_id}")
    def update_product(self, product_id: int, name: str) -> dict:
        return {"updated": product_id, "name": name}
    
    @delete("/{product_id}")
    def delete_product(self, product_id: int) -> dict:
        return {"deleted": product_id}
```

### Example 2: Controller with Dependencies

```python
from ravyn.decorators import controller
from ravyn import get, Inject

def get_database():
    return {"db": "postgresql://connected"}

@controller(
    path="/users",
    dependencies={"db": Inject(get_database)}
)
class UserController:
    @get("/")
    def list_users(self, db: dict) -> dict:
        return {"users": ["Alice"], "db": db["db"]}
```

### Example 3: Controller with Custom Headers

```python
from ravyn.decorators import controller
from ravyn import get

@controller(
    path="/api",
    response_headers={"X-API-Version": "1.0"}
)
class APIController:
    @get("/status")
    def status(self) -> dict:
        return {"status": "ok"}
    # Response includes X-API-Version: 1.0 header
```

### Example 4: Controller with Tags (OpenAPI)

```python
from ravyn.decorators import controller
from ravyn import get, post

@controller(
    path="/auth",
    tags=["authentication"]
)
class AuthController:
    @post("/login")
    def login(self, username: str, password: str) -> dict:
        return {"token": "abc123"}
    
    @post("/logout")
    def logout(self) -> dict:
        return {"logged_out": True}
```

---

## Controller vs Decorator

Both approaches work identically:

| Feature | Subclassing | Decorator |
|---------|-------------|-----------|
| **Syntax** | `class X(Controller)` | `@controller class X` |
| **Configuration** | Class attributes | Decorator parameters |
| **Functionality** | Identical | Identical |
| **Style** | Traditional | Modern |

### Subclassing Approach

```python
from ravyn.routing import Controller

class UserController(Controller):
    path = "/users"
    tags = ["users"]
    
    @get("/")
    def list_users(self) -> dict:
        return {"users": []}
```

### Decorator Approach

```python
from ravyn.decorators import controller

@controller(path="/users", tags=["users"])
class UserController:
    @get("/")
    def list_users(self) -> dict:
        return {"users": []}
```

Choose based on your preference—both are fully supported!

---

## Common Pitfalls & Fixes

### Pitfall 1: Forgetting to Import controller

**Problem:** `NameError: name 'controller' is not defined`

```python
# Wrong - controller not imported
@controller(path="/users")
class UserController:
    pass
```

**Solution:** Import from ravyn.decorators:

```python
# Correct
from ravyn.decorators import controller

@controller(path="/users")
class UserController:
    pass
```

### Pitfall 2: Not Providing path

**Problem:** Controller without a base path.

```python
# Wrong - no path specified
@controller()
class UserController:
    @get("/")
    def list_users(self) -> dict:
        return {}
```

**Solution:** Always specify path:

```python
# Correct
@controller(path="/users")
class UserController:
    @get("/")
    def list_users(self) -> dict:
        return {}
```

### Pitfall 3: Mixing Decorator and Subclassing

**Problem:** Using both approaches together.

```python
# Confusing - don't mix both
from ravyn.routing import Controller

@controller(path="/users")
class UserController(Controller):  # Redundant
    pass
```

**Solution:** Choose one approach:

```python
# Option 1: Decorator only
@controller(path="/users")
class UserController:
    pass

# Option 2: Subclassing only
class UserController(Controller):
    path = "/users"
```

---

## Benefits of Using Decorators

### 1. Cleaner Code

```python
# Without decorator
class UserController(Controller):
    path = "/users"
    tags = ["users"]
    dependencies = {"db": Inject(get_db)}

# With decorator
@controller(path="/users", tags=["users"], dependencies={"db": Inject(get_db)})
class UserController:
    pass
```

### 2. Explicit Configuration

All configuration is visible at the decorator level.

### 3. No Inheritance Required

No need to remember to inherit from Controller.

---

## Complete Example

```python
from ravyn import Ravyn, get, post, delete
from ravyn.decorators import controller
from ravyn.exceptions import NotFound

@controller(
    path="/api/posts",
    tags=["posts"],
    response_headers={"X-API-Version": "2.0"}
)
class PostController:
    @get("/")
    def list_posts(self, limit: int = 10) -> dict:
        return {
            "posts": [
                {"id": 1, "title": "First Post"},
                {"id": 2, "title": "Second Post"}
            ][:limit]
        }
    
    @get("/{post_id}")
    def get_post(self, post_id: int) -> dict:
        if post_id > 100:
            raise NotFound(f"Post {post_id} not found")
        return {"id": post_id, "title": f"Post {post_id}"}
    
    @post("/")
    def create_post(self, title: str, content: str) -> dict:
        return {
            "id": 123,
            "title": title,
            "content": content,
            "created": True
        }
    
    @delete("/{post_id}")
    def delete_post(self, post_id: int) -> dict:
        return {"deleted": post_id}

app = Ravyn(routes=[PostController])
```

---

## Next Steps

Now that you understand the `@controller` decorator, explore:

- [Controllers](./routing/controllers.md) - Full controller documentation
- [Routing](./routing/routes.md) - Route configuration
- [Dependencies](./dependencies.md) - Dependency injection
- [Handlers](./routing/handlers.md) - Handler types
