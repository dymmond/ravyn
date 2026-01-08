<p align="center">
  <a href="https://ravyn.dev"><img src="https://res.cloudinary.com/dymmond/image/upload/v1759490296/ravyn/img/logo_pb3fis.png" alt='Ravyn'></a>
</p>

<p align="center">
    <em>A next-generation async Python framework for building high-performance APIs, microservices, and web applications with type safety and elegance. 🚀</em>
</p>

<p align="center">
<a href="https://github.com/dymmond/ravyn/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/dymmond/ravyn/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" alt="Test Suite">
</a>

<a href="https://pypi.org/project/ravyn" target="_blank">
    <img src="https://img.shields.io/pypi/v/ravyn?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypi.org/project/ravyn" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/ravyn.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: [https://ravyn.dev](https://www.ravyn.dev) 📚

**Source Code**: [https://github.com/dymmond/ravyn](https://github.com/dymmond/ravyn)

**The official supported version is always the latest released**.

!!! Info "Coming from Esmerald?"
    If you came looking for Esmerald, you are in the right place. Esmerald was rebranded to Ravyn. All features remain and continue to grow.

---

## Quick Start

Get your first Ravyn API running in minutes.

### Installation

```shell
pip install ravyn[standard]
```

This installs Ravyn with recommended extras. You'll also need an ASGI server:

```shell
pip install uvicorn
```

### Your First API

Create a file called `app.py`:

```python
from ravyn import Ravyn, get, JSONResponse

app = Ravyn()

@app.get("/")
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Ravyn!"})

@app.get("/hello/{name}")
def greet(name: str) -> JSONResponse:
    return JSONResponse({"message": f"Hello, {name}!"})
```

### Run It

```shell
uvicorn app:app --reload
```

Visit [http://127.0.0.1:8000/hello/World](http://127.0.0.1:8000/hello/World) and you'll see:

```json
{"message": "Hello, World!"}
```

### Explore the Docs

Ravyn automatically generates interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/docs/swagger](http://127.0.0.1:8000/docs/swagger)
- **ReDoc**: [http://127.0.0.1:8000/docs/redoc](http://127.0.0.1:8000/docs/redoc)
- **Stoplight Elements**: [http://127.0.0.1:8000/docs/elements](http://127.0.0.1:8000/docs/elements)

**Congratulations!** 🎉 You've built your first Ravyn API.

---

## Why Ravyn?

Ravyn combines the best ideas from FastAPI, Django, Flask, and NestJS into a framework designed for real-world applications. from prototypes to enterprise systems.

### Key Features

- **⚡ Fast**: Built on [Lilya](https://lilya.dev/) and [Pydantic](https://pydantic-docs.helpmanual.io/), with async-first design
- **🎯 Type-Safe**: Full Python 3.10+ type hints for better IDE support and fewer bugs
- **🧩 Flexible**: Choose OOP (controllers) or functional style. or mix both
- **🔋 Batteries Included**: Dependency injection, middleware, permissions, schedulers, and more
- **Database Ready**: Native support for [Edgy ORM][edgy_orm] and [Mongoz ODM][mongoz_odm]
- **🧪 Testable**: Built-in test client for easy testing
- **📖 Auto-Documented**: OpenAPI/Swagger docs generated automatically

---

## Core Concepts

### Routes and Handlers

Ravyn uses **decorators** or **Gateway objects** to define routes.

!!! warning "Critical Requirements"
    1. **At least one route is required**: An empty `Ravyn()` application does nothing. You must define routes to handle requests.
    2. **Return types are important**: Always specify return type hints (e.g., `-> dict`, `-> JSONResponse`). Ravyn uses these to:
        - Serialize your data correctly
        - Generate accurate API documentation
        - Validate responses

#### Decorator Style (Recommended for Simple APIs)

```python
from ravyn import Ravyn, get, post

app = Ravyn()

@app.get("/users")
def list_users() -> dict:
    return {"users": ["Alice", "Bob"]}

@app.post("/users")
def create_user(name: str) -> dict:
    return {"created": name}
```

#### Gateway Style (Recommended for Larger Apps)

```python
from ravyn import Ravyn, Gateway, get

@get()
def list_users() -> dict:
    return {"users": ["Alice", "Bob"]}

app = Ravyn(
    routes=[
        Gateway("/users", handler=list_users)
    ]
)
```

!!! tip
    Use decorators for quick prototypes. Use Gateway + Include for scalable, organized applications.

### Dependency Injection

Inject dependencies at any level. from application-wide to individual routes.

```python
from ravyn import Ravyn, Gateway, Inject, Injects, get

def get_database():
    return {"db": "connected"}

@get()
def users(db: dict = Injects()) -> dict:
    return {"users": [], "db_status": db}

app = Ravyn(
    routes=[Gateway("/users", handler=users)],
    dependencies={"db": Inject(get_database)}
)
```

Learn more in the [Dependencies](./dependencies.md) guide.

### Settings Management

Ravyn uses environment-based settings inspired by Django.

```python
from ravyn import RavynSettings
from ravyn.conf.enums import EnvironmentType

class DevelopmentSettings(RavynSettings):
    app_name: str = "My App (Dev)"
    environment: str = EnvironmentType.DEVELOPMENT
    debug: bool = True
```

Load your settings via environment variable:

```shell
# MacOS/Linux
RAVYN_SETTINGS_MODULE='myapp.settings.DevelopmentSettings' uvicorn app:app --reload

# Windows
$env:RAVYN_SETTINGS_MODULE="myapp.settings.DevelopmentSettings"; uvicorn app:app --reload
```

If no `RAVYN_SETTINGS_MODULE` is set, Ravyn uses sensible defaults.

Learn more in [Application Settings](./application/settings.md).

---

## Organizing Larger Applications

As your app grows, use **Include** to organize routes into modules.

### Project Structure

```
myapp/
├── app.py
├── urls.py
└── accounts/
    ├── controllers.py
    └── urls.py
```

### accounts/controllers.py

```python
from ravyn import get, post

@get()
def list_accounts() -> dict:
    return {"accounts": []}

@post()
def create_account(name: str) -> dict:
    return {"created": name}
```

### accounts/urls.py

```python
from ravyn import Gateway
from .controllers import list_accounts, create_account

route_patterns = [
    Gateway("/", handler=list_accounts),
    Gateway("/create", handler=create_account),
]
```

### urls.py

```python
from ravyn import Include

route_patterns = [
    Include("/accounts", namespace="myapp.accounts.urls"),
]
```

### app.py

```python
from ravyn import Ravyn

app = Ravyn(routes="myapp.urls")
```

Now your routes are organized:

- `GET /accounts/` → list_accounts
- `POST /accounts/create` → create_account

Learn more in [Routing](./routing/routes.md).

---

## Additional Installation Options

### Testing Support

```shell
pip install ravyn[test]
```

Includes the `RavynTestClient` for testing your application.

### JWT Support

```shell
pip install ravyn[jwt]
```

For JWT-based authentication.

### Scheduler Support

```shell
pip install ravyn[schedulers]
```

For background task scheduling.

### Interactive Shell

```shell
pip install ravyn[ipython]  # IPython shell
pip install ravyn[ptpython]  # ptpython shell
```

Learn more about the [shell](./directives/shell.md).

---

## Start a Project with Scaffolding

!!! warning
    This is for users comfortable with Python project structures. If you're new to Ravyn, continue learning the basics first.

Generate a **simple** project scaffold:

```shell
ravyn createproject myproject --simple
```

Or generate a **complete** scaffold (recommended for enterprise apps):

```shell
ravyn createproject myproject
```

This creates a ready-to-go structure with:

- Pre-configured application
- Sample routes
- Test setup

Learn more in [Directives](./directives/directives.md).

---

## Next Steps

Now that you have Ravyn running, explore these topics:

### Essential Concepts
- [Dependencies](./dependencies.md) - Master dependency injection
- [Routing](./routing/routes.md) - Advanced routing patterns
- [Responses](./responses.md) - Different response types
- [Testing](./testclient.md) - Test your application

### Building Features
- [Middleware](./middleware/index.md) - Add request/response processing
- [Permissions](./permissions/index.md) - Secure your endpoints
- [Database Integration](./databases/edgy/motivation.md) - Connect to databases
- [Background Tasks](./background-tasks.md) - Run async tasks

### Going to Production
- [Settings](./application/settings.md) - Environment configuration
- [Deployment](./deployment/intro.md) - Deploy your application
- [OpenAPI Configuration](./configurations/openapi/config.md) - Customize API docs

---

## Requirements

- **Python 3.10+**

Ravyn is built on:

- <a href="https://lilya.dev/" class="external-link" target="_blank">Lilya</a> - High-performance ASGI framework
- <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a> - Data validation

---

## About Ravyn

### History

Ravyn is the evolution of Esmerald, rebranded to align with a growing ecosystem of tools. **Esmerald continues to exist** for its specific use cases, while Ravyn represents the next generation with improved consistency and future-focused design.

### Motivation

While frameworks like FastAPI, Flask, and Django solve 99% of common problems, they sometimes leave gaps in structure and business logic organization. Ravyn was built to fill those gaps while keeping the best features from:

- **FastAPI** - API design and automatic documentation
- **Django** - Permissions and settings management
- **Flask** - Simplicity and flexibility
- **NestJS** - Controllers and dependency injection
- **Starlite** - Transformers and signature models

Learn more in [About Ravyn](./about.md).

---

## Join the Community

Ravyn is an open source project and we love your contribution!

<p align="center">
    <a href="https://github.com/dymmond/ravyn" target="_blank">
        <img src="https://img.shields.io/github/stars/dymmond/ravyn?style=social" alt="GitHub stars">
    </a>
    <a href="https://discord.gg/eMrM9sWWvu" target="_blank">
        <img src="https://img.shields.io/discord/1018998928332570634?logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2" alt="Discord">
    </a>
    <a href="https://twitter.com/ravyn_framework" target="_blank">
        <img src="https://img.shields.io/twitter/follow/ravyn_framework?style=social" alt="Twitter">
    </a>
</p>

- **Star us on GitHub** to show your support! ⭐️
- **Join our Discord** to ask questions and share your projects.
- **Follow us on X (Twitter)** for the latest updates.

## Sponsors

Currently there are no sponsors of Ravyn but you can financially help and support the author though
[GitHub sponsors](https://github.com/sponsors/tarsil) and become a **Special one** or a **Legend**.

### Powered by

Worth mentioning who is helping us.

**JetBrains**

[![JetBrains logo.](https://resources.jetbrains.com/storage/products/company/brand/logos/jetbrains.svg)](https://jb.gg/OpenSourceSupport)

[edgy_orm]: https://ravyn.dev/databases/edgy/motivation
[mongoz_odm]: https://ravyn.dev/databases/mongoz/motivation

[edgy_orm]: ./databases/edgy/motivation.md
[mongoz_odm]: ./databases/mongoz/motivation.md
