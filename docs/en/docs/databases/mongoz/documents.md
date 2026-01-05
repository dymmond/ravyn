# User Documents

Think of a document as a flexible container for your data. Unlike SQL tables with rigid columns, MongoDB documents are like JSON objects. You can add, remove, or change fields without breaking existing data. In Mongoz, documents are Python classes that automatically become MongoDB collections.

Ravyn provides pre-built User documents so you can focus on building features, not reinventing authentication.

## What You'll Learn

- Using Ravyn's built-in User documents
- Creating and managing users
- Password hashing and validation
- Leveraging settings for cleaner code
- Best practices for user authentication

## Quick Start

```python
from ravyn.contrib.auth.mongoz.documents import User
from ravyn import RavynSettings

# Create a user
user = await User.query.create_user(
    email="user@example.com",
    password="securepassword123",
    first_name="John"
)

# Verify password
is_valid = user.check_password("securepassword123")  # True
```

---

## User Documents Overview

Ravyn provides two user documents for Mongoz integration:

1. **`AbstractUser`** - Base class with all user fields and functionality
2. **`User`** - Ready-to-use subclass of `AbstractUser`

You can use `User` directly or extend `AbstractUser` for custom fields.

---

## Basic Usage

### Using the Default User Document

```python
{!> ../../../docs_src/databases/mongoz/models.py !}
```

This gives you a complete user authentication system with minimal code.

### User Document Fields

The User document includes these Django-inspired fields:

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | String | User's first name |
| `last_name` | String | User's last name |
| `username` | String | Unique username |
| `email` | Email | User's email address |
| `password` | String | Hashed password |
| `last_login` | DateTime | Last login timestamp |
| `is_active` | Boolean | Account active status |
| `is_staff` | Boolean | Staff access flag |
| `is_superuser` | Boolean | Superuser access flag |

---

## Leveraging Settings

Instead of repeating database configuration, use Ravyn settings to centralize your setup:

=== "settings.py"

    ```python hl_lines="10-12"
    {!> ../../../docs_src/databases/mongoz/settings/settings.py !}
    ```

=== "documents.py"

    ```python hl_lines="9 32"
    {!> ../../../docs_src/databases/mongoz/settings/models.py !}
    ```

This approach lets you:

- Access database configuration anywhere in your codebase
- Avoid repeating yourself
- Easily switch between environments
- Share configuration across multiple apps

---

## User Management Functions

!!! Warning
    The following examples assume you're using settings as [described above](#leveraging-settings).

### create_user

Create a regular user with automatic password hashing:

```python
{!> ../../../docs_src/databases/mongoz/create_user.py !}
```

**What happens behind the scenes:**

- Password is automatically hashed using bcrypt
- User is created in the database
- Returns the User instance

### create_superuser

Create an admin user with elevated privileges:

```python
{!> ../../../docs_src/databases/mongoz/create_superuser.py !}
```

**Automatically sets:**
- `is_staff = True`
- `is_superuser = True`
- `is_active = True`

### check_password

Verify a user's password:

```python hl_lines="28"
{!> ../../../docs_src/databases/mongoz/check_password.py !}
```

**Security features:**

- Compares against hashed password
- Constant-time comparison (prevents timing attacks)
- Returns boolean (True/False)

### set_password

Change a user's password:

```python hl_lines="28"
{!> ../../../docs_src/databases/mongoz/set_password.py !}
```

**What happens:**

- New password is hashed
- Old password is replaced
- Document instance is updated (remember to save!)

---

## Password Hashing

Ravyn uses secure password hashing out of the box.

### Default Hashers

```python
@property
def password_hashers(self) -> list[str]:
    return [
        "ravyn.contrib.auth.hashers.BcryptPasswordHasher",
    ]
```

Ravyn uses [passlib](https://passlib.readthedocs.io/en/stable/) under the hood for secure password hashing.

### Custom Hashers

Override the `password_hashers` property in your settings:

```python
{!> ../../../docs_src/databases/mongoz/hashers.py !}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Forgetting to Save After set_password

**Problem:** Password change doesn't persist.

```python
# Wrong - password not saved
user.set_password("newpassword")
# User logs out, can't log back in!
```

**Solution:** Always save after setting password:

```python
# Correct
user.set_password("newpassword")
await user.save()
```

### Pitfall 2: Storing Plain Text Passwords

**Problem:** Manually setting password field.

```python
# Wrong - plain text password!
user = await User.query.create(
    email="user@example.com",
    password="plaintext123"  # Not hashed!
)
```

**Solution:** Use `create_user` or `set_password`:

```python
# Correct
user = await User.query.create_user(
    email="user@example.com",
    password="plaintext123"  # Automatically hashed
)
```

### Pitfall 3: Not Using Unique Indexes

**Problem:** Duplicate emails or usernames.

**Solution:** Add unique indexes in your document:

```python
class CustomUser(AbstractUser):
    email = fields.Email()
    username = fields.String(max_length=150)
    
    class Meta:
        registry = registry
        database = "myapp"
        indexes = [
            mongoz.Index("email", unique=True),
            mongoz.Index("username", unique=True)
        ]
```

---

## Best Practices

### 1. Use create_user for User Creation

```python
# Good - automatic password hashing
user = await User.query.create_user(
    email="user@example.com",
    password="secure123"
)
```

### 2. Validate Before Creating

```python
# Good - validate input first
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# Then create user
data = UserCreate(email="user@example.com", password="securepass123")
user = await User.query.create_user(**data.dict())
```

### 3. Use Settings for Registry

```python
# Good - centralized configuration
from ravyn.conf import settings

class User(AbstractUser):
    class Meta:
        registry = settings.mongo_registry
        database = "myapp"
```

### 4. Add Indexes for Performance

```python
class User(AbstractUser):
    class Meta:
        registry = registry
        database = "myapp"
        indexes = [
            "email",  # Single field
            [("email", 1), ("is_active", -1)]  # Compound
        ]
```

---

## MongoDB Advantages

### No Migrations Needed

Unlike SQL, you can add fields without migrations:

```python
# Start with basic user
class User(AbstractUser):
    pass

# Later, add fields without migrations
class User(AbstractUser):
    phone = fields.String()  # Just add it!
    preferences = fields.Object()  # Flexible nested data
```

### Flexible Schema

Store varying data structures:

```python
# Different users can have different fields
user1 = User(email="user1@example.com", bio="Short bio")
user2 = User(email="user2@example.com", social_links={...})
```

---

## Learn More

- [Mongoz Documentation](https://mongoz.tarsild.io) - Complete Mongoz guide
- [MongoDB Documentation](https://docs.mongodb.com/) - MongoDB reference
- [Passlib Documentation](https://passlib.readthedocs.io/en/stable/) - Password hashing

---

## Next Steps

- [JWT Middleware](./middleware.md) - Secure your APIs
- [Complete Example](./example.md) - Full authentication tutorial
- [Edgy Models](../edgy/models.md) - SQL alternative
