# Testing Your Ravyn Application

Testing ensures your API works correctly and prevents bugs from reaching production. Ravyn includes a built-in test client that makes testing fast and easy.

## What You'll Learn

- How to install and use the Ravyn test client
- Writing tests for routes and handlers
- Testing with pytest and async functions
- Using fixtures and context managers
- Overriding settings for tests

## Quick Start

### Installation

```shell
pip install ravyn[test]
```

This installs `RavynTestClient` and testing dependencies.

### Your First Test

```python
from ravyn import Ravyn, get
from ravyn.testclient import RavynTestClient

app = Ravyn()

@app.get("/hello")
def hello() -> dict:
    return {"message": "Hello, World!"}

# Test it
def test_hello():
    client = RavynTestClient(app)
    response = client.get("/hello")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

Run with pytest:

```shell
pytest test_app.py
```

**That's it!** You've tested your first endpoint.

---

## Why Test Your API?

Testing gives you:

- **Confidence** - Know your code works before deploying
- **Regression Prevention** - Catch bugs when changing code
- **Documentation** - Tests show how your API should work
- **Faster Development** - Fix bugs early, not in production

---

## The RavynTestClient

`RavynTestClient` is built on top of `httpx.Client` with Ravyn-specific features.

### Basic Usage

```python
from ravyn import Ravyn, get, post
from ravyn.testclient import RavynTestClient

app = Ravyn()

@app.get("/users")
def list_users() -> dict:
    return {"users": ["Alice", "Bob"]}

@app.post("/users")
def create_user(name: str) -> dict:
    return {"created": name}

def test_list_users():
    client = RavynTestClient(app)
    response = client.get("/users")
    
    assert response.status_code == 200
    assert response.json() == {"users": ["Alice", "Bob"]}

def test_create_user():
    client = RavynTestClient(app)
    response = client.post("/users", json={"name": "Charlie"})
    
    assert response.status_code == 200
    assert response.json() == {"created": "Charlie"}
```

### Available Methods

All standard HTTP methods are supported:

```python
client.get("/path")
client.post("/path", json={...})
client.put("/path", json={...})
client.patch("/path", json={...})
client.delete("/path")
client.head("/path")
client.options("/path")
```

**Reference:** See the [Test Client API Reference](./references/test-client.md).

---

## Testing with Authentication

Use headers, cookies, and authentication like you would with `httpx`:

### Headers

```python
def test_with_auth_header():
    client = RavynTestClient(app)
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer token123"}
    )
    assert response.status_code == 200
```

### Cookies

```python
def test_with_cookies():
    client = RavynTestClient(app)
    response = client.get(
        "/profile",
        cookies={"session_id": "abc123"}
    )
    assert response.status_code == 200
```

### Session Cookies

```python
def test_login_flow():
    client = RavynTestClient(app)
    
    # Login sets a cookie
    login_response = client.post("/login", json={
        "username": "alice",
        "password": "secret"
    })
    
    # Cookie is automatically included in next request
    profile_response = client.get("/profile")
    assert profile_response.status_code == 200
```

---

## Testing File Uploads

```python
from ravyn import Ravyn, post, UploadFile
from ravyn.testclient import RavynTestClient

app = Ravyn()

@app.post("/upload")
async def upload_file(file: UploadFile) -> dict:
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}

def test_file_upload():
    client = RavynTestClient(app)
    
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"Hello, World!", "text/plain")}
    )
    
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"
    assert response.json()["size"] == 13
```

---

## Testing Async Handlers

Tests can be sync or async. both work with `RavynTestClient`:

### Sync Test (Recommended)

```python
from ravyn import Ravyn, get
from ravyn.testclient import RavynTestClient

app = Ravyn()

@app.get("/async-endpoint")
async def async_handler() -> dict:
    return {"message": "Async works!"}

# Test is sync, handler is async - works fine!
def test_async_handler():
    client = RavynTestClient(app)
    response = client.get("/async-endpoint")
    assert response.status_code == 200
```

### Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_async_handler_async():
    client = RavynTestClient(app)
    response = client.get("/async-endpoint")
    assert response.status_code == 200
```

!!! tip
    Use sync tests unless you specifically need async features. They're simpler and faster.

---

## Testing with Pytest Fixtures

Fixtures make tests cleaner by reusing setup code:

### Basic Fixture

```python
import pytest
from ravyn import Ravyn, get
from ravyn.testclient import RavynTestClient

@pytest.fixture
def app():
    app = Ravyn()
    
    @app.get("/users")
    def list_users() -> dict:
        return {"users": ["Alice", "Bob"]}
    
    return app

@pytest.fixture
def client(app):
    return RavynTestClient(app)

def test_list_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()["users"]) == 2
```

### Fixture with Dependency Injection

```python
import pytest
from ravyn import Ravyn, Gateway, Inject, Injects, get

def get_test_database():
    return {"db": "test_db"}

@pytest.fixture
def app():
    @get()
    def users(db: dict = Injects()) -> dict:
        return {"users": [], "db": db}
    
    return Ravyn(
        routes=[Gateway("/users", handler=users)],
        dependencies={"db": Inject(get_test_database)}
    )

@pytest.fixture
def client(app):
    return RavynTestClient(app)

def test_users_with_test_db(client):
    response = client.get("/users")
    assert response.json()["db"] == {"db": "test_db"}
```

---

## Testing Lifespan Events

Lifespan events (`on_startup`, `on_shutdown`, `lifespan`) only run when using `RavynTestClient` as a **context manager**.

### Using create_client Context Manager

```python
from ravyn import Ravyn, get
from ravyn.testclient import create_client

app = Ravyn()

startup_called = False
shutdown_called = False

@app.on_event("startup")
async def startup():
    global startup_called
    startup_called = True

@app.on_event("shutdown")
async def shutdown():
    global shutdown_called
    shutdown_called = True

@app.get("/test")
def test_endpoint() -> dict:
    return {"message": "test"}

def test_with_lifespan():
    global startup_called, shutdown_called
    
    with create_client(routes=[Gateway("/test", handler=test_endpoint)]) as client:
        # Startup event has run
        assert startup_called is True
        
        response = client.get("/test")
        assert response.status_code == 200
    
    # Shutdown event has run
    assert shutdown_called is True
```

### Manual Context Manager

```python
def test_manual_context_manager():
    with RavynTestClient(app) as client:
        # Startup runs here
        response = client.get("/test")
        assert response.status_code == 200
    # Shutdown runs here
```

!!! warning
    If you instantiate `RavynTestClient` without a context manager, lifespan events **will not run**.

---

## Overriding Settings for Tests

Use `override_settings` to temporarily change settings during tests.

### As a Decorator

```python
from ravyn import Ravyn, Gateway, get
from ravyn.testclient import RavynTestClient, override_settings
from ravyn.responses import PlainText

@get()
def homepage() -> PlainText:
    return PlainText("Ok", status_code=200)

app = Ravyn(routes=[Gateway("/", handler=homepage)])

@override_settings(debug=True, app_name="Test App")
def test_with_custom_settings():
    client = RavynTestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    # Settings are overridden only in this test
```

### As a Context Manager

```python
from ravyn.testclient import override_settings

def test_with_settings_context():
    with override_settings(debug=True):
        client = RavynTestClient(app)
        response = client.get("/")
        assert response.status_code == 200
    # Settings restored after 'with' block
```

### Real-World Example

```python
from lilya.middleware import DefineMiddleware
from ravyn import Ravyn, Gateway, get
from ravyn.middleware.clickjacking import XFrameOptionsMiddleware
from ravyn.responses import PlainText
from ravyn.testclient import RavynTestClient, override_settings

@get()
def homepage() -> PlainText:
    return PlainText("Ok", status_code=200)

@override_settings(x_frame_options="SAMEORIGIN")
def test_xframe_options():
    app = Ravyn(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(XFrameOptionsMiddleware)]
    )
    
    client = RavynTestClient(app)
    response = client.get("/")
    
    assert response.headers["x-frame-options"] == "SAMEORIGIN"
```

---

## Handling Server Exceptions

By default, `RavynTestClient` raises exceptions that occur in your application.

### Default Behavior (Raises Exceptions)

```python
from ravyn import Ravyn, get
from ravyn.testclient import RavynTestClient

app = Ravyn()

@app.get("/error")
def error_endpoint() -> dict:
    raise ValueError("Something went wrong!")

def test_error_raises():
    client = RavynTestClient(app)
    
    # This raises ValueError
    try:
        response = client.get("/error")
    except ValueError as e:
        assert str(e) == "Something went wrong!"
```

### Testing Error Responses (Don't Raise)

```python
def test_error_response():
    client = RavynTestClient(app, raise_server_exceptions=False)
    
    response = client.get("/error")
    
    # Now we get a 500 response instead of an exception
    assert response.status_code == 500
```

!!! tip
    Use `raise_server_exceptions=False` when testing error handling and 500 responses.

---

## Common Pitfalls & Fixes

### Pitfall 1: Lifespan Events Not Running

**Problem:** Startup/shutdown events don't execute.

```python
# Wrong - events don't run
def test_startup():
    client = RavynTestClient(app)  # No context manager
    response = client.get("/test")
```

**Solution:** Use a context manager:

```python
# Correct
def test_startup():
    with RavynTestClient(app) as client:  # Events run!
        response = client.get("/test")
```

Or use `create_client`:

```python
# Also correct
from ravyn.testclient import create_client

def test_startup():
    with create_client(app=app) as client:
        response = client.get("/test")
```

### Pitfall 2: Forgetting to Install Test Dependencies

**Problem:** `ModuleNotFoundError: No module named 'ravyn.testclient'`

**Solution:** Install test extras:

```shell
pip install ravyn[test]
```

### Pitfall 3: Testing Async Code Without pytest-asyncio

**Problem:** Async tests fail with `RuntimeError: no running event loop`

```python
# Wrong - missing pytest mark
async def test_async():
    client = RavynTestClient(app)
    response = client.get("/test")
```

**Solution:** Add `pytest.mark.asyncio` or use sync tests:

```python
# Option 1: Add decorator
import pytest

@pytest.mark.asyncio
async def test_async():
    client = RavynTestClient(app)
    response = client.get("/test")

# Option 2: Use sync test (recommended)
def test_sync():
    client = RavynTestClient(app)
    response = client.get("/test")
```

### Pitfall 4: Not Resetting Global State Between Tests

**Problem:** Tests affect each other through shared state.

```python
# Wrong - shared state
users = []

@app.post("/users")
def create_user(name: str) -> dict:
    users.append(name)  # Modifies global list
    return {"created": name}

def test_create_user_1():
    client = RavynTestClient(app)
    client.post("/users", json={"name": "Alice"})
    assert len(users) == 1  # Passes

def test_create_user_2():
    client = RavynTestClient(app)
    client.post("/users", json={"name": "Bob"})
    assert len(users) == 1  # Fails! users has 2 items
```

**Solution:** Reset state in fixtures or use dependency injection:

```python
# Correct - reset in fixture
import pytest

@pytest.fixture(autouse=True)
def reset_users():
    global users
    users = []
    yield
    users = []
```

---

## Testing Patterns

### Pattern 1: Arrange-Act-Assert

```python
def test_create_and_get_user():
    # Arrange
    client = RavynTestClient(app)
    user_data = {"name": "Alice", "email": "alice@example.com"}
    
    # Act
    create_response = client.post("/users", json=user_data)
    user_id = create_response.json()["id"]
    get_response = client.get(f"/users/{user_id}")
    
    # Assert
    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Alice"
```

### Pattern 2: Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("path,expected_status", [
    ("/users", 200),
    ("/users/123", 200),
    ("/users/invalid", 404),
    ("/admin", 403),
])
def test_endpoints(path, expected_status):
    client = RavynTestClient(app)
    response = client.get(path)
    assert response.status_code == expected_status
```

### Pattern 3: Shared Client Fixture

```python
import pytest

@pytest.fixture(scope="module")
def client():
    """Shared client for all tests in module"""
    return RavynTestClient(app)

def test_endpoint_1(client):
    response = client.get("/test1")
    assert response.status_code == 200

def test_endpoint_2(client):
    response = client.get("/test2")
    assert response.status_code == 200
```

---

## Next Steps

Now that you can test your application, explore:

- [Dependencies](./dependencies.md) - Test with dependency injection
- [Middleware](./middleware/index.md) - Test middleware behavior
- [Permissions](./permissions/index.md) - Test authorization
- [Database Testing](./databases/edgy/motivation.md) - Test with databases
- [Guides](./guides/beginner/index.md) - Full testing examples
