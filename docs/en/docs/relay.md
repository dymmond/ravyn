# Relay

Relay is a mountable ASGI proxy for Ravyn that forwards HTTP and WebSocket traffic to upstream services. Perfect for microservices, authentication services, and API gateways.

## What You'll Learn

- What Relay is and when to use it
- Setting up a basic proxy
- Configuring headers and cookies
- WebSocket proxying
- Error handling and retries
- Testing your proxy

## Quick Start

```python
from ravyn import Ravyn, Include
from lilya.contrib.proxy.relay import Relay

# Create proxy to auth service
proxy = Relay(
    target_base_url="http://auth-service:8000",
    upstream_prefix="/",
    preserve_host=False
)

# Mount proxy in your app
app = Ravyn(
    routes=[
        Include("/auth", app=proxy)  # All /auth/** requests proxied
    ],
    on_startup=[proxy.startup],
    on_shutdown=[proxy.shutdown]
)

# GET /auth/login → GET http://auth-service:8000/login
# POST /auth/register → POST http://auth-service:8000/register
```

!!! info
    Install httpx: `pip install httpx`

---

## Why Use Relay?

### Benefits:

- **Single Public Surface** - Expose one API, proxy to many services

- **No Duplication** - Don't re-implement services, just forward

- **Transparent** - Streams requests/responses without buffering

- **Flexible** - Control headers, cookies, retries, timeouts

- **WebSocket Support** - Proxy WS traffic bidirectionally

### Use Cases:

- **Microservices** - Route to different services
- **Authentication** - Proxy to dedicated auth service
- **API Gateway** - Single entry point for multiple backends
- **Service Isolation** - Keep internal services private

---

## How Relay Works

```
Client Request
    ↓
Your Ravyn App (Public)
    ↓
Relay Proxy
    ↓
Upstream Service (Private)
    ↓
Response flows back
```

**Request Flow:**
1. Client calls `/auth/login`
2. Ravyn routes to Relay at `/auth`
3. Relay forwards to `http://auth-service:8000/login`
4. Response streams back to client

---

## Basic Configuration

### Minimal Setup

```python
from lilya.contrib.proxy.relay import Relay

proxy = Relay(
    target_base_url="http://upstream-service:8000"
)
```

### With Options

```python
proxy = Relay(
    target_base_url="http://auth-service:8000",
    upstream_prefix="/api/v1",  # Prepend to upstream path
    preserve_host=False,         # Use upstream host
    max_retries=2,              # Retry failed requests
    retry_backoff_factor=0.2    # Exponential backoff
)
```

---

## Path Mapping

Control how paths are mapped to upstream:

### Same Path

```python
# Mount at /auth, upstream at /
proxy = Relay(
    target_base_url="http://auth:8000",
    upstream_prefix="/"
)

# /auth/login → http://auth:8000/login
```

### Different Path

```python
# Mount at /auth, upstream at /api/v1
proxy = Relay(
    target_base_url="http://auth:8000",
    upstream_prefix="/api/v1"
)

# /auth/login → http://auth:8000/api/v1/login
```

---

## Header Management

### Automatic Headers

Relay automatically adds:

- `X-Forwarded-For` - Client IP
- `X-Forwarded-Proto` - `http` or `https`
- `X-Forwarded-Host` - Original host

### Custom Headers

```python
proxy = Relay(
    target_base_url="http://upstream:8000",
    extra_request_headers={
        "X-API-Key": "secret-key",
        "X-Service": "main-app"
    }
)
```

### Drop Headers

```python
proxy = Relay(
    target_base_url="http://upstream:8000",
    drop_request_headers=["x-internal-token"],
    drop_response_headers=["x-debug-info"]
)
```

### Allow-List Mode

```python
proxy = Relay(
    target_base_url="http://upstream:8000",
    allow_request_headers=["authorization", "content-type"],
    allow_response_headers=["content-type", "set-cookie"]
)
```

---

## Cookie Handling

### Drop Domain Attribute

```python
# Cookies bind to current host
proxy = Relay(
    target_base_url="http://auth:8000",
    rewrite_set_cookie_domain=lambda original: ""
)
```

### Rewrite Domain

```python
# Set specific domain
proxy = Relay(
    target_base_url="http://auth:8000",
    rewrite_set_cookie_domain=lambda original: "example.com"
)
```

### Preserve Domain

```python
# Keep original domain
proxy = Relay(
    target_base_url="http://auth:8000",
    rewrite_set_cookie_domain=None  # Default
)
```

---

## Retries & Timeouts

### Configure Retries

```python
proxy = Relay(
    target_base_url="http://upstream:8000",
    max_retries=3,
    retry_backoff_factor=0.5,  # 0.5s, 1s, 2s
    retry_statuses=(502, 503, 504),
    retry_exceptions=(httpx.ConnectError, httpx.ReadTimeout)
)
```

### Configure Timeouts

```python
import httpx

proxy = Relay(
    target_base_url="http://upstream:8000",
    timeout=httpx.Timeout(
        connect=5.0,   # Connection timeout
        read=30.0,     # Read timeout
        write=30.0,    # Write timeout
        pool=10.0      # Pool timeout
    )
)
```

---

## WebSocket Proxying

### Enable WebSocket Support

```python
# Install websockets
# pip install websockets

proxy = Relay(target_base_url="http://chat-service:8000")

app = Ravyn(
    routes=[Include("/ws", app=proxy)]
)

# ws://app/ws/room → ws://chat-service:8000/room
```

### How It Works

- Frames (text/binary) stream bidirectionally
- On upstream close: emits `1000` (normal closure)
- On error/timeout: emits `1011` (internal error)

---

## Error Handling

### HTTP Errors

| Error | Status Code | Cause |
|-------|-------------|-------|
| Connection Error | 502 Bad Gateway | Can't reach upstream |
| Timeout | 504 Gateway Timeout | Upstream too slow |
| Retryable Error | Original status | After retries exhausted |

### Logging

```python
import logging

logger = logging.getLogger("proxy")
proxy = Relay(
    target_base_url="http://upstream:8000",
    logger=logger
)

# Logs: retries, timeouts, errors
```

---

## Real-World Examples

### Example 1: Auth Service Proxy

```python
from ravyn import Ravyn, Include
from lilya.contrib.proxy.relay import Relay

# Proxy to dedicated auth service
auth_proxy = Relay(
    target_base_url="http://auth-service:8000",
    upstream_prefix="/",
    rewrite_set_cookie_domain=lambda _: "",  # Bind cookies to main app
    max_retries=2
)

app = Ravyn(
    routes=[
        Include("/auth", app=auth_proxy),
        # Your other routes...
    ],
    on_startup=[auth_proxy.startup],
    on_shutdown=[auth_proxy.shutdown]
)

# /auth/login → auth-service:8000/login
# /auth/logout → auth-service:8000/logout
```

### Example 2: Versioned API Proxy

```python
# Proxy to versioned upstream API
api_proxy = Relay(
    target_base_url="http://api-v2:8000",
    upstream_prefix="/api/v2"
)

app = Ravyn(
    routes=[
        Include("/api", app=api_proxy)
    ],
    on_startup=[api_proxy.startup],
    on_shutdown=[api_proxy.shutdown]
)

# /api/users → http://api-v2:8000/api/v2/users
```

### Example 3: Service-to-Service Auth

```python
import os

# Add service token to upstream requests
service_token = os.getenv("SERVICE_TOKEN")

proxy = Relay(
    target_base_url="http://internal:9000",
    extra_request_headers={
        "X-Service-Auth": service_token
    },
    drop_request_headers=["authorization"]  # Don't forward client auth
)
```

---

## Testing

### In-Memory Testing

```python
import httpx
from ravyn import Ravyn
from lilya.contrib.proxy.relay import Relay

# Create upstream app
upstream_app = Ravyn()

@upstream_app.get("/test")
def test_endpoint() -> dict:
    return {"message": "Hello from upstream"}

# Create proxy with in-memory transport
proxy = Relay(
    target_base_url="http://upstream",
    transport=httpx.ASGITransport(app=upstream_app)
)

# Test app
app = Ravyn(
    routes=[Include("/proxy", app=proxy)],
    on_startup=[proxy.startup],
    on_shutdown=[proxy.shutdown]
)

# Test with RavynTestClient
from ravyn import RavynTestClient

with RavynTestClient(app) as client:
    response = client.get("/proxy/test")
    assert response.json() == {"message": "Hello from upstream"}
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Forgot startup/shutdown

**Problem:** Proxy not initialized.

```python
# Wrong - no startup/shutdown
app = Ravyn(routes=[Include("/auth", app=proxy)])
```

**Solution:** Add lifecycle hooks:

```python
# Correct
app = Ravyn(
    routes=[Include("/auth", app=proxy)],
    on_startup=[proxy.startup],
    on_shutdown=[proxy.shutdown]
)
```

### Pitfall 2: Wrong Path Mapping

**Problem:** Paths don't match upstream.

```python
# Wrong - upstream expects /api/v1/users
proxy = Relay(
    target_base_url="http://api:8000",
    upstream_prefix="/"
)
# /users → http://api:8000/users (404!)
```

**Solution:** Set correct upstream_prefix:

```python
# Correct
proxy = Relay(
    target_base_url="http://api:8000",
    upstream_prefix="/api/v1"
)
# /users → http://api:8000/api/v1/users
```

### Pitfall 3: Cookie Domain Issues

**Problem:** Cookies not working across domains.

```python
# Wrong - upstream sets Domain=auth.example.com
# But app is at api.example.com
proxy = Relay(target_base_url="http://auth:8000")
```

**Solution:** Rewrite cookie domain:

```python
# Correct
proxy = Relay(
    target_base_url="http://auth:8000",
    rewrite_set_cookie_domain=lambda _: ""  # Bind to current host
)
```

---

## Best Practices

### 1. Use Lifecycle Hooks

```python
# Good - proper cleanup
app = Ravyn(
    routes=[Include("/proxy", app=proxy)],
    on_startup=[proxy.startup],
    on_shutdown=[proxy.shutdown]
)
```

### 2. Configure Timeouts

```python
# Good - explicit timeouts
proxy = Relay(
    target_base_url="http://upstream:8000",
    timeout=httpx.Timeout(connect=5.0, read=30.0)
)
```

### 3. Add Retries for Reliability

```python
# Good - handle transient failures
proxy = Relay(
    target_base_url="http://upstream:8000",
    max_retries=2,
    retry_backoff_factor=0.5
)
```

### 4. Use Environment Variables

```python
# Good - configurable
import os

proxy = Relay(
    target_base_url=os.getenv("UPSTREAM_URL", "http://localhost:8000")
)
```

---

## Configuration Reference

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_base_url` | str | Upstream service URL (required) |
| `upstream_prefix` | str | Path prefix for upstream (default: `/`) |
| `preserve_host` | bool | Keep client Host header (default: False) |
| `max_retries` | int | Number of retries (default: 0) |
| `timeout` | Timeout | Request timeout settings |
| `extra_request_headers` | dict | Headers to add to upstream requests |
| `rewrite_set_cookie_domain` | callable | Cookie domain rewriter |

See the [full Relay documentation](https://lilya.dev) for all parameters.

---

## Next Steps

Now that you understand Relay, explore:

- [Routing](./routing/routes.md) - Route configuration
- [Middleware](./middleware/index.md) - Request processing
- [Lifespan Events](./lifespan-events.md) - Application lifecycle
- [Testing](./testclient.md) - Test your proxy
