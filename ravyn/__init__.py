from typing import TYPE_CHECKING

from monkay import Monkay

__version__ = "0.2.2"

if TYPE_CHECKING:
    from lilya import status

    from ravyn.conf import settings
    from ravyn.conf.global_settings import RavynAPISettings, RavynSettings
    from ravyn.context import Context
    from ravyn.core.datastructures import JSON, Redirect, Stream, Template, UploadFile
    from ravyn.injector import Factory, Inject, Injects

    from .applications import ChildRavyn, Ravyn
    from .background import BackgroundTask, BackgroundTasks
    from .core.config import (
        CORSConfig,
        CSRFConfig,
        LoggingConfig,
        OpenAPIConfig,
        SessionConfig,
        StaticFilesConfig,
    )
    from .core.directives.decorator import directive
    from .core.interceptors.interceptor import RavynInterceptor
    from .core.protocols import AsyncDAOProtocol, DaoProtocol, MiddlewareProtocol
    from .exceptions import (
        HTTPException,
        ImproperlyConfigured,
        MethodNotAllowed,
        NotAuthenticated,
        NotFound,
        PermissionDenied,
        ServiceUnavailable,
        ValidationErrorException,
    )
    from .param_functions import Requires, Security
    from .params import Body, Cookie, File, Form, Header, Param, Path, Query
    from .permissions import AllowAny, BasePermission, DenyAll
    from .pluggables import Extension, Pluggable
    from .requests import Request
    from .responses import JSONResponse, Response, TemplateResponse
    from .routing.controllers import APIView, BaseController, Controller, SimpleAPIView, View
    from .routing.gateways import Gateway, WebhookGateway, WebSocketGateway
    from .routing.handlers import (
        delete,
        get,
        head,
        options,
        patch,
        post,
        put,
        route,
        trace,
        websocket,
    )
    from .routing.router import Host, Include, Router
    from .routing.webhooks import (
        whdelete,
        whget,
        whhead,
        whoptions,
        whpatch,
        whpost,
        whput,
        whroute,
        whtrace,
    )
    from .utils.decorators import observable
    from .websockets import WebSocket, WebSocketDisconnect, WebSocketState

__all__ = [
    "AllowAny",
    "APIView",
    "AsyncDAOProtocol",
    "BackgroundTask",
    "BackgroundTasks",
    "Body",
    "BaseController",
    "BasePermission",
    "ChildRavyn",
    "Context",
    "Controller",
    "CORSConfig",
    "CSRFConfig",
    "Cookie",
    "directive",
    "DaoProtocol",
    "DenyAll",
    "Ravyn",
    "RavynAPISettings",
    "RavynSettings",
    "RavynInterceptor",
    "Extension",
    "File",
    "Form",
    "Gateway",
    "Header",
    "HTTPException",
    "Include",
    "Inject",
    "Factory",
    "Host",
    "Injects",
    "ImproperlyConfigured",
    "JSON",
    "JSONResponse",
    "LoggingConfig",
    "MethodNotAllowed",
    "MiddlewareProtocol",
    "NotAuthenticated",
    "NotFound",
    "OpenAPIConfig",
    "Param",
    "Path",
    "PermissionDenied",
    "Pluggable",
    "Query",
    "Redirect",
    "Request",
    "Requires",
    "Response",
    "Router",
    "Security",
    "ServiceUnavailable",
    "SessionConfig",
    "SimpleAPIView",
    "StaticFilesConfig",
    "Stream",
    "Template",
    "TemplateResponse",
    "UploadFile",
    "ValidationErrorException",
    "View",
    "WebhookGateway",
    "WebSocket",
    "WebSocketDisconnect",
    "WebSocketGateway",
    "WebSocketState",
    "delete",
    "get",
    "head",
    "observable",
    "options",
    "patch",
    "post",
    "put",
    "route",
    "settings",
    "status",
    "trace",
    "websocket",
    "whdelete",
    "whhead",
    "whget",
    "whoptions",
    "whpatch",
    "whpost",
    "whput",
    "whroute",
    "whtrace",
]

_monkay: Monkay = Monkay(
    globals(),
    lazy_imports={
        "status": "lilya.status",
        "settings": ".conf.settings",
        "RavynAPISettings": ".conf.global_settings.RavynAPISettings",
        "RavynSettings": ".conf.global_settings.RavynSettings",
        "Context": "ravyn.context.Context",
        "JSON": ".core.datastructures.JSON",
        "Redirect": ".core.datastructures.Redirect",
        "Stream": ".core.datastructures.Stream",
        "Template": ".core.datastructures.Template",
        "UploadFile": ".core.datastructures.UploadFile",
        "Factory": "ravyn.injector.Factory",
        "Inject": "ravyn.injector.Inject",
        "ChildRavyn": ".applications.ChildRavyn",
        "Ravyn": ".applications.Ravyn",
        "BackgroundTask": ".background.BackgroundTask",
        "BackgroundTasks": ".background.BackgroundTasks",
        "CORSConfig": ".core.config.CORSConfig",
        "CSRFConfig": ".core.config.CSRFConfig",
        "OpenAPIConfig": ".core.config.OpenAPIConfig",
        "SessionConfig": ".core.config.SessionConfig",
        "StaticFilesConfig": ".core.config.StaticFilesConfig",
        "LoggingConfig": ".core.config.LoggingConfig",
        "RavynInterceptor": ".core.interceptors.interceptor.RavynInterceptor",
        "HTTPException": ".exceptions.HTTPException",
        "ImproperlyConfigured": ".exceptions.ImproperlyConfigured",
        "MethodNotAllowed": ".exceptions.MethodNotAllowed",
        "NotAuthenticated": ".exceptions.NotAuthenticated",
        "NotFound": ".exceptions.NotFound",
        "PermissionDenied": ".exceptions.PermissionDenied",
        "ServiceUnavailable": ".exceptions.ServiceUnavailable",
        "ValidationErrorException": ".exceptions.ValidationErrorException",
        "Requires": ".param_functions.Requires",
        "Security": ".param_functions.Security",
        "Body": ".params.Body",
        "Cookie": ".params.Cookie",
        "File": ".params.File",
        "Form": ".params.Form",
        "Header": ".params.Header",
        "Injects": ".injector.Injects",
        "Param": ".params.Param",
        "Path": ".params.Path",
        "Query": ".params.Query",
        "AllowAny": ".permissions.AllowAny",
        "BasePermission": ".permissions.BasePermission",
        "DenyAll": ".permissions.DenyAll",
        "Extension": ".pluggables.Extension",
        "Pluggable": ".pluggables.Pluggable",
        "AsyncDAOProtocol": ".core.protocols.AsyncDAOProtocol",
        "DaoProtocol": ".core.protocols.DaoProtocol",
        "MiddlewareProtocol": ".core.protocols.MiddlewareProtocol",
        "Request": ".requests.Request",
        "JSONResponse": ".responses.JSONResponse",
        "Response": ".responses.Response",
        "TemplateResponse": ".responses.TemplateResponse",
        "APIView": ".routing.controllers.APIView",
        "Controller": ".routing.controllers.Controller",
        "SimpleAPIView": ".routing.controllers.SimpleAPIView",
        "View": ".routing.controllers.View",
        "Gateway": ".routing.gateways.Gateway",
        "WebhookGateway": ".routing.gateways.WebhookGateway",
        "WebSocketGateway": ".routing.gateways.WebSocketGateway",
        "websocket": ".routing.handlers.websocket",  # rest is autogenerated
        "Host": ".routing.router.Host",
        "Include": ".routing.router.Include",
        "Router": ".routing.router.Router",
        "observable": ".utils.decorators.observable",
        "WebSocket": ".websockets.WebSocket",
        "WebSocketDisconnect": ".websockets.WebSocketDisconnect",
        "WebSocketState": ".websockets.WebSocketState",
        "directive": ".core.directives.decorator.directive",
    },
    skip_all_update=True,
    package="ravyn",
)
for name in ["delete", "get", "head", "options", "patch", "post", "put", "route", "trace"]:
    _monkay.add_lazy_import(name, f".routing.handlers.{name}")
    _monkay.add_lazy_import(f"wh{name}", f".routing.webhooks.wh{name}")
del name
