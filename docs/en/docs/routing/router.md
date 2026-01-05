# Router

Configure routers and create modular sub-applications with ChildRavyn for better code organization.

## What You'll Learn

- Using the Router class
- Creating custom routers
- Building ChildRavyn applications
- Router utilities

## Quick Start

```python
from ravyn import Ravyn, Router, Gateway, get

@get("/users")
def list_users() -> list:
    return []

# Custom router
router = Router(routes=[
    Gateway(handler=list_users)
])

# Add to app
app = Ravyn()
app.add_route(router)
```

---

## Router Class

The `Router` class connects routes, handlers, and the application together.

### Basic Router

```python
from ravyn import Router, Gateway, get, post

@get("/products")
def list_products() -> list:
    return []

@post("/products")
def create_product(data: dict) -> dict:
    return data

router = Router(
    routes=[
        Gateway(handler=list_products),
        Gateway(handler=create_product)
    ]
)
```

---

## Custom Routers

Organize routes into separate modules:

### Creating a Custom Router

```python
# customers.py
from ravyn import Router, Gateway, get, post, delete

@get("/{customer_id}")
async def get_customer(customer_id: int) -> dict:
    return {"id": customer_id, "name": "Customer"}

@post("/")
async def create_customer(data: dict) -> dict:
    return {"id": 1, **data}

@delete("/{customer_id}")
async def delete_customer(customer_id: int) -> None:
    pass

# Create router
customer_router = Router(
    routes=[
        Gateway(handler=get_customer),
        Gateway(handler=create_customer),
        Gateway(handler=delete_customer)
    ]
)
```

### Adding to Main App

```python
# app.py
from ravyn import Ravyn, Include
from customers import customer_router

app = Ravyn(
    routes=[
        Include("/customers", routes=customer_router.routes)
    ]
)
```

---

## ChildRavyn Applications

Create independent sub-applications with full Ravyn features.

### Why ChildRavyn?

- **Full Features** - All Ravyn parameters available

- **Isolation** - Separate settings, middleware, permissions

- **Organization** - Modular application structure

- **Flexibility** - Treat as independent apps

### Creating ChildRavyn

```python
# customers.py
from ravyn import ChildRavyn, Gateway, get, post

@get("/{customer_id}")
async def get_customer(customer_id: int) -> dict:
    return {"id": customer_id}

@post("/")
async def create_customer(data: dict) -> dict:
    return data

# Create sub-application
customer_app = ChildRavyn(
    routes=[
        Gateway(handler=get_customer),
        Gateway(handler=create_customer)
    ],
    tags=["customers"],
    permissions=[IsAuthenticated]
)
```

### Mounting ChildRavyn

```python
# app.py
from ravyn import Ravyn, Include
from customers import customer_app

app = Ravyn(
    routes=[
        Include("/customers", app=customer_app)
    ]
)

# Routes:
# /customers/{customer_id} → get_customer
# /customers/ → create_customer
```

---

## Router vs ChildRavyn

| Feature | Router | ChildRavyn |
|---------|--------|------------|
| **Complexity** | Simple | Full-featured |
| **Parameters** | Limited | All Ravyn params |
| **Isolation** | Partial | Complete |
| **Use Case** | Simple grouping | Sub-applications |

### Router Limitations

These parameters don't work with Router:

- `response_class`
- `response_cookies`
- `response_headers`
- `tags`
- `include_in_schema`

**Solution:** Use ChildRavyn for these features.

---

## Nested Applications

Create complex application structures:

```python
from ravyn import Ravyn, ChildRavyn, Include, Gateway, get

# Admin sub-app
@get("/users")
async def admin_users() -> list:
    return []

admin_app = ChildRavyn(
    routes=[Gateway(handler=admin_users)],
    permissions=[IsAdmin]
)

# API v1
api_v1 = ChildRavyn(
    routes=[
        Include("/admin", app=admin_app)
    ]
)

# Main app
app = Ravyn(
    routes=[
        Include("/api/v1", app=api_v1)
    ]
)

# Route: /api/v1/admin/users
```

---

## Router Utilities

### add_route()

Add routes dynamically:

```python
from ravyn import Ravyn, get

app = Ravyn()

@get("/users")
def list_users() -> list:
    return []

# Add route dynamically
app.add_route(
    path="/users",
    handler=list_users,
    methods=["GET"]
)
```

### add_websocket_route()

Add WebSocket routes:

```python
from ravyn import websocket
from ravyn.websockets import WebSocket

@websocket("/ws")
async def ws_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello!")

app.add_websocket_route(
    path="/ws",
    handler=ws_endpoint
)
```

### add_child_ravyn()

Add ChildRavyn programmatically:

```python
from ravyn import Ravyn, ChildRavyn

app = Ravyn()
child = ChildRavyn(routes=[...])

app.add_child_ravyn(
    path="/api",
    child=child
)
```

### add_asgi_app()

Mount any ASGI application:

```python
from ravyn import Ravyn
from fastapi import FastAPI

app = Ravyn()
fastapi_app = FastAPI()

# Mount FastAPI app
app.add_asgi_app(
    path="/fastapi",
    app=fastapi_app
)
```

---

## Common Patterns

### Pattern 1: Feature Modules

```python
# users/app.py
from ravyn import ChildRavyn, Gateway, get, post

user_app = ChildRavyn(
    routes=[...],
    tags=["users"]
)

# products/app.py
product_app = ChildRavyn(
    routes=[...],
    tags=["products"]
)

# main.py
from ravyn import Ravyn, Include
from users.app import user_app
from products.app import product_app

app = Ravyn(
    routes=[
        Include("/users", app=user_app),
        Include("/products", app=product_app)
    ]
)
```

### Pattern 2: API Versioning

```python
from ravyn import Ravyn, ChildRavyn, Include

# API v1
api_v1 = ChildRavyn(routes=[...])

# API v2
api_v2 = ChildRavyn(routes=[...])

app = Ravyn(
    routes=[
        Include("/api/v1", app=api_v1),
        Include("/api/v2", app=api_v2)
    ]
)
```

### Pattern 3: Admin Panel

```python
from ravyn import Ravyn, ChildRavyn, Include

admin_app = ChildRavyn(
    routes=[...],
    permissions=[IsAdmin],
    tags=["admin"]
)

app = Ravyn(
    routes=[
        Include("/admin", app=admin_app)
    ]
)
```

---

## Best Practices

### 1. Use ChildRavyn for Isolation

```python
# Good - isolated sub-app
customer_app = ChildRavyn(
    routes=[...],
    permissions=[IsAuthenticated],
    tags=["customers"]
)
```

### 2. Organize by Feature

```
app/
  users/
    app.py  # user_app = ChildRavyn(...)
  products/
    app.py  # product_app = ChildRavyn(...)
  main.py  # Ravyn(routes=[Include...])
```

### 3. Use Descriptive Paths

```python
# Good - clear paths
app = Ravyn(
    routes=[
        Include("/api/v1/users", app=user_app),
        Include("/api/v1/products", app=product_app)
    ]
)
```

---

## Next Steps

- [Routes](./routes.md) - Gateway and Include
- [Handlers](./handlers.md) - HTTP methods
- [Application Levels](../application/levels.md) - Hierarchy
- [Include](./routes.md#include) - Route grouping
