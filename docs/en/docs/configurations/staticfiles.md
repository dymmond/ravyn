# StaticFilesConfig

Configure static file serving for CSS, JavaScript, images, and other assets in your Ravyn application.

## What You'll Learn

- Serving static files
- Configuring static file paths
- Multiple directories
- Best practices

## Quick Start

```python
from ravyn import Ravyn
from ravyn.config import StaticFilesConfig

app = Ravyn(
    static_files_config=StaticFilesConfig(
        path="/static",
        directory="static"
    )
)

# Files in ./static/ served at /static/*
# ./static/css/style.css → /static/css/style.css
```

---

## Basic Configuration

### Single Directory

```python
from ravyn import Ravyn
from ravyn.config import StaticFilesConfig

app = Ravyn(
    static_files_config=StaticFilesConfig(
        path="/static",      # URL path
        directory="static"   # Local directory
    )
)
```

### With Packages

```python
app = Ravyn(
    static_files_config=StaticFilesConfig(
        path="/static",
        directory="static",
        packages=["myapp"]  # Look in package directories
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `path` | str | URL path prefix | **Required** |
| `directory` | str/list | Local directory path(s) | **Required** |
| `packages` | list | Package names to search | `None` |
| `html` | bool | Serve HTML files | `False` |
| `check_dir` | bool | Check if directory exists | `True` |

---

## Multiple Directories

### Without Fallthrough

```python
from ravyn import Ravyn
from ravyn.config import StaticFilesConfig

app = Ravyn(
    static_files_config=[
        StaticFilesConfig(
            path="/static",
            directory="static"
        ),
        StaticFilesConfig(
            path="/node_modules",
            directory="node_modules"
        )
    ]
)

# /static/* → ./static/
# /node_modules/* → ./node_modules/
```

!!! warning
    First match wins - order matters!

### With Fallthrough

```python
# Multiple directories with fallback
app = Ravyn(
    static_files_config=StaticFilesConfig(
        path="/static",
        directory=["custom_static", "static"]  # Try custom first, then static
    )
)

# Looks in custom_static/ first, falls back to static/
```

---

## Common Patterns

### Pattern 1: Frontend Assets

```python
# Serve CSS, JS, images
app = Ravyn(
    static_files_config=StaticFilesConfig(
        path="/static",
        directory="static"
    )
)

# Directory structure:
# static/
#   css/
#     style.css
#   js/
#     app.js
#   images/
#     logo.png
```

### Pattern 2: Node Modules

```python
# Serve npm packages
app = Ravyn(
    static_files_config=[
        StaticFilesConfig(path="/static", directory="static"),
        StaticFilesConfig(path="/node_modules", directory="node_modules")
    ]
)
```

### Pattern 3: Custom Overrides

```python
# Custom files override defaults
app = Ravyn(
    static_files_config=StaticFilesConfig(
        path="/static",
        directory=["custom", "defaults"]  # custom overrides defaults
    )
)
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import StaticFilesConfig

class AppSettings(RavynSettings):
    static_files_config: StaticFilesConfig = StaticFilesConfig(
        path="/static",
        directory="static"
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Best Practices

### 1. Use CDN in Production

```python
# Good - CDN for production
import os

if os.getenv("ENV") == "production":
    # Use CDN, no static files config
    app = Ravyn()
else:
    # Serve locally in development
    app = Ravyn(
        static_files_config=StaticFilesConfig(
            path="/static",
            directory="static"
        )
    )
```

### 2. Organize by Type

```
static/
  css/
    style.css
  js/
    app.js
  images/
    logo.png
  fonts/
    font.woff2
```

### 3. Use Versioning

```html
<!-- Add version to bust cache -->
<link rel="stylesheet" href="/static/css/style.css?v=1.2.3">
```

---

## Next Steps

- [TemplateConfig](./template.md) - Template rendering
- [CORSConfig](./cors.md) - CORS configuration
- [Application Settings](../application/settings.md) - Configuration
