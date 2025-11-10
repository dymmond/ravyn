from copy import copy
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Tuple, Union, cast

from lilya._internal._path import clean_path
from lilya.routing import compile_path
from lilya.types import Receive, Scope, Send
from typing_extensions import Annotated, Doc

from ravyn.permissions.utils import is_ravyn_permission, wrap_permission

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.core.interceptors.types import Interceptor
    from ravyn.core.transformers.model import TransformerModel
    from ravyn.openapi.schemas.v3_1_0.security_scheme import SecurityScheme
    from ravyn.permissions.types import Permission
    from ravyn.routing.gateways import Gateway, WebSocketGateway
    from ravyn.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler
    from ravyn.types import (
        Dependencies,
        ExceptionHandlerMap,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
    )


class BaseController:
    """
    `BaseController` class object acts as the base of all the object
    oriented views used by `Ravyn`.

    The `BaseController` contains all the available parameters that
    can be applied on a global level when subclassing it.

    **Example**

    ```python
    from ravyn.routing.views import BaseController


    class CustomView(BaseController):
        ...
    ```
    """

    __slots__ = (
        "__base_permissions__",
        "__lilya_permissions__",
        "dependencies",
        "exception_handlers",
        "interceptors",
        "permissions",
        "middleware",
        "parent",
        "path",
        "response_class",
        "response_cookies",
        "response_headers",
        "tags",
        "path_regex",
        "path_format",
        "param_convertors",
        "deprecated",
        "include_in_schema",
        "route_map",
        "operation_id",
        "methods",
        "security",
        "before_request",
        "after_request",
        "_filtered_handler_names",
    )

    path: Annotated[
        str,
        Doc(
            """
            Relative path of the `Gateway`.
            The path can contain parameters in a dictionary like format.
            """
        ),
    ]
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
            A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
            """
        ),
    ]
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
            A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
            """
        ),
    ]
    permissions: Annotated[
        Optional[list["Permission"]],
        Doc(
            """
            A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
            """
        ),
    ]
    interceptors: Annotated[
        Optional[Sequence["Interceptor"]],
        Doc(
            """
            A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
            """
        ),
    ]
    middleware: Annotated[
        Optional[list["Middleware"]],
        Doc(
            """
            A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
            """
        ),
    ]
    parent: Annotated[
        Optional[Union["Gateway", "WebSocketGateway"]],
        Doc(
            """
            Used internally by Ravyn to recognise and build the [application levels](https://ravyn.dev/application/levels/).

            !!! Tip
                Unless you know what are you doing, it is advisable not to touch this.
            """
        ),
    ]
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Default response class to be used within the
            Ravyn application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import APIView, JSONResponse


            class MyView(APIView):
                response_class = JSONResponse
            ```
            """
        ),
    ]
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import APIView
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            class MyView(APIView):
                response_cookies = response_cookies
            ```
            """
        ),
    ]
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from ravyn import APIView
            from ravyn.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            class MyView(APIView):
                response_headers = response_headers
            ```
            """
        ),
    ]
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
    ]
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
    ]
    tags: Annotated[
        Optional[list[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.
            """
        ),
    ]
    include_in_schema: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ]
    security: Annotated[
        Optional[list["SecurityScheme"]],
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
    ]
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag for indicating the deprecation of the Include and all of its routes and to display it in the OpenAPI documentation..
            """
        ),
    ]

    def __init__(self, parent: Union["Gateway", "WebSocketGateway"]) -> None:
        for key in self.__slots__:
            if not hasattr(self, key):
                setattr(self, key, None)

        self.path = clean_path(self.path or "/")
        self.path_regex, self.path_format, self.param_convertors, _ = compile_path(self.path)
        self.parent = parent
        self.route_map: dict[str, Tuple["HTTPHandler", "TransformerModel"]] = {}
        self.operation_id: Optional[str] = None
        self.methods: list[str] = []
        self._filtered_handler_names: Optional[list[str]] = None

        self.__base_permissions__ = self.permissions or []

        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.__base_permissions__ or []
            if not is_ravyn_permission(permission)
        ]

        self.__handle_base_permissions()
        self.__handle_lilya_permissions()

        # Filter out the ravyn unique permissions
        if self.__base_permissions__:
            self.permissions = cast(
                Any,
                {
                    index: wrap_permission(permission)
                    for index, permission in enumerate(self.__base_permissions__)
                    if is_ravyn_permission(permission)
                },
            )
        else:
            self.permissions = {}  # type: ignore

        if self.__lilya_permissions__:
            self.lilya_permissions: Any = {
                index: permission in self.__lilya_permissions__
                for index, permission in enumerate(self.__lilya_permissions__)
            }
        else:
            self.lilya_permissions = {}

        assert not (self.permissions and self.lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

    def __handle_base_permissions(self) -> None:
        """
        Handles the inheritance of permissions from base classes.
        This method iterates over the base classes of the current class and checks if they have a 'permissions' attribute.

        If the 'permissions' attribute exists and is not a MemberDescriptorType, and it contains one or more permissions,
        those permissions are inserted at the beginning of the 'permissions' and '__base_permissions__' lists of the current instance.
        """
        for base in self.__class__.__bases__:
            if hasattr(base, "permissions") and isinstance(
                getattr(base, "permissions", None), (list, tuple)
            ):
                unique_perms = [perm for perm in base.permissions if perm not in self.permissions]
                self.__base_permissions__[:0] = unique_perms

    def __handle_lilya_permissions(self) -> None:
        for base in self.__class__.__bases__:
            if hasattr(base, "lilya_permissions") and isinstance(
                getattr(base, "lilya_permissions", None), (list, tuple)
            ):
                unique_perms = [
                    perm for perm in base.lilya_permissions if perm not in self.lilya_permissions
                ]
                self.__lilya_permissions__[:0] = unique_perms

    def get_filtered_handler(self) -> list[str]:
        """
        Filters out the names of the functions that are not part of the handler itself.
        """
        # Fast path: reuse cached handler names
        if self._filtered_handler_names is not None:
            return self._filtered_handler_names

        from ravyn.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        filtered_handlers = [
            attr for attr in dir(self) if not attr.startswith("__") and not attr.endswith("__")
        ]
        route_handlers = []

        for handler_name in filtered_handlers:
            for base in self.__class__.__bases__:
                if handler_name not in dir(base) and isinstance(
                    getattr(self, handler_name),
                    (HTTPHandler, WebSocketHandler, WebhookHandler),
                ):
                    route_handlers.append(handler_name)
        self._filtered_handler_names = route_handlers
        return route_handlers

    def get_route_handlers(
        self,
    ) -> list[Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"]]:
        """A getter for the controller's route handlers that sets their parent.

        Returns:
            A list containing a copy of the route handlers defined inside the BaseController.
        """
        from ravyn.routing.router import WebSocketHandler

        route_handlers: list[Union[HTTPHandler, WebSocketHandler, WebhookHandler]] = []
        filtered_handlers = self.get_filtered_handler()

        for handler in filtered_handlers:
            source_route_handler = cast(
                Union["HTTPHandler", "WebSocketHandler"], getattr(self, handler)
            )
            route_handler = copy(source_route_handler)
            route_handler.parent = self

            if self.include_in_schema is not None and not isinstance(
                route_handler, WebSocketHandler
            ):  # pragma: no cover
                route_handler.include_in_schema = self.include_in_schema

            if self.middleware:
                self.get_route_middleware(route_handler)

            if self.exception_handlers:
                route_handler.exception_handlers = self.get_exception_handlers(route_handler)  # type: ignore

            if self.tags or []:  # pragma: no cover
                for tag in reversed(self.tags):
                    route_handler.tags.insert(0, tag)

            route_handlers.append(route_handler)

        return route_handlers

    def get_route_middleware(
        self,
        handler: Annotated[
            Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"],
            Doc(
                """
                The [handler](https://ravyn.dev/routing/handlers/) being checked against.
                """
            ),
        ],
    ) -> None:
        """
        Gets the list of extended middlewares for the handler starting from the last
        to the first by reversing the list
        """
        for middleware in reversed(self.middleware):
            handler.middleware.insert(0, middleware)

    def get_exception_handlers(
        self, handler: Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"]
    ) -> "ExceptionHandlerMap":
        """
        Gets the dict of extended exception handlers for the handler starting from the last
        to the first by reversing the list
        """
        exception_handlers = {**self.exception_handlers, **handler.exception_handlers}
        return cast("ExceptionHandlerMap", exception_handlers)

    async def handle_dispatch(
        self, scope: "Scope", receive: "Receive", send: "Send"
    ) -> None:  # pragma: no cover
        raise NotImplementedError(
            f"{self.__class__.__name__} object does not implement handle_dispatch()"
        )

    def create_signature_model(self, is_websocket: bool = False) -> None:  # pragma: no cover
        raise NotImplementedError(
            f"{self.__class__.__name__} object does not implement create_signature_model()"
        )

    def get_routes(
        self,
        path: Union[str, None] = None,
        middleware: Union[Sequence["Middleware"], list["Middleware"], None] = None,
        permissions: Union[Sequence["Permission"], Any, None] = None,
        interceptors: Union[Sequence["Interceptor"], list["Interceptor"], None] = None,
        exception_handlers: Union["ExceptionHandlerMap", None] = None,
        include_in_schema: Union[bool, None] = None,
        before_request: Union[Sequence[Callable[..., Any]], None] = None,
        after_request: Union[Sequence[Callable[..., Any]], None] = None,
    ) -> list[Any]:
        """
        Builds the routes and wraps them in a list containing the Gateway and WebSocketGateway.
        """
        from ravyn.routing.gateways import Gateway, WebSocketGateway
        from ravyn.routing.router import HTTPHandler

        if path is None:
            path = "/"

        route_handlers: list[Union[HTTPHandler, WebSocketHandler, WebhookHandler]] = (
            self.get_route_handlers()
        )
        handlers: list[Union[Gateway, WebSocketGateway]] = []

        for route_handler in route_handlers:
            route_path: Union[Gateway, WebSocketGateway]

            route_kwargs = {
                "path": path,
                "handler": route_handler,
                "middleware": middleware,
                "interceptors": interceptors,
                "permissions": (
                    permissions.values() if isinstance(permissions, dict) else permissions
                ),
                "exception_handlers": exception_handlers,
                "before_request": before_request,
                "after_request": after_request,
            }

            route_name_list = [
                self.parent.name,
            ]

            # Make sure the proper name is set for the route
            route_kwargs["name"] = ":".join(route_name_list)
            route_path = (
                Gateway(**route_kwargs)  # type: ignore
                if isinstance(route_handler, HTTPHandler)
                else WebSocketGateway(**route_kwargs)  # type: ignore
            )

            if isinstance(route_path, Gateway):
                if include_in_schema is None:
                    route_path.include_in_schema = (
                        route_handler.include_in_schema
                        if route_handler.include_in_schema is not None
                        else include_in_schema
                    )
                else:
                    route_path.include_in_schema = include_in_schema

            handlers.append(route_path)
        return handlers


class View(BaseController): ...
