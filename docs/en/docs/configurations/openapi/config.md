# OpenAPIConfig

Configure OpenAPI documentation settings for your Ravyn application's auto-generated API docs.

## What You'll Learn

- Configuring OpenAPI documentation
- Customizing documentation URLs
- Available documentation UIs
- Best practices

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import OpenAPIConfig

app = Ravyn(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0"
    )
)

# Access docs at:
# /docs/swagger - Swagger UI
# /docs/redoc - ReDoc
# /docs/elements - Stoplight Elements
# /docs/rapidoc - RapiDoc
```

---

## What is OpenAPI?

**OpenAPI** (formerly Swagger) is a specification for describing REST APIs. Ravyn automatically generates interactive API documentation from your code.

### Available Documentation UIs

| UI | URL | Description |
|----|-----|-------------|
| **Swagger UI** | `/docs/swagger` | Interactive API explorer |
| **ReDoc** | `/docs/redoc` | Clean, responsive docs |
| **Stoplight Elements** | `/docs/elements` | Modern API reference |
| **RapiDoc** | `/docs/rapidoc` | Customizable API docs |

---

## Basic Configuration

### Minimal Setup

```python
from ravyn import Ravyn

# Uses default OpenAPI config
app = Ravyn(
    title="My API",
    version="1.0.0",
    description="API description"
)
```

### Custom Configuration

```python
from ravyn import Ravyn
from ravyn.config import OpenAPIConfig

app = Ravyn(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        description="Comprehensive API documentation",
        contact={
            "name": "API Support",
            "email": "support@example.com"
        },
        license={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `title` | str | API title | `"Ravyn"` |
| `version` | str | API version | `"1.0.0"` |
| `description` | str | API description | `""` |
| `contact` | dict | Contact information | `None` |
| `license` | dict | License information | `None` |
| `servers` | list | Server configurations | `[]` |
| `docs_url` | str | Base docs URL | `"/docs"` |

---

## Customizing Documentation URLs

### Change Base Path

```python
from ravyn.config import OpenAPIConfig

app = Ravyn(
    openapi_config=OpenAPIConfig(
        title="My API",
        docs_url="/api-docs"  # Change base path
    )
)

# Now accessible at:
# /api-docs/swagger
# /api-docs/redoc
# /api-docs/elements
# /api-docs/rapidoc
```

### Disable Specific UIs

```python
app = Ravyn(
    openapi_config=OpenAPIConfig(
        title="My API",
        swagger_ui_url=None,  # Disable Swagger
        redoc_url="/docs"     # ReDoc at /docs
    )
)
```

---

## Complete Example

```python
from ravyn import Ravyn, get
from ravyn.config import OpenAPIConfig

@get("/users")
def list_users() -> list:
    """Get all users."""
    return [{"id": 1, "name": "Alice"}]

app = Ravyn(
    openapi_config=OpenAPIConfig(
        title="User Management API",
        version="2.0.0",
        description="API for managing users and permissions",
        
        contact={
            "name": "API Team",
            "email": "api@example.com",
            "url": "https://example.com/support"
        },
        
        license={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
        },
        
        servers=[
            {
                "url": "https://api.example.com",
                "description": "Production"
            },
            {
                "url": "https://staging-api.example.com",
                "description": "Staging"
            }
        ]
    ),
    
    routes=[Gateway(handler=list_users)]
)
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import OpenAPIConfig

class AppSettings(RavynSettings):
    openapi_config: OpenAPIConfig = OpenAPIConfig(
        title="My API",
        version="1.0.0",
        description="API documentation",
        docs_url="/api-docs"
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Disabling Documentation

### Disable All Docs

```python
app = Ravyn(
    enable_openapi=False  # No documentation
)
```

### Disable in Production

```python
import os

app = Ravyn(
    enable_openapi=os.getenv("ENV") != "production"
)
```

---

## Best Practices

### 1. Provide Complete Metadata

```python
# Good - complete information
openapi_config = OpenAPIConfig(
    title="User API",
    version="1.0.0",
    description="Comprehensive user management API",
    contact={"email": "support@example.com"},
    license={"name": "MIT"}
)
```

### 2. Use Versioning

```python
# Good - version in URL
openapi_config = OpenAPIConfig(
    title="My API",
    version="2.0.0",
    docs_url="/api/v2/docs"
)
```

### 3. Disable in Production (Optional)

```python
# Good - conditional docs
import os

app = Ravyn(
    enable_openapi=os.getenv("ENABLE_DOCS", "true") == "true"
)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Documentation Not Showing

**Problem:** Can't access documentation.

```python
# Wrong - OpenAPI disabled
app = Ravyn(enable_openapi=False)
```

**Solution:** Enable OpenAPI:

```python
# Correct
app = Ravyn(enable_openapi=True)  # Default
```

### Pitfall 2: Wrong URL

**Problem:** Accessing wrong documentation URL.

```
# Wrong URL
http://localhost:8000/docs  # 404
```

**Solution:** Use correct default URLs:

```
# Correct URLs
http://localhost:8000/docs/swagger
http://localhost:8000/docs/redoc
```

### Pitfall 3: Overriding Settings

**Problem:** Settings not applied.

```python
# Wrong - instantiation overrides settings
app = Ravyn(
    docs_url="/custom",  # This overrides settings!
    settings_module=AppSettings
)
```

**Solution:** Use one or the other:

```python
# Correct - use settings
app = Ravyn(settings_module=AppSettings)

# OR use instantiation
app = Ravyn(
    openapi_config=OpenAPIConfig(docs_url="/custom")
)
```

---

## Learn More

- [OpenAPI Specification](https://swagger.io/specification/)
- [OpenAPIConfig Reference](../../references/configurations/openapi.md)
- [OpenAPI Documentation](../../openapi.md)

---

## Next Steps

- [OpenAPI Documentation](../../openapi.md) - Document your API
- [Responses](../../responses.md) - Response models
- [Application Settings](../../application/settings.md) - Configuration
