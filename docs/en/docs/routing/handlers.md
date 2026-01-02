# Handlers

Think of your API like a restaurant. When customers (clients) interact with your menu (API), they do different things:

- **GET** - "Show me the menu" (read)
- **POST** - "I'll order the pasta" (create)
- **PUT** - "Actually, make that whole wheat pasta" (replace)
- **PATCH** - "Add extra cheese" (modify)
- **DELETE** - "Cancel my order" (remove)

Handlers are the decorators that tell your API which "action" each endpoint performs. They're the waiters taking orders and the kitchen fulfilling them.

## What You'll Learn

- Available HTTP handlers (GET, POST, PUT, PATCH, DELETE)
- Using each HTTP method correctly
- WebSocket handlers for real-time communication
- Handler parameters and options

## Quick Start

```python
from ravyn import Ravyn, get, post

@get("/users")
def list_users() -> list:
    return [{"id": 1, "name": "Alice"}]

@post("/users")
def create_user(data: dict) -> dict:
    return {"id": 2, **data}

app = Ravyn(routes=[
    Gateway(handler=list_users),
    Gateway(handler=create_user)
])
```

---

## HTTP Handlers

### @get - Retrieve Resources

```python
from ravyn import get

@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

# Default status code: 200
```

**Use for:** Fetching data, listing resources

### @post - Create Resources

```python
from ravyn import post

@post("/users")
def create_user(name: str, email: str) -> dict:
    return {"id": 1, "name": name, "email": email}

# Default status code: 201
```

**Use for:** Creating new resources, submitting forms

### @put - Update Resources

```python
from ravyn import put

@put("/users/{user_id}")
def update_user(user_id: int, name: str) -> dict:
    return {"id": user_id, "name": name}

# Default status code: 200
```

**Use for:** Full resource updates, replacements

### @patch - Partial Updates

```python
from ravyn import patch

@patch("/users/{user_id}")
def partial_update(user_id: int, name: str = None) -> dict:
    return {"id": user_id, "name": name}

# Default status code: 200
```

**Use for:** Partial resource updates

### @delete - Remove Resources

```python
from ravyn import delete

@delete("/users/{user_id}")
def delete_user(user_id: int) -> None:
    pass  # Delete logic here

# Default status code: 204
```

**Use for:** Deleting resources

---

## HTTP Methods Comparison

| Method | Purpose | Default Status | Request Body |
|--------|---------|----------------|--------------|
| **GET** | Retrieve | 200 | No |
| **POST** | Create | 201 | Yes |
| **PUT** | Update (full) | 200 | Yes |
| **PATCH** | Update (partial) | 200 | Yes |
| **DELETE** | Remove | 204 | No |

---

## Special Handlers

### @route - Multiple Methods

Handle multiple HTTP methods with one function:

```python
from ravyn import route

@route("/users/{user_id}", methods=["GET", "PUT"])
def handle_user(user_id: int, request: Request) -> dict:
    if request.method == "GET":
        return {"id": user_id, "name": "Alice"}
    elif request.method == "PUT":
        return {"id": user_id, "updated": True}
```

**Use for:** Shared logic across methods

### @head - Headers Only

```python
from ravyn import head

@head("/users")
def users_head() -> None:
    pass  # Returns headers only, no body

# Default status code: 200
```

### @options - CORS Preflight

```python
from ravyn import options

@options("/users")
def users_options() -> dict:
    return {"allowed_methods": ["GET", "POST"]}

# Default status code: 200
```

### @trace - Debugging

```python
from ravyn import trace

@trace("/debug")
def trace_request() -> dict:
    return {"trace": "enabled"}

# Default status code: 200
```

---

## WebSocket Handler

### @websocket - Real-time Communication

```python
from ravyn import websocket
from ravyn.websockets import WebSocket

@websocket("/ws")
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    
    while True:
        data = await socket.receive_text()
        await socket.send_text(f"Echo: {data}")
```

!!! info
    WebSocket handlers must be async functions.

---

## Handler Parameters

### Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | str | URL path (default: `/`) |
| `status_code` | int | HTTP status code |
| `response_class` | type | Custom response class |
| `tags` | list | OpenAPI tags |
| `summary` | str | OpenAPI summary |
| `description` | str | OpenAPI description |
| `include_in_schema` | bool | Include in docs |

### Example with Parameters

```python
@get(
    "/users",
    status_code=200,
    tags=["users"],
    summary="List all users",
    description="Returns a list of all users in the system"
)
def list_users() -> list:
    return [{"id": 1, "name": "Alice"}]
```

---

## Best Practices

### 1. Use Appropriate Methods

```python
# Good - correct methods
@get("/users")  # Read
@post("/users")  # Create
@put("/users/{id}")  # Update
@delete("/users/{id}")  # Delete
```

### 2. Set Correct Status Codes

```python
# Good - explicit status codes
@post("/users", status_code=201)  # Created
@delete("/users/{id}", status_code=204)  # No Content
```

### 3. Document Your Endpoints

```python
# Good - documented
@get(
    "/users",
    summary="List users",
    description="Returns all users with pagination"
)
def list_users() -> list:
    return []
```

---

## Next Steps

- [Routes](./routes.md) - Organize handlers with Gateway and Include
- [Router](./router.md) - Advanced routing configuration
- [Controllers](./controllers.md) - Class-based handlers
- [Responses](../responses.md) - Response types
