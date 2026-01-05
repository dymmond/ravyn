# Mongoz - MongoDB ODM Integration

Imagine you're organizing a photo album. With traditional photo albums (SQL), you have fixed slots where each photo must fit a specific size and position. With a scrapbook (NoSQL), you can arrange photos however you want, add notes of any length, and reorganize freely without constraints.

MongoDB is like that scrapbook: flexible, adaptable, and perfect when your data doesn't fit rigid structures. Mongoz makes working with MongoDB feel natural and pythonic.

## What You'll Learn

- Why use Mongoz with Ravyn
- Key features and benefits
- How to install and set up Mongoz
- When to choose NoSQL over SQL
- Getting started with Mongoz integration

## Quick Start

```python
from ravyn import Ravyn
from mongoz import Client, Registry, Document, fields

# Setup MongoDB
client = Client("mongodb://localhost:27017")
registry = Registry(client)

# Define a document
class User(Document):
    name = fields.String(max_length=100)
    email = fields.Email()
    
    class Meta:
        registry = registry
        database = "myapp"

# Use in Ravyn
app = Ravyn()
```

---

## Why Mongoz?

### Built for Modern Python

Mongoz is designed from the ground up for async Python and MongoDB:

✨ **100% Type-Safe** - Full type hints and IDE autocomplete

✨ **Async-First** - Native async/await support

✨ **Pydantic Integration** - Seamless data validation

✨ **Motor-Powered** - Built on the official async MongoDB driver

✨ **Flexible Schemas** - Adapt to changing requirements

### Same Author, Better Integration

[Mongoz](https://mongoz.tarsild.io) is created by the same author as Ravyn, ensuring:

- Consistent design philosophy
- Seamless integration
- Regular updates and compatibility
- Shared best practices

!!! Tip
    While Ravyn provides built-in support for Mongoz, you're free to use any ODM you prefer. Ravyn is database-agnostic: use Motor, PyMongo, Beanie, or any other tool that fits your needs.

---

## What is NoSQL?

**NoSQL** databases store data differently than traditional SQL databases:

- **SQL** - Tables with fixed columns (like a spreadsheet)
- **NoSQL** - Flexible documents (like JSON objects)

**MongoDB** is a document-oriented NoSQL database that stores data as JSON-like documents.

### SQL vs NoSQL

| Aspect | SQL | NoSQL (MongoDB) |
|--------|-----|-----------------|
| **Structure** | Fixed schema | Flexible schema |
| **Data** | Tables, rows, columns | Collections, documents |
| **Relationships** | Foreign keys, joins | Embedded or referenced |
| **Scaling** | Vertical (bigger server) | Horizontal (more servers) |
| **Best For** | Complex queries | Rapid development |

---

## Key Features

### 100% Pydantic

Documents are Pydantic models under the hood:

```python
class User(Document):
    name = fields.String(max_length=100)
    email = fields.Email()
    age = fields.Integer(minimum=0)
    
    class Meta:
        registry = registry
        database = "myapp"

# Automatic validation
user = User(name="John", email="john@example.com", age=25)
```

### Intuitive Querying

Familiar, pythonic query API:

```python
# Simple queries
users = await User.query.all()
user = await User.query.get(id="507f1f77bcf86cd799439011")
active_users = await User.query.filter(is_active=True)

# Complex queries
admins = await User.query.filter(
    is_staff=True,
    is_active=True
).sort("-created_at").limit(10)
```

### Flexible Documents

Adapt to changing requirements:

```python
# Start simple
class Post(Document):
    title = fields.String()
    content = fields.String()

# Add fields later without migrations
class Post(Document):
    title = fields.String()
    content = fields.String()
    tags = fields.Array(str)  # New field!
    metadata = fields.Object()  # Flexible nested data
```

### Async Performance

Built for high-concurrency applications:

```python
# Concurrent database operations
async with client:
    users, posts = await asyncio.gather(
        User.query.all(),
        Post.query.all()
    )
```

---

## Installation

### Basic Installation

```shell
pip install mongoz
```

### With Ravyn

Mongoz works seamlessly with Ravyn out of the box:

```shell
pip install ravyn mongoz
```

### MongoDB Setup

You'll need a MongoDB instance. For local development, use Docker:

```shell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

---

## Common Use Cases

### Perfect For:

- **Content Management** - Flexible content structures
- **User Profiles** - Varying user data
- **Analytics** - Time-series data
- **Catalogs** - Product catalogs with varying attributes
- **Real-time Apps** - Chat, notifications, activity feeds

### When to Choose NoSQL (Mongoz):

- Your data structure changes frequently
- You need rapid development and iteration
- You have unstructured or semi-structured data
- You need horizontal scalability
- You're building content-heavy applications

---

## Integration with Ravyn

Ravyn provides built-in support for Mongoz:

### User Documents

Pre-built authentication documents:

```python
from ravyn.contrib.auth.mongoz.documents import User

# Ready-to-use User document with:
# - Password hashing
# - User management
# - Django-inspired API
```

[Learn more about User documents →](./documents.md)

### JWT Middleware

Built-in JWT authentication:

```python
from ravyn.contrib.auth.mongoz.middleware import JWTAuthMiddleware

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
client = Client(
    "mongodb://localhost:27017",
    maxPoolSize=50,
    minPoolSize=10
)
```

### 2. Leverage Settings

```python
# settings.py
from ravyn import RavynSettings
from mongoz import Client, Registry

class AppSettings(RavynSettings):
    @property
    def mongo_client(self):
        return Client(self.mongodb_url)
    
    @property
    def mongo_registry(self):
        return Registry(self.mongo_client)
```

### 3. Index Your Queries

```python
class User(Document):
    email = fields.Email()
    
    class Meta:
        registry = registry
        database = "myapp"
        indexes = [
            "email",  # Single field index
            [("email", 1), ("is_active", -1)]  # Compound index
        ]
```

### 4. Use Embedded Documents Wisely

```python
# Good - embed related data
class Address(EmbeddedDocument):
    street = fields.String()
    city = fields.String()

class User(Document):
    name = fields.String()
    address = fields.Embed(Address)  # Embedded
```

---

## Learn More

- [Mongoz Documentation](https://mongoz.tarsild.io) - Complete Mongoz guide
- [MongoDB Documentation](https://docs.mongodb.com/) - MongoDB reference
- [Motor Documentation](https://motor.readthedocs.io/) - Async MongoDB driver

---

## Next Steps

- [User Documents](./documents.md) - Authentication and user management
- [JWT Middleware](./middleware.md) - Secure your APIs
- [Complete Example](./example.md) - Full integration tutorial
- [Edgy](../edgy/motivation.md) - SQL alternative
