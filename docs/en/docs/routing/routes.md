# Routing

Ravyn's routing system scales from a single route to hundreds of organized endpoints. Whether you're building a quick prototype or an enterprise application, the routing system handles it elegantly.

## What You'll Learn

- How to create routes with Gateway and WebSocketGateway
- Organizing routes with Include for scalable applications
- Using path parameters and custom converters
- Managing route priority and avoiding conflicts
- Adding middleware, permissions, and dependencies to routes

## Quick Start

Here's the simplest way to create routes:

```python
from ravyn import Ravyn, get, post

app = Ravyn()

@app.get("/users")
def list_users() -> dict:
    return {"users": ["Alice", "Bob"]}

@app.post("/users")
def create_user(name: str) -> dict:
    return {"created": name}
```

That's it! Visit `/users` to see your route in action.

---

## Gateway: The Route Wrapper

A `Gateway` wraps a handler function and maps it to a URL path. It's more powerful than simple decorators because it allows you to organize routes separately from handlers.

### Basic Gateway

```python
from ravyn import Ravyn, Gateway, get

@get()
def welcome() -> dict:
    return {"message": "Welcome!"}

app = Ravyn(
    routes=[
        Gateway("/", handler=welcome)
    ]
)
```

### Gateway with Path Parameters

```python
from ravyn import Ravyn, Gateway, get

@get()
def get_user(user_id: int) -> dict:
    return {"user_id": user_id, "name": "Alice"}

app = Ravyn(
    routes=[
        Gateway("/users/{user_id:int}", handler=get_user)
    ]
)
```

!!! tip
    If you don't provide a path to `Gateway`, it defaults to `/`. The handler's decorator can also specify a path that gets appended to the Gateway path.

### Automatic Gateway Wrapping

You can pass handlers directly. Ravyn automatically wraps them in a Gateway:

```python
from ravyn import Ravyn, get

@get("/users")
def list_users() -> dict:
    return {"users": []}

# These are equivalent:
app1 = Ravyn(routes=[list_users])  # Auto-wrapped
app2 = Ravyn(routes=[Gateway("/users", handler=list_users)])  # Explicit
```

**Reference:** See all [Gateway parameters](../references/routing/gateway.md).

---

## WebSocketGateway: Real-Time Communication

For WebSocket connections, use `WebSocketGateway`. WebSocket handlers must be `async`.

```python
from ravyn import Ravyn, WebSocketGateway, websocket, Websocket

@websocket()
async def chat_socket(socket: Websocket) -> None:
    await socket.accept()
    message = await socket.receive_json()
    await socket.send_json({"echo": message})
    await socket.close()

app = Ravyn(
    routes=[
        WebSocketGateway("/chat", handler=chat_socket)
    ]
)
```

**Reference:** See all [WebSocketGateway parameters](../references/routing/websocketgateway.md).

---

## Include: Organize Routes at Scale

`Include` is Ravyn's secret weapon for organizing large applications. It lets you split routes across multiple files and import them cleanly.

!!! warning
    `Include` **does NOT** support path parameters. Don't use `Include('/api/{id:int}', ...)`.

### Why Use Include?

1. **Scalability** - Manage hundreds of routes without chaos
2. **Clean Design** - Separate concerns by feature/module
3. **Reduced Imports** - Import entire route modules at once
4. **Fewer Bugs** - Less manual route registration

### Include with Namespace

The most common pattern. import routes from a module:

```python
# accounts/urls.py
from ravyn import Gateway
from .controllers import list_accounts, create_account

route_patterns = [
    Gateway("/", handler=list_accounts),
    Gateway("/create", handler=create_account),
]
```

```python
# app.py
from ravyn import Ravyn, Include

app = Ravyn(
    routes=[
        Include("/accounts", namespace="myapp.accounts.urls")
    ]
)
```

This creates:

- `GET /accounts/` → list_accounts
- `POST /accounts/create` → create_account

!!! tip
    By default, `Include` looks for a `route_patterns` list in the namespace. You can change this with the `pattern` parameter.

### Include with Routes List

Pass routes directly instead of using a namespace:

```python
from ravyn import Ravyn, Include, Gateway
from myapp.accounts.controllers import list_accounts

app = Ravyn(
    routes=[
        Include("/accounts", routes=[
            Gateway("/", handler=list_accounts)
        ])
    ]
)
```

### Custom Pattern Name

Use a different variable name instead of `route_patterns`:

```python
# accounts/urls.py
my_custom_routes = [  # Not 'route_patterns'
    Gateway("/", handler=list_accounts),
]
```

```python
# app.py
app = Ravyn(
    routes=[
        Include("/accounts", namespace="myapp.accounts.urls", pattern="my_custom_routes")
    ]
)
```

**Reference:** See all [Include parameters](../references/routing/include.md).

---

## Nested Routes

`Include` supports nesting for complex applications:

### Simple Nesting

```python
from ravyn import Ravyn, Include

app = Ravyn(
    routes=[
        Include("/api", routes=[
            Include("/v1", namespace="myapp.api.v1.urls"),
            Include("/v2", namespace="myapp.api.v2.urls"),
        ])
    ]
)
```

This creates:

- `/api/v1/...` routes
- `/api/v2/...` routes

### Complex Nesting with Features

Each level can have its own middleware, permissions, dependencies, and exception handlers:

```python
from ravyn import Ravyn, Include, Gateway
from lilya.middleware import DefineMiddleware
from myapp.middleware import LoggingMiddleware, AuthMiddleware

app = Ravyn(
    routes=[
        Include("/api", 
            middleware=[DefineMiddleware(LoggingMiddleware)],
            routes=[
                Include("/v1",
                    middleware=[DefineMiddleware(AuthMiddleware)],
                    namespace="myapp.api.v1.urls"
                )
            ]
        )
    ]
)
```

Middleware executes in order: `LoggingMiddleware` → `AuthMiddleware` → handler.

---

## Path Parameters

Capture dynamic values from URLs using path parameters.

### Basic Path Parameters

```python
from ravyn import Gateway, get

@get()
def get_customer(customer_id: str) -> dict:
    return {"customer_id": customer_id}

Gateway("/customers/{customer_id}", handler=get_customer)
```

### Type Converters

Ravyn supports these built-in converters:

| Converter | Python Type | Example |
|-----------|-------------|---------|
| `str` | `str` (default) | `/users/{name}` |
| `int` | `int` | `/users/{id:int}` |
| `float` | `float` | `/prices/{amount:float}` |
| `uuid` | `uuid.UUID` | `/items/{item_id:uuid}` |
| `path` | `str` (with `/`) | `/files/{filepath:path}` |

```python
from ravyn import Gateway, get

@get()
def get_user(user_id: int) -> dict:  # Receives int, not str
    return {"user_id": user_id}

@get()
def get_file(filepath: str) -> dict:  # Can include slashes
    return {"filepath": filepath}

app = Ravyn(routes=[
    Gateway("/users/{user_id:int}", handler=get_user),
    Gateway("/files/{filepath:path}", handler=get_file),
])
```

### Custom Converters

Create your own path converters:

```python
import datetime
from lilya.routing.converters import Converter, register_converter

class DateTimeConverter(Converter):
    regex = r"\d{4}-\d{2}-\d{2}"
    
    def convert(self, value: str) -> datetime.datetime:
        return datetime.datetime.strptime(value, "%Y-%m-%d")
    
    def to_string(self, value: datetime.datetime) -> str:
        return value.strftime("%Y-%m-%d")

# Register it
register_converter("datetime", DateTimeConverter)

# Use it
@get()
def sales_report(date: datetime.datetime) -> dict:
    return {"date": date.isoformat()}

Gateway("/sales/{date:datetime}", handler=sales_report)
```

> [!INFO]
> Path parameters are also available in `request.path_params` dictionary.

---

## Route Priority

Routes are matched in the order they're defined. **More specific routes must come first.**

### Correct Order

```python
from ravyn import Ravyn, Gateway, get

@get()
def special_user() -> dict:
    return {"type": "special"}

@get()
def get_user(user_id: int) -> dict:
    return {"user_id": user_id}

# Correct - specific route first
app = Ravyn(routes=[
    Gateway("/users/special", handler=special_user),  # Matches first
    Gateway("/users/{user_id:int}", handler=get_user),  # Matches after
])
```

### Incorrect Order

```python
# Wrong - generic route first
app = Ravyn(routes=[
    Gateway("/users/{user_id:int}", handler=get_user),  # Matches everything!
    Gateway("/users/special", handler=special_user),  # Never reached
])
```

!!! warning
    Ravyn does some automatic sorting (routes with only `/` path go last), but you should still order routes from most specific to least specific.

---

## Adding Features to Routes

All route objects (Gateway, WebSocketGateway, Include) support middleware, permissions, dependencies, and exception handlers.

### Middleware

```python
from ravyn import Ravyn, Include, Gateway, get
from lilya.middleware import DefineMiddleware
from myapp.middleware import LoggingMiddleware, AuthMiddleware

@get()
def handler() -> dict:
    return {"message": "success"}

app = Ravyn(
    routes=[
        Include("/api",
            middleware=[DefineMiddleware(LoggingMiddleware)],
            routes=[
                Gateway("/test", 
                    handler=handler,
                    middleware=[DefineMiddleware(AuthMiddleware)]
                )
            ]
        )
    ]
)
```

Execution order: App middleware → `LoggingMiddleware` → `AuthMiddleware` → handler.

Learn more in [Middleware](../middleware/index.md).

### Exception Handlers

```python
from ravyn import Ravyn, Gateway, get
from ravyn.exceptions import NotAuthorized

def handle_not_authorized(request, exc):
    return JSONResponse({"error": "Not authorized"}, status_code=401)

@get()
def protected() -> dict:
    raise NotAuthorized("No access")

app = Ravyn(
    routes=[
        Gateway("/protected", 
            handler=protected,
            exception_handlers={NotAuthorized: handle_not_authorized}
        )
    ]
)
```

Learn more in [Exception Handlers](../exception-handlers.md).

### Dependencies

```python
from ravyn import Ravyn, Gateway, Inject, Injects, get

def get_database():
    return {"db": "connected"}

@get()
def users(db: dict = Injects()) -> dict:
    return {"users": [], "db": db}

app = Ravyn(
    routes=[
        Gateway("/users", 
            handler=users,
            dependencies={"db": Inject(get_database)}
        )
    ]
)
```

Learn more in [Dependencies](../dependencies.md).

### Permissions

```python
from ravyn import Ravyn, Gateway, get
from ravyn.permissions import IsAuthenticated

@get(permissions=[IsAuthenticated])
def protected() -> dict:
    return {"message": "You're authenticated!"}

app = Ravyn(
    routes=[
        Gateway("/protected", handler=protected)
    ]
)
```

Learn more in [Permissions](../permissions/index.md).

---

## Common Pitfalls & Fixes

### Pitfall 1: Include Without Path Causes Route Conflicts

**Problem:** Multiple `Include` statements without paths override each other.

```python
# Wrong - both default to '/'
app = Ravyn(routes=[
    Include(namespace="myapp.urls"),  # Path defaults to '/'
    Include(namespace="accounts.urls"),  # Also defaults to '/'
    # Only one will be registered!
])
```

**Solution:** Always specify paths for `Include`:

```python
# Correct
app = Ravyn(routes=[
    Include("/api", namespace="myapp.urls"),
    Include("/accounts", namespace="accounts.urls"),
])
```

### Pitfall 2: Generic Routes Before Specific Routes

**Problem:** Generic route matches everything, specific route never reached.

```python
# Wrong
app = Ravyn(routes=[
    Gateway("/users/{id:int}", handler=get_user),  # Catches /users/me
    Gateway("/users/me", handler=current_user),  # Never reached!
])
```

**Solution:** Put specific routes first:

```python
# Correct
app = Ravyn(routes=[
    Gateway("/users/me", handler=current_user),  # Checked first
    Gateway("/users/{id:int}", handler=get_user),  # Checked second
])
```

### Pitfall 3: Using Path Parameters in Include

**Problem:** `Include` doesn't support path parameters.

```python
# Wrong
app = Ravyn(routes=[
    Include("/users/{user_id:int}", namespace="myapp.users.urls")
])
```

**Solution:** Use path parameters in `Gateway`, not `Include`:

```python
# Correct
# myapp/users/urls.py
route_patterns = [
    Gateway("/{user_id:int}/profile", handler=get_profile),
    Gateway("/{user_id:int}/settings", handler=get_settings),
]

# app.py
app = Ravyn(routes=[
    Include("/users", namespace="myapp.users.urls")
])
# Creates: /users/{user_id:int}/profile, /users/{user_id:int}/settings
```

### Pitfall 4: Forgetting Async for WebSockets

**Problem:** WebSocket handler is not async.

```python
# Wrong
@websocket()
def chat(socket: Websocket):  # Missing 'async'
    await socket.accept()  # SyntaxError!
```

**Solution:** WebSocket handlers must be async:

```python
# Correct
@websocket()
async def chat(socket: Websocket):  # Added 'async'
    await socket.accept()
```

---

## Route Organization Patterns

### Pattern 1: Feature-Based (Recommended)

```
myapp/
├── app.py
├── urls.py
├── accounts/
│   ├── controllers.py
│   └── urls.py
├── products/
│   ├── controllers.py
│   └── urls.py
└── orders/
    ├── controllers.py
    └── urls.py
```

### Pattern 2: API Versioning

```
myapp/
├── app.py
└── api/
    ├── v1/
    │   ├── urls.py
    │   └── endpoints/
    └── v2/
        ├── urls.py
        └── endpoints/
```

```python
# app.py
app = Ravyn(routes=[
    Include("/api/v1", namespace="myapp.api.v1.urls"),
    Include("/api/v2", namespace="myapp.api.v2.urls"),
])
```

---

## Next Steps

Now that you understand routing, explore:

- [Handlers](./handlers.md) - Different handler types and patterns
- [Dependencies](../dependencies.md) - Inject dependencies into routes
- [Middleware](../middleware/index.md) - Add request/response processing
- [Permissions](../permissions/index.md) - Secure your routes
- [Application Levels](../application/levels.md) - Understand the hierarchy
