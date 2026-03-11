import asyncio
import json
from typing import Any, cast

from ravyn import Gateway, Ravyn, get
from ravyn.exceptions import HTTPException
from ravyn.middleware._exception_handlers import wrap_app_handling_exceptions
from ravyn.requests import Request
from ravyn.responses import PlainText, Response
from ravyn.utils.enums import MediaType

Message = dict[str, Any]
Scope = dict[str, Any]
Receive = Any
Send = Any
ASGIApp = Any


async def _receive() -> Message:
    return {"type": "http.request", "body": b"", "more_body": False}


def _http_scope() -> Scope:
    return cast(
        Scope,
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "query_string": b"",
        },
    )


def test_exception_middleware_handles_http_exception_in_request_context(
    test_client_factory,
) -> None:
    @get("/")
    async def fail_http(request: Request) -> None:
        raise HTTPException(status_code=400, detail="invalid request")

    app = Ravyn(routes=[Gateway("/", handler=fail_http)])

    with test_client_factory(app) as client:
        response = client.get("/")

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid request"}


def test_exception_middleware_converts_unhandled_exception_to_500_response(
    test_client_factory,
) -> None:
    @get("/")
    async def fail_runtime(request: Request) -> None:
        raise RuntimeError("boom")

    app = Ravyn(routes=[Gateway("/", handler=fail_runtime)])

    with test_client_factory(app) as client:
        response = client.get("/")

    assert response.status_code == 500
    assert response.json() == {"detail": "RuntimeError('boom')", "status_code": 500}


def test_exception_middleware_uses_registered_custom_exception_handler(
    test_client_factory,
) -> None:
    def runtime_handler(request: Request, exc: Exception) -> Response:
        return Response(content={"handled": str(exc)}, media_type=MediaType.JSON, status_code=418)

    @get("/")
    async def fail_runtime(request: Request) -> None:
        raise RuntimeError("custom boom")

    app = Ravyn(
        routes=[Gateway("/", handler=fail_runtime)],
        exception_handlers=cast(Any, {RuntimeError: runtime_handler}),
    )

    with test_client_factory(app) as client:
        response = client.get("/")

    assert response.status_code == 418
    assert response.json() == {"handled": "custom boom"}


def test_async_exit_stack_middleware_cleans_up_on_success(test_client_factory) -> None:
    cleanup_calls: list[str] = []

    async def cleanup() -> None:
        cleanup_calls.append("closed")

    @get("/")
    async def ok(request: Request) -> PlainText:
        request.scope["ravyn_astack"].push_async_callback(cleanup)
        return PlainText("ok")

    app = Ravyn(routes=[Gateway("/", handler=ok)])

    with test_client_factory(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert cleanup_calls == ["closed"]


def test_async_exit_stack_middleware_cleans_up_when_exception_raised(test_client_factory) -> None:
    cleanup_calls: list[str] = []

    async def cleanup() -> None:
        cleanup_calls.append("closed")

    @get("/")
    async def fail_after_registering_cleanup(request: Request) -> None:
        request.scope["ravyn_astack"].push_async_callback(cleanup)
        raise RuntimeError("cleanup still required")

    app = Ravyn(routes=[Gateway("/", handler=fail_after_registering_cleanup)])

    with test_client_factory(app) as client:
        response = client.get("/")

    assert response.status_code == 500
    assert cleanup_calls == ["closed"]


def test_wrap_app_handling_exceptions_re_raises_without_matching_handler() -> None:
    async def run() -> list[Message]:
        scope = _http_scope()
        scope["lilya.exception_handlers"] = ({}, {})
        events: list[Message] = []

        async def send(message: Message) -> None:
            events.append(message)

        conn = Request(scope, cast(Receive, _receive), cast(Send, send))

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            raise ValueError("missing-handler")

        wrapped = wrap_app_handling_exceptions(cast(ASGIApp, app), conn)
        await wrapped(scope, cast(Receive, _receive), cast(Send, send))
        return events

    has_error = False
    try:
        asyncio.run(run())
    except ValueError as exc:
        has_error = True
        assert str(exc) == "missing-handler"

    assert has_error is True


def test_wrap_app_handling_exceptions_uses_status_handler_for_http_exception() -> None:
    async def run() -> list[Message]:
        async def handler(request: Request, exc: Exception) -> Response:
            return Response(
                content={"status": "handled"}, media_type=MediaType.JSON, status_code=422
            )

        scope = _http_scope()
        scope["lilya.exception_handlers"] = ({}, {400: handler})
        events: list[Message] = []

        async def send(message: Message) -> None:
            events.append(message)

        conn = Request(scope, cast(Receive, _receive), cast(Send, send))

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            raise HTTPException(status_code=400, detail="bad request")

        wrapped = wrap_app_handling_exceptions(cast(ASGIApp, app), conn)
        await wrapped(scope, cast(Receive, _receive), cast(Send, send))
        return events

    events = asyncio.run(run())
    assert events[0]["type"] == "http.response.start"
    assert events[0]["status"] == 422
    assert events[1]["type"] == "http.response.body"
    assert json.loads(events[1]["body"]) == {"status": "handled"}
