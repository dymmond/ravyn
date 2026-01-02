# Protocols

Protocols define interfaces (contracts) for your application, helping you separate business logic from request handlers. Think of them as blueprints that ensure consistent patterns across your codebase.

## What You'll Learn

- What protocols are and why they matter
- Using the DAO pattern for data access
- Separating business logic from handlers
- Creating clean, maintainable code
- Implementing custom protocols

## Quick Start

```python
from ravyn import Ravyn, get, post
from ravyn import AsyncDAOProtocol

class UserDAO(AsyncDAOProtocol):
    async def get(self, user_id: int):
        # Get user from database
        return {"id": user_id, "name": "Alice"}
    
    async def get_all(self):
        # Get all users
        return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    
    async def create(self, data: dict):
        # Create user
        return {"id": 3, **data}
    
    async def update(self, user_id: int, data: dict):
        # Update user
        return {"id": user_id, **data}
    
    async def delete(self, user_id: int):
        # Delete user
        return {"deleted": True}

# Use in handlers
user_dao = UserDAO()

@get("/users")
async def list_users() -> dict:
    users = await user_dao.get_all()
    return {"users": users}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    user = await user_dao.create({"name": name, "email": email})
    return user

app = Ravyn()
app.add_route(list_users)
app.add_route(create_user)
```

---

## Why Use Protocols?

### Benefits:

- **Separation of Concerns** - Business logic separate from handlers

- **Single Source of Truth** - All user operations in one place

- **Testability** - Easy to mock and test

- **Maintainability** - Changes in one place, not scattered

- **Consistency** - Enforced patterns across codebase

### Without Protocols (Bad):

```python
# Handler does everything - hard to maintain
@post("/users")
async def create_user(name: str, email: str) -> dict:
    # Check if user exists
    existing = await db.fetch_one("SELECT * FROM users WHERE email = ?", email)
    if existing:
        raise ValidationError("User exists")
    
    # Create user
    user_id = await db.execute("INSERT INTO users (name, email) VALUES (?, ?)", name, email)
    
    # Send welcome email
    await send_email(email, "Welcome!")
    
    # Log creation
    await log_event("user_created", user_id)
    
    return {"user_id": user_id}
```

### With Protocols (Good):

```python
# Clean handler - delegates to DAO
@post("/users")
async def create_user(name: str, email: str) -> dict:
    user = await user_dao.create({"name": name, "email": email})
    return user

# All logic in DAO
class UserDAO(AsyncDAOProtocol):
    async def create(self, data: dict):
        # Check if exists
        if await self._user_exists(data["email"]):
            raise ValidationError("User exists")
        
        # Create user
        user_id = await db.execute("INSERT INTO users ...")
        
        # Send email
        await send_email(data["email"], "Welcome!")
        
        # Log event
        await log_event("user_created", user_id)
        
        return {"user_id": user_id, **data}
```

---

## DAO Protocol

DAO (Data Access Object) separates data access logic from business logic.

### AsyncDAOProtocol

For async operations:

```python
from ravyn import AsyncDAOProtocol

class ProductDAO(AsyncDAOProtocol):
    async def get(self, product_id: int):
        """Get single product"""
        return await db.fetch_one("SELECT * FROM products WHERE id = ?", product_id)
    
    async def get_all(self):
        """Get all products"""
        return await db.fetch_all("SELECT * FROM products")
    
    async def create(self, data: dict):
        """Create product"""
        product_id = await db.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            data["name"], data["price"]
        )
        return {"id": product_id, **data}
    
    async def update(self, product_id: int, data: dict):
        """Update product"""
        await db.execute(
            "UPDATE products SET name = ?, price = ? WHERE id = ?",
            data["name"], data["price"], product_id
        )
        return {"id": product_id, **data}
    
    async def delete(self, product_id: int):
        """Delete product"""
        await db.execute("DELETE FROM products WHERE id = ?", product_id)
        return {"deleted": True}
```

### DAOProtocol

For sync operations:

```python
from ravyn import DAOProtocol

class UserDAO(DAOProtocol):
    def get(self, user_id: int):
        return db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    def get_all(self):
        return db.query("SELECT * FROM users")
    
    def create(self, data: dict):
        user_id = db.execute("INSERT INTO users ...", data)
        return {"id": user_id, **data}
    
    def update(self, user_id: int, data: dict):
        db.execute("UPDATE users ...", data, user_id)
        return {"id": user_id, **data}
    
    def delete(self, user_id: int):
        db.execute("DELETE FROM users WHERE id = ?", user_id)
        return {"deleted": True}
```

---

## Required Methods

Both `AsyncDAOProtocol` and `DAOProtocol` require these methods:

| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `get()` | Get single item | ID or key | Single item |
| `get_all()` | Get all items | None | List of items |
| `create()` | Create item | Data dict | Created item |
| `update()` | Update item | ID, Data dict | Updated item |
| `delete()` | Delete item | ID | Deletion confirmation |

!!! info
    You can add additional methods beyond these five required ones!

---

## Practical Examples

### Example 1: Complete User DAO

```python
from ravyn import AsyncDAOProtocol
from ravyn.exceptions import NotFound, ValidationError

class UserDAO(AsyncDAOProtocol):
    async def get(self, user_id: int):
        user = await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
        if not user:
            raise NotFound(f"User {user_id} not found")
        return user
    
    async def get_all(self):
        return await db.fetch_all("SELECT * FROM users")
    
    async def create(self, data: dict):
        # Validate
        if await self.email_exists(data["email"]):
            raise ValidationError("Email already exists")
        
        # Create
        user_id = await db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            data["name"], data["email"], data["password"]
        )
        
        # Send welcome email
        await self._send_welcome_email(data["email"])
        
        return {"id": user_id, **data}
    
    async def update(self, user_id: int, data: dict):
        # Check exists
        if not await self.exists(user_id):
            raise NotFound(f"User {user_id} not found")
        
        # Update
        await db.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            data["name"], data["email"], user_id
        )
        
        return {"id": user_id, **data}
    
    async def delete(self, user_id: int):
        await db.execute("DELETE FROM users WHERE id = ?", user_id)
        return {"deleted": True}
    
    # Additional custom methods
    async def email_exists(self, email: str) -> bool:
        result = await db.fetch_one("SELECT id FROM users WHERE email = ?", email)
        return result is not None
    
    async def exists(self, user_id: int) -> bool:
        result = await db.fetch_one("SELECT id FROM users WHERE id = ?", user_id)
        return result is not None
    
    async def _send_welcome_email(self, email: str):
        # Email sending logic
        pass
```

### Example 2: Using DAO in Handlers

```python
from ravyn import get, post, put, delete

user_dao = UserDAO()

@get("/users")
async def list_users() -> dict:
    users = await user_dao.get_all()
    return {"users": users}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    user = await user_dao.get(user_id)
    return user

@post("/users")
async def create_user(name: str, email: str, password: str) -> dict:
    user = await user_dao.create({
        "name": name,
        "email": email,
        "password": password
    })
    return user

@put("/users/{user_id}")
async def update_user(user_id: int, name: str, email: str) -> dict:
    user = await user_dao.update(user_id, {"name": name, "email": email})
    return user

@delete("/users/{user_id}")
async def delete_user(user_id: int) -> dict:
    result = await user_dao.delete(user_id)
    return result
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Not Implementing All Methods

**Problem:** Missing required methods.

```python
# Wrong - missing methods
class UserDAO(AsyncDAOProtocol):
    async def get(self, user_id: int):
        return await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
    
    # Missing: get_all, create, update, delete
```

**Solution:** Implement all five required methods:

```python
# Correct
class UserDAO(AsyncDAOProtocol):
    async def get(self, user_id: int):
        pass
    
    async def get_all(self):
        pass
    
    async def create(self, data: dict):
        pass
    
    async def update(self, user_id: int, data: dict):
        pass
    
    async def delete(self, user_id: int):
        pass
```

### Pitfall 2: Business Logic in Handlers

**Problem:** Handler contains business logic.

```python
# Wrong - logic in handler
@post("/users")
async def create_user(email: str) -> dict:
    # Check if exists
    existing = await db.fetch_one("SELECT * FROM users WHERE email = ?", email)
    if existing:
        raise ValidationError("User exists")
    
    # Create user
    user_id = await db.execute("INSERT INTO users ...")
    
    # Send email
    await send_email(email, "Welcome!")
    
    return {"user_id": user_id}
```

**Solution:** Move logic to DAO:

```python
# Correct - logic in DAO
@post("/users")
async def create_user(email: str) -> dict:
    user = await user_dao.create({"email": email})
    return user

class UserDAO(AsyncDAOProtocol):
    async def create(self, data: dict):
        # All logic here
        if await self.email_exists(data["email"]):
            raise ValidationError("User exists")
        
        user_id = await db.execute("INSERT INTO users ...")
        await send_email(data["email"], "Welcome!")
        
        return {"user_id": user_id, **data}
```

### Pitfall 3: Not Using Type Hints

**Problem:** Missing type hints make code unclear.

```python
# Wrong - no type hints
class UserDAO(AsyncDAOProtocol):
    async def get(self, user_id):
        return await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
```

**Solution:** Add type hints:

```python
# Correct
class UserDAO(AsyncDAOProtocol):
    async def get(self, user_id: int) -> dict:
        return await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
```

---

## Best Practices

### 1. One DAO Per Entity

```python
# Good - separate DAOs
class UserDAO(AsyncDAOProtocol):
    pass

class ProductDAO(AsyncDAOProtocol):
    pass

class OrderDAO(AsyncDAOProtocol):
    pass
```

### 2. Add Custom Methods

```python
# Good - custom methods beyond required ones
class UserDAO(AsyncDAOProtocol):
    # Required methods
    async def get(self, user_id: int):
        pass
    
    # ... other required methods ...
    
    # Custom methods
    async def get_by_email(self, email: str):
        return await db.fetch_one("SELECT * FROM users WHERE email = ?", email)
    
    async def get_active_users(self):
        return await db.fetch_all("SELECT * FROM users WHERE active = true")
    
    async def deactivate(self, user_id: int):
        await db.execute("UPDATE users SET active = false WHERE id = ?", user_id)
```

### 3. Handle Errors in DAO

```python
# Good - error handling in DAO
class UserDAO(AsyncDAOProtocol):
    async def get(self, user_id: int):
        user = await db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
        if not user:
            raise NotFound(f"User {user_id} not found")
        return user
```

---

## InterceptorProtocol

For creating custom interceptors:

```python
from ravyn.protocols import InterceptorProtocol

class MyInterceptor(InterceptorProtocol):
    async def intercept(self, request, call_next):
        # Pre-request logic
        print(f"Request: {request.url.path}")
        
        # Call handler
        response = await call_next(request)
        
        # Post-request logic
        print(f"Response: {response.status_code}")
        
        return response
```

See [Interceptors](./interceptors.md) for more details.

---

## Next Steps

Now that you understand protocols, explore:

- [Dependencies](./dependencies.md) - Inject DAOs into handlers
- [Interceptors](./interceptors.md) - Request interception
- [Edgy ORM](./databases/edgy/motivation.md) - Database integration
- [Testing](./testclient.md) - Test your DAOs
