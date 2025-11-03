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


class BaseMiddleware:
    def handle_middleware(
        self, handler: Any, base_middleware: list["Middleware"]
    ) -> list["Middleware"]:
        """
        Handles both types of middlewares for Gateway and WebSocketGateway
        """
        _middleware: list["Middleware"] = []

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


class GatewayUtil:
    def is_class_based(
        self, handler: Union["HTTPHandler", "WebSocketHandler", "ParentType"]
    ) -> bool:
        return bool(
            is_class_and_subclass(handler, BaseController) or isinstance(handler, BaseController)
        )

    def is_handler(self, handler: Callable[..., Any]) -> bool:
        return bool(
            not is_class_and_subclass(handler, BaseController)
            and not isinstance(handler, BaseController)
        )

    def generate_operation_id(
        self,
        name: Union[str, None],
        handler: Union["HTTPHandler", "WebSocketHandler", BaseController],
    ) -> str:
        """
        Generates an unique operation if for the handler.

        We need to be able to handle with edge cases when a view does not default a path like `/format` and a default name needs to be passed when its a class based view.
        """
        if self.is_class_based(handler.parent):
            operation_id = handler.parent.__class__.__name__.lower() + handler.path_format
        else:
            operation_id = name + handler.path_format

        operation_id = re.sub(r"\W", "_", operation_id)
        methods = list(handler.methods)

        assert handler.methods
        operation_id = f"{operation_id}_{methods[0].lower()}"
        return operation_id


class Gateway(LilyaPath, Dispatcher, BaseMiddleware, GatewayUtil):
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
                The name for the Gateway. The name can be reversed by `path_for()`.
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
        if not path:
            path = "/"
        if is_class_and_subclass(handler, BaseController):
            handler = handler(parent=self)

        if not is_from_router:
            self.path = clean_path(path + handler.path)
        else:
            self.path = clean_path(path)

        self.methods = getattr(handler, "http_methods", None)

        if not name:
            if not isinstance(handler, BaseController):
                name = handler.name or clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        else:
            route_name_list = [name]
            if not isinstance(handler, BaseController) and handler.name:
                route_name_list.append(handler.name)
                name = ":".join(route_name_list)

        # Handle middleware
        self.middleware = middleware or []
        self._middleware: list["Middleware"] = self.handle_middleware(
            handler=handler, base_middleware=self.middleware
        )

        self.__base_permissions__ = permissions or []

        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.__base_permissions__ or []
            if is_lilya_permission(permission)
        ]

        super().__init__(
            path=self.path,
            handler=cast(Callable, handler),
            include_in_schema=include_in_schema,
            name=name,
            methods=self.methods,
            middleware=self._middleware,
            exception_handlers=exception_handlers,
            permissions=self.__lilya_permissions__,  # type: ignore
        )
        """
        A "bridge" to a handler and router mapping functionality.
        Since the default Lilya Route handler does not understand the Ravyn handlers,
        the Gateway bridges both functionalities and adds an extra "flair" to be compliant with both class based views and decorated function views.
        """
        self.before_request = before_request if before_request is not None else []
        self.after_request = after_request if after_request is not None else []

        if self.before_request:
            if handler.before_request is None:
                handler.before_request = []

            for before in self.before_request:
                handler.before_request.insert(0, before)

        if self.after_request:
            if handler.after_request is None:
                handler.after_request = []

            for after in self.after_request:
                handler.after_request.append(after)

        self.name = name
        self.handler = cast("Callable", handler)
        self.dependencies = dependencies or {}  # type: ignore
        self.interceptors: Sequence["Interceptor"] = interceptors or []

        if self.interceptors:
            if not handler.interceptors:
                handler.interceptors = self.interceptors
            else:
                for interceptor in self.interceptors:
                    handler.interceptors.insert(0, interceptor)

        # Filter out the lilya unique permissions
        if self.__lilya_permissions__:
            self.lilya_permissions: Any = dict(enumerate(self.__lilya_permissions__))
            if not self.handler.lilya_permissions:
                self.handler.lilya_permissions = self.lilya_permissions
            else:
                handler_lilya_permissions = {
                    index + len(self.lilya_permissions): permission
                    for index, permission in enumerate(self.handler.lilya_permissions.values())
                }
                self.handler.lilya_permissions = {
                    **self.lilya_permissions,
                    **handler_lilya_permissions,
                }
        else:
            self.lilya_permissions = {}

        assert not (self.permissions and self.lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

        # Filter out the ravyn unique permissions
        if self.__base_permissions__:
            self.permissions: Any = {
                index: wrap_permission(permission)
                for index, permission in enumerate(permissions)
                if is_ravyn_permission(permission)
            }

            if not self.handler.permissions:
                self.handler.permissions = self.permissions
            else:
                handler_permissions = {
                    index + len(self.permissions): permission
                    for index, permission in enumerate(self.handler.permissions.values())
                }
                self.handler.permissions = {
                    **self.permissions,
                    **handler_permissions,
                }
        else:
            self.permissions = {}

        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.deprecated = deprecated
        self.parent = parent
        self.security = security
        self.tags = tags or []
        (handler.path_regex, handler.path_format, handler.param_convertors, _) = compile_path(
            self.path
        )
        self.operation_id = operation_id

        if self.is_handler(self.handler):
            if self.operation_id or handler.operation_id is not None:
                handler_id = self.generate_operation_id(
                    name=self.name or "",
                    handler=self.handler,  # type: ignore
                )
                self.operation_id = f"{operation_id}_{handler_id}" if operation_id else handler_id

            elif not handler.operation_id:
                handler.operation_id = self.generate_operation_id(
                    name=self.name or "",
                    handler=self.handler,  # type: ignore
                )

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interception of messages and calls from the API.
        """
        await self.app(scope, receive, send)


class WebSocketGateway(LilyaWebSocketPath, Dispatcher, BaseMiddleware):
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
                The name for the Gateway. The name can be reversed by `path_for()`.
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
        if not path:
            path = "/"
        if is_class_and_subclass(handler, BaseController):
            handler = handler(parent=self)
        if not is_from_router:
            self.path = clean_path(path + handler.path)
        else:
            self.path = clean_path(path)

        if not name:
            if not isinstance(handler, BaseController):
                name = handler.name or clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        else:
            route_name_list = [name]
            if not isinstance(handler, BaseController) and handler.name:
                route_name_list.append(handler.name)
                name = ":".join(route_name_list)

        # Handle middleware
        self.middleware = middleware or []
        self._middleware: list["Middleware"] = self.handle_middleware(
            handler=handler, base_middleware=self.middleware
        )
        self.is_middleware: bool = False

        self.__base_permissions__ = permissions or []
        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.__base_permissions__ or []
            if is_lilya_permission(permission)
        ]
        super().__init__(
            path=self.path,
            handler=cast("Callable", handler),
            name=name,
            middleware=self._middleware,
            exception_handlers=exception_handlers,
            permissions=self.__lilya_permissions__,  # type: ignore
            before_request=before_request,
            after_request=after_request,
        )
        """
        A "bridge" to a handler and router mapping functionality.
        Since the default Lilya Route handler does not understand the Ravyn handlers,
        the Gateway bridges both functionalities and adds an extra "flair" to be compliant with both class based views and decorated function views.
        """
        self.before_request = before_request if before_request is not None else []
        self.after_request = after_request if after_request is not None else []

        if self.before_request:
            if handler.before_request is None:
                handler.before_request = []

            for before in self.before_request:
                handler.before_request.insert(0, before)

        if self.after_request:
            if handler.after_request is None:
                handler.after_request = []

            for after in self.after_request:
                handler.after_request.append(after)

        self.handler = cast("Callable", handler)
        self.dependencies = dependencies or {}  # type: ignore
        self.interceptors = interceptors or []

        if self.interceptors:
            if not handler.interceptors:
                handler.interceptors = self.interceptors
            else:
                for interceptor in self.interceptors:
                    handler.interceptors.insert(0, interceptor)

        # Filter out the lilya unique permissions
        if self.__lilya_permissions__:
            self.lilya_permissions: Any = dict(enumerate(self.__lilya_permissions__))
            if not self.handler.lilya_permissions:
                self.handler.lilya_permissions = self.lilya_permissions
            else:
                handler_lilya_permissions = {
                    index + len(self.lilya_permissions): permission
                    for index, permission in enumerate(self.handler.lilya_permissions.values())
                }
                self.handler.lilya_permissions = {
                    **self.lilya_permissions,
                    **handler_lilya_permissions,
                }
        else:
            self.lilya_permissions = {}

        assert not (self.permissions and self.lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

        # Filter out the ravyn unique permissions
        if self.__base_permissions__:
            self.permissions: Any = {
                index: wrap_permission(permission)
                for index, permission in enumerate(permissions)
                if is_ravyn_permission(permission)
            }

            if not self.handler.permissions:
                self.handler.permissions = self.permissions
            else:
                handler_permissions = {
                    index + len(self.permissions): permission
                    for index, permission in enumerate(self.handler.permissions.values())
                }
                self.handler.permissions = {
                    **self.permissions,
                    **handler_permissions,
                }
        else:
            self.permissions = {}

        self.include_in_schema = False
        self.parent = parent
        (handler.path_regex, handler.path_format, handler.param_convertors, _) = compile_path(
            self.path
        )

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interception of messages and calls from the API.
        if self._middleware:
            self.is_middleware = True
        """
        await self.app(scope, receive, send)


class WebhookGateway(LilyaPath, Dispatcher, GatewayUtil):
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
        if is_class_and_subclass(handler, BaseController):
            handler = handler(parent=self)  # type: ignore

        self.path = handler.path
        self.methods = getattr(handler, "http_methods", None)

        if not name:
            if not isinstance(handler, BaseController):
                name = clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        self.handler = cast("Callable", handler)
        self.include_in_schema = include_in_schema

        self.name = name
        self.dependencies: Any = {}
        self.interceptors: Sequence["Interceptor"] = []
        self.permissions: Sequence["Permission"] = []  # type: ignore
        self.middleware: Any = []
        self.exception_handlers: Any = {}
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.deprecated = deprecated
        self.parent = parent
        self.security = security
        self.before_request = before_request
        self.after_request = after_request
        self.tags = tags or []
        (handler.path_regex, handler.path_format, handler.param_convertors, _) = compile_path(
            self.path
        )

        if self.is_handler(self.handler):
            self.handler.name = self.name

            if not handler.operation_id:
                handler.operation_id = self.generate_operation_id(
                    name=self.name,
                    handler=self.handler,  # type: ignore
                )
