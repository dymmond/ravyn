# Database Integrations

Think of databases as the memory of your application. Just like humans have different ways of organizing information (some prefer notebooks with structured tables, others prefer sticky notes scattered around), applications need different types of databases. SQL databases are like well-organized filing cabinets, while NoSQL databases are like flexible notebooks that adapt to your needs.

Ravyn supports both worlds seamlessly, giving you the freedom to choose the right tool for your data.

## What You'll Learn

- How to integrate SQL databases with Edgy ORM
- How to integrate MongoDB with Mongoz ODM
- When to use SQL vs NoSQL databases
- Best practices for database integration in Ravyn

## Quick Start

### SQL with Edgy

```python
from ravyn import Ravyn
from edgy import Database, Registry

database = Database("sqlite:///db.sqlite")
registry = Registry(database=database)

app = Ravyn()
```

### MongoDB with Mongoz

```python
from ravyn import Ravyn
from mongoz import Client, Registry

client = Client("mongodb://localhost:27017")
registry = Registry(client)

app = Ravyn()
```

---

## Supported Integrations

Ravyn provides out-of-the-box support for two powerful database libraries:

### Edgy - SQL ORM

**Edgy** is a modern, async-first ORM for SQL databases built on SQLAlchemy Core.

- **Type**: SQL (Relational)
- **Best For**: Structured data, complex relationships, transactions
- **Databases**: PostgreSQL, MySQL, SQLite, and more
- **Documentation**: [edgy.dymmond.com](https://edgy.dymmond.com)

[Learn more about Edgy →](./edgy/motivation.md)

### Mongoz - MongoDB ODM

**Mongoz** is a powerful ODM (Object Document Mapper) for MongoDB.

- **Type**: NoSQL (Document)
- **Best For**: Flexible schemas, rapid development, unstructured data
- **Database**: MongoDB
- **Documentation**: [mongoz.tarsild.io](https://mongoz.tarsild.io)

[Learn more about Mongoz →](./mongoz/motivation.md)

---

## SQL vs NoSQL: Which to Choose?

| Feature | SQL (Edgy) | NoSQL (Mongoz) |
|---------|------------|----------------|
| **Schema** | Fixed, predefined | Flexible, dynamic |
| **Relationships** | Strong, enforced | Flexible, embedded |
| **Transactions** | ACID compliant | Eventually consistent |
| **Scalability** | Vertical (scale up) | Horizontal (scale out) |
| **Best For** | Complex queries, relationships | Rapid iteration, flexibility |
| **Use Cases** | Financial systems, e-commerce | Content management, analytics |

---

## Database Agnostic

While Ravyn provides built-in support for Edgy and Mongoz, **you're not limited to these choices**.

Ravyn is completely database-agnostic. You can use:

- **Any ORM**: SQLAlchemy, Tortoise ORM, Piccolo, etc.
- **Any ODM**: Motor, PyMongo, Beanie, etc.
- **Raw Drivers**: psycopg, asyncpg, aiomysql, etc.
- **Multiple Databases**: Mix SQL and NoSQL in the same application

The integrations provided are conveniences, not requirements.

---

## Integration Features

Both Edgy and Mongoz integrations provide:

### User Authentication Models

Pre-built `User` models with:
- Password hashing (bcrypt)
- User management functions
- Django-inspired API
- Ready for production

### JWT Middleware

Built-in JWT authentication middleware:
- Token generation and validation
- User authentication
- Protected routes
- Refresh token support

### Settings Integration

Seamless integration with Ravyn settings:
- Centralized configuration
- Environment-based setup
- Reusable across applications

---

## Best Practices

### 1. Use Settings for Configuration

```python
# settings.py
from ravyn import RavynSettings
from edgy import Database, Registry

class AppSettings(RavynSettings):
    @property
    def edgy_database(self):
        return Database("postgresql://user:pass@localhost/db")
    
    @property
    def edgy_registry(self):
        return Registry(database=self.edgy_database)
```

### 2. Separate Database Logic

Keep database operations separate from route handlers:

```python
# Good - separate concerns
@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    user = await UserService.get_by_id(user_id)
    return user.model_dump()
```

### 3. Use Connection Pooling

Configure appropriate connection pool sizes for production:

```python
database = Database(
    "postgresql://localhost/db",
    pool_size=20,
    max_overflow=10
)
```

---

## Learn More

- [Edgy Documentation](https://edgy.dymmond.com)
- [Mongoz Documentation](https://mongoz.tarsild.io)
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/14/core/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

## Next Steps

Choose your database integration:

- [Edgy (SQL) →](./edgy/motivation.md) - Relational databases
- [Mongoz (MongoDB) →](./mongoz/motivation.md) - Document databases

Or explore specific topics:

- [User Models (Edgy)](./edgy/models.md)
- [User Documents (Mongoz)](./mongoz/documents.md)
- [JWT Middleware](./edgy/middleware.md)
