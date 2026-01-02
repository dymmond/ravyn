# Password Hashers

Password hashers provide secure, salted password hashing for your Ravyn application. Never store passwords in plain text—always hash them with a strong algorithm.

## What You'll Learn

- Using built-in password hashers
- Hashing and verifying passwords
- Creating custom hashers
- Configuring hashers in settings

## Quick Start

```python
from ravyn.contrib.auth.hashers import make_password, check_password

# Hash a password
hashed = make_password("my-secret-password")
# Returns: "$bcrypt$2b$12$..."

# Verify a password
is_valid = check_password("my-secret-password", hashed)
# Returns: True

is_valid = check_password("wrong-password", hashed)
# Returns: False
```

---

## Why Use Password Hashers?

### Security Benefits:

- **Salted Hashing** - Each password gets a unique salt

- **One-Way Function** - Cannot reverse hash to get password

- **Slow Algorithms** - Resistant to brute-force attacks

- **Industry Standard** - Uses proven algorithms (bcrypt, PBKDF2)

### Never Do This:

Store passwords in plain text

Use simple hashing (MD5, SHA1) without salt

Use fast hashing algorithms

---

## Built-In Hashers

Ravyn provides password hashers via `passlib`:

```python
from ravyn.contrib.auth.hashers import (
    make_password,
    check_password,
    BcryptPasswordHasher,
    PBKDF2PasswordHasher,
    PBKDF2SHA1PasswordHasher
)
```

### Default Hasher: Bcrypt

```python
from ravyn.contrib.auth.hashers import make_password

# Uses bcrypt by default
hashed = make_password("my-password")
print(hashed)
# Output: $bcrypt$2b$12$abcd1234...
```

---

## Using Password Hashers

### Hash a Password

```python
from ravyn.contrib.auth.hashers import make_password

# Hash password
hashed_password = make_password("user-password-123")

# Store in database
user.password = hashed_password
await user.save()
```

### Verify a Password

```python
from ravyn.contrib.auth.hashers import check_password

# Get user from database
user = await User.get(email="user@example.com")

# Check password
if check_password("user-input-password", user.password):
    print("Password correct!")
else:
    print("Password incorrect!")
```

### Complete Login Example

```python
from ravyn import post
from ravyn.contrib.auth.hashers import check_password
from ravyn.exceptions import NotAuthorized

@post("/login")
async def login(email: str, password: str) -> dict:
    # Get user from database
    user = await User.get_or_none(email=email)
    
    if not user:
        raise NotAuthorized("Invalid credentials")
    
    # Verify password
    if not check_password(password, user.password):
        raise NotAuthorized("Invalid credentials")
    
    # Generate token or session
    return {"token": "abc123", "user_id": user.id}
```

### Registration Example

```python
from ravyn import post
from ravyn.contrib.auth.hashers import make_password

@post("/register")
async def register(email: str, password: str, name: str) -> dict:
    # Hash password
    hashed_password = make_password(password)
    
    # Create user
    user = await User.create(
        email=email,
        password=hashed_password,
        name=name
    )
    
    return {"user_id": user.id, "email": user.email}
```

---

## Configuring Hashers

### Via Settings

```python
from ravyn import RavynSettings

class Settings(RavynSettings):
    @property
    def password_hashers(self) -> list[str]:
        return [
            "ravyn.contrib.auth.hashers.BcryptPasswordHasher",
            "ravyn.contrib.auth.hashers.PBKDF2PasswordHasher",
        ]

app = Ravyn(settings_module=Settings)
```

### Available Hashers

| Hasher | Algorithm | Speed | Security |
|--------|-----------|-------|----------|
| `BcryptPasswordHasher` | bcrypt | Slow (good) | ⭐⭐⭐⭐⭐ |
| `PBKDF2PasswordHasher` | PBKDF2-SHA256 | Slow (good) | ⭐⭐⭐⭐ |
| `PBKDF2SHA1PasswordHasher` | PBKDF2-SHA1 | Slow (good) | ⭐⭐⭐ |

!!! tip
    Use `BcryptPasswordHasher` (default) for best security.

---

## Creating Custom Hashers

Subclass `BasePasswordHasher` to create custom hashers:

```python
from ravyn.contrib.auth.hashers import BasePasswordHasher
import hashlib

class CustomHasher(BasePasswordHasher):
    algorithm = "custom"
    
    def encode(self, password: str, salt: str) -> str:
        # Your hashing logic
        hash_value = hashlib.sha256(
            f"{salt}{password}".encode()
        ).hexdigest()
        return f"${self.algorithm}${salt}${hash_value}"
    
    def verify(self, password: str, encoded: str) -> bool:
        # Your verification logic
        algorithm, salt, hash_value = encoded.split("$")[1:]
        return self.encode(password, salt) == encoded
    
    def safe_summary(self, encoded: str) -> dict:
        algorithm, salt, hash_value = encoded.split("$")[1:]
        return {
            "algorithm": algorithm,
            "salt": salt[:8] + "...",
            "hash": hash_value[:8] + "..."
        }
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Storing Plain Text Passwords

**Problem:** Passwords stored without hashing.

```python
# NEVER DO THIS - Security vulnerability!
@post("/register")
async def register(email: str, password: str) -> dict:
    user = await User.create(
        email=email,
        password=password  # Plain text!
    )
    return {"user_id": user.id}
```

**Solution:** Always hash passwords:

```python
# Correct - Hash before storing
from ravyn.contrib.auth.hashers import make_password

@post("/register")
async def register(email: str, password: str) -> dict:
    user = await User.create(
        email=email,
        password=make_password(password)  # Hashed!
    )
    return {"user_id": user.id}
```

### Pitfall 2: Comparing Hashed Passwords Directly

**Problem:** Using `==` to compare passwords.

```python
# Wrong - won't work
if user_input_password == user.password:
    # This will never be True!
    pass
```

**Solution:** Use `check_password()`:

```python
# Correct
from ravyn.contrib.auth.hashers import check_password

if check_password(user_input_password, user.password):
    # Correct verification
    pass
```

### Pitfall 3: Revealing User Existence

**Problem:** Different error messages for invalid email vs password.

```python
# Security issue - reveals if email exists
@post("/login")
async def login(email: str, password: str) -> dict:
    user = await User.get_or_none(email=email)
    
    if not user:
        raise NotAuthorized("Email not found")  # Reveals email doesn't exist
    
    if not check_password(password, user.password):
        raise NotAuthorized("Wrong password")  # Reveals email exists
```

**Solution:** Use same error message:

```python
# Correct - same error for both cases
@post("/login")
async def login(email: str, password: str) -> dict:
    user = await User.get_or_none(email=email)
    
    if not user or not check_password(password, user.password):
        raise NotAuthorized("Invalid credentials")  # Same message
    
    return {"token": "..."}
```

### Pitfall 4: Not Installing passlib

**Problem:** `ModuleNotFoundError` when using hashers.

```python
# Error if passlib not installed
from ravyn.contrib.auth.hashers import make_password
```

**Solution:** Install passlib:

```shell
pip install passlib[bcrypt]
```

---

## Best Practices

### 1. Use Strong Passwords

```python
# Good - enforce password strength
from ravyn.exceptions import ValidationError

@post("/register")
async def register(email: str, password: str) -> dict:
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain uppercase letter")
    
    hashed = make_password(password)
    user = await User.create(email=email, password=hashed)
    return {"user_id": user.id}
```

### 2. Add Rate Limiting

```python
# Good - prevent brute force
from ravyn import post
from ravyn.exceptions import TooManyRequests

login_attempts = {}

@post("/login")
async def login(email: str, password: str, request: Request) -> dict:
    client_ip = request.client.host
    
    # Check attempts
    if login_attempts.get(client_ip, 0) >= 5:
        raise TooManyRequests("Too many login attempts")
    
    user = await User.get_or_none(email=email)
    
    if not user or not check_password(password, user.password):
        login_attempts[client_ip] = login_attempts.get(client_ip, 0) + 1
        raise NotAuthorized("Invalid credentials")
    
    # Reset on success
    login_attempts.pop(client_ip, None)
    return {"token": "..."}
```

### 3. Use Timing-Safe Comparison

```python
# Good - check_password uses timing-safe comparison
if check_password(user_input, stored_hash):
    # Safe from timing attacks
    pass
```

---

## Integration with Edgy ORM

Ravyn works seamlessly with Edgy for user management:

```python
from edgy import Database, Registry, Model, fields
from ravyn.contrib.auth.hashers import make_password, check_password

database = Database("postgresql://localhost/mydb")
registry = Registry(database=database)

class User(Model):
    email = fields.EmailField(max_length=100, unique=True)
    password = fields.CharField(max_length=255)
    name = fields.CharField(max_length=100)
    
    class Meta:
        registry = registry
    
    def set_password(self, raw_password: str):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

# Usage
user = User(email="user@example.com", name="Alice")
user.set_password("my-secret-password")
await user.save()

# Verify
if user.check_password("my-secret-password"):
    print("Password correct!")
```

---

## Next Steps

Now that you understand password hashers, explore:

- [Security](./security/index.md) - Authentication & authorization
- [Permissions](./permissions/index.md) - Access control
- [Edgy ORM](./databases/edgy/motivation.md) - Database integration
- [Exceptions](./exceptions.md) - Error handling
