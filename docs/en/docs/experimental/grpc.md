# gRPC Integration (Experimental)

Imagine you're building a city with different neighborhoods that need to talk to each other. REST APIs are like sending letters. simple and universal, but slower. gRPC is like having a direct phone line. faster, more efficient, and you know exactly what format the conversation will take.

Ravyn's gRPC integration lets you build high-performance microservices that speak both gRPC and HTTP.

!!! Warning
    **Experimental Feature**
    
    The gRPC integration in Ravyn is currently experimental and subject to change.
    While it is stable enough for real use-cases, APIs may evolve based on community feedback.

## What You'll Learn

- What gRPC is and when to use it
- Setting up gRPC services in Ravyn
- Exposing services via both gRPC and HTTP
- Testing gRPC endpoints
- Advanced gRPC features

## Quick Start

```python
from ravyn import Ravyn
from ravyn.contrib.grpc import GrpcGateway
from ravyn.contrib.grpc.register import register_grpc_http_routes

# Create gRPC gateway
grpc_gateway = GrpcGateway(
    path="/grpc",
    services=[GreeterService],
    expose_http=True
)

# Register with Ravyn
app = Ravyn()
register_grpc_http_routes(app, [grpc_gateway])
```

---

## What is gRPC?

[gRPC](https://grpc.io/) is a high-performance, open-source Remote Procedure Call (RPC) framework that enables efficient communication between services.

**Key Features:**
- **Fast** - Uses HTTP/2 and binary serialization (Protocol Buffers)
- **Strongly Typed** - Contract-first API design with `.proto` files
- **Streaming** - Supports client, server, and bidirectional streaming
- **Language Agnostic** - Works across Python, Go, Java, C++, and more
- **Production Ready** - Used by Google, Netflix, Square, and others

### How It Works

1. **Define** - Write a `.proto` file describing your service
2. **Generate** - Create code from the proto file
3. **Implement** - Write your service logic
4. **Deploy** - Run as a gRPC server

---

## When to Use gRPC

### Perfect For:

**Microservices** - High-performance service-to-service communication

**Real-time Systems** - Low latency requirements

**Streaming** - Server-sent events, live updates, file uploads

**Polyglot Environments** - Services in different languages

**Mobile Backends** - Efficient binary protocol saves bandwidth

### Not Ideal For:

**Browser APIs** - Limited browser support (requires grpc-web)

**Public APIs** - REST/JSON is more accessible

**Simple CRUD** - REST is simpler for basic operations

**Human-Readable APIs** - Binary format isn't debuggable without tools

---

## gRPC in Ravyn

Ravyn's `GrpcGateway` provides:

- **Dual Protocol** - Expose services via both gRPC and HTTP
- **Automatic Routing** - HTTP endpoints generated from proto definitions
- **Unified Implementation** - Write once, serve both protocols
- **TLS Support** - Secure gRPC connections
- **Error Handling** - Proper gRPC status codes

---

## Step-by-Step Guide

### Step 1: Define Your Service

Create a `.proto` file:

```proto
syntax = "proto3";

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply);
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

### Step 2: Generate Python Code

```bash
# Install grpcio-tools
pip install grpcio-tools

# Generate code
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. greeter.proto
```

This creates:
- `greeter_pb2.py` - Message classes
- `greeter_pb2_grpc.py` - Service classes

### Step 3: Implement the Service

```python
from greeter_pb2 import HelloReply
from greeter_pb2_grpc import GreeterServicer, add_GreeterServicer_to_server
import grpc

class GreeterService(GreeterServicer):
    async def SayHello(self, request, context):
        # Validate input
        if request.name == "error":
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid request")
            return HelloReply()
        
        # Return response
        return HelloReply(message=f"Hello, {request.name}!")
    
    @classmethod
    def __add_to_server__(cls, instance, server):
        """Required method for Ravyn integration"""
        add_GreeterServicer_to_server(instance, server)
```

### Step 4: Create the Gateway

```python
from ravyn.contrib.grpc import GrpcGateway

grpc_gateway = GrpcGateway(
    path="/grpc",
    services=[GreeterService],
    expose_http=True,
    host="127.0.0.1",
    port=50051
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `path` | str | HTTP base path | Required |
| `services` | list | gRPC service classes | Required |
| `expose_http` | bool | Enable HTTP endpoints | `False` |
| `http_methods` | list | Allowed HTTP methods | All |
| `host` | str | gRPC server host | `"127.0.0.1"` |
| `port` | int | gRPC server port | `50051` |
| `is_secure` | bool | Enable TLS | `False` |
| `server_credentials` | grpc.ServerCredentials | TLS credentials | `None` |

### Step 5: Register with Ravyn

```python
from ravyn import Ravyn
from ravyn.contrib.grpc.register import register_grpc_http_routes

app = Ravyn()

# Register gRPC routes
register_grpc_http_routes(app, [grpc_gateway])
```

### Step 6: Start the Server

```python
# In your lifespan or startup event
await grpc_gateway.startup()

# In your shutdown event
await grpc_gateway.shutdown()
```

---

## Dual Protocol: gRPC + HTTP

With `expose_http=True`, your service is accessible via both protocols:

### HTTP Request

```bash
curl -X POST http://localhost:8000/grpc/greeterservice/sayhello \
  -H "Content-Type: application/json" \
  -d '{"name": "World"}'
```

**Response:**
```json
{
  "message": "Hello, World!"
}
```

### gRPC Request

```python
import grpc
from greeter_pb2 import HelloRequest
from greeter_pb2_grpc import GreeterStub

async with grpc.aio.insecure_channel("127.0.0.1:50051") as channel:
    stub = GreeterStub(channel)
    response = await stub.SayHello(HelloRequest(name="World"))
    print(response.message)  # "Hello, World!"
```

---

## Testing Your Service

### HTTP Testing

```python
from ravyn.testclient import TestClient

client = TestClient(app)

# Test successful request
response = client.post("/grpc/greeterservice/sayhello", json={"name": "World"})
assert response.status_code == 200
assert response.json() == {"message": "Hello, World!"}

# Test error handling
response = client.post("/grpc/greeterservice/sayhello", json={"name": "error"})
assert response.status_code == 400
assert response.json()["detail"] == "Invalid request"
```

### gRPC Testing

```python
import grpc.aio as aio
from greeter_pb2 import HelloRequest
from greeter_pb2_grpc import GreeterStub

async def test_grpc():
    async with aio.insecure_channel("127.0.0.1:50051") as channel:
        stub = GreeterStub(channel)
        response = await stub.SayHello(HelloRequest(name="GRPC"))
        assert response.message == "Hello, GRPC!"
```

---

## Advanced Features

### Secure gRPC (TLS)

```python
import grpc

# Load TLS credentials
with open("server.key", "rb") as f:
    private_key = f.read()
with open("server.crt", "rb") as f:
    certificate_chain = f.read()

credentials = grpc.ssl_server_credentials([(private_key, certificate_chain)])

# Create secure gateway
grpc_gateway = GrpcGateway(
    path="/secure",
    services=[SecureService],
    is_secure=True,
    server_credentials=credentials
)
```

### Limiting HTTP Methods

```python
grpc_gateway = GrpcGateway(
    path="/grpc",
    services=[MyService],
    http_methods=["POST"]  # Only allow POST
)
```

### Custom Base Path

```python
register_grpc_http_routes(
    app,
    [grpc_gateway],
    base_path="/api/v1"  # Routes become /api/v1/grpc/...
)
```

### Multiple Services

```python
grpc_gateway = GrpcGateway(
    path="/grpc",
    services=[
        GreeterService,
        UserService,
        ProductService
    ],
    expose_http=True
)
```

---

## Common Pitfalls & Fixes

### Pitfall 1: Missing `__add_to_server__`

**Problem:** Service not registered.

**Solution:** Add the required method:

```python
@classmethod
def __add_to_server__(cls, instance, server):
    add_YourServicer_to_server(instance, server)
```

### Pitfall 2: Port Conflicts

**Problem:** gRPC server fails to start.

**Solution:** Use a different port:

```python
grpc_gateway = GrpcGateway(
    path="/grpc",
    services=[MyService],
    port=50052  # Different port
)
```

### Pitfall 3: Not Starting the Server

**Problem:** gRPC calls fail.

**Solution:** Call startup in lifespan:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    await grpc_gateway.startup()
    yield
    await grpc_gateway.shutdown()

app = Ravyn(lifespan=lifespan)
```

---

## Best Practices

### 1. Use Versioned Proto Files

```proto
syntax = "proto3";

package myapp.v1;

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
}
```

### 2. Handle Errors Properly

```python
async def GetUser(self, request, context):
    try:
        user = await get_user(request.id)
        return user
    except UserNotFound:
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return User()
```

### 3. Use Streaming for Large Data

```proto
service FileService {
  rpc DownloadFile (FileRequest) returns (stream FileChunk);
}
```

### 4. Monitor Performance

```python
import time

async def SayHello(self, request, context):
    start = time.time()
    result = await process_request(request)
    duration = time.time() - start
    logger.info(f"SayHello took {duration:.3f}s")
    return result
```

---

## Learn More

- [gRPC Official Documentation](https://grpc.io/docs/) - Complete gRPC guide
- [Protocol Buffers](https://developers.google.com/protocol-buffers) - Proto file syntax
- [grpcio Python](https://grpc.github.io/grpc/python/) - Python gRPC library
- [gRPC Best Practices](https://grpc.io/docs/guides/performance/) - Performance tips

---

## Feedback Welcome!

This is an experimental feature. We'd love to hear:

- How you're using gRPC in Ravyn
- What features you'd like to see
- Any issues or improvements

[Share your feedback →](https://github.com/dymmond/ravyn/discussions)

---

## Next Steps

- [Experimental Features](./index.md) - Other experimental features
- [Microservices](../application/index.md) - Build microservice architectures
- [Testing](../guides/more-advanced/02-testing.md) - Test your gRPC services
