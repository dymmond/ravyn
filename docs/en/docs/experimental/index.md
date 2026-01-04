# Experimental Features

Think of experimental features as a test kitchen where chefs try new recipes before adding them to the main menu. These features are stable enough to use, but we're still gathering feedback and refining them based on real-world usage.

Ravyn's experimental features give you early access to cutting-edge functionality while we perfect the APIs.

## What You'll Learn

- What experimental features are available
- How to use gRPC integration
- When to use experimental features
- How to provide feedback

## Quick Start

Try gRPC integration:

```python
from ravyn import Ravyn
from ravyn.contrib.grpc import GrpcGateway

# Create gRPC gateway
grpc_gateway = GrpcGateway(
    path="/grpc",
    services=[YourService],
    expose_http=True
)

app = Ravyn()
```

---

## Available Experimental Features

### gRPC Integration

**Status:** Experimental (Stable for use)

Integrate gRPC services with your Ravyn application, exposing them via both gRPC and HTTP.

**Use cases:**
- Microservices communication
- High-performance APIs
- Polyglot service architectures
- Streaming data

[Learn more about gRPC →](./grpc.md)

---

## What Does "Experimental" Mean?

### Stable Enough to Use

Experimental features are:
- Tested and working
- Safe for production use
- Documented with examples
- Actively maintained

### Subject to Change

However, they may:
- Have evolving APIs
- Receive breaking changes in minor versions
- Be promoted to stable or deprecated
- Change based on community feedback

---

## Should You Use Experimental Features?

### Use Them If:

- You need the functionality now
- You're comfortable with potential API changes
- You can provide feedback to improve them
- You understand the risks

### Wait If:

- You need absolute API stability
- You can't tolerate breaking changes
- The feature isn't critical to your project
- You prefer battle-tested solutions

---

## Providing Feedback

Your feedback helps shape these features! Let us know:

- What works well
- What's confusing or difficult
- What features are missing
- How you're using it in production

**How to provide feedback:**
- [GitHub Discussions](https://github.com/dymmond/ravyn/discussions)
- [GitHub Issues](https://github.com/dymmond/ravyn/issues)
- [Discord Community](https://discord.gg/eMrM9sWWvu)

---

## Feature Lifecycle

### 1. Experimental

- New feature, stable but evolving
- APIs may change
- Documented and tested

### 2. Stable

- Promoted from experimental
- API is locked
- Backward compatibility guaranteed

### 3. Deprecated

- Marked for removal
- Migration path provided
- Removed in future major version

---

## Learn More

- [gRPC Integration](./grpc.md) - Complete gRPC guide
- [Contributing](../contributing.md) - Help improve Ravyn
- [Release Notes](../release-notes.md) - Track feature changes

---

## Next Steps

- [Try gRPC Integration](./grpc.md) - Build high-performance APIs
- [Join Discussions](https://github.com/dymmond/ravyn/discussions) - Share your experience
- [Report Issues](https://github.com/dymmond/ravyn/issues) - Help us improve
