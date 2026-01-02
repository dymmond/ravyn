# About Ravyn

Ravyn is a modern, high-performance Python web framework designed for building scalable APIs and web applications with ease.

## What is Ravyn?

Ravyn is an **ASGI framework** that combines the power of async Python with developer-friendly features. Built on top of Lilya and leveraging Pydantic for data validation, Ravyn provides everything you need to build production-ready applications.

### Key Features

✨ **Async-First** - Built on ASGI for high concurrency

✨ **Type Safety** - Full type hints and Pydantic integration

✨ **Auto Documentation** - OpenAPI docs generated automatically

✨ **Dependency Injection** - Clean, testable code architecture

✨ **Flexible Routing** - Powerful routing with includes and gateways

✨ **Built-in Security** - Authentication, permissions, CSRF protection

✨ **Database Ready** - Edgy ORM and Mongoz support

✨ **Developer Experience** - Clear errors, great tooling

---

## Philosophy

### Simple Things Should Be Simple

```python
from ravyn import Ravyn, get

@get("/hello")
def hello(name: str) -> dict:
    return {"message": f"Hello, {name}!"}

app = Ravyn()
app.add_route(hello)
```

That's it. No boilerplate, no complexity.

### Complex Things Should Be Possible

When you need advanced features, Ravyn has you covered:

- Dependency injection
- Middleware layers
- Custom interceptors
- WebSocket support
- Background tasks
- Event-driven architecture

### Production Ready

Ravyn is designed for real-world applications:

- High performance
- Comprehensive testing
- Security best practices
- Scalable architecture
- Clear documentation

---

## Why Ravyn?

### Coming from Flask?

Ravyn gives you:

- **Async support** - Handle thousands of concurrent connections
- **Type safety** - Catch errors before runtime
- **Auto docs** - OpenAPI documentation out of the box
- **Modern patterns** - Dependency injection, middleware

### Coming from FastAPI?

Ravyn offers:

- **More flexibility** - Multiple routing patterns
- **Built-in features** - Permissions, interceptors, schedulers
- **Better organization** - Controllers, includes, child apps
- **Rich ecosystem** - Edgy ORM, Mongoz, extensions

### Coming from Django?

You'll appreciate:

- **Async performance** - Much faster for I/O operations
- **Simplicity** - Less magic, more explicit
- **Modern Python** - Async/await, type hints
- **Lightweight** - Start small, scale as needed

---

## Technology Stack

### Core Technologies

- **Python 3.8+** - Modern Python features
- **ASGI** - Async server gateway interface
- **Lilya** - ASGI toolkit foundation
- **Pydantic** - Data validation and serialization
- **Starlette** - Inspiration and compatibility

### Optional Integrations

- **Edgy** - Async ORM for SQL databases
- **Mongoz** - MongoDB ODM
- **Asyncz** - Task scheduling
- **MsgSpec** - High-performance serialization

---

## History

### The Esmerald Era

Ravyn was originally created as **Esmerald** by Tiago Silva. Esmerald grew into a powerful framework with a dedicated community and extensive features.

### The Rebrand

In 2025, Esmerald was rebranded to **Ravyn** to align with the growing Dymmond ecosystem. The rebrand brought:

- Fresh identity
- Clearer positioning
- Better ecosystem alignment
- Same great features

See the [Migration Guide](./migration.md) for upgrading from Esmerald.

---

## Design Principles

### 1. Developer Experience First

Every API is designed to be intuitive and discoverable. Clear error messages, comprehensive documentation, and helpful tooling.

### 2. Performance Matters

Ravyn is built for speed without sacrificing developer experience. Async-first architecture, efficient routing, and optimized internals.

### 3. Flexibility Over Magic

Explicit is better than implicit. Ravyn gives you powerful tools but lets you decide how to use them.

### 4. Production Ready

Security, testing, and scalability are built-in, not afterthoughts.

---

## Use Cases

### Perfect For:

- **REST APIs** - Build fast, scalable APIs

- **Microservices** - Lightweight and modular

- **Real-time Apps** - WebSocket support

- **Data Pipelines** - Async processing

- **API Gateways** - Proxy and routing

### Also Great For:

- GraphQL APIs
- Server-side rendering
- Background job processing
- Event-driven systems
- Legacy app integration (WSGI support)

---

## Community

### Get Involved

- **GitHub** - [Star us](https://github.com/dymmond/ravyn) ⭐
- **Discord** - [Join the community](https://discord.gg/eMrM9sWWvu) 💬
- **Discussions** - [Ask questions](https://github.com/dymmond/ravyn/discussions) - **Twitter** - [@apiesmerald](https://twitter.com/apiesmerald) 🐦

### Contribute

We welcome contributions of all kinds:

- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions

See our [Contributing Guide](./contributing.md) to get started.

---

## License

Ravyn is released under the **MIT License**. Free for personal and commercial use.

---

## Credits

### Creator

**Tiago Silva** ([@tarsil](https://github.com/tarsil))
- Creator and lead maintainer
- Vision and direction

### Built On

- **Lilya** - ASGI toolkit
- **Pydantic** - Data validation
- **Starlette** - Inspiration

### Community

Thank you to all our [contributors](./ravyn-people.md) who make Ravyn better every day.

---

## Next Steps

Ready to get started?

- [Quick Start](./index.md) - Build your first app
- [Tutorial](./index.md#quick-start) - Learn the basics
- [Documentation](https://ravyn.dev) - Explore all features
- [Examples](https://github.com/dymmond/ravyn/tree/main/examples) - See real code

---

**Welcome to Ravyn. Let's build something amazing together.** 