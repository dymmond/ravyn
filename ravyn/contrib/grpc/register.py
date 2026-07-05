from __future__ import annotations

from lilya.types import ASGIApp

from ravyn.contrib.grpc.gateway import GrpcGateway


def register_grpc_http_routes(
    app: ASGIApp, grpc_gateways: list[GrpcGateway], base_path: str | None = None
) -> None:
    """
    Registers HTTP routes corresponding to gRPC service methods to the Ravyn app.

    This function takes a gRPC gateway (GrpcGateway) instance that maps gRPC service
    methods to HTTP routes and registers these HTTP routes to the provided Ravyn app.

    The HTTP routes are dynamically created based on the service methods in the
    GrpcGateway instance, and the appropriate handler is attached for each HTTP method
    (GET, POST, PUT, DELETE, PATCH). The handler is a wrapper that invokes the
    corresponding gRPC method and returns the result as a JSON response.
    Supported methods include GET, QUERY, POST, PUT, DELETE, PATCH, OPTIONS, and TRACE.

    Args:
        app (ASGIApp): The Ravyn app instance where the HTTP routes will be registered.
        grpc_gateways (list[GrpcGateway]): The GrpcGateway list of instances that contains the gRPC services
                                    and their method mappings to HTTP routes.
        base_path (str, optional): The base path for the HTTP routes. Defaults to None.


    Yields:
        None: This function does not return any values, but it registers routes in-place.
    """
    if not base_path:
        base_path = "/"

    for grpc_gateway in grpc_gateways:
        for handler in grpc_gateway._register_http_endpoints():
            app.add_route(base_path, handler)
