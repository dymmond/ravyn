# Ravyn Introspection Graph (`ApplicationGraph`)

* **What**: A structural, immutable graph of your Ravyn application nodes for apps, routers, routes, middleware, permissions, and includes; edges for relationships like `WRAPS` and `DISPATCHES_TO`. It's designed for **introspection**, **auditing**, and **tooling**, not routing or runtime matching.
* **Why**: To answer questions such as: *Which middlewares wrap my app and in what order?*; *What permissions apply to a route?*; *How do includes compose with child apps?*; *Can I export my architecture to JSON for visualization and CI checks?*
* **How**: Access `app.graph` and use the `ApplicationGraph` helpers (`middlewares()`, `routes()`, `permissions_for()`, `include_layers()`, `to_dict()`, `to_json()`, etc.). Ravyn lazily builds the graph the first time you access `app.graph`.

---

## Quickstart

```python
from ravyn import Ravyn

app = Ravyn()
print(app.graph)  # Builds once, then reuses the same immutable graph
```

The property `app.graph` constructs the graph on first access using `GraphBuilder().build(app)` and caches it on `app._graph`. Subsequent accesses return the same instance.

---

## Core Concepts

### Nodes & Kinds

The graph contains typed nodes, including:
- **APPLICATION** – The Ravyn app itself (exactly one).
- **ROUTER** – The dispatching router discovered from the app.
- **ROUTE** – Path-like entries (e.g., `Gateway`, `WebSocketGateway`) with metadata such as `path` and `methods`.
- **MIDDLEWARE** – Classes wrapping either the application, includes, or routes. Metadata keeps the class name.
- **PERMISSION** – Classes wrapping includes or routes; metadata keeps the class name.
- **INCLUDE** – Entries that compose child apps or raw routes under a prefix.

### Edges & Relationships

- **`WRAPS`** – ordered chain (outer -> inner) for middleware and permissions around an app, include, or route. The builder preserves declaration order. `ApplicationGraph` traverses the first `WRAPS` target in a linear fashion.
- **`DISPATCHES_TO`** – dispatch relationship (e.g., app -> router, router -> route/include, include -> child router or raw routes).

---

## Building the Graph (under the hood)

### Router discovery

`GraphBuilder` discovers a router-like object with the following preference order:
1. `app.router` if present and `None`.
2. Fallbacks: `app._router`, `app.routes` (if the object has a `routes` attribute).

### Global middleware chain

For each entry in `app.user_middleware`, the builder resolves the **class** (supports both raw classes and `DefineMiddleware`) and creates a `WRAPS` chain from the **APPLICATION** node to each **MIDDLEWARE** in declaration order.

### Router traversal

From the discovered **ROUTER**, the builder walks `router.routes` and:

- If the entry is an **INCLUDE**: adds the include, attaches its local **middlewares** then **permissions** as a `WRAPS` chain, and, if a **child app** is present, descends into its router (with cycle protection via visited app IDs). If the include has **raw routes** (no child app), those are attached under the include.
- Otherwise, treats the entry as a **ROUTE**, attaches it via `DISPATCHES_TO`, then attaches **route-level middlewares** followed by **permissions** using `WRAPS`.

### Determinism & safety

- Dangling edges (where source/target nodes aren't present) are ignored defensively during `ApplicationGraph` construction.
- Adjacency lists for outgoing/incoming edges are frozen. Edge insertion order is preserved.
- JSON serialization uses `_to_json_safe` which converts Enums to values, recurses into mappings, lists/tuples, and sorts sets for deterministic output.

---

## `ApplicationGraph` API Reference

### Properties

- `nodes: Mapping[str, GraphNode]` – All nodes by ID (read-only).
- `edges: tuple[GraphEdge, ...]` – All edges in insertion order (read-only).

### Queries & helpers
- `by_kind(kind: NodeKind) -> tuple[GraphNode, ...]` – Filter nodes by kind.
- `application() -> GraphNode` – Return the single **APPLICATION** node. Raises `RuntimeError` if missing or duplicated.
- `middlewares() -> tuple[GraphNode, ...]` – Global middlewares wrapping the application, outer->inner order, by traversing the linear `WRAPS` chain.
- `routes() -> tuple[GraphNode, ...]` – All route nodes.
- `route_by_path(path: str) -> GraphNode | None` – Structural lookup by exact `metadata['path']`. **Not** a runtime matcher.
- `permissions_for(route: GraphNode) -> tuple[GraphNode, ...]` – Permission chain wrapping a route (outer->inner). Requires a **ROUTE** node.
- `route_middlewares(route: GraphNode) -> tuple[GraphNode, ...]` – Middleware chain wrapping a route. Requires a **ROUTE** node.
- `includes() -> tuple[GraphNode, ...]` – All include nodes.
- `include_layers(include: GraphNode) -> {"middlewares": ..., "permissions": ...}` – Layers attached directly to an include. Requires an **INCLUDE** node.
- `explain(path: str) -> dict` – Structural explanation for a route that includes app `debug`, global middlewares (by class name), route `{path, methods}`, and route permissions (by class name).

### Export

- `to_dict() -> dict` – JSON-friendly dict with `nodes` and `edges`. Node `ref` is intentionally excluded. Metadata is normalized via `_to_json_safe`.
- `to_json(indent: int | None = 2, sort_keys: bool = False) -> str` – JSON string export. Pairs with your favorite visualization tools (Mermaid, Graphviz, etc.).

---

## Real‑World Scenarios & Recipes

### Audit global middleware order

```python
app = Ravyn(middleware=[MiddlewareA, MiddlewareB])
order = [n.metadata["class"] for n in app.graph.middlewares()]

assert order == ["MiddlewareA", "MiddlewareB"]
```

This preserves the declaration order (outer->inner) of global middlewares. '

### Inspect route methods & HEAD insertion

```python
app = Ravyn(routes=[Gateway("/r", handler=handler)])
route = app.graph.route_by_path("/r")

assert set(route.metadata["methods"]) == {"GET", "HEAD", "POST"}
```

The methods metadata captures the effective methods for the route, including implicit `HEAD`.

### Explain a route end‑to‑end

```python
app = Ravyn(middleware=[MiddlewareA], routes=[Gateway("/ping", handler=handler)])
info = app.graph.explain("/ping")
# info = {"app": {"debug": False}, "middlewares": ("MiddlewareA",),
#         "route": {"path": "/ping", "methods": ("GET", "HEAD")},
#         "permissions": ()}
```

`explain()` combines the app debug flag, global middleware classes, route `{path, methods}`, and route permissions into one compact dict.

### Verify route‑level middleware chain

```python
class RouteMW1: ...

class RouteMW2: ...

app = Ravyn(routes=[Gateway("/with-mw", handler=handler,
                        middleware=[DefineMiddleware(RouteMW1), DefineMiddleware(RouteMW2)])])

route = app.graph.route_by_path("/with-mw")
chain = app.graph.route_middlewares(route)

names = [n.metadata["class"] for n in chain]

assert names == ["RouteMW1", "RouteMW2"]
```

Route-level middlewares are attached as a linear `WRAPS` chain in the declared order.

### Check a route's permission chain

```python
class Allow(BasePermission): ...

class Deny(BasePermission): ...

app = Ravyn(routes=[Gateway("/users/{id}", handler=handler, permissions=[Allow, Deny])])
route = app.graph.route_by_path("/users/{id}")
perms = app.graph.permissions_for(route)

assert [p.metadata["class"] for p in perms] == ["Allow", "Deny"]
```

`permissions_for()` returns the ordered permission classes wrapping a specific route. '

### Compose includes with child apps

```python
async def inner():
    return "child"

child = ChildRavyn(routes=[Gateway("/inner", handler=inner)])
app = Ravyn(routes=[Include("/child", app=child)])

inc_nodes = app.graph.includes()
assert inc_nodes[0].metadata["path"] == "/child"

# Child routes appear exactly once under the include
paths = [r.metadata["path"] for r in app.graph.routes()]
assert paths.count("/inner") == 1
```

Includes attach, and child app routers are traversed safely with cycle protection; child routes aren't duplicated.

### Include with local layers (middlewares & permissions)

```python
class IncMW: ...

class IncAllow(BasePermission): ...

child = ChildRavyn(routes=[Gateway("/i", handler=handler)])
inc = Include("/inc", app=child,
              middleware=[DefineMiddleware(IncMW)],
              permissions=[DefinePermission(IncAllow)])

app = Ravyn(routes=[inc])
layers = app.graph.include_layers(app.graph.includes()[0])

assert [n.metadata["class"] for n in layers["middlewares"]] == ["IncMW"]
assert [n.metadata["class"] for n in layers["permissions"]] == ["IncAllow"]
```

Include-level layers are attached as a `WRAPS` chain (middlewares first, then permissions) in the declared order.

### WebSocket route presence

```python
app = Ravyn(routes=[WebSocketGateway("/ws", handler=ws_handler)])
ws_route = app.graph.route_by_path("/ws")

assert ws_route is not None
```

WebSocket paths are represented as **ROUTE** nodes and can be looked up by exact path.

### Export for tooling & CI

```python
from ravyn.serializers import serializer

# Dict export
data = app.graph.to_dict()
assert "nodes" in data and "edges" in data

# JSON export
json_data = app.graph.to_json()
loaded = serializer.loads(json_data)

assert loaded == app.graph.to_dict()
```

`to_dict()` returns a tooling-friendly shape (no `ref`), and `to_json()` round-trips cleanly with Ravyn's serializer. '

---

## Best Practices

- **Use `DefineMiddleware` / `DefinePermission`** when you need to pass constructor args. The builder resolves the class correctly even if wrappers vary.
- **Prefer exact path lookups** with `route_by_path()` for static analysis. Remember this is structural, not a runtime matcher.
- **Keep chains linear**: The traversal assumes a first `WRAPS` target per step and preserves insertion order.
- **Export JSON for visualization**: `_to_json_safe` guarantees deterministic ordering (e.g., sorted sets), which is ideal for diffs in PRs.

---

## Troubleshooting & FAQs

**Q: `ApplicationGraph has no APPLICATION node`?**
- Ensure you're building the graph from a valid `Ravyn` instance. The API raises if the node is missing or duplicated.

**Q: My route isn't found by `route_by_path()`**
- The lookup is an **exact** match against `metadata['path']`. Confirm the path string, including braces for parameters (e.g., `"/users/{id}"`).

**Q: Why do I see `HEAD` among methods?**
- Ravyn's routing may implicitly include `HEAD` for `GET` routes. The graph reflects effective methods from the route entry. Validate using tests as shown.

**Q: How do includes with child apps work?**
- The builder descends into the child app's router and marks visited apps to prevent cycles. Child routes are attached under the include correctly without duplication.

---

## Data Shapes

### Node (dict form)

```json
{
  "id": "route:8f3e...",
  "kind": "route",
  "metadata": {
    "path": "/users/{id}",
    "methods": ["GET", "HEAD"]
  }
}
```

Nodes are exported without runtime `ref`. Metadata is normalized to JSON-safe values.

### Edge (dict form)

```json
{
  "source": "router:...",
  "target": "route:...",
  "kind": "dispatches_to"
}
```

Edges preserve insertion order and reference valid node IDs.

---

## Complete Example

```python
from ravyn import get, websocket, Ravyn, ChildRavyn, Include, Gateway, WebSocketGateway, WebSocket
from ravyn.permissions import BasePermission
from lilya.middleware.base import DefineMiddleware
from lilya.permissions.base import DefinePermission

# Middlewares
class GlobalMW: ...
class RouteMW1: ...
class RouteMW2: ...
class IncMW: ...

# Permissions
class Allow(BasePermission): ...
class Deny(BasePermission): ...
class IncAllow(BasePermission): ...

@get()
async def handler() -> str:
    return "Hello"


@websocket()
async def ws_handler(socket: WebSocket):
    await socket.accept()
    await socket.close()


async def inner():
    return "child"

child = ChildRavyn(routes=[Gateway("/inner", handler=inner)])

app = Ravyn(
    middleware=[GlobalMW],
    routes=[
        Gateway("/users/{id}", handler=handler,
             middleware=[DefineMiddleware(RouteMW1), DefineMiddleware(RouteMW2)],
             permissions=[Allow, Deny]),
        Include("/inc", app=child,
                middleware=[DefineMiddleware(IncMW)],
                permissions=[DefinePermission(IncAllow)]),
        WebSocketGateway("/ws", handler=ws_handler),
    ],
)

g = app.graph
print(g.explain("/users/{id}"))
print(g.to_json())
```

This example exercises global middleware, route-level middleware and permissions, include-local layers with a child app, and a WebSocket route—all reflected in `ApplicationGraph` and exportable to JSON.
