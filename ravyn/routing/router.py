from __future__ import annotations

import inspect
import types
import warnings
from enum import IntEnum
from inspect import Signature
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from lilya import status
from lilya._internal._connection import Connection
from lilya._internal._path import clean_path
from lilya.concurrency import run_in_threadpool
from lilya.datastructures import URLPath
from lilya.middleware import DefineMiddleware
from lilya.permissions import DefinePermission
from lilya.responses import JSONResponse, Response as LilyaResponse
from lilya.routing import (
    BasePath as LilyaBasePath,
    Host,
    Include as LilyaInclude,
    NoMatchFound,
    Path as LilyaPath,
    Router as LilyaRouter,
    WebSocketPath as LilyaWebSocketPath,
    compile_path,
)
from lilya.types import ASGIApp, Lifespan, Receive, Scope, Send
from monkay import load
from typing_extensions import Annotated, Doc

from ravyn.conf import settings
from ravyn.core.datastructures import File, Redirect
from ravyn.core.interceptors.types import Interceptor
from ravyn.core.transformers.model import TransformerModel, get_signature
from ravyn.core.transformers.signature import SignatureModel
from ravyn.core.urls import include
from ravyn.exceptions import (
    ImproperlyConfigured,
    MethodNotAllowed,
    NotFound,
    OpenAPIException,
    ValidationErrorException,
)
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.openapi.utils import is_status_code_allowed
from ravyn.params import Form
from ravyn.permissions.utils import is_ravyn_permission, wrap_permission
from ravyn.requests import Request
from ravyn.responses import Response
from ravyn.routing.controllers.base import BaseController
from ravyn.routing.core._internal import OpenAPIFieldInfoMixin
from ravyn.routing.core.base import Dispatcher
from ravyn.routing.gateways import Gateway, WebhookGateway, WebSocketGateway
from ravyn.typing import Void, VoidType
from ravyn.utils.constants import (
    DATA,
    PAYLOAD,
    REDIRECT_STATUS_CODES,
    REQUEST,
    SOCKET,
)
from ravyn.utils.enums import HttpMethod, MediaType
from ravyn.utils.helpers import (
    is_async_callable,
    is_class_and_subclass,
    is_optional_union,
)
from ravyn.websockets import WebSocket, WebSocketClose

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.applications import Application, Ravyn
    from ravyn.core.interceptors.interceptor import RavynInterceptor
    from ravyn.openapi.schemas.v3_1_0.security_scheme import SecurityScheme
    from ravyn.permissions.types import Permission
    from ravyn.types import (
        APIGateHandler,
        BackgroundTaskType,
        Dependencies,
        ExceptionHandlerMap,
        LifeSpanHandler,
        Middleware,
        ParentType,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
        RouteParent,
    )
    from ravyn.typing import AnyCallable


class BaseRouter(Dispatcher, LilyaRouter):
    __slots__ = (
        "redirect_slashes",
        "default",
        "name",
        "dependencies",
        "exception_handlers",
        "interceptors",
        "permissions",
        "middleware",
        "response_class",
        "response_cookies",
        "response_headers",
        "parent",
        "tags",
        "deprecated",
        "security",
        "on_startup",
        "on_shutdown",
        "root_path",
        "path",
        "_app",
        "ravyn_lifespan",
        "routing",
        "before_request",
        "after_request",
        "_interceptors",
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
                Include()
                ```

                **Example with parameters**

                ```python
                Include(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        app: Annotated[
            Optional[Application],
            Doc(
                """
                A `Router` instance always expects an `Ravyn` instance
                as an app or any subclass of Ravyn, like a `ChildRavyn`.

                **Example**

                ```python
                from ravyn import ChildRavyn, Router

                Router('/child', app=ChildRavyn(...))
                ```
                """
            ),
        ] = None,
        parent: Annotated[
            Optional[ParentType],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://ravyn.dev/application/levels/).
                """
            ),
        ] = None,
        on_startup: Annotated[
            Optional[list[LifeSpanHandler]],
            Doc(
                """
                A `list` of events that are trigger upon the application
                starts.

                Read more about the [events](https://ravyn.dev/lifespan-events/).

                **Example**

                ```python
                from pydantic import BaseModel
                from saffier import Database, Registry

                from ravyn import Router, Gateway, post

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                class User(BaseModel):
                    name: str
                    email: str
                    password: str
                    retype_password: str


                @post("/create", tags=["user"], description="Creates a new user in the database")
                async def create_user(data: User) -> None:
                    # Logic to create the user
                    ...


                app = Router(
                    routes=[Gateway(handler=create_user)],
                    on_startup=[database.connect],
                )
                ```
                """
            ),
        ] = None,
        on_shutdown: Annotated[
            Optional[list[LifeSpanHandler]],
            Doc(
                """
                A `list` of events that are trigger upon the application
                shuts down.

                Read more about the [events](https://ravyn.dev/lifespan-events/).

                **Example**

                ```python
                from pydantic import BaseModel
                from saffier import Database, Registry

                from ravyn import Router, Gateway, post

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                class User(BaseModel):
                    name: str
                    email: str
                    password: str
                    retype_password: str


                @post("/create", tags=["user"], description="Creates a new user in the database")
                async def create_user(data: User) -> None:
                    # Logic to create the user
                    ...


                app = Router(
                    routes=[Gateway(handler=create_user)],
                    on_shutdown=[database.disconnect],
                )
                ```
                """
            ),
        ] = None,
        redirect_slashes: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag indicating if the redirect slashes are enabled for the
                routes or not.
                """
            ),
        ] = None,
        default: Annotated[
            Optional[ASGIApp],
            Doc(
                """
                A `default` ASGI callable.
                """
            ),
        ] = None,
        routes: Annotated[
            Optional[Sequence[Union[APIGateHandler, Include, HTTPHandler, WebSocketHandler]]],
            Doc(
                """
                A `list` of ravyn routes. Those routes may vary and those can
                be `Gateway`, `WebSocketGateWay` or even an `Include`.

                This is also an entry-point for the routes of the `Router`
                but it **does not rely on only one [level](https://ravyn.dev/application/levels/)**.

                Read more about how to use and leverage
                the [Ravyn routing system](https://ravyn.dev/routing/routes/).

                **Example**

                ```python
                from ravyn import Ravyn, Gateway, Request, get, Include


                @get()
                async def homepage(request: Request) -> str:
                    return "Hello, home!"


                @get()
                async def another(request: Request) -> str:
                    return "Hello, another!"

                app = Ravyn(
                    routes=[
                        Gateway(handler=homepage)
                        Include("/nested", routes=[
                            Gateway(handler=another)
                        ])
                    ]
                )
                ```

                !!! Note
                    The Include is very powerful and this example
                    is not enough to understand what more things you can do.
                    Read in [more detail](https://ravyn.dev/routing/routes/#include) about this.
                """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        response_class: Annotated[
            Optional[ResponseType],
            Doc(
                """
                Default response class to be used within the
                Ravyn application.

                Read more about the [Responses](https://ravyn.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from ravyn import Router, JSONResponse

                Router(response_class=JSONResponse)
                ```
                """
            ),
        ] = None,
        response_cookies: Annotated[
            Optional[ResponseCookies],
            Doc(
                """
                A sequence of `ravyn.datastructures.Cookie` objects.

                Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from ravyn import Router
                from ravyn.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                Router(response_cookies=response_cookies)
                ```
                """
            ),
        ] = None,
        response_headers: Annotated[
            Optional[ResponseHeaders],
            Doc(
                """
                A mapping of `ravyn.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from ravyn import Router
                from ravyn.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                Router(response_headers=response_headers)
                ```
                """
            ),
        ] = None,
        lifespan: Annotated[
            Optional[Lifespan[Any]],
            Doc(
                """
                A `lifespan` context manager handler. This is an alternative
                to `on_startup` and `on_shutdown` and you **cannot used all combined**.

                Read more about the [lifespan](https://ravyn.dev/lifespan-events/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
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
            Union[Sequence[Callable[..., Any]], None],
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
        deprecated: Optional[bool] = None,
        security: Annotated[
            Optional[Sequence[SecurityScheme]],
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
    ):
        self._app = app
        if not path:
            path = "/"
        else:
            assert path.startswith("/"), "A path prefix must start with '/'"
            assert not path.endswith("/"), (
                "A path must not end with '/', as the routes will start with '/'"
            )

        new_routes: list[Any] = []
        for route in routes or []:
            if isinstance(route, WebhookHandler):
                # WebhookHandler is a subclass of HTTPHandler, make sure to not upgrade it
                ...
            elif isinstance(route, HTTPHandler):
                route = Gateway(handler=route)
            elif is_class_and_subclass(route, BaseController):
                route = Gateway(
                    handler=cast(BaseController, route),
                    permissions=(
                        route.permissions
                        if not self.is_member_descriptor(route.permissions)
                        else []
                    ),
                    interceptors=(
                        route.interceptors
                        if not self.is_member_descriptor(route.interceptors)
                        else []
                    ),
                    exception_handlers=(
                        route.exception_handlers
                        if not self.is_member_descriptor(route.exception_handlers)
                        else {}
                    ),
                    dependencies=(
                        route.dependencies
                        if not self.is_member_descriptor(route.dependencies)
                        else {}
                    ),
                    middleware=(
                        route.middleware if not self.is_member_descriptor(route.middleware) else []
                    ),
                    before_request=(
                        route.before_request
                        if not self.is_member_descriptor(route.before_request)
                        else []
                    ),
                    after_request=(
                        route.after_request
                        if not self.is_member_descriptor(route.after_request)
                        else []
                    ),
                    security=(
                        route.security if not self.is_member_descriptor(route.security) else []
                    ),
                    tags=route.tags if not self.is_member_descriptor(route.tags) else [],
                    include_in_schema=(
                        route.include_in_schema
                        if not self.is_member_descriptor(route.include_in_schema)
                        else True
                    ),
                    deprecated=(
                        route.deprecated
                        if not self.is_member_descriptor(route.deprecated)
                        else None
                    ),
                )
            elif isinstance(route, WebSocketHandler):
                route = WebSocketGateway(handler=route)
            if not isinstance(
                route,
                (
                    Include,
                    Gateway,
                    WebSocketGateway,
                    LilyaBasePath,
                    Host,
                    Router,
                ),
            ) or isinstance(cast(Any, route), (WebhookGateway, WebhookHandler)):
                # WebhookGateway is subclass of LilyaBasePath
                raise ImproperlyConfigured(
                    f"The route {route} must be of type HTTPHandler, WebSocketHandler, Gateway, WebSocketGateway or Include"
                )
            new_routes.append(route)

        assert lifespan is None or (on_startup is None and on_shutdown is None), (
            "Use either 'lifespan' or 'on_startup'/'on_shutdown', not both."
        )

        self.__base_permissions__ = permissions or []
        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.__base_permissions__ or []
            if not is_ravyn_permission(permission)
        ]

        super().__init__(
            redirect_slashes=redirect_slashes,
            routes=new_routes,
            default=default,
            lifespan=lifespan,
            on_shutdown=on_shutdown,
            on_startup=on_startup,
            permissions=self.__lilya_permissions__,  # type: ignore
            before_request=before_request,
            after_request=after_request,
        )
        self.path = path
        self.on_startup = [] if on_startup is None else list(on_startup)
        self.on_shutdown = [] if on_shutdown is None else list(on_shutdown)
        self.parent: Optional[ParentType] = parent or app
        self.dependencies = dependencies or {}  # type: ignore
        self.exception_handlers = exception_handlers or {}
        self.interceptors: Sequence[Interceptor] = interceptors or []
        self._interceptors: Union[list["RavynInterceptor"], VoidType] = Void
        self._permissions_cache: dict[int, Any] | VoidType = Void
        self._lilya_permissions_cache: dict[int, Any] | VoidType = Void

        # Filter out the lilya unique permissions
        if self.__lilya_permissions__:
            self.lilya_permissions: Any = {
                index: permission in self.__lilya_permissions__
                for index, permission in enumerate(self.__lilya_permissions__)
            }
        else:
            self.lilya_permissions = {}

        # Filter out the ravyn unique permissions
        if self.__base_permissions__:
            self.permissions: Any = {
                index: wrap_permission(permission)
                for index, permission in enumerate(permissions)
                if is_ravyn_permission(permission)
            }
        else:
            self.permissions = {}

        assert not (self.permissions and self.lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

        self.routes: Any = new_routes
        self.middleware = middleware or []
        self.tags = tags or []
        self.name = name
        self.response_class = response_class
        self.response_cookies = response_cookies or []
        self.response_headers = response_headers or {}
        self.deprecated = deprecated
        self.security = security or []

        # copy routes shallow, fixes bug with tests/dependencies/test_http_handler_dependency_injection.py
        # routes are modified by validate_root_route_parent
        for route in list(self.routes):
            self.validate_root_route_parent(route)

        for route in self.routes:
            self.create_signature_models(route)

        self.activate()

    def is_member_descriptor(self, value: Any) -> bool:
        """
        Checks if the value is a member descriptor type.
        This is used to determine if the value is a class attribute or not.
        """
        return isinstance(value, types.MemberDescriptorType)

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        await self.handle_interceptors(scope, receive, send)
        await self.handle_permissions(scope, receive, send)
        await super().__call__(scope, receive, send)

    def reorder_routes(self) -> list[Sequence[Union[APIGateHandler, Include]]]:
        routes = sorted(
            self.routes,
            key=lambda router: router.path != "" and router.path != "/",
            reverse=True,
        )
        return routes

    def activate(self) -> None:
        self.routes = self.reorder_routes()

    async def handle_interceptors(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        # Inherit interceptors from parent if any
        if self.parent and self.parent.interceptors:
            for parent_interceptor in self.parent.interceptors:
                if parent_interceptor not in self.interceptors:
                    self.interceptors.insert(0, parent_interceptor)

        # If no factories defined and no cache, nothing to do
        if (self._interceptors is Void) and not self.interceptors:
            return

        # Instantiate once and cache for reuse across requests
        if self._interceptors is Void:
            self._interceptors = [factory() for factory in self.interceptors]

        for interceptor in self._interceptors:
            if is_async_callable(interceptor.intercept):
                await interceptor.intercept(scope, receive, send)
            else:
                await run_in_threadpool(interceptor.intercept, scope, receive, send)

    async def handle_permissions(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles the permissions for the Include.
        This method ensures that the permissions are set correctly
        and that they are compatible with the Lilya permissions system.
        """
        # Use cached permissions if already computed
        if self._permissions_cache is not Void or self._lilya_permissions_cache is not Void:
            effective_permissions = (
                self._permissions_cache if self._permissions_cache is not Void else {}
            )
            effective_lilya_permissions = (
                self._lilya_permissions_cache if self._lilya_permissions_cache is not Void else {}
            )
        else:
            if self.parent and self.parent.permissions:
                # If the parent has permissions, we need to merge them with the current permissions
                self.permissions.update(
                    {
                        index + len(self.permissions): wrap_permission(permission)
                        for index, permission in enumerate(self.parent.permissions)
                        if is_ravyn_permission(permission)
                    }
                )

            effective_permissions = self.permissions
            effective_lilya_permissions = self.lilya_permissions
            # Cache the computed permissions
            self._permissions_cache = effective_permissions or Void
            self._lilya_permissions_cache = effective_lilya_permissions or Void

        if not effective_permissions and not effective_lilya_permissions:
            return

        connection = Connection(scope=scope, receive=receive)

        if effective_lilya_permissions:
            await self.dispatch_allow_connection(
                effective_lilya_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=self.app,
            )
        else:
            await self.dispatch_allow_connection(
                effective_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=self.app,
            )

    async def not_found(
        self, scope: "Scope", receive: "Receive", send: "Send"
    ) -> None:  # pragma: no cover
        """Ravyn version of a not found handler when a resource is
        called and cannot be dealt with properly.

        Ravyn overrides the original Lilya not_found to return always
        JSONReponse.

        For plain ASGI apps, just returns the response.
        """
        if scope["type"] == "websocket":
            websocket_close = WebSocketClose()
            await websocket_close(scope, receive, send)
            return

        if "app" in scope:
            raise NotFound(status_code=status.HTTP_404_NOT_FOUND)
        else:
            response = JSONResponse({"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND)
        await response(scope, receive, send)

    def path_for(self, name: str, **path_params: Any) -> URLPath:
        warnings.warn(
            "Ravyn `path_for` is deprecated and will be removed in a future version. Use url_path_for instead.",
            UserWarning,
            stacklevel=2,
        )
        for route in self.routes or []:
            try:
                return cast("URLPath", route.path_for(name, **path_params))
            except NoMatchFound:
                ...

            if isinstance(route, (Gateway, WebSocketGateway)):
                handler = cast("Union[HTTPHandler, WebSocketHandler]", route.handler)
                try:
                    return handler.path_for(name, **path_params)
                except NoMatchFound:
                    ...

        raise NoMatchFound(name, path_params)

    def url_path_for(self, name: str, **path_params: Any) -> URLPath:
        for route in self.routes or []:
            try:
                return cast("URLPath", route.url_path_for(name, **path_params))
            except NoMatchFound:
                ...

            if isinstance(route, (Gateway, WebSocketGateway)):
                handler = cast("Union[HTTPHandler, WebSocketHandler]", route.handler)
                try:
                    return handler.url_path_for(name, **path_params)
                except NoMatchFound:
                    ...

        raise NoMatchFound(name, path_params)

    def add_event_handler(self, event_type: str, func: Callable) -> None:  # pragma: no cover
        assert event_type in ("startup", "shutdown")

        if event_type == "startup":
            self.on_startup.append(func)

        else:
            self.on_shutdown.append(func)

    def on_event(self, event_type: str) -> Callable:  # pragma: no cover
        def decorator(func: Callable) -> Callable:
            self.add_event_handler(event_type, func)
            return func

        return decorator

    def create_signature_models(self, route: RouteParent) -> None:
        """
        Creates the signature models for the given routes.

        Args:
            route: The route for the signature model to be created.
        """
        if isinstance(route, (Include, Host)):
            for _route in route.routes:
                self.create_signature_models(_route)

        if isinstance(route, (Gateway, WebhookGateway)):
            if not route.handler.parent:  # pragma: no cover
                route.handler.parent = route

            if not is_class_and_subclass(route.handler, BaseController) and not isinstance(
                route.handler, BaseController
            ):
                route.handler.create_signature_model()

        if isinstance(route, WebSocketGateway):
            route.handler.create_signature_model(is_websocket=True)

    def validate_root_route_parent(
        self,
        value: Union[Router, Include, Gateway, WebSocketGateway, WebhookGateway],
        override: bool = False,
    ) -> None:
        """
        Handles everything parent from the root. When in the root, the parent must be setup.
        Appends the route path if exists.
        """
        # Getting the value of the router for the path
        value.path = clean_path(self.path + getattr(value, "path", "/"))

        if isinstance(value, (Include, Gateway, WebSocketGateway, WebhookGateway)):
            if not value.parent and not override:
                value.parent = cast("Union[Router, Include, Gateway, WebSocketGateway]", self)

        if isinstance(value, (Gateway, WebSocketGateway, WebhookGateway)):
            if not is_class_and_subclass(value.handler, BaseController) and not isinstance(
                value.handler, BaseController
            ):
                if not value.handler.parent:
                    value.handler.parent = value
            else:
                if not value.handler.parent:  # pragma: no cover
                    value(parent=self)  # type: ignore

                handler: BaseController = cast("BaseController", value.handler)
                route_handlers = handler.get_routes(
                    path=value.path,
                    middleware=value.middleware,
                    permissions=value.permissions,
                    interceptors=value.interceptors,
                    exception_handlers=value.exception_handlers,
                )
                if route_handlers:
                    self.routes.extend(route_handlers)
                self.routes.pop(self.routes.index(value))


class RoutingMethodsMixin:
    def get(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.GET.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def head(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.HEAD.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def post(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.POST.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def put(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.PUT.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def patch(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.PATCH.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def delete(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.DELETE.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def trace(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.TRACE.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def options(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.forward_single_method_route(
            path=path,
            method=HttpMethod.OPTIONS.value,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def forward_single_method_route(self, path: str, method: str, **kwargs: Any) -> Callable:
        """For customization, defaults to route."""
        return self.route(path=path, methods=[method], **kwargs)

    def route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        methods: Annotated[
            Optional[list[str]],
            Doc(
                """
                A list of HTTP methods to serve the Gateway.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        raise NotImplementedError()

    def websocket(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
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
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        raise NotImplementedError()


class Router(RoutingMethodsMixin, BaseRouter):
    """
    The `Router` object used by `Ravyn` upon instantiation.

    The router is what is created by default when the `routes` parameter is
    defined.

    This object is complex and very powerful. Read more in detail about [the Router](https://ravyn.dev/routing/router/) and how to use it.

    """

    def add_apiview(
        self,
        value: Annotated[
            Union[Gateway, WebSocketGateway],
            Doc(
                """
                The `Controller` or similar to be added.
                """
            ),
        ],
    ) -> None:
        """
        Adds an [Controller](https://ravyn.dev/routing/controllers/) or related
        to the application routing.

        **Example**

        ```python
        from ravyn import Router, Controller, Gateway, get


        class BaseController(Controller):
            path = "/"

            @get(status_code=status_code)
            async def hello(self) -> str:
                return "Hello, World!"


        gateway = Gateway(handler=View)

        app = Router()
        app.add_apiview(value=gateway)
        ```
        """
        warnings.warn(
            "add_apiview is deprecated and will be removed in the release 0.4.0. "
            "Please use add_controller instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_controller(value=value)

    def add_controller(
        self,
        value: Annotated[
            Union[Gateway, WebSocketGateway],
            Doc(
                """
                The `Controller` or similar to be added.
                """
            ),
        ],
    ) -> None:
        """
        Adds an [Controller](https://ravyn.dev/routing/controllers/) or related
        to the application routing.

        **Example**

        ```python
        from ravyn import Router, Controller, Gateway, get


        class View(Controller):
            path = "/"

            @get(status_code=status_code)
            async def hello(self) -> str:
                return "Hello, World!"


        gateway = Gateway(handler=View)

        app = Router()
        app.add_controller(value=gateway)
        ```
        """
        routes = []
        if not value.handler.parent:  # pragma: no cover
            value.handler(parent=self)

        route_handlers: list[Union[HTTPHandler, WebSocketHandler]] = value.handler.get_routes(
            path=value.path,
            middleware=value.middleware,
            interceptors=value.interceptors,
            permissions=value.permissions,
            exception_handlers=value.exception_handlers,
            include_in_schema=value.include_in_schema,
            before_request=value.before_request,
            after_request=value.after_request,
        )
        if route_handlers:
            self.routes.extend(route_handlers)
            routes.extend(route_handlers)

        for route in routes or []:
            self.create_signature_models(route)
        self.activate()

    def add_route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        handler: Annotated[
            HTTPHandler,
            Doc(
                """
                An instance of [handler](https://ravyn.dev/routing/handlers/#http-handlers).
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> None:
        """
        Adds a [Route](https://ravyn.dev/routing/routes/)
        to the application routing.

        This is a dynamic way of adding routes on the fly.

        **Example**

        ```python
        from ravyn import get


        @get(status_code=status_code)
        async def hello(self) -> str:
            return "Hello, World!"


        app = Ravyn()
        app.add_route(path="/hello", handler=hello)
        ```
        """
        if not isinstance(handler, HTTPHandler) or isinstance(handler, WebhookHandler):
            raise ImproperlyConfigured(
                f"handler must be a instance of HTTPHandler and not {handler.__class__.__name__}. "
                "Example: get(), put(), post(), delete(), patch(), route()."
            )
        gateway = Gateway(
            path=self.path + path,
            handler=handler,
            name=name,
            include_in_schema=include_in_schema,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            interceptors=interceptors,
            permissions=permissions,
            middleware=middleware,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )
        self.validate_root_route_parent(gateway)
        self.create_signature_models(gateway)
        self.routes.append(gateway)

    def add_websocket_route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        handler: Annotated[
            WebSocketHandler,
            Doc(
                """
                An instance of [websocket handler](https://ravyn.dev/routing/handlers/#websocket-handler).
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
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> None:
        """
        Adds a websocket [Route](https://ravyn.dev/routing/routes/)
        to the application routing.

        This is a dynamic way of adding routes on the fly.

        **Example**

        ```python
        from ravyn import websocket


        @websocket()
        async def websocket_route(socket: WebSocket) -> None:
            await socket.accept()
            data = await socket.receive_json()

            assert data
            await socket.send_json({"data": "ravyn"})
            await socket.close()


        app = Ravyn()
        app.add_websocket_route(path="/ws", handler=websocket_route)
        ```
        """
        if not isinstance(handler, WebSocketHandler):
            raise ImproperlyConfigured(
                f"handler must be a instance of WebSocketHandler and not {handler.__class__.__name__}. "
                "Example: websocket()."
            )
        websocket_gateway = WebSocketGateway(
            path=path,
            handler=handler,
            name=name,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            interceptors=interceptors,
            permissions=permissions,
            middleware=middleware,
            before_request=before_request,
            after_request=after_request,
        )
        self.validate_root_route_parent(websocket_gateway)
        self.create_signature_models(websocket_gateway)
        self.routes.append(websocket_gateway)

    def route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        methods: Annotated[
            Optional[list[str]],
            Doc(
                """
                A list of HTTP methods to serve the Gateway.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        if methods is None:
            methods = [HttpMethod.GET.value]

        def wrapper(func: Callable) -> Callable:
            handler = HTTPHandler(
                handler=func,
                methods=methods,
                dependencies=dependencies,
                permissions=cast(list["Permission"], permissions),
                exception_handlers=exception_handlers,
                middleware=middleware,
                include_in_schema=include_in_schema,
                deprecated=deprecated,
                before_request=before_request,
                after_request=after_request,
            )
            handler.fn = func
            self.add_route(path=path, handler=handler, name=name, interceptors=interceptors)
            return func

        return wrapper

    def websocket(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
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
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Sequence[Callable[..., Any]] | None,
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        def wrapper(func: Callable) -> Callable:
            handler = WebSocketHandler(
                dependencies=dependencies,
                exception_handlers=exception_handlers,
                permissions=cast(list["Permission"], permissions),
                middleware=middleware,
                before_request=before_request,
                after_request=after_request,
            )
            handler.fn = func
            self.add_websocket_route(
                path=path, handler=handler, name=name, interceptors=interceptors
            )
            return func

        return wrapper


_body_less_methods = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


class HTTPHandler(Dispatcher, OpenAPIFieldInfoMixin, LilyaPath):
    __slots__ = (
        "path",
        "_interceptors",
        "_permissions",
        "_dependencies",
        "_response_handler",
        "_middleware",
        "name",
        "methods",
        "status_code",
        "content_encoding",
        "media_type",
        "content_media_type",
        "summary",
        "description",
        "include_in_schema",
        "dependencies",
        "exception_handlers",
        "permissions",
        "middleware",
        "response_class",
        "response_cookies",
        "response_headers",
        "parent",
        "tags",
        "deprecated",
        "security",
        "operation_id",
        "interceptors",
        "__type__",
        "before_request",
        "after_request",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        handler: Callable[..., Any] = None,
        *,
        name: Optional[str] = None,
        methods: Optional[Sequence[str]] = None,
        status_code: Optional[int] = None,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional[BackgroundTaskType] = None,
        dependencies: Optional[Dependencies] = None,
        exception_handlers: Optional[ExceptionHandlerMap] = None,
        permissions: Optional[list[Permission]] = None,
        middleware: Optional[list[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        before_request: Sequence[Callable[..., Any]] | None = None,
        after_request: Sequence[Callable[..., Any]] | None = None,
        tags: Optional[Sequence[str]] = None,
        deprecated: Optional[bool] = None,
        response_description: Optional[str] = "Successful Response",
        responses: Optional[dict[int, OpenAPIResponse]] = None,
        security: Optional[list[SecurityScheme]] = None,
        operation_id: Optional[str] = None,
    ) -> None:
        """
        Handles the "handler" or "controller" of the platform. A handler can be any get, put, patch, post, delete or route.
        """
        if not path:
            path = "/"

        self.__base_permissions__ = permissions or []

        self._lilya_permissions: Union[list[DefinePermission], VoidType] = Void
        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.__base_permissions__ or []
            if not is_ravyn_permission(permission)
        ]

        super().__init__(
            path=path,
            handler=handler,
            include_in_schema=include_in_schema,
            exception_handlers=exception_handlers,
            name=name,
            permissions=self.__lilya_permissions__,  # type: ignore
        )

        self._permissions: Union[list[Permission], VoidType] = Void
        self._dependencies: Dependencies = {}
        self._response_handler: Union[Callable[[Any], Awaitable[LilyaResponse]], VoidType] = Void
        self._interceptors: Union[list["RavynInterceptor"], VoidType] = Void
        self._permissions_cache: dict[int, Any] | VoidType = Void
        self._lilya_permissions_cache: dict[int, Any] | VoidType = Void

        self.parent: ParentType = None
        self.path = path

        self.handler = handler
        self.summary = summary
        self.name = name
        self.tags = tags or []
        self.include_in_schema = include_in_schema
        self.deprecated = deprecated

        if not self.deprecated:
            self.deprecated = False

        self.security = security or []
        self.operation_id = operation_id

        if not methods:
            methods = [HttpMethod.GET.value]

        for method in methods or []:
            if not isinstance(method, str):
                raise ImproperlyConfigured(f"`{method}` in `methods` must be a string.")

        self.methods: Set[str] = {HttpMethod[method].value for method in methods}  # type: ignore

        if isinstance(status_code, IntEnum):  # pragma: no cover
            status_code = int(status_code)
        self.status_code = status_code

        self.dependencies: Dependencies = dependencies or {}  # type: ignore

        if not description:
            description = inspect.cleandoc(self.handler.__doc__ or "") if self.handler else ""

        self.description = description

        # Filter out the lilya unique permissions
        if self.__lilya_permissions__:
            self.lilya_permissions: Any = {
                index: permission in self.__lilya_permissions__
                for index, permission in enumerate(self.__lilya_permissions__)
            }
        else:
            self.lilya_permissions = {}

        # Filter out the ravyn unique permissions
        if self.__base_permissions__:
            self.permissions: Any = {
                index: wrap_permission(permission)
                for index, permission in enumerate(permissions)
                if is_ravyn_permission(permission)
            }
        else:
            self.permissions = {}

        assert not (self.permissions and self.lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

        self.before_request = list(before_request or [])
        self.after_request = list(after_request or [])
        self.interceptors: Sequence[Interceptor] = []
        self.middleware = list(middleware) if middleware else []
        self.description = self.description.split("\f")[0]
        self.media_type = media_type
        self.response_class = response_class
        self.response_cookies = response_cookies
        self.response_headers = response_headers
        self.background = background
        self.signature_model: Optional[Type[SignatureModel]] = None
        self.transformer: Optional[TransformerModel] = None
        self.response_description = response_description
        self.responses = responses or {}
        self.content_encoding = content_encoding
        self.content_media_type = content_media_type

        self.fn: Optional[AnyCallable] = None
        self.route_map: dict[str, Tuple[HTTPHandler, TransformerModel]] = {}
        self.path_regex, self.path_format, self.param_convertors, _ = compile_path(path)
        self._middleware: list[Middleware] = []
        self.__type__: Union[str, None] = None
        self.before_request = list(before_request or [])
        self.after_request = list(after_request or [])

        if self.responses:
            self.validate_responses(responses=self.responses)

    async def handle_interceptors(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interceptors for the HTTPHandler.
        This method ensures that the interceptors are set correctly
        and that they are compatible with the Lilya interceptors system.
        """
        # If no factories defined and no cache, nothing to do
        if (self._interceptors is Void) and not self.interceptors:
            return

        # Instantiate once and cache for reuse across requests
        if self._interceptors is Void:
            self._interceptors = [factory() for factory in self.interceptors]

        for interceptor in self._interceptors:
            if is_async_callable(interceptor.intercept):
                await interceptor.intercept(scope, receive, send)
            else:
                await run_in_threadpool(interceptor.intercept, scope, receive, send)

    async def handle_permissions(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles the permissions for the Include.
        This method ensures that the permissions are set correctly
        and that they are compatible with the Lilya permissions system.
        """
        # Use cached permissions if already computed
        if self._permissions_cache is not Void or self._lilya_permissions_cache is not Void:
            effective_permissions = (
                self._permissions_cache if self._permissions_cache is not Void else {}
            )
            effective_lilya_permissions = (
                self._lilya_permissions_cache if self._lilya_permissions_cache is not Void else {}
            )
        else:
            if self.parent and self.parent.permissions:
                if not self.permissions:
                    # If the parent has permissions, we need to merge them with the current permissions
                    self.permissions.update(self.parent.permissions)
                else:
                    # If the parent has permissions, we need to merge them with the current permissions
                    all_perms = list(self.parent.permissions.values())
                    for perm in self.permissions.values():
                        all_perms.append(perm)
                    self.permissions = dict(enumerate(all_perms))  #

            effective_permissions = self.permissions if self.permissions else {}
            effective_lilya_permissions = self.lilya_permissions if self.lilya_permissions else {}

            # Cache the computed permissions
            self._permissions_cache = effective_permissions or Void
            self._lilya_permissions_cache = effective_lilya_permissions or Void

        if not effective_permissions and not effective_lilya_permissions:
            return

        connection = Connection(scope=scope, receive=receive)

        if effective_lilya_permissions:
            await self.dispatch_allow_connection(
                effective_lilya_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=self.app,
            )
        else:
            dispatch_call = super().handle_dispatch
            await self.dispatch_allow_connection(
                effective_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=dispatch_call,
            )

    def validate_responses(self, responses: dict[int, OpenAPIResponse]) -> None:
        """
        Checks if the responses are valid or raises an exception otherwise.
        """
        for status_code, response in responses.items():
            if not isinstance(response, OpenAPIResponse):
                raise OpenAPIException(
                    detail="An additional response must be an instance of OpenAPIResponse."
                )

            if not is_status_code_allowed(status_code):
                raise OpenAPIException(detail="The status is not a valid OpenAPI status response.")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        await self.handle_dispatch(scope=scope, receive=receive, send=send)

    @property
    def http_methods(self) -> list[str]:
        """
        Converts the methods set into a list of methods.
        """
        return list(self.methods)

    async def allowed_methods(
        self, scope: "Scope", receive: "Receive", send: "Send", methods: list[str]
    ) -> None:
        """
        Validates if the scope method is available within the handler and raises
        a MethodNotAllowed if otherwise.
        """
        for method in methods:
            if method not in self.http_methods:
                raise MethodNotAllowed(detail=f"Method {method.upper()} not allowed.")

    @property
    def allow_header(self) -> Mapping[str, str]:
        """
        Default allow header to be injected in the Response and Lilya Response type
        handlers.
        """
        return {"allow": str(self.methods)}

    def get_response_class(self) -> Type[Response]:
        """
        Returns the closest custom Response class in the parent graph or the
        default Response class.
        """
        response_class = Response
        for layer in self.parent_levels:
            if layer.response_class is not None:
                response_class = layer.response_class
        return response_class

    def get_response_headers(self) -> ResponseHeaders:
        """
        Returns all header parameters in the scope of the handler function.
        """
        resolved_response_headers: ResponseHeaders = {}
        for layer in self.parent_levels:
            resolved_response_headers.update(layer.response_headers or {})
        return resolved_response_headers

    def get_response_cookies(self) -> ResponseCookies:
        """Returns a list of Cookie instances. Filters the list to ensure each
        cookie key is unique.
        """

        cookies: ResponseCookies = []
        for layer in self.parent_levels:
            cookies.extend(layer.response_cookies or [])
        filtered_cookies: ResponseCookies = []
        for cookie in reversed(cookies):
            if not any(cookie.key == c.key for c in filtered_cookies):
                filtered_cookies.append(cookie)
        return filtered_cookies

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the dispatching of a request.
        This method processes the incoming request by performing the following steps:

        1. Intercepts the request if interceptors are present.
        2. Checks if the request method is allowed.
        3. Creates a Request object from the scope, receive, and send parameters.
        4. Retrieves the route handler and parameter model for the request method.
        5. Checks and dispatches application permissions if they exist.
        6. Gets the response for the request and sends it.

        Args:
            scope (Scope): The ASGI scope dictionary containing request information.
            receive (Receive): The ASGI receive callable.
            send (Send): The ASGI send callable.
        Returns:
            None
        """
        for before_request in self.before_request:
            if inspect.isclass(before_request):
                before_request = before_request()

            if is_async_callable(before_request):
                await before_request(scope, receive, send)
            else:
                await run_in_threadpool(before_request, scope, receive, send)

        await self.handle_interceptors(scope, receive, send)

        methods = [scope["method"]]
        await self.allowed_methods(scope, receive, send, methods)

        request = Request(scope=scope, receive=receive, send=send)
        route_handler, parameter_model = self.route_map[scope["method"]]

        # Check the permissions for the application if they exist.
        await self.handle_permissions(scope, receive, send)

        response = await self.get_response_for_request(
            scope=scope,
            request=request,
            route=route_handler,
            parameter_model=parameter_model,
        )
        await response(scope, receive, send)

        for after_request in self.after_request:
            if inspect.isclass(after_request):
                after_request = after_request()

            if is_async_callable(after_request):
                await after_request(scope, receive, send)
            else:
                await run_in_threadpool(after_request, scope, receive, send)

    def check_handler_function(self) -> None:
        """Validates the route handler function once it's set by inspecting its
        return annotations.

        `enable_sync_handlers` from the application settings enables/disables the possibility
        of having `sync` handlers.

        Example:
            enable_sync_handlers = True

            @get(path'/')
            def index(request: Request) -> Response:
                return Response("Welcome Home")

            enable_sync_handlers = False

            @get(path'/')
            async def index(request: Request) -> Response:
                return Response("Welcome Home")

        Raises:
            ImproperlyConfigured if enable_sync_handlers is False and the function is sync.
        """
        if not self.fn:
            raise ImproperlyConfigured(
                "Cannot call check_handler_function without first setting self.fn"
            )

        if not settings.enable_sync_handlers:  # pragma: no cover
            fn = self.fn
            if not is_async_callable(fn):
                raise ImproperlyConfigured(
                    "Functions decorated with 'route, websocket, get, patch, put, post and delete' must be async functions"
                )

    def validate_annotations(self) -> None:  # pragma: no cover
        """
        Validate annotations of the handlers.
        """
        return_annotation = self.handler_signature.return_annotation

        if return_annotation is Signature.empty:
            raise ImproperlyConfigured(
                "A return value of a route handler function should be type annotated. "
                "If your function doesn't return a value or returns None, annotate it as returning 'NoReturn' or 'None' respectively."
            )
        if (
            self.status_code < status.HTTP_200_OK
            or self.status_code in {status.HTTP_204_NO_CONTENT, status.HTTP_304_NOT_MODIFIED}
        ) and return_annotation not in [NoReturn, None]:
            raise ImproperlyConfigured(
                "A status code 204, 304 or in the range below 200 does not support a response body."
                " If the function should return a value, change the route handler status code to an appropriate value.",
            )
        if (
            is_class_and_subclass(return_annotation, Redirect)
            and self.status_code not in REDIRECT_STATUS_CODES
        ):
            raise ValidationErrorException(
                f"Redirect responses should have one of "
                f"the following status codes: {', '.join([str(s) for s in REDIRECT_STATUS_CODES])}"
            )
        if is_class_and_subclass(return_annotation, File) and self.media_type in [
            MediaType.JSON,
            MediaType.HTML,
        ]:
            self.media_type = MediaType.TEXT

    def validate_bodyless_kwargs(self) -> None:
        if _body_less_methods.isdisjoint(self.methods):
            return
        body_less_only = _body_less_methods.issuperset(self.methods)
        for special in [DATA, PAYLOAD]:
            if special in self.handler_signature.parameters:
                if body_less_only:
                    raise ImproperlyConfigured(
                        f"'{special}' argument unsupported when only body-less methods like 'GET' and 'HEAD' are handled"
                    )
                elif not is_optional_union(self.handler_signature.parameters[special].annotation):
                    raise ImproperlyConfigured(
                        f"'{special}' argument must be optional when body-less methods like 'GET' and 'HEAD' are handled"
                    )
        for parameter_name, parameter in self.handler_signature.parameters.items():
            # don't check twice
            if parameter_name == DATA or parameter_name == PAYLOAD:
                continue
            if isinstance(parameter.default, Form):
                if body_less_only:
                    raise ImproperlyConfigured(
                        f"'{special}' uses Form() which is unsupported when only body-less methods "
                        "like 'GET' and 'HEAD' are handled"
                    )
                elif not is_optional_union(parameter.annotation):
                    raise ImproperlyConfigured(
                        f"'{special}' argument must be optional when body-less methods like 'GET' and 'HEAD' are handled"
                    )

    def validate_reserved_kwargs(self) -> None:  # pragma: no cover
        """
        Validates if special words are in the signature.
        """

        if SOCKET in self.handler_signature.parameters:
            raise ImproperlyConfigured("The 'socket' argument is not supported with http handlers")

    def validate_handler(self) -> None:
        self.check_handler_function()
        self.validate_annotations()
        self.validate_bodyless_kwargs()
        self.validate_reserved_kwargs()

    async def to_response(self, app: "Ravyn", data: Any) -> LilyaResponse:
        response_handler = self.get_response_for_handler()
        return await response_handler(app=app, data=data)  # type: ignore[call-arg]


class WebhookHandler(HTTPHandler, OpenAPIFieldInfoMixin):
    """
    The Webhook handler object representation.

    This class extends the `HTTPHandler` class and is used to represent a webhook handler in the application.

    It inherits all the properties and methods of the `HTTPHandler` class, allowing it to handle HTTP requests specifically for webhooks.

    Attributes:
            path (str | None): The relative path of the webhook handler. It can contain parameters in a dictionary-like format.
    """

    def __init__(self, *args: Any, path: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.path = path


class WebSocketHandler(Dispatcher, LilyaWebSocketPath):
    """
    Websocket handler object representation.
    """

    __slots__ = (
        "path",
        "dependencies",
        "exception_handlers",
        "permissions",
        "middleware",
        "parent",
        "name",
        "before_request",
        "after_request",
        "__type__",
        "_interceptors",
        "_permissions_cache",
        "_lilya_permissions_cache",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        handler: Callable[..., Any] = None,
        dependencies: Optional[Dependencies] = None,
        exception_handlers: Optional[ExceptionHandlerMap] = None,
        permissions: Optional[list[Permission]] = None,
        middleware: Optional[list[Middleware]] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        before_request: Sequence[Callable[..., Any]] | None = None,
        after_request: Sequence[Callable[..., Any]] | None = None,
    ):
        if not path:
            path = "/"

        self.__base_permissions__ = permissions or []
        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.__base_permissions__ or []
            if not is_ravyn_permission(permission)
        ]
        super().__init__(
            path=path,
            handler=handler,
            exception_handlers=exception_handlers,
            permissions=self.__lilya_permissions__,  # type: ignore
            before_request=before_request,
            after_request=after_request,
        )
        self._permissions: Union[list[Permission], VoidType] = Void
        self._lilya_permissions: Union[list[DefinePermission], VoidType] = Void
        self._dependencies: Dependencies = {}
        self._response_handler: Union[Callable[[Any], Awaitable[LilyaResponse]], VoidType] = Void
        self._interceptors: Union[list["RavynInterceptor"], VoidType] = Void
        self._permissions_cache: dict[int, Any] | VoidType = Void
        self._lilya_permissions_cache: dict[int, Any] | VoidType = Void
        self.interceptors: Sequence[Interceptor] = []
        self.handler = handler
        self.parent: ParentType = None
        self.dependencies = dependencies  # type: ignore

        # Filter out the lilya unique permissions
        if self.__lilya_permissions__:
            self.lilya_permissions: Any = {
                index: permission in self.__lilya_permissions__
                for index, permission in enumerate(self.__lilya_permissions__)
            }
        else:
            self.lilya_permissions = {}

        # Filter out the ravyn unique permissions
        if self.__base_permissions__:
            self.permissions: Any = {
                index: wrap_permission(permission)
                for index, permission in enumerate(permissions)
                if is_ravyn_permission(permission)
            }
        else:
            self.permissions = {}

        assert not (self.permissions and self.lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

        self.middleware = middleware
        self.signature_model: Optional[Type[SignatureModel]] = None
        self.websocket_parameter_model: Optional[TransformerModel] = None
        self.include_in_schema = None
        self.fn: Optional[AnyCallable] = None
        self.tags: Sequence[str] = []
        self.__type__: Union[str, None] = None
        self.name = name

    async def handle_interceptors(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interceptors for the Websockets.
        This method ensures that the interceptors are set correctly
        and that they are compatible with the Lilya interceptors system.
        """
        # If no factories defined and no cache, nothing to do
        if (self._interceptors is Void) and not self.interceptors:
            return

        # Instantiate once and cache for reuse across requests
        if self._interceptors is Void:
            self._interceptors = [factory() for factory in self.interceptors]

        for interceptor in self._interceptors:
            if is_async_callable(interceptor.intercept):
                await interceptor.intercept(scope, receive, send)
            else:
                await run_in_threadpool(interceptor.intercept, scope, receive, send)

    async def handle_permissions(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles the permissions for the Include.
        This method ensures that the permissions are set correctly
        and that they are compatible with the Lilya permissions system.
        """
        # Use cached permissions if already computed
        if self._permissions_cache is not Void or self._lilya_permissions_cache is not Void:
            effective_permissions = (
                self._permissions_cache if self._permissions_cache is not Void else {}
            )
            effective_lilya_permissions = (
                self._lilya_permissions_cache if self._lilya_permissions_cache is not Void else {}
            )
        else:
            if self.parent and self.parent.permissions:
                parent_perms = self.parent.permissions.copy()
            else:
                parent_perms = {}

            effective_permissions = {}
            if self.permissions:
                all_perms = list(parent_perms.values()) + list(self.permissions.values())
                effective_permissions = dict(enumerate(all_perms))
            elif parent_perms:
                effective_permissions = parent_perms.copy()

            effective_lilya_permissions = (
                self.lilya_permissions.copy() if self.lilya_permissions else {}
            )

            # Cache the computed permissions
            self._permissions_cache = effective_permissions or Void
            self._lilya_permissions_cache = effective_lilya_permissions or Void

        if not effective_permissions and not effective_lilya_permissions:
            return

        connection = WebSocket(scope=scope, receive=receive, send=send)

        if effective_lilya_permissions:
            await self.dispatch_allow_connection(
                effective_lilya_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=self.app,
            )
        else:
            dispatch_call = super().handle_dispatch
            await self.dispatch_allow_connection(
                effective_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=dispatch_call,
            )

    def validate_reserved_words(self, signature: Signature) -> None:
        """
        Validates if special words are in the signature.
        """
        if signature.return_annotation is not None:
            raise ImproperlyConfigured("Websocket functions should return 'None'.")

        unsupported_kwargs = [REQUEST, DATA, PAYLOAD]
        for kwarg in unsupported_kwargs:
            if kwarg in signature.parameters:
                raise ImproperlyConfigured(
                    f"The '{kwarg}'is not supported with websocket handlers."
                )

    def validate_websocket_handler_function(self) -> None:  # pragma: no cover
        """
        Validates the route handler function once it is set by inspecting its
        return annotations.
        """
        if not self.fn:
            raise ImproperlyConfigured(
                "Cannot call check_handler_function without first setting self.fn"
            )
        signature = Signature.from_callable(self.fn)
        self.validate_reserved_words(signature=signature)

        if SOCKET not in signature.parameters:
            raise ImproperlyConfigured("Websocket handlers must set a 'socket' argument.")
        if not is_async_callable(self.fn):
            raise ImproperlyConfigured(
                "Functions decorated with 'asgi, get, patch, put, post and delete' must be async functions."
            )

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the dispatching of a request.
        This method processes the incoming request by handling interceptors,
        checking permissions, and dispatching the request to the appropriate
        handler function.

        Args:
            scope (Scope): The ASGI scope dictionary containing request information.
            receive (Receive): The ASGI receive callable to receive messages.
            send (Send): The ASGI send callable to send messages.
        Returns:
            None
        """

        for before_request in self.before_request:
            if inspect.isclass(before_request):
                before_request = before_request()

            if is_async_callable(before_request):
                await before_request(scope, receive, send)
            else:
                await run_in_threadpool(before_request, scope, receive, send)

        # Handle the interceptors for the WebSocket handler.
        await self.handle_interceptors(scope, receive, send)

        websocket = WebSocket(scope=scope, receive=receive, send=send)

        # Manages the permissions for the WebSocket handler.
        await self.handle_permissions(scope, receive, send)

        kwargs = await self.get_kwargs(websocket=websocket)

        fn = self.fn
        if isinstance(self.parent, BaseController):
            await fn(self.parent, **kwargs)
        else:
            await fn(**kwargs)

        for after_request in self.after_request:
            if inspect.isclass(after_request):
                after_request = after_request()

            if is_async_callable(after_request):
                await after_request(scope, receive, send)
            else:
                await run_in_threadpool(after_request, scope, receive, send)

    async def get_kwargs(self, websocket: WebSocket) -> Any:
        """Resolves the required kwargs from the request data.

        Args:
            websocket: WebSocket instance

        Returns:
            Dictionary of parsed kwargs
        """
        assert self.websocket_parameter_model, "handler parameter model not defined."

        signature_model = get_signature(self)
        kwargs = await self.websocket_parameter_model.to_kwargs(connection=websocket)
        for dependency in self.websocket_parameter_model.dependencies:
            kwargs[dependency.key] = await self.websocket_parameter_model.get_dependencies(
                dependency=dependency, connection=websocket, **kwargs
            )
        return await signature_model.parse_values_for_connection(connection=websocket, **kwargs)


class Include(Dispatcher, LilyaInclude):
    """
    `Include` object class that allows scalability and modularity
    to happen with elegance.

    Read more about the [Include](https://ravyn.dev/routing/routes/#include) to understand
    what can be done.

    Include manages routes as a list or as a namespace but not both or a
    `ImproperlyConfigured` is raised.
    """

    __slots__ = (
        "path",
        "app",
        "namespace",
        "pattern",
        "name",
        "dependencies",
        "exception_handlers",
        "interceptors",
        "permissions",
        "middleware",
        "deprecated",
        "security",
        "tags",
        "redirect_slashes",
        "before_request",
        "after_request",
        "_interceptors",
    )

    def __init__(
        self,
        path: Annotated[
            Optional[str],
            Doc(
                """
                Relative path of the `Include`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                Include()
                ```

                **Example with parameters**

                ```python
                Include(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        app: Annotated[
            ASGIApp | str,
            Doc(
                """
                An application can be anything that is treated as an ASGI application.
                For example, it can be a [ChildRavyn](https://ravyn.dev/routing/router/#child-ravyn-application), another `Ravyn`, a [Router](https://ravyn.dev/routing/router/#router-class) or even an external [WSGI application](https://ravyn.dev/wsgi/) (Django, Flask...)

                The app is a parameter that makes the Include extremely powerful when it comes
                to integrate with ease with whatever Python stack you want and need.

                **Example**

                ```python
                from ravyn import Ravyn, ChildRavyn, Include

                Ravyn(
                    routes=[
                        Include('/child', app=ChildRavyn(...))
                    ]
                )
                ```

                **Example with a WSGI framework**

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

                """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        routes: Annotated[
            Optional[Sequence[Union[APIGateHandler, Include, HTTPHandler, WebSocketHandler]]],
            Doc(
                """
                A global `list` of ravyn routes. Those routes may vary and those can
                be `Gateway`, `WebSocketGateWay` or even another `Include`.

                This is also an entry-point for the routes of the Include
                but it **does not rely on only one [level](https://ravyn.dev/application/levels/)**.

                Read more about how to use and leverage
                the [Ravyn routing system](https://ravyn.dev/routing/routes/).

                **Example**

                ```python
                from ravyn import Ravyn, Gateway, Request, get, Include


                @get()
                async def homepage(request: Request) -> str:
                    return "Hello, home!"


                @get()
                async def another(request: Request) -> str:
                    return "Hello, another!"

                app = Ravyn(
                    routes=[
                        Gateway(handler=homepage)
                        Include("/nested", routes=[
                            Gateway(handler=another)
                        ])
                    ]
                )
                ```

                !!! Note
                    The Include is very powerful and this example
                    is not enough to understand what more things you can do.
                    Read in [more detail](https://ravyn.dev/routing/routes/#include) about this.
                """
            ),
        ] = None,
        namespace: Annotated[
            Optional[str],
            Doc(
                """
                A string with a qualified namespace from where the URLs should be loaded.

                The namespace is an alternative to `routes` parameter. When a `namespace` is
                specified and a routes as well, an `ImproperlyCOnfigured` exception is raised as
                it can only be one or another.

                The `namespace` can be extremely useful as it avoids the imports from the top
                of the file that can lead to `partially imported` errors.

                When using a `namespace`, the `Include` will look for the default `route_patterns` list in the imported namespace (object) unless a different `pattern` is specified.

                **Example**

                Assuming there is a file with some routes located at `myapp/auth/urls.py`.

                ```python title="myapp/auth/urls.py"
                from ravyn import Gateway
                from .view import welcome, create_user

                route_patterns = [
                    Gateway(handler=welcome, name="welcome"),
                    Gateway(handler=create_user, name="create-user"),
                ]
                ```

                Using the `namespace` to import the URLs.

                ```python
                from ravyn import Include

                Include("/auth", namespace="myapp.auth.urls")
                ```
                """
            ),
        ] = None,
        pattern: Annotated[
            Optional[str],
            Doc(
                """
                A string `pattern` information from where the urls shall be read from.

                By default, the when using the `namespace` it will lookup for a `route_patterns`
                but somethimes you might want to opt for a different name and this is where the
                `pattern` comes along.

                **Example**

                Assuming there is a file with some routes located at `myapp/auth/urls.py`.
                The urls will be placed inside a `urls` list.

                ```python title="myapp/auth/urls.py"
                from ravyn import Gateway
                from .view import welcome, create_user

                urls = [
                    Gateway(handler=welcome, name="welcome"),
                    Gateway(handler=create_user, name="create-user"),
                ]
                ```

                Using the `namespace` to import the URLs.

                ```python
                from ravyn import Include

                Include("/auth", namespace="myapp.auth.urls", pattern="urls")
                ```
                """
            ),
        ] = None,
        parent: Annotated[
            Optional[ParentType],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://ravyn.dev/application/levels/).
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://ravyn.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission] | Any],
            Doc(
                """
                A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.

                This will add all the routes of the Include even those nested (Include containing more Includes.)
                """
            ),
        ] = True,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Include and all of its routes and to display it in the OpenAPI documentation..
                """
            ),
        ] = None,
        security: Annotated[
            Optional[Sequence[SecurityScheme]],
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
        redirect_slashes: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag indicating if the redirect slashes are enabled for the
                routes or not.
                """
            ),
        ] = True,
    ) -> None:
        self.path = path
        if not path:
            self.path = "/"

        if namespace and routes:
            raise ImproperlyConfigured("It can only be namespace or routes, not both.")

        if namespace and not isinstance(namespace, str):
            raise ImproperlyConfigured("Namespace must be a string. Example: 'myapp.routes'.")

        if pattern and not isinstance(pattern, str):
            raise ImproperlyConfigured("Pattern must be a string. Example: 'route_patterns'.")

        if pattern and routes:
            raise ImproperlyConfigured("Pattern must be used only with namespace.")

        if namespace:
            routes = include(namespace, pattern)

        # Add the middleware to the include
        self.middleware = middleware or []
        include_middleware: Sequence[Middleware] = []

        for _middleware in self.middleware:
            if isinstance(_middleware, DefineMiddleware):  # pragma: no cover
                include_middleware.append(_middleware)
            else:
                include_middleware.append(  # type: ignore
                    DefineMiddleware(cast("Type[DefineMiddleware]", _middleware))
                )

        if isinstance(app, str):
            app = load(app)

        self.app = self.resolve_app_parent(app=app)

        self.dependencies = dependencies or {}  # type: ignore
        self.interceptors: Sequence[Interceptor] = interceptors or []
        self._interceptors: Union[list["RavynInterceptor"], VoidType] = Void
        self._permissions_cache: dict[int, Any] | VoidType = Void
        self._lilya_permissions_cache: dict[int, Any] | VoidType = Void
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.parent = parent
        self.security = security or []
        self.tags = tags or []

        if namespace:
            routes = include(namespace, pattern)

        if routes:
            routes = self.resolve_route_path_handler(routes)

        self.__base_permissions__ = permissions or []
        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.__base_permissions__ or []
            if not is_ravyn_permission(permission)
        ]

        super().__init__(
            path=self.path,
            app=self.app,
            routes=routes,
            name=name,
            middleware=include_middleware,
            exception_handlers=exception_handlers,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            redirect_slashes=redirect_slashes,
            permissions=self.__lilya_permissions__,  # type: ignore
            before_request=before_request,
            after_request=after_request,
        )

        # Filter out the lilya unique permissions
        if self.__lilya_permissions__:
            self.lilya_permissions: Any = {
                index: permission in self.__lilya_permissions__
                for index, permission in enumerate(self.__lilya_permissions__)
            }
        else:
            self.lilya_permissions = {}

        # Making sure Ravyn uses the Ravyn permission system and not Lilya's.
        # Filter out the ravyn unique permissions
        if self.__base_permissions__:
            self.permissions: Any = {
                index: wrap_permission(permission)
                for index, permission in enumerate(permissions)
                if is_ravyn_permission(permission)
            }
        else:
            self.permissions = {}

        assert not (self.permissions and self.lilya_permissions), (
            "Use either `Ravyn permissions` OR `Lilya permissions`, not both."
        )

    def resolve_app_parent(self, app: Optional[Any]) -> Optional[Any]:
        """
        Resolves the owner of ChildRavyn or Ravyn iself.
        """
        from ravyn import ChildRavyn, Ravyn

        if app is not None and isinstance(app, (Ravyn, ChildRavyn)):
            app.parent = self
        return app

    def resolve_route_path_handler(
        self,
        routes: Sequence[Union[APIGateHandler, Include, HTTPHandler, WebSocketHandler]],
    ) -> list[Union[Gateway, WebSocketGateway, Include]]:
        """
        Make sure the paths are properly configured from the handler handler.
        The handler can be a Lilya function, an View or a HTTPHandler.

        LilyaBasePath() has a limitation of not allowing nested LilyaBasePath().

        Example:

            route_patterns = [
                LilyaBasePath(path='/my path', routes=[
                    LilyaBasePath(path='/another mount')
                ])
            ]


        Include() extends the LilyaBasePath and adds extras on the top. Allowing nested
        Include() also allows importing in different ways. Via qualified namespace
        or via list() but not both.

        Example:

            1. Root of the application, example, `urls.py`.

            route_patterns = [
                Include(path='/api/v1/', namespace='myapp.v1.urls'),
                Gateway(path='/example', handler=example_endpoint, name='example')
                ...
            ]

            2. Inside `myapp.v1.urls`

            from mysecondapp.urls import route_patterns

            route_patterns = [
                Include(path='/api/v2/', routes=route_patterns),
                Gateway(path='/another-example', handler=another_endpoint, name='example')
                ...
            ]

            3. Inside `mysecondapp.v1.urls`:

            route_patterns = [
                Gateway(path='/last-example', handler=another_endpoint, name='example')
                ...
            ]

        """
        routing: list[Union[Gateway, WebSocketGateway, Include]] = []

        for route in routes:  # pragma: no cover
            if isinstance(route, WebhookHandler):
                # fail later, a WebhookHandler is subclass of HTTPHandler, so pass down
                ...
            elif isinstance(route, HTTPHandler):
                route = Gateway(handler=route)
            elif isinstance(route, WebSocketHandler):
                route = WebSocketGateway(handler=route)

            if not isinstance(route, (Include, Gateway, WebSocketGateway)):
                raise ImproperlyConfigured("The route must be of type Gateway or Include")

            route.parent = self
            if isinstance(route, Include):
                routing.append(route)
                continue

            if isinstance(route.handler, (HTTPHandler, WebSocketHandler)):
                route.handler.parent = route
                routing.append(route)
                continue

            if is_class_and_subclass(route.handler, BaseController) or isinstance(
                route.handler, BaseController
            ):
                if not route.handler.parent:
                    route.handler = route.handler(parent=self)  # type: ignore

                route_handlers: list[Union[Gateway, WebhookGateway, Include]] = (
                    route.handler.get_routes(  # type: ignore
                        path=route.path,
                        middleware=route.middleware,
                        interceptors=self.interceptors,
                        permissions=route.permissions,
                        exception_handlers=route.exception_handlers,
                        before_request=route.before_request,
                        after_request=route.after_request,
                    )
                )
                if route_handlers:
                    routing.extend(
                        cast(
                            list[Union[Gateway, WebSocketGateway, Include]],
                            route_handlers,
                        )
                    )
        return routing

    async def handle_interceptors(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interceptors for the Include.
        This method ensures that the interceptors are set correctly
        and that they are compatible with the Lilya interceptors system.
        """
        # If no factories defined and no cache, nothing to do
        if (self._interceptors is Void) and not self.interceptors:
            return

        # Instantiate once and cache for reuse across requests
        if self._interceptors is Void:
            self._interceptors = [factory() for factory in self.interceptors]

        for interceptor in self._interceptors:
            if is_async_callable(interceptor.intercept):
                await interceptor.intercept(scope, receive, send)
            else:
                await run_in_threadpool(interceptor.intercept, scope, receive, send)

    async def handle_permissions(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles the permissions for the Include.
        This method ensures that the permissions are set correctly
        and that they are compatible with the Lilya permissions system.
        """
        # Use cached permissions if already computed
        if self._permissions_cache is not Void or self._lilya_permissions_cache is not Void:
            effective_permissions = (
                self._permissions_cache if self._permissions_cache is not Void else {}
            )
            effective_lilya_permissions = (
                self._lilya_permissions_cache if self._lilya_permissions_cache is not Void else {}
            )
        else:
            effective_permissions = self.permissions.copy() if self.permissions else {}
            effective_lilya_permissions = (
                self.lilya_permissions.copy() if self.lilya_permissions else {}
            )
            # Cache the computed permissions
            self._permissions_cache = effective_permissions or Void
            self._lilya_permissions_cache = effective_lilya_permissions or Void

        if not effective_permissions and not effective_lilya_permissions:
            return

        connection = Connection(scope=scope, receive=receive)

        if effective_lilya_permissions:
            await self.dispatch_allow_connection(
                effective_lilya_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=self.app,
            )
        else:
            dispatch_call = super().handle_dispatch
            await self.dispatch_allow_connection(
                effective_permissions,
                connection,
                scope,
                receive,
                send,
                dispatch_call=dispatch_call,
            )

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        In the call we need to make sure we call the permissions and validations first to
        assure it won't even reach the lower app and run the validation against.
        """
        await self.handle_interceptors(scope, receive, send)
        await self.handle_permissions(scope, receive, send)
        await super().handle_dispatch(scope, receive, send)
