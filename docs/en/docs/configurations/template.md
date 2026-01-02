# TemplateConfig

Configure template rendering for server-side HTML generation in your Ravyn application.

## What You'll Learn

- Setting up Jinja2 templates
- Rendering templates
- Using async templates
- Template best practices

## Quick Start

```python
from ravyn import Ravyn, get
from ravyn.config import TemplateConfig
from ravyn.responses import Template

app = Ravyn(
    template_config=TemplateConfig(
        directory="templates"
    )
)

@get("/")
def homepage() -> Template:
    return Template("index.html", context={"title": "Home"})
```

---

## Basic Configuration

### Minimal Setup

```python
from ravyn import Ravyn
from ravyn.config import TemplateConfig

app = Ravyn(
    template_config=TemplateConfig(
        directory="templates"
    )
)
```

### Complete Configuration

```python
app = Ravyn(
    template_config=TemplateConfig(
        directory="templates",
        autoescape=True,
        auto_reload=True,  # Development only
        enable_async=True  # For async templates
    )
)
```

---

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `directory` | str/list | Template directory path(s) | **Required** |
| `autoescape` | bool | Auto-escape HTML | `True` |
| `auto_reload` | bool | Reload templates on change | `False` |
| `enable_async` | bool | Enable async templates | `False` |

---

## Rendering Templates

### Basic Template

```python
from ravyn import get
from ravyn.responses import Template

@get("/")
def homepage() -> Template:
    return Template("index.html")
```

**templates/index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
</head>
<body>
    <h1>Welcome to Ravyn!</h1>
</body>
</html>
```

### With Context Data

```python
@get("/users/{user_id}")
async def user_profile(user_id: int) -> Template:
    user = await User.get(id=user_id)
    
    return Template(
        "profile.html",
        context={
            "user": user,
            "title": f"Profile - {user.name}"
        }
    )
```

**templates/profile.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ user.name }}</h1>
    <p>Email: {{ user.email }}</p>
</body>
</html>
```

---

## Async Templates

Enable async templates for async database queries:

### Configuration

```python
app = Ravyn(
    template_config=TemplateConfig(
        directory="templates",
        enable_async=True  # Enable async
    )
)
```

### Using Async in Templates

```python
@get("/products")
async def products() -> Template:
    # Pass QuerySet directly
    products = Product.query.all()  # Async QuerySet
    
    return Template(
        "products.html",
        context={"products": products}
    )
```

**templates/products.html:**
```html
<ul>
{% for product in products %}
    <li>{{ product.name }} - ${{ product.price }}</li>
{% endfor %}
</ul>
```

> [!INFO]
> With `enable_async=True`, Jinja2 automatically resolves async iterables.

---

## Built-in Template Functions

### url_for

Generate URLs for routes:

```html
<a href="{{ url_for('homepage') }}">Home</a>
<a href="{{ url_for('user_profile', user_id=123) }}">Profile</a>
```

### Template Inheritance

**base.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

**page.html:**
```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <h1>Page Content</h1>
{% endblock %}
```

---

## Using with Settings

```python
from ravyn import RavynSettings
from ravyn.config import TemplateConfig

class AppSettings(RavynSettings):
    template_config: TemplateConfig = TemplateConfig(
        directory="templates",
        autoescape=True,
        enable_async=True
    )

app = Ravyn(settings_module=AppSettings)
```

---

## Common Patterns

### Pattern 1: Layout with Partials

```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    {% include "partials/head.html" %}
</head>
<body>
    {% include "partials/header.html" %}
    {% block content %}{% endblock %}
    {% include "partials/footer.html" %}
</body>
</html>
```

### Pattern 2: Form Rendering

```python
@get("/contact")
def contact_form() -> Template:
    return Template("contact.html")

@post("/contact")
async def submit_contact(name: str, email: str, message: str) -> Template:
    await send_email(name, email, message)
    
    return Template(
        "contact.html",
        context={"success": True}
    )
```

### Pattern 3: Error Pages

```python
from ravyn import Ravyn
from ravyn.responses import Template

app = Ravyn(
    template_config=TemplateConfig(directory="templates")
)

@app.exception_handler(404)
async def not_found(request, exc) -> Template:
    return Template("404.html", status_code=404)

@app.exception_handler(500)
async def server_error(request, exc) -> Template:
    return Template("500.html", status_code=500)
```

---

## Best Practices

### 1. Organize Templates

```
templates/
  base.html
  index.html
  partials/
    header.html
    footer.html
  users/
    profile.html
    list.html
  errors/
    404.html
    500.html
```

### 2. Use Template Inheritance

```html
<!-- Good - reuse base layout -->
{% extends "base.html" %}

{% block content %}
    <h1>Page Content</h1>
{% endblock %}
```

### 3. Enable Auto-Escape

```python
# Good - prevent XSS
template_config = TemplateConfig(
    directory="templates",
    autoescape=True  # Always escape HTML
)
```

---

## Next Steps

- [StaticFilesConfig](./staticfiles.md) - Serve static files
- [Responses](../responses.md) - Response types
- [Application Settings](../application/settings.md) - Configuration
