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

## Advanced Testing Scenarios

### Testing Authenticated Endpoints

When your API requires authentication, you can test protected endpoints by providing authentication credentials in your test client.

#### Basic Authentication Testing

```python
from ravyn import Ravyn, Gateway, get, Injects, Inject
from ravyn.requests import Request
from ravyn.responses import JSONResponse
from ravyn.testclient import RavynTestClient

app = Ravyn()

# Dependency that checks for valid token
def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid token")

    token = auth_header.replace("Bearer ", "")
    if token != "valid-token-123":
        raise ValueError("Invalid token")

    return {"user_id": "user123", "username": "alice"}

@get()
def protected_endpoint(user: dict = Injects()) -> JSONResponse:
    return JSONResponse({
        "message": f"Welcome {user['username']}!",
        "user_id": user["user_id"]
    })

app = Ravyn(
    routes=[Gateway("/protected", handler=protected_endpoint)],
    dependencies={"user": Inject(get_current_user)}
)

# Test with valid authentication
def test_protected_endpoint_authorized():
    client = RavynTestClient(app)

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer valid-token-123"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome alice!",
        "user_id": "user123"
    }

# Test without authentication
def test_protected_endpoint_unauthorized():
    client = RavynTestClient(app, raise_server_exceptions=False)

    response = client.get("/protected")

    assert response.status_code == 500  # Dependency raises error

# Test with invalid token
def test_protected_endpoint_invalid_token():
    client = RavynTestClient(app, raise_server_exceptions=False)

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 500
```

#### Using Authentication Middleware

```python
from ravyn import Ravyn, Gateway, get
from ravyn.middleware.authentication import AuthenticationMiddleware
from ravyn.requests import Request
from ravyn.responses import JSONResponse
from ravyn.testclient import RavynTestClient
from lilya.authentication import AuthCredentials, BaseUser
from lilya.middleware import DefineMiddleware

# Custom authentication backend
class CustomAuthMiddleware(AuthenticationMiddleware):
    async def authenticate(self, request: Request):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")
        if token == "valid-token":
            return AuthCredentials(["authenticated"]), BaseUser("alice")

        return None

@get()
def user_profile(request: Request) -> JSONResponse:
    if not request.user.is_authenticated:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    return JSONResponse({
        "username": request.user.display_name,
        "authenticated": True
    })

app = Ravyn(
    routes=[Gateway("/profile", handler=user_profile)],
    middleware=[DefineMiddleware(CustomAuthMiddleware)]
)

def test_authenticated_user():
    client = RavynTestClient(app)

    response = client.get(
        "/profile",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert response.json()["authenticated"] is True

def test_unauthenticated_user():
    client = RavynTestClient(app)

    response = client.get("/profile")

    assert response.status_code == 401
    assert response.json()["error"] == "Unauthorized"
```

---

### Testing File Uploads

Test endpoints that handle file uploads using the `files` parameter.

#### Single File Upload

```python
from ravyn import Ravyn, Gateway, post, UploadFile
from ravyn.params import File
from ravyn.testclient import RavynTestClient
import io

app = Ravyn()

@post()
async def upload_document(file: UploadFile = File()) -> dict:
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    }

app = Ravyn(routes=[Gateway("/upload", handler=upload_document)])

def test_upload_text_file():
    client = RavynTestClient(app)

    # Create a file-like object
    file_content = b"This is a test document"

    response = client.post(
        "/upload",
        files={"file": ("document.txt", file_content, "text/plain")}
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "document.txt",
        "content_type": "text/plain",
        "size": 23
    }

def test_upload_binary_file():
    client = RavynTestClient(app)

    # Simulate uploading an image
    binary_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    response = client.post(
        "/upload",
        files={"file": ("image.png", binary_content, "image/png")}
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "image.png"
    assert response.json()["content_type"] == "image/png"
```

#### Multiple File Upload

```python
from ravyn import Ravyn, Gateway, post, UploadFile
from ravyn.params import File
from ravyn.testclient import RavynTestClient
from typing import List

app = Ravyn()

@post()
async def upload_multiple(files: List[UploadFile] = File()) -> dict:
    results = []
    for file in files:
        content = await file.read()
        results.append({
            "filename": file.filename,
            "size": len(content)
        })
    return {"files": results}

app = Ravyn(routes=[Gateway("/upload-multiple", handler=upload_multiple)])

def test_upload_multiple_files():
    client = RavynTestClient(app)

    response = client.post(
        "/upload-multiple",
        files=[
            ("files", ("file1.txt", b"Content 1", "text/plain")),
            ("files", ("file2.txt", b"Content 2", "text/plain")),
            ("files", ("file3.txt", b"Content 3", "text/plain"))
        ]
    )

    assert response.status_code == 200
    assert len(response.json()["files"]) == 3
    assert response.json()["files"][0]["filename"] == "file1.txt"
    assert response.json()["files"][1]["size"] == 9
```

---

### Testing WebSocket Endpoints

Ravyn's test client includes support for testing WebSocket connections.

#### Basic WebSocket Test

```python
from ravyn import Ravyn, websocket
from ravyn.routing.gateways import WebSocketGateway
from ravyn.websockets import WebSocket
from ravyn.testclient import create_client

@websocket(path="/")
async def echo_websocket(socket: WebSocket) -> None:
    await socket.accept()

    # Receive and echo messages
    data = await socket.receive_json()
    await socket.send_json({"echo": data})

    await socket.close()

def test_websocket_echo():
    client = create_client(
        routes=[WebSocketGateway(path="/ws", handler=echo_websocket)]
    )

    with client.websocket_connect("/ws") as websocket:
        # Send data to WebSocket
        websocket.send_json({"message": "Hello WebSocket!"})

        # Receive response
        response = websocket.receive_json()

        assert response == {"echo": {"message": "Hello WebSocket!"}}

def test_websocket_multiple_messages():
    @websocket(path="/")
    async def chat_websocket(socket: WebSocket) -> None:
        await socket.accept()

        # Handle multiple messages
        for i in range(3):
            data = await socket.receive_text()
            await socket.send_text(f"Message {i+1}: {data}")

        await socket.close()

    client = create_client(
        routes=[WebSocketGateway(path="/chat", handler=chat_websocket)]
    )

    with client.websocket_connect("/chat") as websocket:
        websocket.send_text("First")
        assert websocket.receive_text() == "Message 1: First"

        websocket.send_text("Second")
        assert websocket.receive_text() == "Message 2: Second"

        websocket.send_text("Third")
        assert websocket.receive_text() == "Message 3: Third"
```

#### WebSocket with Authentication

```python
from ravyn import Ravyn, websocket
from ravyn.routing.gateways import WebSocketGateway
from ravyn.websockets import WebSocket, WebSocketDisconnect
from ravyn.testclient import create_client

@websocket(path="/")
async def secure_websocket(socket: WebSocket) -> None:
    # Check authentication in headers
    token = socket.headers.get("Authorization", "")

    if token != "Bearer valid-token":
        await socket.close(code=1008)  # Policy violation
        return

    await socket.accept()
    await socket.send_json({"status": "connected", "authenticated": True})
    await socket.close()

def test_websocket_authenticated():
    client = create_client(
        routes=[WebSocketGateway(path="/secure", handler=secure_websocket)]
    )

    # Test with valid token
    with client.websocket_connect(
        "/secure",
        headers={"Authorization": "Bearer valid-token"}
    ) as websocket:
        data = websocket.receive_json()
        assert data["authenticated"] is True

def test_websocket_unauthenticated():
    client = create_client(
        routes=[WebSocketGateway(path="/secure", handler=secure_websocket)]
    )

    # Test without token - should close immediately
    try:
        with client.websocket_connect("/secure") as websocket:
            # Connection should be closed
            pass
    except WebSocketDisconnect:
        # Expected behavior
        pass
```

---

### Testing with Database Fixtures

When testing endpoints that interact with databases, use pytest fixtures to set up and tear down test data.

#### Using In-Memory Database

```python
import pytest
from ravyn import Ravyn, Gateway, get, post, Inject, Injects
from ravyn.testclient import RavynTestClient

# Simulate a database
class InMemoryDB:
    def __init__(self):
        self.users = {}
        self.next_id = 1

    def create_user(self, name: str, email: str) -> dict:
        user = {
            "id": self.next_id,
            "name": name,
            "email": email
        }
        self.users[self.next_id] = user
        self.next_id += 1
        return user

    def get_user(self, user_id: int) -> dict:
        return self.users.get(user_id)

    def list_users(self) -> list:
        return list(self.users.values())

    def clear(self):
        self.users = {}
        self.next_id = 1

# Global database instance for testing
test_db = InMemoryDB()

def get_database() -> InMemoryDB:
    return test_db

@get()
def list_users(db: InMemoryDB = Injects()) -> dict:
    return {"users": db.list_users()}

@post()
def create_user(name: str, email: str, db: InMemoryDB = Injects()) -> dict:
    return db.create_user(name, email)

@get()
def get_user(user_id: int, db: InMemoryDB = Injects()) -> dict:
    user = db.get_user(user_id)
    if not user:
        raise ValueError("User not found")
    return user

app = Ravyn(
    routes=[
        Gateway("/users", handler=list_users),
        Gateway("/users/create", handler=create_user),
        Gateway("/users/{user_id}", handler=get_user)
    ],
    dependencies={"db": Inject(get_database)}
)

@pytest.fixture
def client():
    """Create test client with fresh database"""
    test_db.clear()  # Reset database before each test
    return RavynTestClient(app)

def test_create_and_retrieve_user(client):
    # Create a user
    create_response = client.post(
        "/users/create",
        json={"name": "Alice", "email": "alice@example.com"}
    )

    assert create_response.status_code == 200
    user = create_response.json()
    assert user["name"] == "Alice"
    assert user["id"] == 1

    # Retrieve the user
    get_response = client.get(f"/users/{user['id']}")

    assert get_response.status_code == 200
    assert get_response.json() == user

def test_list_users(client):
    # Create multiple users
    client.post("/users/create", json={"name": "Alice", "email": "alice@example.com"})
    client.post("/users/create", json={"name": "Bob", "email": "bob@example.com"})
    client.post("/users/create", json={"name": "Charlie", "email": "charlie@example.com"})

    # List all users
    response = client.get("/users")

    assert response.status_code == 200
    users = response.json()["users"]
    assert len(users) == 3
    assert users[0]["name"] == "Alice"
    assert users[1]["name"] == "Bob"
    assert users[2]["name"] == "Charlie"

def test_user_not_found(client):
    response = client.get("/users/999", raise_server_exceptions=False)

    # In Ravyn, if handler raises exception and raise_server_exceptions=False,
    # it returns 500 by default
    assert response.status_code == 500
```

#### Using Database Fixtures with Lifespan

```python
import pytest
from ravyn import Ravyn, Gateway, get
from ravyn.testclient import create_client

# Simulated database that initializes on startup
database_state = {"initialized": False, "data": []}

@pytest.fixture
def app():
    async def startup():
        database_state["initialized"] = True
        database_state["data"] = [
            {"id": 1, "name": "Initial Item 1"},
            {"id": 2, "name": "Initial Item 2"}
        ]

    async def shutdown():
        database_state["initialized"] = False
        database_state["data"] = []

    @get()
    def get_items() -> dict:
        if not database_state["initialized"]:
            raise RuntimeError("Database not initialized")
        return {"items": database_state["data"]}

    return Ravyn(
        routes=[Gateway("/items", handler=get_items)],
        on_startup=[startup],
        on_shutdown=[shutdown]
    )

def test_with_database_initialized(app):
    # Use context manager to trigger lifespan events
    with create_client(app=app) as client:
        response = client.get("/items")

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 2
        assert items[0]["name"] == "Initial Item 1"

    # After context exits, shutdown should have run
    assert database_state["initialized"] is False
```

---

### Testing Error Responses

Test how your application handles errors and returns proper error responses.

#### Testing Validation Errors

```python
from ravyn import Ravyn, Gateway, post
from ravyn.testclient import RavynTestClient
from pydantic import BaseModel, field_validator

app = Ravyn()

class UserCreate(BaseModel):
    username: str
    email: str
    age: int

    @field_validator("age")
    def validate_age(cls, v):
        if v < 18:
            raise ValueError("Must be at least 18 years old")
        return v

@post()
def create_user(data: UserCreate) -> dict:
    return {"user": data.model_dump()}

app = Ravyn(routes=[Gateway("/users", handler=create_user)])

def test_validation_error_missing_field():
    client = RavynTestClient(app, raise_server_exceptions=False)

    # Missing required field
    response = client.post(
        "/users",
        json={"username": "alice", "email": "alice@example.com"}
    )

    assert response.status_code == 422  # Validation error
    error_data = response.json()
    assert "detail" in error_data

def test_validation_error_invalid_age():
    client = RavynTestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "age": 16  # Too young
        }
    )

    assert response.status_code == 422
    assert "Must be at least 18 years old" in str(response.json())

def test_successful_user_creation():
    client = RavynTestClient(app)

    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "age": 25
        }
    )

    assert response.status_code == 200
    assert response.json()["user"]["username"] == "alice"
```

#### Testing Custom Error Handlers

```python
from ravyn import Ravyn, Gateway, get
from ravyn.requests import Request
from ravyn.responses import JSONResponse
from ravyn.testclient import RavynTestClient

class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

def item_not_found_handler(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    return JSONResponse(
        {
            "error": "Item not found",
            "item_id": exc.item_id,
            "message": f"Item with ID {exc.item_id} does not exist"
        },
        status_code=404
    )

@get()
def get_item(item_id: int) -> dict:
    # Simulate item lookup
    items = {1: "Apple", 2: "Banana", 3: "Cherry"}

    if item_id not in items:
        raise ItemNotFoundError(item_id)

    return {"id": item_id, "name": items[item_id]}

app = Ravyn(
    routes=[Gateway("/items/{item_id}", handler=get_item)],
    exception_handlers={ItemNotFoundError: item_not_found_handler}
)

def test_item_found():
    client = RavynTestClient(app)

    response = client.get("/items/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Apple"}

def test_item_not_found_custom_error():
    client = RavynTestClient(app)

    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json()["error"] == "Item not found"
    assert response.json()["item_id"] == 999
    assert "does not exist" in response.json()["message"]

def test_multiple_error_scenarios():
    client = RavynTestClient(app)

    # Test various non-existent IDs
    for bad_id in [100, 500, 999]:
        response = client.get(f"/items/{bad_id}")
        assert response.status_code == 404
        assert response.json()["item_id"] == bad_id
```

#### Testing HTTP Exception Responses

```python
from ravyn import Ravyn, Gateway, get
from ravyn.exceptions import HTTPException
from ravyn.testclient import RavynTestClient

app = Ravyn()

@get()
def protected_resource(api_key: str) -> dict:
    if api_key != "secret-key":
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    return {"data": "sensitive information"}

app = Ravyn(routes=[Gateway("/resource", handler=protected_resource)])

def test_valid_api_key():
    client = RavynTestClient(app, raise_server_exceptions=False)

    response = client.get("/resource", params={"api_key": "secret-key"})

    assert response.status_code == 200
    assert response.json()["data"] == "sensitive information"

def test_invalid_api_key():
    client = RavynTestClient(app, raise_server_exceptions=False)

    response = client.get("/resource", params={"api_key": "wrong-key"})

    assert response.status_code == 403
    assert "Invalid API key" in str(response.json())

def test_missing_api_key():
    client = RavynTestClient(app, raise_server_exceptions=False)

    response = client.get("/resource")

    assert response.status_code == 422  # Validation error for missing param
```

---

## RavynTestClient API Reference

The `RavynTestClient` provides a complete testing interface for your Ravyn applications.

### Constructor Parameters

```python
RavynTestClient(
    app: Ravyn,
    base_url: str = "http://testserver",
    raise_server_exceptions: bool = True,
    root_path: str = "",
    backend: Literal["asyncio", "trio"] = "asyncio",
    backend_options: Optional[dict[str, Any]] = None,
    cookies: Optional[CookieTypes] = None,
    headers: dict[str, str] = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app` | `Ravyn` | Required | The Ravyn application to test |
| `base_url` | `str` | `"http://testserver"` | Base URL for requests |
| `raise_server_exceptions` | `bool` | `True` | Whether to raise exceptions that occur in handlers |
| `root_path` | `str` | `""` | ASGI root path |
| `backend` | `Literal["asyncio", "trio"]` | `"asyncio"` | Async backend to use |
| `backend_options` | `Optional[dict]` | `None` | Backend-specific options |
| `cookies` | `Optional[CookieTypes]` | `None` | Default cookies for all requests |
| `headers` | `dict[str, str]` | `None` | Default headers for all requests |

### HTTP Methods

All standard HTTP methods are available:

#### client.get()

```python
response = client.get(
    url: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    cookies: Optional[dict] = None,
    follow_redirects: bool = False,
)
```

#### client.post()

```python
response = client.post(
    url: str,
    json: Optional[dict] = None,
    data: Optional[dict] = None,
    files: Optional[dict] = None,
    headers: Optional[dict] = None,
    cookies: Optional[dict] = None,
)
```

#### client.put()

```python
response = client.put(
    url: str,
    json: Optional[dict] = None,
    data: Optional[dict] = None,
    headers: Optional[dict] = None,
)
```

#### client.patch()

```python
response = client.patch(
    url: str,
    json: Optional[dict] = None,
    data: Optional[dict] = None,
    headers: Optional[dict] = None,
)
```

#### client.delete()

```python
response = client.delete(
    url: str,
    headers: Optional[dict] = None,
)
```

#### client.head()

```python
response = client.head(
    url: str,
    headers: Optional[dict] = None,
)
```

#### client.options()

```python
response = client.options(
    url: str,
    headers: Optional[dict] = None,
)
```

### WebSocket Support

#### client.websocket_connect()

```python
with client.websocket_connect(
    url: str,
    subprotocols: Optional[Sequence[str]] = None,
    headers: Optional[dict] = None,
) as websocket:
    websocket.send_json({"message": "Hello"})
    data = websocket.receive_json()
```

**WebSocket methods:**

- `websocket.send_text(data: str)` - Send text message
- `websocket.send_json(data: dict)` - Send JSON message
- `websocket.send_bytes(data: bytes)` - Send binary message
- `websocket.receive_text() -> str` - Receive text message
- `websocket.receive_json() -> dict` - Receive JSON message
- `websocket.receive_bytes() -> bytes` - Receive binary message
- `websocket.close(code: int = 1000)` - Close connection

### Response Object

All HTTP methods return a response object with:

```python
response.status_code      # HTTP status code (int)
response.headers          # Response headers (dict-like)
response.json()           # Parse JSON body (returns dict/list)
response.text             # Response body as string
response.content          # Response body as bytes
response.cookies          # Response cookies
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
