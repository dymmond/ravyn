# Application Levels

Ravyn applications are composed of hierarchical levels. Understanding these levels helps you organize your code and apply configurations at the right scope.

## What You'll Learn

- Application level hierarchy
- How levels inherit settings
- Using ChildRavyn for isolation
- Global vs local configurations
- Best practices for organization

## Quick Overview

```
Ravyn (App)
├── Gateway (Route)
│   └── Handler (Function)
├── Include (Group)
│   ├── Gateway
│   │   └── Handler
│   └── WebSocketGateway
│       └── Handler
└── ChildRavyn (Sub-app)
    └── Gateway
        └── Handler
```

---

## The Hierarchy

### Level 1: Ravyn Application

The top-level application instance:

```python
from ravyn import Ravyn

app = Ravyn(
    title="My API",
    debug=True,
    middleware=[...],
    permissions=[...]
)
```

### Level 2: Include / Gateway

Routes and route groups:

```python
from ravyn import Include, Gateway, get

@get("/users")
def list_users() -> dict:
    return {"users": []}

app = Ravyn(
    routes=[
        Include("/api", routes=[
            Gateway(handler=list_users)
        ])
    ]
)
```

### Level 3: Handlers

The actual endpoint functions:

```python
@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"user_id": user_id}
```

---

## Complete Example

```python
from ravyn import Ravyn, Include, Gateway, get, post

# Level 3: Handlers
@get("/")
def homepage() -> dict:
    return {"message": "Home"}

@get("/users")
def list_users() -> dict:
    return {"users": []}

@post("/users")
def create_user(data: dict) -> dict:
    return {"created": True}

# Level 1: Application
app = Ravyn(
    title="My API",
    
    # Level 2: Routes
    routes=[
        Gateway(handler=homepage),  # Direct gateway
        
        Include("/api", routes=[  # Grouped routes
            Gateway(handler=list_users),
            Gateway(handler=create_user)
        ])
    ]
)
```

**Hierarchy:**
1. `Ravyn` - Application (Level 1)
2. `Include` - Route group (Level 2)
3. `Gateway` - Individual route (Level 2/3)
4. `Handler` - Endpoint function (Level 3/4)

---

## Using ChildRavyn

ChildRavyn creates an isolated sub-application:

```python
from ravyn import Ravyn, ChildRavyn, Include, Gateway, get

# Sub-application
@get("/status")
def admin_status() -> dict:
    return {"status": "ok"}

admin_app = ChildRavyn(
    routes=[Gateway(handler=admin_status)]
)

# Main application
@get("/")
def homepage() -> dict:
    return {"message": "Home"}

app = Ravyn(
    routes=[
        Gateway(handler=homepage),
        Include("/admin", app=admin_app)  # Mount sub-app
    ]
)

# / → homepage
# /admin/status → admin_status
```

**Hierarchy with ChildRavyn:**
1. `Ravyn` - Main app (Level 1)
2. `Include` - Mount point (Level 2)
3. `ChildRavyn` - Sub-app (Level 3, also Level 1 for itself)
4. `Gateway` - Route in sub-app (Level 4, Level 2 for sub-app)
5. `Handler` - Function (Level 5, Level 3 for sub-app)

---

## Configuration Inheritance

### Settings Cascade Down

```python
from ravyn import Ravyn, Include, Gateway, get

@get("/protected")
def protected_route() -> dict:
    return {"data": "secret"}

app = Ravyn(
    # Applied to ALL routes
    permissions=[IsAuthenticated],
    
    routes=[
        Include("/api", routes=[
            Gateway(handler=protected_route)
        ])
    ]
)

# /api/protected inherits IsAuthenticated permission
```

### Override at Lower Levels

```python
@get("/public", permissions=[])  # Override: no permissions
def public_route() -> dict:
    return {"data": "public"}

app = Ravyn(
    permissions=[IsAuthenticated],  # Default for all
    routes=[
        Gateway(handler=public_route)  # Overrides to []
    ]
)
```

---

## Global vs Local

### Global (Middleware & Permissions)

These cascade from Ravyn → ChildRavyn:

```python
from ravyn import Ravyn, ChildRavyn, Include

# Main app with global middleware
app = Ravyn(
    middleware=[LoggingMiddleware],  # Applied globally
    permissions=[IsAuthenticated],   # Applied globally
    
    routes=[
        Include("/admin", app=ChildRavyn(
            routes=[...]  # Inherits middleware & permissions
        ))
    ]
)
```

### Local (Other Settings)

These are isolated per ChildRavyn:

```python
admin_app = ChildRavyn(
    title="Admin API",           # Separate from main app
    debug=True,                  # Independent setting
    exception_handlers={...}     # Local handlers
)

app = Ravyn(
    title="Main API",
    routes=[Include("/admin", app=admin_app)]
)
```

---

## Complex Example

```python
from ravyn import Ravyn, ChildRavyn, Include, Gateway, get, post

# Admin sub-app
@get("/users")
def admin_list_users() -> dict:
    return {"users": [], "admin": True}

admin_app = ChildRavyn(
    routes=[Gateway(handler=admin_list_users)],
    permissions=[IsAdmin]  # Additional permission for admin
)

# API routes
@get("/products")
def list_products() -> dict:
    return {"products": []}

@post("/products")
def create_product(data: dict) -> dict:
    return {"created": True}

# Main app
app = Ravyn(
    title="E-commerce API",
    middleware=[LoggingMiddleware],      # Global
    permissions=[IsAuthenticated],       # Global
    
    routes=[
        Include("/api", routes=[
            Gateway(handler=list_products),
            Gateway(handler=create_product)
        ]),
        
        Include("/admin", app=admin_app)  # Isolated sub-app
    ]
)
```

**Permissions Applied:**
- `/api/products` → `IsAuthenticated` (from app)
- `/admin/users` → `IsAuthenticated` + `IsAdmin` (from app + admin_app)

---

## Common Pitfalls & Fixes

### Pitfall 1: Expecting ChildRavyn to Inherit Everything

**Problem:** ChildRavyn doesn't inherit all settings.

```python
# Wrong assumption
app = Ravyn(
    title="Main API",
    debug=True
)

child = ChildRavyn()  # Does NOT inherit title or debug
```

**Solution:** Set explicitly or use middleware/permissions (which DO inherit):

```python
# Correct
child = ChildRavyn(
    title="Admin API",
    debug=True
)
```

### Pitfall 2: Repeating Global Middleware

**Problem:** Adding same middleware to both app and ChildRavyn.

```python
# Wrong - duplicate middleware
app = Ravyn(
    middleware=[LoggingMiddleware]
)

child = ChildRavyn(
    middleware=[LoggingMiddleware]  # Duplicate!
)
```

**Solution:** Only add to main app:

```python
# Correct
app = Ravyn(
    middleware=[LoggingMiddleware]  # Applied globally
)

child = ChildRavyn()  # Inherits middleware
```

---

## Best Practices

### 1. Use Include for Grouping

```python
# Good - organized with Include
app = Ravyn(
    routes=[
        Include("/api/v1", routes=v1_routes),
        Include("/api/v2", routes=v2_routes)
    ]
)
```

### 2. Use ChildRavyn for Isolation

```python
# Good - isolated admin area
admin_app = ChildRavyn(
    title="Admin Panel",
    permissions=[IsAdmin]
)

app = Ravyn(
    routes=[Include("/admin", app=admin_app)]
)
```

### 3. Apply Common Settings Globally

```python
# Good - global middleware
app = Ravyn(
    middleware=[LoggingMiddleware, CORSMiddleware],
    permissions=[IsAuthenticated],
    routes=[...]
)
```

---

## Next Steps

Now that you understand application levels, explore:

- [Applications](./applications.md) - Ravyn class details
- [Routing](../routing/routes.md) - Route configuration
- [ChildRavyn](../routing/router.md#child-ravyn-application) - Sub-applications
- [Middleware](../middleware/index.md) - Request processing
