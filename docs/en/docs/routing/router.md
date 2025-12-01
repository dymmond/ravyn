# Router

The Router is the main object that links the whole Ravyn to the [Gateway](./routes.md#gateway),
[WebSocketGateway](./routes.md#websocketgateway) and [handlers](./handlers.md).

## Router class

The router class is composed by many attributes that are, by default, populated within the application. However, Ravyn
also allows to add extra [custom routers](#custom-router), or alternatively, you can add a [ChildRavyn](#child-ravyn-application) app.

```python
{!> ../../../docs_src/routing/router/router_class.py!}
```

The main `Router` class is instantiated within the `Ravyn` application with the given routes and the application
starts.

!!! Info
    When adding another router to the application, [custom routers](#custom-router) and
    [ChildRavyn](#child-ravyn-application) are available as a way of doing it. One is more limited than
    the other, in this case, custom routers are more limited than `ChildRavyn`.

### Parameters

All the parameters and defaults are available in the [Router Reference](../references/routing/router.md).

!!! Warning
    The `response_class`, `response_cookies`, `response_headers`, `tags` and `include_in_schema` are not used
    when [add_route](#add_route) is used, only when using [ChildRavyn](#child-ravyn-application) app.

## Custom Router

Let's assume there are specific **customer** submodules inside a `customers` dedicated file.
There are three ways of separating the routes within the application, using [Include](./routes.md#include),
a [ChildRavyn](#child-ravyn-application) or by creating another router. Let's focus on the latter.

```python hl_lines="28-35" title="/application/apps/routers/customers.py"
{!> ../../../docs_src/routing/router/customers.py!}
```

Above, you created the `/application/apps/routers/customers.py` with all the information you need. It does not need
to be in one file, you can have a entirely separate package just to manage the customer, it is up to you.

Now you need to add the new custom router into the main application.

```python hl_lines="1 6" title="/application/app.py"
{!> ../../../docs_src/routing/router/app.py!}
```

This simple and your router is added to the main **Ravyn** application.

## Child Ravyn Application

What is this? We call it `ChildRavyn` but in fact is simply Ravyn but under a different name mostly for
visualisation purposes and for the sake of organisation.

!!! Check
    Using `ChildRavyn` or `Ravyn` is exactly the same thing, it is only if you prefer to create a
    `sub application` and you prefer to use a different class instead of `Ravyn` to make it more organised.

When organising routes, using the `Router` class itself can be a bit limiting because there are certain attributes
that when used within an instance or a `Router` to be passed to [add_route](#add_route) they will not be picked up.

Example:

* `response_class`
* `response_cookies`
* `response_headers`
* `tags`
* `include_in_schema`

This is not a limitation or a bug, in fact it is intentional as we want to preserve the integrity of the application.

### How does it work

Let's use the same example used in the [custom routers](#custom-router) with the customers specific routes and rules.

```python hl_lines="28-40" title="/application/apps/routers/customers.py"
{!> ../../../docs_src/routing/router/childravyn/customers.py!}
```

Since the `ChildRavyn` is a representation of an [Ravyn](../application/applications.md) class, we can pass
the otherwise limited parameters in the [custom router](#custom-router) and all the parameters available to
[Ravyn](../application/applications.md).

You can add as many `ChildRavyn` as you desire, there are no limits.

**Now in the main application**:

```python hl_lines="5" title="/application/app.py"
{!> ../../../docs_src/routing/router/childravyn/app.py!}
```

**Adding nested applications**

```python hl_lines="9 13-14" title="/application/app.py"
{!> ../../../docs_src/routing/router/childravyn/nested.py!}
```

The example above shows that you could even add the same application within nested includes, and for each
include, you can add specific unique [permissions](../permissions/index.md), [middlewares](../middleware/middleware.md),
[exception handlers](../exception-handlers.md) and [dependencies](../dependencies.md), which are available on each
instance of the `Include`. The options are endless.

!!! Note
    In terms of organisation, `ChildRavyn` has a clean approach to the isolation of responsabilities and allows
    treating every individual module separately and simply adding it in to the main application
    in the form of [Include](./routes.md#include).

!!! Tip
    Treat the `ChildRavyn` as an independent `Ravyn` instance.

!!! Check
    When adding a `ChildRavyn` or `Ravyn` application, don't forget to add the unique path to the base
    `Include`, this way you can assure the routes are found properly.

## Utils

The `Router` object has some available functionalities that can be useful.

### add_route()

```python
{!> ../../../docs_src/routing/router/add_route.py!}
```

#### Parameters

* **name** - Name of the route.
* **include_in_schema** - If route should be added to the OpenAPI Schema
* [handler](./handlers.md#http-handlers) - A HTTP handler.
* **permissions** - A list of [permissions](../permissions/index.md) to serve the application incoming
requests (HTTP and Websockets).
* **middleware** - A list of middleware to run for every request. The middlewares of a Include will be checked from
top-down.
* **interceptors** - A list of [interceptors](../interceptors.md)
or <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a>, as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.
* **exception_handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.

### add_websocket_route()

```python
{!> ../../../docs_src/routing/router/add_websocket_route.py!}
```

#### Parameters

* **name** - Name of the route.
* [Websocket handler](./handlers.md#websocket-handler) - A websocket handler.
* **permissions** - A list of [permissions](../permissions/index.md) to serve the application incoming
requests (HTTP and Websockets).
* **interceptors** - A list of [interceptors](../interceptors.md).
* **middleware** - A list of middleware to run for every request. The middlewares of a Include will be checked from
top-down.
or <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.
* **exception_handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.

### add_child_ravyn()

```python
{!> ../../../docs_src/routing/router/add_child_ravyn.py!}
```

### add_asgi_app()

The same as the [add_child_ravyn](#add_child_ravyn) but not restrained only to Ravyn or ChildRavyn. This means
you can call this helper and add any other ASGI application (FastAPI, Starlette, Litestar...) and it will fit automatically.

#### Parameters

* **path** - The path for the child ravyn.
* **child** - The [ChildRavyn](#child-ravyn-application) instance.
* **name** - Name of the route.
* [Websocket handler](./handlers.md#websocket-handler) - A websocket handler.
* **permissions** - A list of [permissions](../permissions/index.md) to serve the application incoming
requests (HTTP and Websockets).
* **interceptors** - A list of [interceptors](../interceptors.md).
* **middleware** - A list of middleware to run for every request. The middlewares of a Include will be checked from
top-down.
or <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.
* **exception_handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.
* **include_in_schema** - Boolean if this ChildRavyn should be included in the OpenAPI Schema.
* **deprecated** - Boolean if this ChildRavyn should be marked as deprecated.
