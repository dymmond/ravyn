from typing import Any

from lilya.introspection.__builder import (
    GraphBuilder as LilyaGraphBuilder,
    _resolve_middleware_class,
    _resolve_permission_class,
)
from lilya.introspection._graph import ApplicationGraph
from lilya.introspection._types import EdgeKind, GraphNode
from lilya.routing import Include as LilyaInclude

from ravyn.routing.router import Include


class GraphBuilder(LilyaGraphBuilder):
    """Extract a structural graph representation from a Ravyn application.

    This utility inspects a Ravyn application instance and builds a read-only
    `ApplicationGraph` depicting the app's composition:

    * Global middleware wrapping the application
    * Router dispatch relationships
    * Includes and their local middleware/permissions
    * Routes and their local middleware/permissions

    Notes:
        - The graph is *structural* only; it does not perform runtime matching.
        - Edge insertion order is preserved, and WRAPS chains are treated as linear.

    Attributes:
        _nodes: Accumulated nodes for the final graph.
        _edges: Accumulated edges for the final graph.
        _visited_apps: Set of visited app identities (via `id(...)`) to avoid cycles.
    """

    __slots__ = ("_nodes", "_edges", "_visited_apps")

    def build(self, app: Any, external: bool = False) -> ApplicationGraph:
        """Build an `ApplicationGraph` from a Ravyn application instance.

        The resulting graph contains:
            - One APPLICATION node
            - A linear WRAPS chain for global middleware
            - A DISPATCHES_TO edge to the router (if discovered)
            - Router traversal that attaches includes, routes, and their layers

        Args:
            app: Ravyn application instance.

        Returns:
            An `ApplicationGraph` representing the app's structure.
        """
        app_node = self._add_application(app)

        last_wrapped_node = app_node
        for middleware_like in getattr(app, "user_middleware", ()):
            middleware_class = _resolve_middleware_class(middleware_like)
            middleware_node = self._add_middleware(middleware_class)
            self._add_edge(last_wrapped_node, middleware_node, EdgeKind.WRAPS)
            last_wrapped_node = middleware_node

        router = self._resolve_router(app)
        if router is not None:
            router_node = self._add_router(router)
            self._add_edge(last_wrapped_node, router_node, EdgeKind.DISPATCHES_TO)
            self._traverse_router(router, router_node)

        return ApplicationGraph(nodes=self._nodes, edges=self._edges)

    def _traverse_router(self, router: Any, router_node: GraphNode) -> None:
        """Traverse a router-like object and attach includes and routes.

        For each entry in `router.routes`:
            * If `Include`:
                - Attach INCLUDE node via DISPATCHES_TO
                - Add include-level middleware then permissions (WRAPS chain)
                - If include has a child app, descend into its router
                - If include has raw `routes`, attach them under the include
            * Else:
                - Treat as a route path entry and attach its local layers

        Args:
            router: A router-like object with a `routes` attribute.
            router_node: The ROUTER node from which we dispatch.
        """
        from ravyn import ChildRavyn, Ravyn

        routes = getattr(router, "routes", None)
        if not routes:
            return

        for route_entry in routes:
            # Include?
            if isinstance(route_entry, (Include, LilyaInclude)):
                include_node = self._add_include(route_entry)
                self._add_edge(router_node, include_node, EdgeKind.DISPATCHES_TO)

                # Include-level middleware (declared outer -> inner)
                last_wrapped_node = include_node
                include_middleware = getattr(route_entry, "middleware", None) or ()
                for middleware_like in include_middleware:
                    middleware_class = _resolve_middleware_class(middleware_like)
                    middleware_node = self._add_middleware(middleware_class)
                    self._add_edge(last_wrapped_node, middleware_node, EdgeKind.WRAPS)
                    last_wrapped_node = middleware_node

                # Include-level permissions (declared order)
                include_permissions = getattr(route_entry, "permissions", None) or ()
                for permission_like in include_permissions:
                    permission_class = _resolve_permission_class(permission_like)
                    permission_node = self._add_permission(permission_class)
                    self._add_edge(last_wrapped_node, permission_node, EdgeKind.WRAPS)
                    last_wrapped_node = permission_node

                # Dive into child app, if present
                child_app = getattr(route_entry, "app", None)
                if (
                    isinstance(child_app, (Ravyn, ChildRavyn))
                    and id(child_app) not in self._visited_apps
                ):
                    self._visited_apps.add(id(child_app))
                    child_router = getattr(child_app, "router", None)
                    if child_router is not None:
                        child_router_node = self._add_router(child_router)
                        self._add_edge(
                            last_wrapped_node, child_router_node, EdgeKind.DISPATCHES_TO
                        )
                        self._traverse_router(child_router, child_router_node)

                # If entry has its own `routes` list (raw), walk those too.
                if child_app is None:
                    raw_routes = getattr(route_entry, "routes", None)
                    if raw_routes:
                        base_dispatch_node = include_node
                        for raw_route in raw_routes:
                            path_node = self._add_route(raw_route)
                            self._add_edge(base_dispatch_node, path_node, EdgeKind.DISPATCHES_TO)
                            self._attach_route_layers(raw_route, path_node)

                continue  # handled include

            route_node = self._add_route(route_entry)
            self._add_edge(router_node, route_node, EdgeKind.DISPATCHES_TO)
            self._attach_route_layers(route_entry, route_node)

    def _attach_route_layers(self, route_entry: Any, route_node: GraphNode) -> None:
        """Attach route-level middleware and permissions to a route node.

        Order of attachment:
            1. Route middleware (declared order; WRAPS chain)
            2. Route permissions (declared order; WRAPS chain)

        Args:
            route_entry: A route-like object with optional `middleware` / `permissions`.
            route_node: The route node to which layers will be attached.
        """
        # Route-level middleware (declared outer -> inner)
        last_wrapped_node = route_node
        route_middleware = getattr(route_entry, "middleware", None) or ()
        for middleware_like in route_middleware:
            middleware_class = _resolve_middleware_class(middleware_like)
            middleware_node = self._add_middleware(middleware_class)
            self._add_edge(last_wrapped_node, middleware_node, EdgeKind.WRAPS)
            last_wrapped_node = middleware_node

        # Route-level permissions (declared order)
        base_permissions = getattr(route_entry, "permissions", None) or []
        handler_permissions = getattr(route_entry.handler, "permissions", None) or []
        permission_classes = set()

        if handler_permissions:
            async_callables = list(handler_permissions.values())

            for call in async_callables:
                permission_classes.add(call.fn.args[0])

        route_permissions = base_permissions + list(permission_classes) or ()
        for permission_like in route_permissions:
            permission_class = _resolve_permission_class(permission_like)
            permission_node = self._add_permission(permission_class)
            self._add_edge(last_wrapped_node, permission_node, EdgeKind.WRAPS)
            last_wrapped_node = permission_node
