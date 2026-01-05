# Architecture Patterns

When building scalable and maintainable Ravyn applications, it's essential to choose the right architecture pattern. This guide explores common architecture styles and how to implement them using Ravyn.

---

## Project Structure

Keeping your project organized is crucial. A common structure for medium to large Ravyn applications looks like this:

```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   └── __init__.py
│   └── __init__.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── __init__.py
├── models/
├── services/
├── schemas/
├── utils/
├── main.py
└── __init__.py
```

---

## Pattern 1: Monolithic

All code is packaged into a single deployable unit.

**Pros**:

- Simple to develop and deploy
- Great for small projects

**Cons**:

- Hard to scale and maintain as the app grows

**Example**:

```python
from ravyn import Ravyn, get

@get("/")
def home() -> dict:
    return {"message": "Welcome to the monolith"}

app = Ravyn(routes=[home])
```

---

## Pattern 2: Modular / Feature-Based

Break your application into features or domains.

**Structure**:
```
app/
├── features/
│   ├── users/
│   │   ├── routes.py
│   │   ├── models.py
│   │   ├── services.py
│   │   └── schemas.py
│   └── items/
...
```

**Benefits**:

- Easier to maintain
- Encourages separation of concerns

**Example**:

```python
# features/users/routes.py
from ravyn import get

@get("/users")
def list_users() -> dict:
    return ["Alice", "Bob"]

# main.py
from ravyn import Ravyn
from features.users.routes import list_users

app = Ravyn(routes=[list_users])
```

---

## Pattern 3: Domain-Driven Design (DDD)

Structure your application around domain concepts.

**Folders**:

- `domain/` (core business logic)
- `application/` (use cases)
- `infrastructure/` (DB, APIs)
- `interfaces/` (HTTP, CLI)

**Benefits**:

- Better separation of concerns
- Easier to reason about business rules

---

## Pattern 4: Microservices

Split functionality into separate deployable services.

**Ravyn's support**:

- Lightweight
- Decoupled services via HTTP or gRPC
- Dynamic routing with versioning

**Example**:

- Service A: `/users`
- Service B: `/payments`

Deploy independently and communicate via HTTP or messaging queues.

---

## Choosing the Right Pattern

| Project Type        | Suggested Pattern       |
|---------------------|--------------------------|
| Small Script/API    | Monolith                 |
| Medium App          | Modular / Feature-Based  |
| Large App/Enterprise| DDD or Microservices     |

---

## What's Next?

You've learned about architecture patterns in Ravyn. Next, we'll explore advanced dependency injection and lifecycle
management.

👉 Continue to [16-dependency-injection](./06-dependency-injection.md).
