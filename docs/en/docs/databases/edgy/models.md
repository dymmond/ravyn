# User Models

Think of a model as a blueprint for your database table. Just like an architect's blueprint defines what a building will look like, a model defines what data you'll store and how it's structured. In Edgy, models are Python classes that automatically become database tables.

Ravyn provides pre-built User models so you don't have to reinvent the wheel for authentication.

## What You'll Learn

- Using Ravyn's built-in User models
- Creating and managing users
- Password hashing and validation
- Leveraging settings for cleaner code
- Best practices for user authentication

## Quick Start

```python
from ravyn.contrib.auth.edgy.models import User
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

## User Models Overview

Ravyn provides two user models for Edgy integration:

1. **`AbstractUser`** - Base class with all user fields and functionality
2. **`User`** - Ready-to-use subclass of `AbstractUser`

You can use `User` directly or extend `AbstractUser` for custom fields.

---

## Basic Usage

### Using the Default User Model

```python hl_lines="18 33"
{!> ../../../docs_src/databases/edgy/models.py !}
```

This gives you a complete user authentication system with minimal code.

### User Model Fields

The User model includes these Django-inspired fields:

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | CharField | User's first name |
| `last_name` | CharField | User's last name |
| `username` | CharField | Unique username |
| `email` | EmailField | User's email address |
| `password` | CharField | Hashed password |
| `last_login` | DateTimeField | Last login timestamp |
| `is_active` | BooleanField | Account active status |
| `is_staff` | BooleanField | Staff access flag |
| `is_superuser` | BooleanField | Superuser access flag |

---

## Leveraging Settings

Instead of repeating database configuration, use Ravyn settings to centralize your setup:

=== "settings.py"

    ```python hl_lines="15-17"
    {!> ../../../docs_src/databases/edgy/settings/settings.py !}
    ```

=== "models.py"

    ```python hl_lines="18 33"
    {!> ../../../docs_src/databases/edgy/settings/models.py !}
    ```

=== "app.py"

    ```python
    {!> ../../../docs_src/databases/edgy/settings/app.py !}
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
{!> ../../../docs_src/databases/edgy/create_user.py !}
```

**What happens behind the scenes:**

- Password is automatically hashed using bcrypt
- User is created in the database
- Returns the User instance

### create_superuser

Create an admin user with elevated privileges:

```python
{!> ../../../docs_src/databases/edgy/create_superuser.py !}
```

**Automatically sets:**
- `is_staff = True`
- `is_superuser = True`
- `is_active = True`

### check_password

Verify a user's password:

```python hl_lines="28"
{!> ../../../docs_src/databases/edgy/check_password.py !}
```

**Security features:**

- Compares against hashed password
- Constant-time comparison (prevents timing attacks)
- Returns boolean (True/False)

### set_password

Change a user's password:

```python hl_lines="28"
{!> ../../../docs_src/databases/edgy/set_password.py !}
```

**What happens:**

- New password is hashed
- Old password is replaced
- User instance is updated (remember to save!)

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
{!> ../../../docs_src/databases/edgy/hashers.py !}
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

### Pitfall 3: Not Using Unique Constraints

**Problem:** Duplicate emails or usernames.

**Solution:** Add unique constraints in your model:

```python
class CustomUser(AbstractUser):
    email = fields.EmailField(unique=True)
    username = fields.CharField(max_length=150, unique=True)
    
    class Meta:
        registry = registry
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
        registry = settings.edgy_registry
```

---

## Database Migrations

Edgy provides built-in migration commands that use Alembic under the hood:

```shell
# Install Edgy (includes Alembic)
pip install edgy

# Initialize migrations
edgy init

# Create migration
edgy makemigrations

# Apply migrations
edgy migrate
```

Edgy's migration system supports auto-discovery and can be configured using the `--app` flag or `EDGY_DEFAULT_APP` environment variable.

For advanced migration scenarios, you can also use Alembic directly. See [Edgy Migrations](https://edgy.dymmond.com/migrations/discovery/) for complete documentation.

#### Initialize Migrations

**Auto-Discovery:**
```shell
$ edgy init
```

Edgy automatically discovers your application in `src/main.py` following its search pattern.

**Using --app:**
```shell
$ edgy --app src.main init
```

**Using Environment Variable:**
```shell
$ export EDGY_DEFAULT_APP=src.main
$ edgy init
```

#### Create Migrations

**Auto-Discovery:**
```shell
$ edgy makemigrations
```

**Using --app:**
```shell
$ edgy --app src.main makemigrations
```

**Using Environment Variable:**
```shell
$ export EDGY_DEFAULT_APP=src.main
$ edgy makemigrations
```

!!! Note
    As of version 0.23.0, the import path must point to a module where the Instance object triggers automatic registration.

#### Using Preloads

Instead of `--app` or `EDGY_DEFAULT_APP`, use the `preloads` setting in your configuration to specify an import path. When an instance is set in a preloaded file, auto-discovery is skipped.

Edgy provides detailed migration guidance in its [documentation](https://edgy.dymmond.com/migrations/discovery/).

---

## Learn More

- [Edgy Documentation](https://edgy.dymmond.com) - Complete Edgy guide
- [Edgy Migrations](https://edgy.dymmond.com/migrations/discovery/) - Database migrations
- [Passlib Documentation](https://passlib.readthedocs.io/en/stable/) - Password hashing

---

## Next Steps

- [JWT Middleware](./middleware.md) - Secure your APIs
- [Complete Example](./example.md) - Full authentication tutorial
- [Mongoz Documents](../mongoz/documents.md) - NoSQL alternative
