# Learning and Examples

This section is dedicated to those interested in knowing some of the how tos and guides using Ravyn.

The documentation is extremely thorough but it is also interesting to understand how to use some of the compoents,
examples and practices using it.

## Introduction to Ravyn

Welcome to the Ravyn framework! This guide will walk you through everything you need to get started with Ravyn, a powerful and flexible Python web framework built on top of [Lylia](https://www.lilya.dev/) with modern features inspired by NestJS, FastAPI, and Angular.

## What is Ravyn?

Ravyn is a feature-rich, highly extensible ASGI web framework that provides a clean architectural structure for building maintainable APIs and web applications. It aims to offer more than just route declarations by including:

- **Controllers & Gateways**
- **Dependency injection system**
- **Interceptors & Middleware**
- **Multi-tenancy support**
- **Event-driven programming**
- **Built-in background tasks & caching**
- **gRPC Gateway support**
- **OpenAPI integration**

## Why Ravyn Over FastAPI or Django?

| Feature                        | Ravyn | FastAPI | Django |
|-------------------------------|----------|---------|--------|
| Dependency Injection (DI)     | | | |
| Controllers                   | | | |
| Interceptors                  | | | |
| Multi-tenancy support         | (Edgy) | | |
| Async/Await Native            | | | |
| Background Jobs Scheduler     | (Asyncz)| | |
| gRPC + HTTP Hybrid            | | | |

If you are looking for structured codebases, advanced routing, and full control over your application lifecycle, Ravyn is the way to go.

---

## Installation

```bash
pip install ravyn[all]  # Includes all optional features
```

If you plan to use **PostgreSQL**, **Redis**, or **Edgy**:

```bash
pip install postgres redis edgy[postgres]
```

---

## Hello, Ravyn

Let's build your first minimal Ravyn application.

```python
from ravyn import Ravyn, get

@get("/")
def home() -> dict:
    return {"message": "Hello, Ravyn!"}

app = Ravyn(routes=[home])
```

To run the app:
```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000` and you'll see:
```json
{"message": "Hello, Ravyn!"}
```

---

## OpenAPI and Documentation

Ravyn automatically generates OpenAPI documentation (Swagger and ReDoc).

- Swagger UI: `http://127.0.0.1:8000/docs/swagger`
- ReDoc: `http://127.0.0.1:8000/docs/redoc`
- Raw OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

To enable it explicitly:
```python
app = Ravyn(routes=[...], enable_openapi=True)
```

---

## What's Next?

Now that your Ravyn app is running, the next step is to learn how to structure routes and build a real API.

👉 Continue to [the next section](./beginner/02-building-your-first-api.md) to start building out real endpoints and working with query and path parameters.

---

Happy hacking with Ravyn! 💎
