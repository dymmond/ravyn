# Responses

Responses determine how your API sends data back to clients. Ravyn supports multiple response types from simple JSON to file downloads, templates, and streaming—all with clean, type-safe syntax.

## What You'll Learn

- Available response types and when to use them
- Returning JSON with different serializers (ORJSON, UJSON)
- Serving templates, files, and streams
- Managing status codes
- Adding responses to OpenAPI documentation

## Quick Start

### Simple JSON Response

```python
from ravyn import Ravyn, get
from ravyn.responses import JSONResponse

@get("/users")
def list_users() -> JSONResponse:
    return JSONResponse({"users": ["Alice", "Bob"]})

app = Ravyn()
app.add_route(list_users)
```

### Auto-Conversion (Recommended)

Ravyn automatically converts Pydantic models, dataclasses, and dicts to JSON:

```python
from ravyn import Ravyn, get
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

@get("/user")
def get_user() -> User:
    return User(name="Alice", email="alice@example.com")
    # Automatically converted to JSONResponse!

app = Ravyn()
app.add_route(get_user)
```

!!! tip
    Return Pydantic models, dataclasses, or dicts directly—Ravyn converts them to JSON automatically.

---

## Available Response Types

| Response | Use Case | Example |
|----------|----------|---------|
| `JSONResponse` | API responses (default) | `{"status": "ok"}` |
| `TemplateResponse` | HTML pages | Jinja2 templates |
| `RedirectResponse` | Redirects | Login → Dashboard |
| `FileResponse` | File downloads | PDFs, images |
| `StreamingResponse` | Large data | Video streaming |
| `PlainTextResponse` | Plain text | Simple messages |

---

## JSON Responses

### JSONResponse (ORJSON - Fastest)

Ravyn uses ORJSON by default for maximum performance:

```python
from ravyn import get
from ravyn.responses import JSONResponse

@get("/data")
def get_data() -> JSONResponse:
    return JSONResponse({
        "items": [1, 2, 3],
        "total": 3
    })
```

### Direct Import

```python
from ravyn.responses import JSONResponse  # ORJSON-based
```

### UJSONResponse (Alternative)

Another fast JSON serializer:

```python
from ravyn.responses.encoders import UJSONResponse

@get("/data")
def get_data() -> UJSONResponse:
    return UJSONResponse({"message": "Using UJSON"})
```

!!! warning
    UJSON and ORJSON require installation: `pip install ujson orjson`

### Status Codes

Control status codes in multiple ways:

```python
from ravyn import get, post
from ravyn.responses import JSONResponse

# Option 1: In the response
@get("/method1")
def method1() -> JSONResponse:
    return JSONResponse({"created": True}, status_code=201)

# Option 2: In the handler decorator
@post("/method2", status_code=201)
def method2() -> JSONResponse:
    return JSONResponse({"created": True})

# Option 3: Both (response takes precedence!)
@post("/method3", status_code=201)
def method3() -> JSONResponse:
    return JSONResponse({"created": True}, status_code=202)
    # Returns 202, not 201!
```

**Priority:** Response `status_code` > Handler `status_code`

---

## Template Responses

Render HTML templates with Jinja2:

```python
from ravyn import get
from ravyn.responses import Template

@get("/profile")
def profile(name: str) -> Template:
    return Template(
        name="profile.html",
        context={"user_name": name}
    )
```

### Setup Template Engine

Configure in settings:

```python
from ravyn import RavynSettings
from ravyn.configurations import TemplateConfig

class Settings(RavynSettings):
    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(directory="templates")
```

> [!INFO]
> For async templates (e.g., iterating over Edgy QuerySets), see [Template Configuration](./configurations/template.md).

---

## Redirect Responses

Redirect users to different URLs:

```python
from ravyn import get, post
from ravyn.responses import Redirect

@post("/login")
def login(username: str, password: str) -> Redirect:
    # Authenticate user...
    return Redirect(path="/dashboard")

@get("/old-page")
def old_page() -> Redirect:
    return Redirect(path="/new-page", status_code=301)  # Permanent redirect
```

---

## File Responses

Send files for download:

```python
from ravyn import get
from ravyn.responses import File

@get("/download")
def download_report() -> File:
    return File(
        path="/reports/monthly.pdf",
        filename="report.pdf"
    )

@get("/image")
def get_image() -> File:
    return File(
        path="/images/logo.png",
        media_type="image/png"
    )
```

---

## Streaming Responses

Stream large responses:

```python
from ravyn import get
from ravyn.responses import Stream

async def generate_data():
    for i in range(1000):
        yield f"data: {i}\n\n"

@get("/stream")
async def stream_data() -> Stream:
    return Stream(generate_data())
```

---

## Other Response Types

### Plain Text

```python
from ravyn.responses import PlainText

@get("/health")
def health() -> PlainText:
    return PlainText("OK")
```

### Direct Returns

Return basic Python types directly:

```python
@get("/string")
def return_string() -> str:
    return "Hello, World!"

@get("/dict")
def return_dict() -> dict:
    return {"message": "Hello"}

@get("/list")
def return_list() -> list:
    return [1, 2, 3]
```

Ravyn automatically wraps these in appropriate responses.

---

## OpenAPI Response Documentation

Document multiple response types in your OpenAPI spec:

```python
from ravyn import get, post
from ravyn.openapi.datastructures import OpenAPIResponse
from pydantic import BaseModel

class Item(BaseModel):
    sku: str
    description: str

class Error(BaseModel):
    detail: str

@post(
    "/items",
    responses={
        201: OpenAPIResponse(model=Item, description="Item created"),
        400: OpenAPIResponse(model=Error, description="Validation error"),
        401: OpenAPIResponse(model=Error, description="Not authorized")
    }
)
def create_item() -> Item:
    return Item(sku="ABC123", description="New item")
```

### List Responses

Document array responses:

```python
@get(
    "/items",
    responses={
        200: OpenAPIResponse(model=[Item], description="List of items")
    }
)
def list_items() -> list[Item]:
    return [Item(sku="A", description="Item A")]
```

!!! tip
    Use `model=[YourModel]` (list syntax) to indicate array responses in OpenAPI.

---

## Common Pitfalls & Fixes

### Pitfall 1: Status Code Confusion

**Problem:** Handler status_code doesn't apply.

```python
# Confusing - which status code wins?
@post("/create", status_code=201)
def create() -> JSONResponse:
    return JSONResponse({"created": True}, status_code=202)
    # Returns 202, not 201!
```

**Solution:** Be consistent—use one or the other:

```python
# Clear - use handler decorator
@post("/create", status_code=201)
def create() -> JSONResponse:
    return JSONResponse({"created": True})

# Or use response
@post("/create")
def create() -> JSONResponse:
    return JSONResponse({"created": True}, status_code=201)
```

### Pitfall 2: Missing ORJSON/UJSON

**Problem:** `ModuleNotFoundError` when using fast JSON serializers.

```python
# Error if orjson not installed
from ravyn.responses import JSONResponse
```

**Solution:** Install the dependencies:

```shell
pip install orjson ujson
```

### Pitfall 3: Template Engine Not Configured

**Problem:** `ImproperlyConfigured` when using templates.

```python
# Error - no template engine configured
@get("/page")
def page() -> Template:
    return Template(name="page.html", context={})
```

**Solution:** Configure template engine in settings:

```python
from ravyn import RavynSettings
from ravyn.configurations import TemplateConfig

class Settings(RavynSettings):
    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(directory="templates")
```

### Pitfall 4: File Path Errors

**Problem:** File not found when serving files.

```python
# Wrong - relative path might not work
@get("/download")
def download() -> File:
    return File(path="report.pdf")  # Where is this file?
```

**Solution:** Use absolute paths:

```python
# Correct
from pathlib import Path

@get("/download")
def download() -> File:
    file_path = Path(__file__).parent / "reports" / "report.pdf"
    return File(path=str(file_path))
```

---

## Response Headers and Cookies

All responses support headers and cookies:

```python
from ravyn.responses import JSONResponse

@get("/with-headers")
def with_headers() -> JSONResponse:
    return JSONResponse(
        {"message": "Hello"},
        headers={"X-Custom-Header": "value"},
        cookies={"session_id": "abc123"}
    )
```

---

## Next Steps

Now that you understand responses, explore:

- [Requests](./requests.md) - Handle incoming data
- [Handlers](./routing/handlers.md) - Different handler types
- [OpenAPI Configuration](./configurations/openapi/config.md) - Customize API docs
- [Template Configuration](./configurations/template.md) - Configure templates
- [Exceptions](./exceptions.md) - Handle errors
