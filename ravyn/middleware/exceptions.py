from typing import Any, Callable, Mapping, Optional, Type, Union

from lilya import status
from lilya.compat import is_async_callable
from lilya.concurrency import run_in_threadpool
from lilya.exceptions import HTTPException as LilyaException
from lilya.middleware.exceptions import ExceptionMiddleware as LilyaExceptionMiddleware
from lilya.responses import Response as LilyaResponse
from lilya.types import ASGIApp, Receive, Scope, Send
from pydantic import BaseModel

from ravyn.exception_handlers import http_exception_handler
from ravyn.exceptions import HTTPException, WebSocketException
from ravyn.middleware._exception_handlers import wrap_app_handling_exceptions
from ravyn.middleware.errors import ServerErrorMiddleware
from ravyn.requests import Request
from ravyn.responses import Response
from ravyn.types import ExceptionHandler, ExceptionHandlerMap
from ravyn.utils.enums import MediaType, ScopeType
from ravyn.websockets import WebSocket


class ExceptionMiddleware(LilyaExceptionMiddleware):
    """
    Reimplementation of the Exception Middleware.
    """

    def __init__(
        self,
        app: ASGIApp,
        handlers: Optional[Mapping[Any, Callable[[Request, Exception], Response]]] = None,
        debug: bool = False,
    ) -> None:
        super().__init__(app=app, debug=debug)
        self.app = app
        self.debug = debug
        self._status_handlers: dict[int, Callable] = {}
        self._exception_handlers: dict[Type[Exception], Callable] = {
            HTTPException: http_exception_handler,
            LilyaException: http_exception_handler,
            WebSocketException: self.websocket_exception,
        }
        if handlers is not None:
            for key, value in handlers.items():
                self.add_exception_handler(key, value)  # type: ignore

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:  # pragma: no cover
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        scope["lilya.exception_handlers"] = (
            self._exception_handlers,
            self._status_handlers,
        )

        conn: Union[Request, WebSocket]
        if scope["type"] == "http":
            conn = Request(scope, receive, send)
        else:
            conn = WebSocket(scope, receive, send)
        await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)


class ResponseContent(BaseModel):
    detail: Optional[str]
    extra: Optional[Union[dict[str, Any], list[Any]]] = None
    headers: Optional[dict[str, str]] = None
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR


class RavynAPIException:  # pragma: no cover
    def __init__(
        self,
        app: "ASGIApp",
        debug: bool,
        exception_handlers: "ExceptionHandlerMap",
        error_handler: Optional[Callable] = None,
    ) -> None:
        self.app = app
        self.exception_handlers = exception_handlers
        self.debug = debug
        self.error_handler = error_handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self.app(scope, receive, send)
        except Exception as ex:
            if scope["type"] == ScopeType.HTTP:
                exception_handler = self.get_exception_handler(self.exception_handlers, ex)
                if (
                    exception_handler is None
                    and scope.get("_ravyn_route_boundary")
                    and isinstance(ex, (HTTPException, LilyaException))
                ):
                    exception_handler = http_exception_handler  # type: ignore
                if exception_handler is None:
                    exception_handler = self.default_http_exception_handler  # type: ignore
                request = Request(scope, receive, send)
                if is_async_callable(exception_handler):
                    response = await exception_handler(request, ex)
                else:
                    response = await run_in_threadpool(exception_handler, request, ex)
                await response(scope, receive, send)
                return

            if isinstance(ex, WebSocketException):
                code = ex.code
                reason = ex.detail
            elif isinstance(ex, LilyaException):
                code = ex.status_code + 4000
                reason = ex.detail
            else:
                code = status.HTTP_500_INTERNAL_SERVER_ERROR + 4000
                reason = repr(ex)

            event = {"type": "websocket.close", "code": code, "reason": reason}
            await send(event)

    def default_http_exception_handler(self, request: Request, exc: Exception) -> "LilyaResponse":
        """Default handler for exceptions subclassed from HTTPException."""
        status_code = (
            exc.status_code
            if isinstance(exc, LilyaException)
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR and self.debug:
            server_error = ServerErrorMiddleware(app=self.app, handler=self.error_handler)
            return server_error.debug_response(request=request, exc=exc)
        return self.create_exception_response(exc)

    def create_exception_response(self, exc: Exception) -> Response:
        if isinstance(exc, (HTTPException, LilyaException)):
            content = ResponseContent(detail=exc.detail, status_code=exc.status_code)
            if isinstance(exc, HTTPException):
                extra = exc.extra.get("extra", {})
                if extra:
                    content.extra = extra
        else:
            content = ResponseContent(detail=repr(exc))
        return Response(
            media_type=MediaType.JSON,
            content=content.model_dump(exclude_none=True),
            status_code=content.status_code,
            headers=(exc.headers if isinstance(exc, (HTTPException, LilyaException)) else None),
        )

    def get_exception_handler(
        self,
        exception_handlers: ExceptionHandlerMap,
        exc: Exception,
    ) -> Union[ExceptionHandler, None]:
        status_code = (
            exc.status_code
            if isinstance(exc, LilyaException)
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        if not exception_handlers:
            return None

        handler = self.exception_handlers.get(status_code)
        if handler is not None:
            return handler

        for exc_cls in type(exc).__mro__:
            handler = self.exception_handlers.get(exc_cls)
            if handler is not None:
                return handler

        return None
