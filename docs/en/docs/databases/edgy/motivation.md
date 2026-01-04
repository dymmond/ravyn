# Edgy - SQL ORM Integration

Think of an ORM as a translator between two languages. Your Python code speaks in objects and methods, while your database speaks in tables and SQL. An ORM bridges this gap, letting you work with databases using familiar Python syntax instead of writing raw SQL queries.

Edgy is a modern, async-first ORM that makes working with SQL databases feel natural and pythonic.

## What You'll Learn

- Why use Edgy with Ravyn
- Key features and benefits
- How to install and set up Edgy
- When to choose SQL over NoSQL
- Getting started with Edgy integration

## Quick Start

```python
from ravyn import Ravyn
from edgy import Database, Registry, Model, fields

# Setup database
database = Database("sqlite:///db.sqlite")
registry = Registry(database=database)

# Define a model
class User(Model):
    name = fields.CharField(max_length=100)
    email = fields.EmailField()
    
    class Meta:
        registry = registry

# Use in Ravyn
app = Ravyn()
```

---

## Why Edgy?

### Built for Modern Python

Edgy is designed from the ground up for async Python and modern development practices:

✨ **100% Type-Safe** - Full type hints and IDE autocomplete

✨ **Async-First** - Native async/await support

✨ **Pydantic Integration** - Seamless data validation

✨ **SQLAlchemy Core** - Battle-tested SQL generation

✨ **Multiple Databases** - PostgreSQL, MySQL, SQLite, and more

### Same Author, Better Integration

[Edgy](https://edgy.dymmond.com) is created by the same author as Ravyn, ensuring:

- Consistent design philosophy
- Seamless integration
- Regular updates and compatibility
- Shared best practices

!!! Tip
    While Ravyn provides built-in support for Edgy, you're free to use any ORM you prefer. Ravyn is database-agnostic: use SQLAlchemy, Tortoise ORM, Piccolo, or any other tool that fits your needs.

---

## Key Features

### 100% Pydantic

Models are Pydantic models under the hood:

```python
class User(Model):
    name = fields.CharField(max_length=100)
    email = fields.EmailField()
    age = fields.IntegerField(minimum=0)
    
    class Meta:
        registry = registry

# Automatic validation
user = User(name="John", email="john@example.com", age=25)
```

### Intuitive Querying

Django-inspired query API that feels natural:

```python
# Simple queries
users = await User.query.all()
user = await User.query.get(id=1)
active_users = await User.query.filter(is_active=True)

# Complex queries
admins = await User.query.filter(
    is_staff=True,
    is_active=True
).order_by("-created_at").limit(10)
```

### Powerful Relationships

Define relationships with ease:

```python
class Post(Model):
    title = fields.CharField(max_length=200)
    author = fields.ForeignKey("User", on_delete=fields.CASCADE)
    
    class Meta:
        registry = registry

# Query with relationships
posts = await Post.query.select_related("author").all()
```

### Async Performance

Built for high-concurrency applications:

```python
# Concurrent database operations
async with database:
    users, posts = await asyncio.gather(
        User.query.all(),
        Post.query.all()
    )
```

---

## Installation

### Basic Installation

```shell
pip install edgy
```

### With Database Drivers

**PostgreSQL:**
```shell
pip install edgy[postgres]
```

**MySQL:**
```shell
pip install edgy[mysql]
```

**SQLite (included):**
```shell
pip install edgy[sqlite]
```

### JDBC Support

For databases without async drivers, use JDBC (requires Java):

```shell
pip install edgy[jdbc]
# or manually
pip install edgy jpype1
```

---

## Common Use Cases

### Perfect For:

- **User Authentication** - Built-in User models and password hashing
- **E-commerce** - Complex relationships and transactions
- **Financial Systems** - ACID compliance and data integrity
- **Content Management** - Structured content with relationships
- **APIs with Complex Queries** - Powerful query capabilities

### When to Choose SQL (Edgy):

- You need complex relationships between entities
- Data integrity and ACID transactions are critical
- You have structured, predictable data
- You need powerful query capabilities
- You're building traditional web applications

---

## Integration with Ravyn

Ravyn provides built-in support for Edgy:

### User Models

Pre-built authentication models:

```python
from ravyn.contrib.auth.edgy.models import User

# Ready-to-use User model with:
# - Password hashing
# - User management
# - Django-inspired API
```

[Learn more about User models →](./models.md)

### JWT Middleware

Built-in JWT authentication:

```python
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware

# Automatic JWT authentication
# Token validation
# User injection
```

[Learn more about JWT middleware →](./middleware.md)

### Complete Example

Full integration example with authentication:

[See complete example →](./example.md)

---

## Best Practices

### 1. Use Connection Pooling

```python
database = Database(
    "postgresql://localhost/db",
    pool_size=20,
    max_overflow=10
)
```

### 2. Leverage Settings

```python
# settings.py
from ravyn import RavynSettings
from edgy import Database, Registry

class AppSettings(RavynSettings):
    @property
    def database(self):
        return Database(self.database_url)
    
    @property
    def registry(self):
        return Registry(database=self.database)
```

### 3. Use Migrations

Always use migrations for schema changes:

```shell
# Edgy has built-in migration commands
pip install edgy

# Initialize migrations
edgy init

# Create migration
edgy makemigrations

# Apply migrations
edgy migrate
```

---

## Learn More

- [Edgy Documentation](https://edgy.dymmond.com) - Complete Edgy guide
- [Edgy Migrations](https://edgy.dymmond.com/migrations/discovery/) - Database migrations
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/14/core/) - Underlying SQL engine

---

## Next Steps

- [User Models](./models.md) - Authentication and user management
- [JWT Middleware](./middleware.md) - Secure your APIs
- [Complete Example](./example.md) - Full integration tutorial
- [Mongoz](../mongoz/motivation.md) - NoSQL alternative
