# Requests

The `Request` object gives you access to all incoming data. path parameters, query strings, headers, cookies, request body, and more. It's your gateway to understanding what the client is asking for.

## What You'll Learn

- Accessing request data (params, headers, body)
- Working with path and query parameters
- Reading request body (JSON, form data)
- Accessing user and authentication data
- Request properties and methods

## Quick Start

```python
from ravyn import Ravyn, get, Request

@get("/users/{user_id}")
def get_user(request: Request, user_id: int) -> dict:
    # Access path parameters
    user_id_from_path = request.path_params["user_id"]
    
    # Access query parameters
    include_posts = request.query_params.get("include_posts", "false")
    
    # Access headers
    user_agent = request.headers.get("user-agent")
    
    # Access client info
    client_host = request.client.host
    
    return {
        "user_id": user_id,
        "include_posts": include_posts,
        "client": client_host
    }

app = Ravyn()
app.add_route(get_user)
```

!!! tip
    Ravyn automatically extracts path parameters and injects them as function arguments. You can use either approach!

---

## Importing Request

```python
from ravyn import Request
```

The Ravyn `Request` extends Lilya's `Request` with additional features for JSON handling and framework integration.

**API Reference:** See the [Request Reference](./references/request.md) for all properties and methods.

**Lilya Docs:** Learn more in the [Lilya Request documentation](https://www.lilya.dev/requests/).

---

## Accessing Request Data

### Path Parameters

```python
from ravyn import get, Request

# Option 1: Function parameter (recommended)
@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"user_id": user_id}

# Option 2: Via request object
@get("/users/{user_id}")
def get_user(request: Request) -> dict:
    user_id = request.path_params["user_id"]
    return {"user_id": user_id}
```

### Query Parameters

```python
from ravyn import get, Request

@get("/search")
def search(request: Request) -> dict:
    query = request.query_params.get("q", "")
    page = request.query_params.get("page", "1")
    limit = request.query_params.get("limit", "10")
    
    return {
        "query": query,
        "page": int(page),
        "limit": int(limit)
    }

# Example: GET /search?q=python&page=2&limit=20
```

### Headers

```python
from ravyn import get, Request

@get("/info")
def request_info(request: Request) -> dict:
    return {
        "user_agent": request.headers.get("user-agent"),
        "content_type": request.headers.get("content-type"),
        "authorization": request.headers.get("authorization"),
        "custom_header": request.headers.get("x-custom-header")
    }
```

### Cookies

```python
from ravyn import get, Request

@get("/profile")
def profile(request: Request) -> dict:
    session_id = request.cookies.get("session_id")
    preferences = request.cookies.get("preferences", "default")
    
    return {
        "session": session_id,
        "preferences": preferences
    }
```

---

## Request Body

### JSON Body

```python
from ravyn import post, Request

@post("/users")
async def create_user(request: Request) -> dict:
    data = await request.json()
    
    name = data.get("name")
    email = data.get("email")
    
    return {"created": {"name": name, "email": email}}

# Request body: {"name": "Alice", "email": "alice@example.com"}
```

### Form Data

```python
from ravyn import post, Request

@post("/upload")
async def upload_form(request: Request) -> dict:
    form = await request.form()
    
    title = form.get("title")
    description = form.get("description")
    
    return {"title": title, "description": description}
```

### File Uploads

```python
from ravyn import post, Request

@post("/upload-file")
async def upload_file(request: Request) -> dict:
    form = await request.form()
    file = form.get("file")
    
    if file:
        contents = await file.read()
        return {
            "filename": file.filename,
            "size": len(contents),
            "content_type": file.content_type
        }
    
    return {"error": "No file uploaded"}
```

---

## Request Properties

### Client Information

```python
from ravyn import get, Request

@get("/client-info")
def client_info(request: Request) -> dict:
    return {
        "host": request.client.host,
        "port": request.client.port
    }
```

### URL Information

```python
from ravyn import get, Request

@get("/url-info")
def url_info(request: Request) -> dict:
    return {
        "path": request.url.path,
        "scheme": request.url.scheme,
        "hostname": request.url.hostname,
        "port": request.url.port,
        "query": str(request.url.query)
    }

# Example: GET http://localhost:8000/url-info?test=value
# Returns: {"path": "/url-info", "scheme": "http", ...}
```

### HTTP Method

```python
from ravyn import route, Request

@route(methods=["GET", "POST"])
def flexible_handler(request: Request) -> dict:
    if request.method == "GET":
        return {"action": "fetching data"}
    elif request.method == "POST":
        return {"action": "creating data"}
```

---

## User and Authentication

Access authenticated user data (set by authentication middleware):

```python
from ravyn import get, Request

@get("/me")
def current_user(request: Request) -> dict:
    user = request.user
    
    if user.is_authenticated:
        return {
            "username": user.username,
            "email": user.email
        }
    
    return {"error": "Not authenticated"}
```

> [!INFO]
> `request.user` is populated by authentication middleware. See [Security](./security/index.md) for setup.

---

## Request State

Store custom data during request processing:

```python
from ravyn import get, Request, RavynInterceptor

class TimingInterceptor(RavynInterceptor):
    async def intercept(self, request):
        import time
        request.state.start_time = time.time()

@get("/timed")
def timed_endpoint(request: Request) -> dict:
    import time
    duration = time.time() - request.state.start_time
    return {"duration_ms": duration * 1000}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Forgetting to Await Async Methods

**Problem:** Not awaiting `request.json()` or `request.form()`.

```python
# Wrong - missing await
@post("/create")
async def create(request: Request) -> dict:
    data = request.json()  # Returns coroutine, not data!
    return {"data": data}
```

**Solution:** Always await async methods:

```python
# Correct
@post("/create")
async def create(request: Request) -> dict:
    data = await request.json()
    return {"data": data}
```

### Pitfall 2: Accessing Missing Query Parameters

**Problem:** KeyError when query parameter doesn't exist.

```python
# Wrong - raises KeyError if 'page' missing
@get("/items")
def list_items(request: Request) -> dict:
    page = request.query_params["page"]  # KeyError!
```

**Solution:** Use `.get()` with default value:

```python
# Correct
@get("/items")
def list_items(request: Request) -> dict:
    page = request.query_params.get("page", "1")
    return {"page": int(page)}
```

### Pitfall 3: Reading Body Multiple Times

**Problem:** Request body can only be read once.

```python
# Wrong - second read fails
@post("/process")
async def process(request: Request) -> dict:
    data1 = await request.json()
    data2 = await request.json()  # Empty or error!
```

**Solution:** Read once and store:

```python
# Correct
@post("/process")
async def process(request: Request) -> dict:
    data = await request.json()
    # Use 'data' for all processing
    return {"processed": data}
```

### Pitfall 4: Using Request in Sync Handler with Async Methods

**Problem:** Calling async methods in sync handler.

```python
# Wrong - can't await in sync function
@post("/create")
def create(request: Request) -> dict:
    data = await request.json()  # SyntaxError!
```

**Solution:** Make handler async:

```python
# Correct
@post("/create")
async def create(request: Request) -> dict:
    data = await request.json()
    return {"data": data}
```

---

## Request vs Context

| Feature | Request | Context |
|---------|---------|---------|
| **Access to** | Request data only | Request + Settings + Handler |
| **Use when** | Need request data | Need multiple pieces of info |
| **Simplicity** | Simple | More comprehensive |

```python
# Use Request when you only need request data
@get("/simple")
def simple(request: Request) -> dict:
    return {"path": request.url.path}

# Use Context when you need request + settings + handler info
from ravyn import Context

@get("/complex")
def complex(context: Context) -> dict:
    return {
        "path": context.request.url.path,
        "app_name": context.settings.app_name,
        "handler": context.handler.fn.__name__
    }
```

---

## Next Steps

Now that you understand requests, explore:

- [Context](./context.md) - Access request, settings, and handler info
- [Responses](./responses.md) - Return data to clients
- [Dependencies](./dependencies.md) - Inject dependencies
- [Handlers](./routing/handlers.md) - Different handler types
- [Request Reference](./references/request.md) - Complete API documentation
