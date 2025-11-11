import re
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Type, Union, cast

from lilya._internal._connection import Connection  # noqa
from lilya._internal._path import clean_path
from lilya._utils import is_class_and_subclass
from lilya.middleware import DefineMiddleware
from lilya.routing import Path as LilyaPath, WebSocketPath as LilyaWebSocketPath, compile_path
from lilya.types import Receive, Scope, Send
from typing_extensions import Annotated, Doc

from ravyn.permissions.utils import is_lilya_permission, is_ravyn_permission, wrap_permission
from ravyn.routing.controllers.base import BaseController
from ravyn.routing.core.base import Dispatcher
from ravyn.utils.helpers import clean_string

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.core.interceptors.types import Interceptor
    from ravyn.openapi.schemas.v3_1_0.security_scheme import SecurityScheme
    from ravyn.permissions.types import Permission
    from ravyn.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler
    from ravyn.types import Dependencies, ExceptionHandlerMap, Middleware, ParentType


class _GatewayCommon:
    """
    Internal mixin with the shared mechanics used by HTTP/WebSocket/Webhook gateways.
    Keeps configuration and compilation behavior identical while removing duplication.
    """

    @staticmethod
    def is_class_based(
        handler: "HTTPHandler | WebSocketHandler | ParentType | BaseController",
    ) -> bool:
        """Checks if the handler object or class is a subclass or instance of BaseController."""
        return bool(
            is_class_and_subclass(handler, BaseController) or isinstance(handler, BaseController)
        )

    @staticmethod
    def is_handler(handler: Callable[..., Any]) -> bool:
        """Checks if the callable is a standalone function/method and NOT a BaseController instance/subclass."""
        return bool(
            not is_class_and_subclass(handler, BaseController)
            and not isinstance(handler, BaseController)
        )

    def generate_operation_id(
        self,
        name: str | None,
        handler: "HTTPHandler | WebSocketHandler | BaseController",
    ) -> str:
        """
        Generates a unique, normalized operation ID suitable for OpenAPI specification.

        The ID is constructed from the handler's base name/class name and the route path,
        often appended with the primary HTTP method.

        Args:
            name: The explicit name given to the route (if any).
            handler: The handler object (HTTPHandler, WebSocketHandler, or BaseController instance).

        Returns:
            A cleaned string suitable for use as an OpenAPI operationId.
        """
        if self.is_class_based(getattr(handler, "parent", None) or handler):
            base: str = handler.parent.__class__.__name__.lower()
        else:
            base = name or getattr(handler, "name", "") or ""

        path_fmt: str = getattr(handler, "path_format", "") or ""

        # Remove non-word characters and combine base and path format
        operation_id: str = re.sub(r"\W", "_", f"{base}{path_fmt}")

        # Append the primary method (if available)
        methods: list[str] = list(
            getattr(handler, "methods", []) or getattr(handler, "http_methods", []) or []
        )
        if methods:
            operation_id = f"{operation_id}_{methods[0].lower()}"

        return operation_id

    @staticmethod
    def handle_middleware(handler: Any, base_middleware: list["Middleware"]) -> list["Middleware"]:
        """
        Normalizes a list of middleware classes/instances into a list of `DefineMiddleware` instances.

        Merges `handler`-defined middleware with `Gateway`-level middleware.

        Args:
            handler: The route handler object.
            base_middleware: The list of middleware defined at the Gateway level.

        Returns:
            A list of `Middleware` objects, all wrapped in `DefineMiddleware` if necessary.
        """
        _middleware: list["Middleware"] = []

        # Merge handler middleware if handler is not a Controller
        if not is_class_and_subclass(handler, BaseController) and not isinstance(
            handler, BaseController
        ):
            base_middleware += handler.middleware or []

        for middleware in base_middleware or []:
            if isinstance(middleware, DefineMiddleware):
                _middleware.append(middleware)
            else:
                _middleware.append(DefineMiddleware(middleware))  # type: ignore
        return _middleware

    @staticmethod
    def _instantiate_if_controller(
        handler: "Callable[..., Any] | BaseController",
        parent: "ParentType | None",
    ) -> Callable[..., Any]:
        """
        Instantiates a BaseController class handler and binds the parent router.

        Args:
            handler: The route handler (function, method, or controller class/instance).
            parent: The parent router/app object.

        Returns:
            The instantiated handler callable (either the original function or the controller instance).
        """
        if is_class_and_subclass(handler, BaseController):
            # Instantiate the controller class
            return cast(Callable[..., Any], handler(parent=parent))  # type: ignore
        return cast(Callable[..., Any], handler)

    @staticmethod
    def _resolve_path(
        base_path: str | None,
        handler_path: str,
        *,
        is_from_router: bool,
    ) -> str:
        """
        Combines the router's base path and the handler's path, then cleans the result.

        Args:
            base_path: The path inherited from the parent router.
            handler_path: The path segment defined on the handler itself.
            is_from_router: True if the handler path is implicitly just the base path.

        Returns:
            The clean, final path string.
        """
        path: str = base_path or "/"
        if is_from_router:
            return clean_path(path)
        return clean_path(path + handler_path)

    @staticmethod
    def _resolve_name(
        name: str | None,
        handler: Any,
    ) -> str:
        """
        Determines the final, canonical name of the route.

        Args:
            name: The explicit name provided to the Gateway/route.
            handler: The route handler object.

        Returns:
            The resolved name string.
        """
        if name:
            # Explicit name takes precedence and is combined with handler name if present
            if not isinstance(handler, BaseController) and getattr(handler, "name", None):
                return ":".join([name, handler.name])
            return name

        # Fallback: derive name from handler function or class name
        if not isinstance(handler, BaseController):
            base: str = getattr(handler, "name", None) or clean_string(handler.fn.__name__)
        else:
            base = clean_string(handler.__class__.__name__)
        return base

    def _prepare_middleware(
        self,
        handler: Any,
        middleware: list["Middleware"] | None,
    ) -> list["Middleware"]:
        """
        Prepares and normalizes the final list of middleware for the route.
        """
        return self.handle_middleware(handler=handler, base_middleware=middleware or [])

    @staticmethod
    def _apply_events(
        handler: Any,
        before_request: Sequence[Callable[[], Any]] | None,
        after_request: Sequence[Callable[[], Any]] | None,
    ) -> None:
        """
        Merges handler-defined `before_request` and `after_request` events with
        events passed to the Gateway.

        Gateway events are prepended (`before_request`) or appended (`after_request`).
        """
        if before_request:
            if getattr(handler, "before_request", None) is None:
                handler.before_request = []
            for before in before_request:
                handler.before_request.insert(0, before)

        if after_request:
            if getattr(handler, "after_request", None) is None:
                handler.after_request = []
            for after in after_request:
                handler.after_request.append(after)

    @staticmethod
    def _apply_interceptors(handler: Any, interceptors: Sequence["Interceptor"] | None) -> None:
        """
        Merges handler-defined interceptors with those passed to the Gateway.

        Gateway-level interceptors are prepended to ensure they run before handler-defined ones.
        """
        if not interceptors:
            return

        if not getattr(handler, "interceptors", None):
            handler.interceptors = list(interceptors)
            return

        # Prepend so Gateway-level interceptors run before handler-defined ones
        for interceptor in interceptors:
            handler.interceptors.insert(0, interceptor)

    @staticmethod
    def _prepare_permissions(
        handler: Any,
        permissions: Sequence["Permission"] | None,
    ) -> tuple[dict[int, "Middleware"], dict[int, "Permission"]]:
        """
        Prepares, wraps, and merges permissions into the handler's internal `lilya_permissions`
        (wrapped in middleware) and `permissions` (Ravyn native) dictionaries.

        Ensures that Lilya and Ravyn permissions are **not mixed** on the same Gateway.

        Args:
            handler: The route handler object.
            permissions: Permissions defined at the Gateway level.

        Returns:
            A tuple containing: (lilya_permissions_dict, ravyn_permissions_dict)

        Raises:
            AssertionError: If both Lilya-style and Ravyn-style permissions are simultaneously used.
        """
        base_permissions: Sequence["Permission"] = permissions or []

        lilya_wrapped: list["Middleware"] = [  # noqa
            wrap_permission(permission)
            for permission in base_permissions
            if is_lilya_permission(permission)
        ]
        lilya_permissions: dict[int, "Middleware"] = dict(enumerate(lilya_wrapped))

        if lilya_permissions:
            if not getattr(handler, "lilya_permissions", None):
                handler.lilya_permissions = lilya_permissions
            else:
                offset: int = len(lilya_permissions)
                existing: dict[int, "Middleware"] = {
                    idx + offset: perm
                    for idx, perm in enumerate(handler.lilya_permissions.values())
                }

                # New permissions run first (lower index)
                handler.lilya_permissions = {**lilya_permissions, **existing}
        else:
            lilya_permissions = {}

        # Ravyn Permissions (Native)
        ravyn_wrapped: dict[int, "Permission"] = {
            idx: wrap_permission(p)
            for idx, p in enumerate(base_permissions)
            if is_ravyn_permission(p)
        }

        if ravyn_wrapped:
            if not getattr(handler, "permissions", None):
                handler.permissions = ravyn_wrapped
            else:
                offset = len(ravyn_wrapped)
                existing = {
                    idx + offset: perm for idx, perm in enumerate(handler.permissions.values())
                }
                # New permissions run first (lower index)
                handler.permissions = {**ravyn_wrapped, **existing}
        else:
            ravyn_wrapped = {}

        # Cannot mix both simultaneously on the same Gateway definition
        assert not (ravyn_wrapped and lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

        return lilya_permissions, ravyn_wrapped

    @staticmethod
    def _compile(handler: Any, path: str) -> None:
        """
        Compiles the path string into a regular expression, path format string,
        and parameter convertors, storing them on the handler object.
        """
        handler.path_regex, handler.path_format, handler.param_convertors, _ = compile_path(path)


class Gateway(LilyaPath, Dispatcher, _GatewayCommon):
    """
    `Gateway` object class used by Ravyn routes.

    The Gateway act as a brigde between the router handlers and
    the main Ravyn routing system.

    Read more about [Gateway](https://ravyn.dev/routing/routes/#gateway) and
    how to use it.

    **Example**

    ```python
    from ravyn import Ravyn. get

    @get()
    async def home() -> str:
        return "Hello, World!"

    Gateway(path="/home", handler=home)
    ```
    """

    __slots__ = (
        "_interceptors",
        "path",
        "handler",
        "name",
        "include_in_schema",
        "parent",
        "dependencies",
        "middleware",
        "exception_handlers",
        "interceptors",
        "permissions",
        "deprecated",
        "tags",
        "operation_id",
        "before_request",
        "after_request",
        "lilya_permissions",
        "security",
        "methods",
        "response_class",
        "response_cookies",
        "response_headers",
    )

    def __init__(
        self,
        path: Annotated[
            Optional[str],
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                Gateway()
                ```

                **Example with parameters**

                ```python
                Gateway(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        *,
        handler: Annotated[
            Union["HTTPHandler", BaseController, Type[BaseController], Type["HTTPHandler"]],
            Doc(
                """
            An instance of [handler](https://ravyn.dev/routing/handlers/#http-handlers).
            """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
            ),
        ] = True,
        parent: Annotated[
            Optional["ParentType"],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://ravyn.dev/application/levels/).
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional["Dependencies"],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list["Middleware"]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of a Gateway will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence["Interceptor"]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence["Permission"]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional["ExceptionHandlerMap"],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[[], Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).

                **Example**

                ```python
                from edgy import Database, Registry

                from ravyn import Ravyn, Request, Gateway, get

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)

                async def create_user(request: Request):
                    # Logic to create the user
                    data = await request.json()
                    ...


                app = Ravyn(
                    routes=[Gateway("/create", handler=create_user)],
                    after_request=[database.disconnect],
                )
                ```
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[[], Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).

                **Example**

                ```python
                from edgy import Database, Registry

                from ravyn import Ravyn, Request, Gateway, get

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                async def create_user(request: Request):
                    # Logic to create the user
                    data = await request.json()
                    ...


                app = Ravyn(
                    routes=[Gateway("/create", handler=create_user)],
                    after_request=[database.disconnect],
                )
                ```
                """
            ),
        ] = None,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        is_from_router: Annotated[
            bool,
            Doc(
                """
                Used by the `.add_router()` function of the `Ravyn` class indicating if the
                Gateway is coming from a router.
                """
            ),
        ] = False,
        security: Annotated[
            Optional[Sequence["SecurityScheme"]],
            Doc(
                """
                Used by OpenAPI definition, the security must be compliant with the norms.
                Ravyn offers some out of the box solutions where this is implemented.

                The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

                The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

                For custom security objects, you **must** subclass
                `ravyn.openapi.security.base.HTTPBase` object.
                """
            ),
        ] = None,
        tags: Annotated[
            Optional[Sequence[str]],
            Doc(
                """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
                these tags on a Ravyn instance, means it will be added to every route even
                if those routes also contain tags.
                """
            ),
        ] = None,
        operation_id: Annotated[
            Optional[str],
            Doc(
                """
                Unique operation id that allows distinguishing the same handler in different Gateways.

                Used for OpenAPI purposes.
                """
            ),
        ] = None,
    ) -> None:
        raw_handler = handler
        handler = self._instantiate_if_controller(raw_handler, self)  # type: ignore

        self.path = self._resolve_path(
            path, getattr(handler, "path", "/"), is_from_router=is_from_router
        )
        self.methods = getattr(handler, "http_methods", None)
        resolved_name = self._resolve_name(name, handler)

        prepared_middleware = self._prepare_middleware(handler, middleware)
        lilya_permissions, _ = self._prepare_permissions(handler, permissions)

        super().__init__(
            path=self.path,
            handler=cast(Callable, handler),
            include_in_schema=include_in_schema,
            name=resolved_name,
            methods=self.methods,
            middleware=prepared_middleware,
            exception_handlers=exception_handlers,
            permissions=lilya_permissions or {},  # type: ignore
        )

        self._apply_events(handler, before_request, after_request)
        self._apply_interceptors(handler, interceptors)

        self.before_request = list(before_request or [])
        self.after_request = list(after_request or [])
        self.name = resolved_name
        self.handler = cast("Callable", handler)
        self.dependencies = dependencies or {}  # type: ignore
        self.interceptors = list(interceptors or [])
        self.deprecated = deprecated
        self.parent = parent
        self.security = security
        self.tags = list(tags or [])
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.operation_id = operation_id
        self.lilya_permissions = lilya_permissions or {}
        self.include_in_schema = include_in_schema

        self._compile(handler, self.path)

        if self.is_handler(self.handler):
            if self.operation_id or getattr(handler, "operation_id", None) is not None:
                generated = self.generate_operation_id(self.name or "", self.handler)  # type: ignore
                self.operation_id = f"{operation_id}_{generated}" if operation_id else generated
            elif not getattr(handler, "operation_id", None):
                handler.operation_id = self.generate_operation_id(self.name or "", self.handler)  # type: ignore

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interception of messages and calls from the API.
        """
        await self.app(scope, receive, send)


class WebSocketGateway(LilyaWebSocketPath, Dispatcher, _GatewayCommon):
    """
    `WebSocketGateway` object class used by Ravyn routes.

    The WebSocketGateway act as a brigde between the router handlers and
    the main Ravyn routing system.

    Read more about [WebSocketGateway](https://ravyn.dev/routing/routes/#websocketgateway) and
    how to use it.

    **Example**

    ```python
    from ravyn import Ravyn. websocket

    @websocket()
    async def world_socket(socket: Websocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()

    WebSocketGateway(path="/ws", handler=home)
    ```
    """

    __slots__ = (
        "_interceptors",
        "path",
        "handler",
        "name",
        "dependencies",
        "middleware",
        "exception_handlers",
        "interceptors",
        "permissions",
        "parent",
        "security",
        "tags",
        "before_request",
        "after_request",
        "lilya_permissions",
        "include_in_schema",
    )

    def __init__(
        self,
        path: Annotated[
            Optional[str],
            Doc(
                """
                Relative path of the `WebSocketGateway`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                WebSocketGateway()
                ```

                **Example with parameters**

                ```python
                WebSocketGateway(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        *,
        handler: Annotated[
            Union[
                "WebSocketHandler", BaseController, Type[BaseController], Type["WebSocketHandler"]
            ],
            Doc(
                """
            An instance of [handler](https://ravyn.dev/routing/handlers/#websocket-handler).
            """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        parent: Annotated[
            Optional["ParentType"],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://ravyn.dev/application/levels/).
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional["Dependencies"],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list["Middleware"]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of a Gateway will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence["Interceptor"]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence["Permission"]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional["ExceptionHandlerMap"],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[[], Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[[], Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).
                """
            ),
        ] = None,
        is_from_router: Annotated[
            bool,
            Doc(
                """
                Used by the `.add_router()` function of the `Ravyn` class indicating if the
                Gateway is coming from a router.
                """
            ),
        ] = False,
    ) -> None:
        raw_handler = handler
        handler = self._instantiate_if_controller(raw_handler, self)  # type: ignore

        self.path = self._resolve_path(
            path, getattr(handler, "path", "/"), is_from_router=is_from_router
        )
        resolved_name = self._resolve_name(name, handler)

        prepared_middleware = self._prepare_middleware(handler, middleware)

        lilya_permissions, _ = self._prepare_permissions(handler, permissions)

        super().__init__(
            path=self.path,
            handler=cast(Callable, handler),
            name=resolved_name,
            middleware=prepared_middleware,
            exception_handlers=exception_handlers,
            permissions=lilya_permissions or {},  # type: ignore
            before_request=before_request,
            after_request=after_request,
        )

        self._apply_events(handler, before_request, after_request)
        self._apply_interceptors(handler, interceptors)

        self.before_request = list(before_request or [])
        self.after_request = list(after_request or [])
        self.handler = cast("Callable", handler)
        self.dependencies = dependencies or {}  # type: ignore
        self.interceptors = list(interceptors or [])
        self.parent = parent
        self.name = resolved_name
        self.lilya_permissions = lilya_permissions or {}
        self.permissions = getattr(handler, "permissions", {}) or {}  # type: ignore
        self.include_in_schema = False  # websockets are excluded by default

        self._compile(handler, self.path)

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interception of messages and calls from the API.
        """
        await self.app(scope, receive, send)


class WebhookGateway(LilyaPath, Dispatcher, _GatewayCommon):
    """
    `WebhookGateway` object class used by Ravyn routes.

    The WebhookGateway act as a brigde between the webhook handlers and
    the main Ravyn routing system.

    Read more about [WebhookGateway](https://ravyn.dev/routing/webhooks/) and
    how to use it.

    !!! Note
        This is used for OpenAPI documentation purposes only.
    """

    __slots__ = (
        "_interceptors",
        "path",
        "handler",
        "name",
        "include_in_schema",
        "parent",
        "dependencies",
        "middleware",
        "exception_handlers",
        "interceptors",
        "permissions",
        "security",
        "tags",
        "before_request",
        "after_request",
        "deprecated",
        "methods",
        "response_class",
        "response_cookies",
        "response_headers",
    )

    def __init__(
        self,
        *,
        handler: Annotated[
            Union["WebhookHandler", BaseController, Type[BaseController], Type["WebhookHandler"]],
            Doc(
                """
                An instance of [handler](https://ravyn.dev/routing/webhooks/#handlers).
                """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the WebhookGateway.
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
            ),
        ] = True,
        parent: Annotated[
            Optional["ParentType"],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://ravyn.dev/application/levels/).
                """
            ),
        ] = None,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        security: Annotated[
            Optional[Sequence["SecurityScheme"]],
            Doc(
                """
                Used by OpenAPI definition, the security must be compliant with the norms.
                Ravyn offers some out of the box solutions where this is implemented.

                The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

                The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

                For custom security objects, you **must** subclass
                `ravyn.openapi.security.base.HTTPBase` object.
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[[], Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[[], Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).
                """
            ),
        ] = None,
        tags: Annotated[
            Optional[Sequence[str]],
            Doc(
                """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
                these tags on a Ravyn instance, means it will be added to every route even
                if those routes also contain tags.
                """
            ),
        ] = None,
    ) -> None:
        raw_handler = handler
        handler = self._instantiate_if_controller(raw_handler, self)  # type: ignore

        self.path = getattr(handler, "path", "/")
        self.methods = getattr(handler, "http_methods", None)
        resolved_name = self._resolve_name(name, handler)

        self.handler = cast("Callable", handler)
        self.include_in_schema = include_in_schema
        self.name = resolved_name
        self.dependencies = {}
        self.interceptors = []  # type: ignore
        self.permissions = []
        self.middleware = []
        self.exception_handlers = {}
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.deprecated = deprecated
        self.parent = parent
        self.security = security
        self.before_request = before_request
        self.after_request = after_request
        self.tags = list(tags or [])

        self._compile(handler, self.path)

        if self.is_handler(self.handler):
            self.handler.name = self.name
            if not getattr(handler, "operation_id", None):
                handler.operation_id = self.generate_operation_id(self.name, self.handler)  # type: ignore
