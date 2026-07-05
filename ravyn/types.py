from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Mapping,
    Type,
    TypeVar,
    Union,
    get_args,
)

from lilya.middleware import DefineMiddleware
from lilya.types import ASGIApp
from typing_extensions import Literal

from ravyn.background import BackgroundTask, BackgroundTasks
from ravyn.exceptions import MissingDependency
from ravyn.routing.gateways import WebSocketGateway
from ravyn.routing.router import Include

try:
    from ravyn.core.config.template import TemplateConfig as TemplateConfig
except MissingDependency:
    TemplateConfig = Any  # type: ignore

if TYPE_CHECKING:
    from ravyn.applications import Application, Ravyn
    from ravyn.conf.global_settings import RavynSettings  # noqa
    from ravyn.core.datastructures import Cookie, ResponseHeader
    from ravyn.injector import Inject
    from ravyn.requests import Request
    from ravyn.responses import Response
    from ravyn.routing.controllers.base import BaseController  # noqa
    from ravyn.routing.gateways import Gateway, WebhookGateway  # noqa
    from ravyn.routing.router import (
        HTTPHandler as HTTPHandler,  # noqa
        Router,
        WebSocketHandler as WebSocketHandler,  # noqa
    )
    from ravyn.websockets import WebSocket  # noqa

    # prevent ciruclar and unneccessary imports
    # by only exposing it when type checking
    # also only expose if available otherwise fallback to Any
    try:
        from asyncz.schedulers.types import SchedulerType as SchedulerType  # noqa
    except ImportError:
        SchedulerType = Any  # type: ignore
else:
    HTTPHandler = Any
    Application = Any
    Message = Any
    Receive = Any
    Scope = Any
    Send = Any
    BaseHTTPMiddleware = Any
    Inject = Any
    Request = Any
    WebSocket = Any
    State = Any
    Response = Any
    ResponseHeader = Any
    Cookie = Any
    Router = Any
    MiddlewareProtocol = Any
    BaseController = Any
    Gateway = Any
    WebhookGateway = Any
    Ravyn = Any
    RavynSettings = Any
    SchedulerType = Any

AsyncAnyCallable = Callable[..., Awaitable[Any]]
HTTPMethod = Literal[
    "GET",
    "QUERY",
    "POST",
    "DELETE",
    "PATCH",
    "PUT",
    "HEAD",
    "OPTIONS",
    "TRACE",
]
HTTPMethods = get_args(HTTPMethod)

Middleware = DefineMiddleware

ResponseType = Type[Response]

Dependencies = Union[dict[str, Inject], dict[str, Any], Any]

ExceptionType = TypeVar("ExceptionType", bound=Exception)
ExceptionHandler = Callable[[Request, ExceptionType], Response]
ExceptionHandlerMap = Mapping[Union[int, Type[Exception]], ExceptionHandler]

_ReservedKwargs = Literal[
    "request", "socket", "headers", "query", "cookies", "state", "data", "payload"
]

ReservedKwargs = get_args(_ReservedKwargs)

ResponseHeaders = dict[str, ResponseHeader]
ResponseCookies = list[Cookie]
AsyncAnyCallable = Callable[..., Awaitable[Any]]

DatetimeType = TypeVar("DatetimeType", bound=datetime)

ParentType = Union[BaseController, Router, Gateway, WebSocketGateway, Ravyn, Include, Application]
APIGateHandler = Union[
    Gateway,
    WebSocketGateway,
]

RouteParent = Union[
    "Router", "Include", ASGIApp, "Gateway", "WebSocketGateway", "WebhookGateway", "BaseController"
]

BackgroundTaskType = Union[BackgroundTask, BackgroundTasks]
SecurityScheme = dict[str, list[str]]

ConnectionType = Union["Request", "WebSocket"]
DictStr = dict[str, str]
DictAny = dict[str, Any]
SettingsType = Type["RavynSettings"]

LifeSpanHandler = Union[Callable[[], None], Callable[[], Awaitable[None]]]
