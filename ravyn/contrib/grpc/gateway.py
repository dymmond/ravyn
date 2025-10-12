from __future__ import annotations

from typing import Any

try:
    import grpc
except ImportError:
    raise ImportError(
        "You must have the official `grpcio-tools` installed to use this module."
    ) from None

from google.protobuf.json_format import MessageToDict
from grpc import aio
from lilya._internal._path import clean_path

from ravyn import HTTPException, Request, route
from ravyn.exceptions import ImproperlyMiddlewareConfigured
from ravyn.injector import Inject, Injects
from ravyn.responses import JSONResponse
from ravyn.utils.helpers import make_callable

# Allowed HTTP methods for endpoints.
HTTP_ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"]


class HTTPContext:
    """
    A minimal dummy gRPC context for HTTP calls.
    It implements only the methods required to satisfy the service signature.
    """

    def __init__(self) -> None:
        self._code = grpc.StatusCode.OK
        self._details = ""

    def set_code(self, code: grpc.StatusCode) -> None:
        self._code = code

    def set_details(self, details: str) -> None:
        self._details = details

    @property
    def code(self) -> grpc.StatusCode:
        return self._code

    @property
    def details(self) -> str:
        return self._details


class GrpcGateway:
    """
    GrpcGateway bridges gRPC services (using grpcio) and HTTP endpoints in an Ravyn app.
    It registers the gRPC services with a grpc.aio.Server and (optionally) exposes HTTP endpoints
    that call the service methods directly.

    Attributes:
        services (list[type]): list of gRPC service classes.
        grpc_server (aio.Server): The grpc.aio server instance.
        path (str): The base HTTP path used for generating endpoints.
        server_options (dict): Options such as host and port for the gRPC server.
        http_methods (list[str]): Allowed HTTP methods for the endpoints.
    """

    def __init__(
        self,
        path: str,
        services: list[type],
        expose_http: bool = True,
        http_methods: list[str] | None = None,
        is_secure: bool = False,
        server_credentials: grpc.ServerCredentials | None = None,
        **server_options: Any,
    ) -> None:
        """
        Initializes the GrpcGateway instance.

        Args:
            path (str): Base HTTP path (must start with '/').
            services (list[type]): list of gRPC service classes to expose.
            expose_http (bool): Whether to register HTTP endpoints that map to gRPC methods.
            http_methods (list[str] | None): If provided, limits the HTTP methods allowed.
            **server_options (Any): Additional options (e.g., host and port) for the gRPC server.

        Raises:
            AssertionError: If the provided path does not start with '/'.
        """
        assert path.startswith("/"), "Paths must start with '/'"

        self.path = clean_path(path)
        self.services = services
        # Create a grpc.aio.Server instance.
        self.grpc_server = aio.server()
        self.server_options = server_options
        self.http_methods = (
            [method.upper() for method in http_methods]
            if http_methods is not None
            else HTTP_ALLOWED_METHODS
        )

        # Register each service with the grpc.aio server.
        for service in services:
            instance = service()
            # We expect each service type to have a callable '__add_to_server__'
            # which registers the service with a grpc.aio.Server.
            add_fn = getattr(service, "__add_to_server__", None)
            if add_fn is None or not callable(add_fn):
                raise ValueError(
                    f"Service {service.__name__} must provide a '__add_to_server__' callable."
                )
            add_fn(instance, self.grpc_server)

        if expose_http:
            self._register_http_endpoints()

        # Set default host/port if not provided.
        if "host" not in self.server_options:
            self.server_options["host"] = "127.0.0.1"
        if "port" not in self.server_options:
            self.server_options["port"] = 50051

        self.is_secure = is_secure
        self.server_credentials = server_credentials

        if self.is_secure and not self.server_credentials:
            raise ImproperlyMiddlewareConfigured(
                "When `is_secure` is true, you must provide the `server_credentials`."
            )

    async def startup(self) -> None:
        """
        Starts the grpc.aio server asynchronously.
        """
        host = self.server_options["host"]
        port = self.server_options["port"]

        if not self.is_secure:
            self.grpc_server.add_insecure_port(f"{host}:{port}")
        else:
            self.grpc_server.add_secure_port(
                f"{host}:{port}", server_credentials=self.server_credentials
            )
        await self.grpc_server.start()

    async def shutdown(self) -> None:
        """
        Shuts down the grpc.aio server asynchronously.
        """
        await self.grpc_server.stop(0)

    def _register_http_endpoints(self) -> Any:
        """
        Registers HTTP endpoints for each gRPC service method.

        For each service in `self.services`, this method dynamically generates HTTP routes and associates
        them with the corresponding gRPC service method. It uses Ravyn decorators to define the HTTP
        methods (`GET`, `POST`, etc.), maps them to gRPC methods, and defines a handler that wraps the
        gRPC method with HTTP request handling.

        This method assumes that each service has callable methods that should be exposed as HTTP routes.
        """
        for service in self.services:
            service_instance = service()

            for method_name in dir(service_instance):
                if method_name.startswith("_"):
                    continue  # Skip private methods

                method = getattr(service_instance, method_name)
                if callable(method):
                    route_path = clean_path(
                        f"/{self.path}/{service.__name__.lower()}/{method_name.lower()}"
                    )
                    name = route_path.replace("/", "_").replace(".", "_").replace("__", "_")

                    if name.startswith("_"):
                        name = name[1:]

                    # Define a dependency for the service instance
                    def service_dependency() -> Any:
                        return service_instance  # noqa

                    callable_fn = make_callable(method_name)

                    @route(
                        path=route_path,
                        tags=["gRPC"],
                        methods=self.http_methods,
                        name=name,
                        dependencies={
                            "service": Inject(service_dependency),
                            "service_method": Inject(callable_fn),
                        },
                    )
                    async def http_wrapper(
                        request: Request,
                        service: Any = Injects(),
                        service_method: Any = Injects(),
                    ) -> Any:
                        """
                        HTTP handler that wraps the gRPC method. It receives HTTP requests, converts them into
                        data that can be processed by the gRPC method, and returns the result as an HTTP response.

                        Args:
                            request (Request): The HTTP request object containing input data.
                            service (Any): The gRPC service instance injected from dependencies.
                            service_method (Any): The gRPC method to be invoked, injected from dependencies.

                        Returns:
                            JSONResponse: The response that will be sent back to the client, wrapped as a JSON response.

                        Raises:
                            HTTPException: If an error occurs while invoking the gRPC method, this exception is raised
                            with the appropriate HTTP status code and error message.
                        """
                        method = getattr(service, service_method)

                        try:
                            data = await request.json()  # Expecting a dict.
                            http_context = HTTPContext()  # Create a dummy context.
                            response = await method(
                                data, http_context
                            )  # Call the gRPC method with (data, context).
                            # If response is a protobuf message, convert it to dict.
                            if http_context.code != grpc.StatusCode.OK:
                                raise HTTPException(
                                    status_code=self.__grpc_to_http_status(http_context.code),
                                    detail=http_context.details,
                                )

                            if hasattr(response, "SerializeToString"):
                                response = MessageToDict(
                                    response, preserving_proto_field_name=True
                                )
                            return JSONResponse(response)
                        except grpc.aio.AioRpcError as e:
                            raise HTTPException(
                                status_code=self.__grpc_to_http_status(e.code()),
                                detail=e.details(),
                            ) from e

                    # Yield the HTTP method, route, and handler for use by the framework
                    http_name = f"http_handler_{service_instance.__class__.__name__.lower()}_{method.__name__.lower()}"
                    http_wrapper.fn.__name__ = http_name
                    yield http_wrapper

    def __grpc_to_http_status(self, grpc_status: grpc.StatusCode) -> int:
        """
        Converts gRPC status codes to HTTP status codes.

        This method maps common gRPC status codes to their corresponding HTTP status codes. This mapping is used
        to ensure that gRPC errors are communicated effectively as HTTP responses.

        Args:
            grpc_status (Status): The gRPC status code to be converted to an HTTP status code.

        Returns:
            int: The corresponding HTTP status code. Defaults to 500 (Internal Server Error) if the status code
                 is not mapped.
        """
        mapping = {
            grpc.StatusCode.OK: 200,
            grpc.StatusCode.CANCELLED: 499,
            grpc.StatusCode.UNKNOWN: 500,
            grpc.StatusCode.INVALID_ARGUMENT: 400,
            grpc.StatusCode.DEADLINE_EXCEEDED: 504,
            grpc.StatusCode.NOT_FOUND: 404,
            grpc.StatusCode.ALREADY_EXISTS: 409,
            grpc.StatusCode.PERMISSION_DENIED: 403,
            grpc.StatusCode.UNAUTHENTICATED: 401,
            grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
            grpc.StatusCode.FAILED_PRECONDITION: 400,
            grpc.StatusCode.ABORTED: 409,
            grpc.StatusCode.OUT_OF_RANGE: 400,
            grpc.StatusCode.UNIMPLEMENTED: 501,
            grpc.StatusCode.INTERNAL: 500,
            grpc.StatusCode.UNAVAILABLE: 503,
            grpc.StatusCode.DATA_LOSS: 500,
        }
        return mapping.get(grpc_status, 500)  # Default to 500 if the status code is unknown
