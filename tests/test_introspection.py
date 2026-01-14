import sys

import pytest
from lilya.introspection import NodeKind
from lilya.middleware.base import DefineMiddleware
from lilya.protocols.permissions import PermissionProtocol
from lilya.routing import Include, Path
from lilya.serializers import serializer

from ravyn import Gateway, WebSocket, WebSocketGateway, get, route, websocket
from ravyn.applications import ChildRavyn, Ravyn
from ravyn.permissions import BasePermission


def test_graph_contains_application_node(test_client_factory):
    app = Ravyn()
    graph = app.graph
    apps = graph.by_kind(NodeKind.APPLICATION)

    assert len(apps) == 1
    assert apps[0].ref is app


class MiddlewareA:
    def __init__(self, app: Ravyn):
        self.app = app


class MiddlewareB:
    def __init__(self, app: Ravyn):
        self.app = app


def test_middleware_order_is_preserved(test_client_factory):
    app = Ravyn(middleware=[MiddlewareA, MiddlewareB])
    graph = app.graph

    names = [node.metadata["class"] for node in graph.by_kind(NodeKind.MIDDLEWARE)]
    assert names == ["TrustedHostMiddleware", "MiddlewareA", "MiddlewareB"]


class Allow(BasePermission):
    async def has_permission(self, *args, **kwargs):
        return True


class Deny(BasePermission):
    async def has_permission(self, *args, **kwargs):
        return True


@route(methods=["GET", "POST"])
async def handler() -> str:
    return "Hello"


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_route_permissions_chain(test_client_factory):
    app = Ravyn(
        routes=[
            Gateway(
                "/users/{id}",
                handler=handler,
                permissions=[Allow, Deny],
            )
        ]
    )

    graph = app.graph
    route = graph.route_by_path("/users/{id}")

    perms = graph.permissions_for(route)
    classes = [p.metadata["class"] for p in perms]

    assert classes == ["Allow", "Deny"]


def test_explain_returns_structural_data(test_client_factory):
    app = Ravyn(middleware=[MiddlewareA], routes=[Gateway("/ping", handler=handler)])

    info = app.graph.explain("/ping")

    assert info["route"]["path"] == "/ping"
    assert info["middlewares"] == (
        "TrustedHostMiddleware",
        "MiddlewareA",
    )


def test_graph_contains_router_node(test_client_factory):
    app = Ravyn(routes=[Gateway("/r", handler=handler)])
    graph = app.graph
    routers = graph.by_kind(NodeKind.ROUTER)

    assert len(routers) == 1


def test_route_metadata_methods_present(test_client_factory):
    app = Ravyn(
        routes=[
            Gateway(
                "/r",
                handler=handler,
            )
        ]
    )
    graph = app.graph
    route = graph.route_by_path("/r")

    assert route is not None
    assert set(route.metadata["methods"]) == {"GET", "HEAD", "POST"}


class RouteMW1:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        return await self.app(scope, receive, send)


class RouteMW2:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        return await self.app(scope, receive, send)


def test_route_level_middleware_chain_order(test_client_factory):
    app = Ravyn(
        routes=[
            Gateway(
                "/with-mw",
                handler=handler,
                middleware=[DefineMiddleware(RouteMW1), DefineMiddleware(RouteMW2)],
            )
        ]
    )
    g = app.graph
    r = g.route_by_path("/with-mw")

    chain = g.route_middlewares(r)
    names = [n.metadata["class"] for n in chain]

    assert names == ["RouteMW1", "RouteMW2"]


@get()
async def inner() -> str:
    return "child"


def test_include_and_nested_routes(test_client_factory):
    child = ChildRavyn(routes=[Gateway("/inner", handler=inner)])
    app = Ravyn(routes=[Include("/child", app=child)])

    g = app.graph

    # Include node present
    includes = g.includes()

    assert len(includes) == 1
    assert includes[0].metadata["path"] == "/child"

    # Child router present
    child_routes = [n for n in g.routes() if n.metadata["path"] == "/inner"]

    assert len(child_routes) == 1


class IncMW:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        return await self.app(scope, receive, send)


class IncAllow(PermissionProtocol):
    async def __call__(self, scope, receive, send):
        return await super().__call__(scope, receive, send)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python 3.11 or higher")
def test_include_layers_middleware_and_permissions(test_client_factory):
    child = ChildRavyn(routes=[Gateway("/i", handler=handler)])
    from lilya.middleware.base import DefineMiddleware
    from lilya.permissions.base import DefinePermission

    inc = Include(
        "/inc",
        app=child,
        middleware=[DefineMiddleware(IncMW)],
        permissions=[DefinePermission(IncAllow)],
    )

    app = Ravyn(routes=[inc])
    g = app.graph

    inc_nodes = g.includes()
    assert len(inc_nodes) == 1

    layers = g.include_layers(inc_nodes[0])

    inc_mw_names = [n.metadata["class"] for n in layers["middlewares"]]
    inc_perm_names = [n.metadata["class"] for n in layers["permissions"]]

    assert inc_mw_names == ["IncMW"]
    assert inc_perm_names == ["IncAllow"]


def test_include_with_child_does_not_duplicate_routes(test_client_factory):
    child = ChildRavyn(routes=[Path("/inner", inner)])
    app = Ravyn(routes=[Include("/child", app=child)])
    g = app.graph
    paths = [r.metadata["path"] for r in g.routes()]

    assert paths.count("/inner") == 1


@websocket()
async def ws_handler(socket: WebSocket) -> None:
    await socket.accept()
    await socket.close()


def test_websocket_route_presence(test_client_factory):
    app = Ravyn(routes=[WebSocketGateway("/ws", handler=ws_handler)])
    g = app.graph
    ws_route = g.route_by_path("/ws")

    assert ws_route is not None


def test_graph_to_dict_shape(test_client_factory):
    app = Ravyn(routes=[Gateway("/ping", handler=handler)])
    graph = app.graph

    data = graph.to_dict()

    assert "nodes" in data
    assert "edges" in data

    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


def test_graph_to_dict_route_metadata(test_client_factory):
    app = Ravyn(routes=[Gateway("/users/{id}", handler=handler)])
    graph = app.graph

    data = graph.to_dict()

    routes = [n for n in data["nodes"] if n["kind"] == "route"]

    assert len(routes) == 1
    assert routes[0]["metadata"]["path"] == "/users/{id}"


def test_graph_to_dict_edges_reference_nodes(test_client_factory):
    app = Ravyn(routes=[Gateway("/ping", handler=handler)])
    graph = app.graph

    data = graph.to_dict()

    node_ids = {n["id"] for n in data["nodes"]}

    for edge in data["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids


def test_graph_to_json_round_trip(test_client_factory):
    app = Ravyn(routes=[Gateway("/ping", handler=handler)])
    graph = app.graph

    json_data = graph.to_json()
    loaded = serializer.loads(json_data)

    assert loaded == graph.to_dict()
