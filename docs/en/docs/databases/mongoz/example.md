# Complete Authentication Example

Building a secure authentication system from scratch can take days. Between password hashing, JWT tokens, user management, and protecting routes, there's a lot to get right. This example shows you how to build a production-ready auth system with Ravyn and Mongoz in minutes, not days.

Let's build a complete user authentication system with registration, login, and protected routes using MongoDB.

## What You'll Learn

- Creating user documents with Mongoz
- Building registration and login APIs
- Implementing JWT authentication
- Protecting routes with middleware
- Refreshing JWT tokens
- Testing the complete flow

## What We're Building

A complete authentication system with:

- **User Registration** - Create new accounts
- **User Login** - Authenticate and get JWT token
- **Protected Routes** - Access user-specific data
- **Token Refresh** - Keep users logged in
- **Password Security** - Automatic hashing with bcrypt

---

## Project Structure

We'll organize our code like this:

```
myapp/
├── accounts/
│   ├── documents.py     # User document
│   └── controllers.py   # API endpoints
├── settings.py          # App configuration
└── app.py              # Main application
```

**Assumptions:**
- Documents are in `accounts/documents.py`
- Controllers/APIs are in `accounts/controllers.py`
- Main app is in `app.py`
- [JWTConfig](../../configurations/jwt.md#jwtconfig-and-application-settings) is in your global [settings](../../application/settings.md)

!!! Tip
    For local development, use Docker for MongoDB:
    ```shell
    docker run -d -p 27017:27017 --name mongodb mongo:latest
    ```

**Let's go!**

---

## Step 1: Create User Document

First, define a User document using Ravyn's built-in authentication document:

```python title="accounts/documents.py"
{!> ../../../docs_src/databases/mongoz/example/create_model.py !}
```

This gives you a complete User document with password hashing, validation, and all the fields you need.

---

## Step 2: Create User API

Build an API endpoint to register new users:

```python title="accounts/controllers.py"
{!> ../../../docs_src/databases/mongoz/example/create_user.py !}
```

**What this does:**
- Accepts user registration data
- Validates email and password
- Creates user with hashed password
- Returns success response

!!! Note
    This example doesn't handle edge cases like duplicate emails. In production, add proper error handling for unique constraint violations.

---

## Step 3: Login API

Create an endpoint that authenticates users and returns a JWT token:

```python title="accounts/controllers.py"
{!> ../../../docs_src/databases/mongoz/example/login.py !}
```

**What's happening here:**

1. **Receive credentials** - Email and password from the request
2. **Validate data** - `BackendAuthentication` uses Pydantic for validation
3. **Authenticate user** - Checks password and generates JWT
4. **Return token** - Client uses this for subsequent requests

The `BackendAuthentication` class handles all the heavy lifting:
- Validates credentials
- Checks password hash
- Generates JWT token
- Returns token or raises error

!!! Warning
    Make sure your [JWTConfig](../../configurations/jwt.md#jwtconfig-and-application-settings) is configured in your global settings as assumed at the top of this document.

---

## Step 4: Protected Home API

Create an endpoint that requires authentication:

```python title="accounts/controllers.py"
{!> ../../../docs_src/databases/mongoz/example/home.py !}
```

**Simple and clean:**
- Middleware validates JWT token
- User is automatically injected into `request.user`
- Return user-specific data

---

## Step 5: Assemble the Application

Put it all together in your main application:

```python title="app.py"
{!> ../../../docs_src/databases/mongoz/example/assemble.py !}
```

**Notice the middleware placement:**

The `JWTAuthMiddleware` is inside the `Include` for `/`, not in the main Ravyn instance. This is intentional!

- **Public routes** (`/create`, `/login`) - No authentication needed
- **Protected routes** (`/`) - Authentication required

Each `Include` can have its own middleware, giving you fine-grained control over which routes require authentication.

---

## Step 6: Refreshing Tokens

JWT tokens expire for security. Implement token refresh to keep users logged in without re-entering credentials.

Ravyn provides a complete guide for implementing refresh tokens:

[See refresh token implementation →](../../configurations/jwt.md#the-claims)

**Key concepts:**
- Issue both access and refresh tokens
- Access tokens expire quickly (15 minutes)
- Refresh tokens last longer (7 days)
- Use refresh token to get new access token

---

## Testing the Flow

Let's test the complete authentication flow using `httpx`:

### Complete Test Script

```python
{!> ../../../docs_src/databases/mongoz/example/access.py !}
```

### Step-by-Step

**1. Create a user:**
```python
response = client.post("/create", json={
    "email": "user@example.com",
    "password": "securepass123"
})
```

**2. Login and get token:**
```python
response = client.post("/login", json={
    "email": "user@example.com",
    "password": "securepass123"
})
token = response.json()["token"]
```

**3. Access protected route:**
```python
response = client.get("/", headers={
    "Authorization": f"Bearer {token}"
})
```

**The Authorization header:**

Notice the `Authorization` header format: `Bearer {token}`. This is the default expected by [JWTConfig](../../configurations/jwt.md#parameters). The header name (`Authorization`) is configurable in JWTConfig.

---

## Common Pitfalls & Fixes

### Pitfall 1: Middleware on Wrong Routes

**Problem:** Auth middleware on login/register routes.

```python
# Wrong - can't login if auth is required!
app = Ravyn(
    middleware=[JWTAuthMiddleware(...)],  # Applies to ALL routes
    routes=[...]
)
```

**Solution:** Apply middleware selectively:

```python
# Correct - auth only where needed
app = Ravyn(routes=[
    Gateway(handler=create_user),  # No auth
    Gateway(handler=login),        # No auth
    Include(
        routes=[Gateway(handler=home)],
        middleware=[JWTAuthMiddleware(...)]  # Auth required
    )
])
```

### Pitfall 2: Missing Token in Requests

**Problem:** Forgetting to include JWT token.

```javascript
// Wrong
fetch('/api/profile')
```

**Solution:** Always include Authorization header:

```javascript
// Correct
fetch('/api/profile', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
```

### Pitfall 3: MongoDB Connection Not Closed

**Problem:** Not properly closing MongoDB connections.

**Solution:** Use context managers or lifespan events:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # Startup
    await client.connect()
    yield
    # Shutdown
    await client.disconnect()

app = Ravyn(lifespan=lifespan)
```

---

## Best Practices

### 1. Use Environment Variables

```python
# settings.py
import os

class AppSettings(RavynSettings):
    jwt_secret: str = os.getenv("JWT_SECRET")
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
```

### 2. Validate Input Data

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        return v
```

### 3. Handle Errors Gracefully

```python
@post("/login")
async def login(data: dict) -> JSONResponse:
    try:
        auth = BackendAuthentication(**data)
        token = await auth.authenticate()
        return JSONResponse({"token": token})
    except AuthenticationError:
        return JSONResponse(
            {"error": "Invalid credentials"},
            status_code=401
        )
```

### 4. Use Indexes for Performance

```python
class User(AbstractUser):
    class Meta:
        registry = registry
        database = "myapp"
        indexes = [
            mongoz.Index("email", unique=True),
            mongoz.Index("username", unique=True)
        ]
```

### 5. Use HTTPS in Production

Always use HTTPS to protect JWT tokens in transit.

---

## MongoDB Advantages

### No Migrations

Unlike SQL, you can modify your schema without migrations:

```python
# Add fields anytime
class User(AbstractUser):
    phone = fields.String()  # Just add it!
    preferences = fields.Object()  # No migration needed
```

### Flexible Data

Store varying user data:

```python
# Different users can have different fields
user1 = User(email="user1@example.com", bio="Short")
user2 = User(email="user2@example.com", social={...})
```

---

## Conclusion

You've built a complete, production-ready authentication system with:

✅ User registration with password hashing
✅ Login with JWT token generation  
✅ Protected routes with middleware
✅ Clean, maintainable code structure
✅ MongoDB flexibility

This is just the beginning. You can extend this with:
- Email verification
- Password reset
- Role-based permissions
- OAuth integration
- Two-factor authentication

---

## Learn More

- [User Documents](./documents.md) - Deep dive into user documents
- [JWT Middleware](./middleware.md) - Middleware configuration
- [JWTConfig](../../configurations/jwt.md) - JWT configuration options
- [Refresh Tokens](../../configurations/jwt.md#the-claims) - Token refresh implementation

---

## Next Steps

- [Edgy Example](../edgy/example.md) - SQL authentication
- [Permissions](../../permissions/index.md) - Add role-based access
- [Testing](../../guides/more-advanced/02-testing.md) - Test your authentication
