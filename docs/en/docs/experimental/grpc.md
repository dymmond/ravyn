# gRPC Integration in Ravyn (Experimental)

!!! Warning
    **Experimental Feature**

    The gRPC integration in Ravyn is currently experimental and subject to change.
    While it is stable enough for real use-cases, APIs may evolve based on community feedback.

---

## What is gRPC?

[gRPC](https://grpc.io/) is a high-performance, open-source remote procedure call (RPC) framework that enables communication between services in different languages. It uses Protocol Buffers (protobuf) as its interface definition language (IDL) and supports streaming, authentication, and more.

With gRPC, clients can call methods on a server as if they were local, enabling efficient and strongly typed communication.

## Benefits of gRPC

- **Language Agnostic**: Works across multiple languages like Python, Go, Java, and more.
- **High Performance**: Uses HTTP/2 under the hood and binary serialization (protobuf), resulting in low latency and high throughput.
- **Streaming**: Supports client-side, server-side, and bidirectional streaming.
- **Contract-First**: The API is defined using `.proto` files, making it clear and consistent.
- **Tooling Support**: Comes with a rich ecosystem of code generation and debugging tools.

## When Should You Use gRPC?

Use gRPC when:

- You need high performance and low latency between microservices.
- You want strongly-typed contracts for service interfaces.
- You need streaming capabilities.
- You’re working in a polyglot environment where services are written in different languages.
- Your system architecture is microservice-based or uses service mesh patterns.

Avoid gRPC when:

- You need to expose APIs directly to web browsers (gRPC is not well-supported in browsers without additional setup).
- You prefer human-readable JSON APIs.

## gRPC and Ravyn

Ravyn supports gRPC integration via the `GrpcGateway`, allowing services to:

- Run as gRPC servers using `grpc.aio`.
- Optionally expose HTTP endpoints that call into gRPC service methods.

This makes it easy to write business logic once and expose it over both HTTP and gRPC.

## GrpcGateway Overview

The `GrpcGateway` class bridges the world of gRPC and HTTP:

```python
GrpcGateway(
    path="/grpc",
    services=[GreeterService],
    expose_http=True,
    http_methods=["POST"],
    host="127.0.0.1",
    port=50051,
)
```

### Key Parameters:

- `path`: HTTP base path for the exposed routes.
- `services`: List of gRPC service classes (must implement `__add_to_server__`).
- `expose_http`: Whether to expose HTTP endpoints for service methods.
- `http_methods`: Restrict allowed HTTP methods. If none are provided, all methods are allowed.
- `is_secure`: Enables TLS if set to `True`.
- `server_credentials`: Credentials required for TLS if `is_secure=True`.

## How to Use GrpcGateway with Ravyn

### Step 1: Define the gRPC Protobuf File

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

Generate Python code using `grpcio-tools`:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. greeter.proto
```

### Step 2: Implement the gRPC Service in Python

To implement the gRPC service, create a class that inherits from `GreeterServicer` and implements the methods defined in
the protobuf file.

Ravyn will also use the `__add_to_server__` method to register the service with the gRPC server.

```python
from greeter_pb2 import HelloReply
from greeter_pb2_grpc import GreeterServicer, add_GreeterServicer_to_server
import grpc

class GreeterService(GreeterServicer):
    async def SayHello(self, request, context):
        if request.name == "error":
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid request")
            return HelloReply()

        return HelloReply(message=f"Hello, {request.name}!")

    @classmethod
    def __add_to_server__(cls, instance, server):
        add_GreeterServicer_to_server(instance, server)
```

### Step 3: Create the GrpcGateway

To create a gRPC gateway, instantiate `GrpcGateway` with the desired parameters:

```python
from ravyn.contrib.grpc import GrpcGateway

grpc_gateway = GrpcGateway(
    path="/grpc",
    services=[GreeterService],
    expose_http=True
)
```

### Step 4: Register HTTP Routes

To register the gRPC service with Ravyn, use the `register_grpc_http_routes` function:

```python
from ravyn import Ravyn
from ravyn.contrib.grpc.register import register_grpc_http_routes

app = Ravyn()

register_grpc_http_routes(app, [grpc_gateway])
```

### Step 5: Start the gRPC Server

Call `await grpc_gateway.startup()` during app startup and `await grpc_gateway.shutdown()` during shutdown.

## Dual Protocol: HTTP and gRPC

With `GrpcGateway`, you can:

- Call `/grpc/greeterservice/sayhello` using an HTTP POST with JSON payload:

```json
{
  "name": "World"
}
```

- Or use a gRPC client with the protobuf service definition.

### HTTP Equivalent Handler

The HTTP request is internally converted into a gRPC call using a simulated context. This enables one implementation
for both protocols.

## Unit Test Examples

### HTTP Test:

```python
response = http_client.post("/grpc/greeterservice/sayhello", json={"name": "World"})
assert response.status_code == 200
assert response.json() == {"message": "Hello, World!"}
```

### gRPC Test:

```python
async with aio.insecure_channel("127.0.0.1:50051") as channel:
    stub = GreeterStub(channel)
    message = await stub.SayHello("GRPC")
    assert message == "Hello, GRPC!"
```

### Error Test:

```python
response = http_client.post("/grpc/greeterservice/sayhello", json={"name": "error"})
assert response.status_code == 400
assert response.json()["detail"] == "Invalid request"
```

## Advanced Use Cases

- **Secure gRPC**:

```python
GrpcGateway(
    path="/secure",
    services=[SecureService],
    is_secure=True,
    server_credentials=grpc.ssl_server_credentials([...])
)
```

- **Limiting HTTP Methods**:

```python
GrpcGateway(
    path="/grpc",
    services=[MyService],
    http_methods=["POST"]
)
```

- **Custom Route Base Path**:

```python
register_grpc_http_routes(app, [gateway], base_path="/api")
```

---

## Summary

With the experimental `GrpcGateway`, Ravyn provides a powerful way to combine gRPC and HTTP APIs using a shared codebase and contract. This allows developers to:

- Serve both gRPC and HTTP clients.
- Build robust microservice interfaces.
- Leverage HTTP for debugging while running gRPC in production.

As this feature evolves, expect improvements in type safety, streaming support, and tooling integration.

Want more? Let us know what features or improvements you'd like to see for gRPC support in Ravyn!
