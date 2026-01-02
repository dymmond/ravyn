# Advanced Routing, Handlers, Controllers, and Include in Ravyn

Ravyn offers a highly flexible routing system, allowing you to structure your application in a modular way.
This guide covers essential concepts such as **routers**, **routes**, **handlers**, **API views**,
and especially **Include**, which is one of the most powerful features in Ravyn for modular routing and
reusability.

By combining these components, you can create scalable, organized applications that are easy to maintain.

---

## Routers in Ravyn

A **router** is a mechanism for grouping routes that share common functionality, such as applying middleware or
settings across related routes. Routers help modularize your application by encapsulating related routes into
distinct units.

### Example: Defining and Using Routers

```python
from ravyn import Ravyn, Router, Gateway, JSONResponse, get

# Create a router for user-related endpoints
user_router = Router()

@user_router.get("/profile/{user_id}")
async def get_user_profile(user_id: int) -> JSONResponse:
    return JSONResponse({"user_id": user_id, "message": "User profile fetched"})

# Create an application with the router
app = Ravyn()
app.add_router(user_router)
```

### Explanation:

- The `user_router` groups routes related to user profiles, making it easy to manage.
- The `@user_router.get("/profile/{user_id}")` decorator maps the `/profile/{user_id}` path to the `get_user_profile` function.
- The `app` includes the `user_router` and connects the handler via `Gateway`.

---

## Routes in Ravyn

Routes define the actual HTTP paths in your application. They are the endpoints that users or clients interact with.
In Ravyn, routes are associated with handler functions that process requests and return responses.

### Example: Defining Routes

```python
from ravyn import Ravyn, Gateway, JSONResponse, post

@post("/create")
async def create_user() -> JSONResponse:
    return JSONResponse({"message": "User created successfully"})

app = Ravyn(routes=[Gateway(handler=create_user)])
```

### Explanation:

- The `@post("/create")` decorator maps the `/create` path to the `create_user` handler.
- The `Gateway(handler=create_user)` connects the route to the handler, ensuring that requests to `/create` are processed
by the `create_user` function.

### Use Cases:

- Handling different HTTP methods (GET, POST, PUT, DELETE).
- Creating RESTful APIs for CRUD operations.
- Mapping dynamic routes with path parameters.

---

## Handlers in Ravyn

Handlers are functions or classes that process incoming requests. They take in request data
(like path parameters, body data, cookies, or headers) and return an appropriate response.

### Example: Basic Handler Function

```python
from ravyn import Ravyn, Gateway, JSONResponse, get

@get("/hello")
async def hello_world() -> JSONResponse:
    return JSONResponse({"message": "Hello, world!"})

app = Ravyn(routes=[Gateway(handler=hello_world)])
```

### Explanation:

- The `hello_world` function handles the `/hello` route and returns a `JSONResponse` containing a greeting message.
- The `@get("/hello")` decorator registers the route, while the `Gateway(handler=hello_world)` connects
the route to the handler.

---

## Controllers in Ravyn

Controllers or Controllers are class-based views that allow you to group multiple routes under one class.
This makes it easier to share logic and group related routes, improving the maintainability of your application.

### Example: API Controller with Multiple Routes

```python
from ravyn import Ravyn, Gateway, JSONResponse, post, get, Controller

class UserController(Controller):
    @get("/user/{user_id}")
    async def get_user(self, user_id: int) -> JSONResponse:
        return JSONResponse({"user_id": user_id, "message": "User details fetched"})

    @post("/create")
    async def create_user(self) -> JSONResponse:
        return JSONResponse({"message": "User created successfully"})

app = Ravyn(routes=[Gateway(handler=UserController)])
```

### Explanation:

- The `UserController` class groups related user routes under one class.
- Each method in the `UserController` class is mapped to a route, either using `@get` or `@post`.

---

## Include in Ravyn

One of the most powerful features of Ravyn is **Include**. This feature allows you to include other routes,
routers, API views within your application, include external apps (Django, Flask, FastAPI), effectively allowing for modular routing.
It helps in breaking down your application into smaller, manageable pieces.

### Example: Using `Include` to Modularize Routes

```python
from ravyn import Ravyn, Router, Gateway, Include, JSONResponse, get

@get("/profile/{user_id}")
async def get_user_profile(user_id: int) -> JSONResponse:
    return JSONResponse({"user_id": user_id, "message": "User profile fetched"})

# Include the user
app = Ravyn(routes=[Include(routes=[Gateway(handler=get_user_profile)])])
```

### Explanation:

- The `user_router` defines a group of routes for user-related endpoints.
- The `Include(routes=[Gateway(handler=get_user_profile)])` includes the `@get` into the main application, making its routes available.

### Use Cases for `Include`:

- Modularizing large applications by breaking them down into smaller routers.
- Reusing common routes across different parts of the application or in multiple projects.
- Improving maintainability by isolating concerns (e.g., user management, authentication).

Or if you want to include an external app, for example in Flask:

```python
from flask import Flask, escape, request

from ravyn import Ravyn, Gateway, Include, Request, get
from ravyn.middleware.wsgi import WSGIMiddleware

flask_app = Flask(__name__)

@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "Ravyn")
    return f"Hello, {escape(name)} from your Flask integrated!"

@get("/home/{name:str}")
async def home(request: Request) -> dict:
    name = request.path_params["name"]
    return {"name": escape(name)}

app = Ravyn(
    routes=[
        Gateway(handler=home),
        Include("/flask", WSGIMiddleware(flask_app)),
    ]
)
```

---

## Combining Routers, Routes, Handlers, Controllers, and Include

In Ravyn, you can combine **routers**, **routes**, **handlers** and **Controllers** to create
flexible and maintainable applications. You can use **Include** to modularize your application into
different components, allowing for better code organization.

### Example: Complex Application Using All Features

```python
from ravyn import Ravyn, Gateway, JSONResponse, Router, Controller, post, get, Controller
from ravyn.datastructures import Webhook

@user_router.get("/status")
async def status() -> JSONResponse:
    return JSONResponse({"status": "OK"})

@get("/include-status")
async def include_status() -> JSONResponse:
    return JSONResponse({"status": "OK"})

# Define an API view for users
class UserController(Controller):
    @get("/user/{user_id}")
    async def get_user(self, user_id: int) -> JSONResponse:
        return JSONResponse({"user_id": user_id, "message": "User found"})

    @post("/create")
    async def create_user(self) -> JSONResponse:
        return JSONResponse({"message": "User created successfully"})

# Create app with all components
app = Ravyn(
    routes=[
        Include('/internal', routes=[Gateway(handler=include_status)]),  # Include include_status
        Gateway(handler=UserController),  # Include API View
    ]
)
app.add_router(user_router)
```

### Explanation:

- The `user_router` groups related user routes (like `/status`).
- The `UserController` class-based view handles user-related routes.
- The `Include('/internal', routes=[Gateway(handler=include_status)])` modularizes other routes.

---

## Summary

- **Routers**: Group related routes and apply common middleware or settings.
- **Routes**: Define URL paths and map them to handler functions.
- **Handlers**: Functions that process incoming requests and return responses.
- **Controllers**: Class-based handlers for organizing and sharing logic across related routes.
- **Include**: Modularize routes, routers, or API views and include them in your main app for better organization and reusability.

Ravyn’s routing system allows for highly flexible and modular web application design. You can group related routes,
use class-based views for shared logic, and handle external webhooks with ease.

The `Include` feature is particularly useful for organizing your code and reusing common
routes across multiple applications.

---

## What's Next?

Now that you're comfortable structuring your app with routes and includes, it's time to learn about middlewares.

👉 Continue to [middlewares](06-middlewares.md) to handle things like logging, CORS, sessions, and more.
