from asyncio import sleep as async_sleep
from json import loads
from pathlib import Path
from time import sleep
from typing import Any, AsyncGenerator, AsyncIterator, Generator, Iterator

import pytest
from lilya import status
from lilya.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainText,
    RedirectResponse,
    Response as LilyaResponse,
    StreamingResponse,
)
from lilya.status import HTTP_200_OK, HTTP_308_PERMANENT_REDIRECT
from pydantic import ValidationError

from ravyn.background import BackgroundTask
from ravyn.core.datastructures import Cookie, File, Redirect, ResponseHeader, Stream, Template
from ravyn.core.transformers.signature import SignatureFactory
from ravyn.requests import Request
from ravyn.responses import Response, TemplateResponse
from ravyn.responses.encoders import UJSONResponse
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get, post, route
from ravyn.routing.router import HTTPHandler
from ravyn.testclient import create_client
from ravyn.utils.enums import HttpMethod, MediaType
from tests.models import Individual, IndividualFactory


def my_generator() -> Generator[str, None, None]:  # pragma: no cover
    count = 0
    while True:
        count += 1
        yield str(count)


async def my_async_generator() -> "AsyncGenerator[str, None]":  # pragma: no cover
    count = 0
    while True:
        count += 1
        yield str(count)


class MySyncIterator:  # pragma: no cover
    def __init__(self) -> None:
        self.delay = 0.01
        self.i = 0
        self.to = 0.1

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        i = self.i
        if i >= self.to:
            raise StopAsyncIteration
        self.i += 1
        if i:
            sleep(self.delay)
        return str(i)


class MyAsyncIterator:  # pragma: no cover
    def __init__(self) -> None:
        self.delay = 0.01
        self.i = 0
        self.to = 0.1

    def __aiter__(self) -> AsyncIterator[str]:
        return self

    async def __anext__(self) -> str:
        i = self.i
        if i >= self.to:
            raise StopAsyncIteration
        self.i += 1
        if i:
            await async_sleep(self.delay)
        return str(i)


@pytest.mark.asyncio()
async def test_to_response_async_await() -> None:
    @route(methods=[HttpMethod.POST], path="/person")
    async def test_function(data: Individual) -> Individual:
        assert isinstance(data, Individual)
        return data

    person_instance = IndividualFactory.build()
    test_function.signature_model = SignatureFactory(
        test_function.fn,
        set(),  # type:ignore[arg-type]
    ).create_signature()

    # we need the encoders
    with create_client([]):
        response = await test_function.to_response(
            data=test_function.fn(data=person_instance),
            app=None,  # type: ignore
        )
        assert loads(response.body) == person_instance.model_dump()


@pytest.mark.asyncio()
async def test_to_response_async_await_with_post_handler() -> None:
    @post(path="/person")
    async def test_function(data: Individual) -> Individual:
        assert isinstance(data, Individual)
        return data

    person_instance = IndividualFactory.build()
    test_function.signature_model = SignatureFactory(
        test_function.fn,
        set(),  # type:ignore[arg-type]
    ).create_signature()

    # we need the encoders
    with create_client([]):
        response = await test_function.to_response(
            data=test_function.fn(data=person_instance),
            app=None,  # type: ignore
        )
        assert loads(response.body) == person_instance.model_dump()


@pytest.mark.asyncio()
async def test_to_response_returning_ravyn_response() -> None:
    @get(path="/test")
    def test_function() -> Response:
        return Response(status_code=HTTP_200_OK, media_type=MediaType.TEXT, content="ok")

    with create_client(test_function) as client:
        route: HTTPHandler = client.app.routes[0].handler  # type: ignore
        response = await route.to_response(data=route.fn(), app=None)  # type: ignore
        assert isinstance(response, Response)


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "expected_response",
    [
        Response(status_code=HTTP_200_OK, content=b"abc", media_type=MediaType.TEXT),
        LilyaResponse(status_code=HTTP_200_OK, content=b"abc"),
        PlainText(content="abc"),
        HTMLResponse(content="<div><span/></div"),
        JSONResponse(status_code=HTTP_200_OK, content={}),
        UJSONResponse(status_code=HTTP_200_OK, content={}),
        RedirectResponse(url="/person"),
        StreamingResponse(status_code=HTTP_200_OK, content=MySyncIterator()),
        FileResponse("./test_to_response.py"),
    ],
)
async def test_to_response_returning_redirect_starlette_response(
    expected_response: LilyaResponse,
) -> None:
    @get(path="/test")
    def test_function() -> LilyaResponse:
        return expected_response

    with create_client(test_function) as client:
        route = client.app.routes[0].handler  # type: ignore
        response = await route.to_response(data=route.fn(), app=None)  # type: ignore
        assert isinstance(response, LilyaResponse)
        assert response is expected_response


@pytest.mark.asyncio()
async def test_to_response_returning_redirect_response() -> None:
    background_task = BackgroundTask(lambda: "")

    @get(
        path="/test",
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        response_headers={"local-header": ResponseHeader(value="123")},
        response_cookies=[
            Cookie(key="redirect-cookie", value="aaa"),
            Cookie(key="general-cookie", value="xxx"),
        ],
    )
    def test_function() -> Redirect:
        return Redirect(
            path="/somewhere-else",
            headers={"response-header": "abc"},
            cookies=[Cookie(key="redirect-cookie", value="xyz")],
            background=background_task,
        )

    with create_client(test_function) as client:
        route = client.app.routes[0].handler
        response = await route.to_response(data=route.fn(), app=None)  # type: ignore
        assert isinstance(response, RedirectResponse)
        assert response.headers["location"] == "/somewhere-else"
        assert response.headers["local-header"] == "123"
        assert response.headers["response-header"] == "abc"

        cookies = response.headers.getlist("set-cookie")
        assert len(cookies) == 2
        assert cookies[0] == "redirect-cookie=xyz; Path=/; SameSite=lax"
        assert cookies[1] == "general-cookie=xxx; Path=/; SameSite=lax"
        assert response.background == background_task


def test_to_response_returning_redirect_response_from_redirect() -> None:
    @get(path="/", status_code=status.HTTP_200_OK)
    def proxy_handler() -> UJSONResponse:
        return UJSONResponse({"message": "redirected by /test"})

    @get(path="/")
    def redirect_handler(request: Request) -> RedirectResponse:
        return Redirect(path="/proxy").to_response(
            headers={},
            media_type=MediaType.JSON,
            status_code=HTTP_308_PERMANENT_REDIRECT,
            app=request.app,
        )

    routes = [
        Gateway(path="/proxy", handler=proxy_handler),
        Gateway(path="/test", handler=redirect_handler),
    ]

    with create_client(routes=routes) as client:
        response = client.get("/test")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "redirected by /test"}


@pytest.mark.asyncio()
async def test_to_response_returning_file_response() -> None:
    current_file_path = Path(__file__).resolve()
    filename = Path(__file__).name
    background_task = BackgroundTask(lambda: "")

    @get(
        path="/test",
        response_headers={"local-header": ResponseHeader(value="123")},
        response_cookies=[
            Cookie(key="redirect-cookie", value="aaa"),
            Cookie(key="general-cookie", value="xxx"),
        ],
    )
    def test_function() -> File:
        return File(
            path=current_file_path,
            filename=filename,
            headers={"response-header": "abc"},
            cookies=[Cookie(key="file-cookie", value="xyz")],
            background=background_task,
        )

    with create_client(test_function) as client:
        route = client.app.routes[0].handler  # type: ignore
        response = await route.to_response(data=route.fn(), app=None)  # type: ignore

        assert isinstance(response, FileResponse)
        assert response.stat_result
        assert response.path == str(current_file_path)
        assert response.filename == filename
        assert response.headers["local-header"] == "123"
        assert response.headers["response-header"] == "abc"

        cookies = response.headers.getlist("set-cookie")
        assert len(cookies) == 3
        assert cookies[0] == "file-cookie=xyz; Path=/; SameSite=lax"
        assert cookies[1] == "general-cookie=xxx; Path=/; SameSite=lax"
        assert response.background == background_task


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "iterator, should_raise",
    [
        [my_generator(), False],
        [my_async_generator(), False],
        [MySyncIterator(), False],
        [MyAsyncIterator(), False],
        [my_generator, False],
        [my_async_generator, False],
        [MyAsyncIterator, False],
        [MySyncIterator, False],
        [{"key": 1}, True],
    ],
)
async def test_to_response_streaming_response(
    iterator: Any, should_raise: bool
) -> None:  # pragma: no cover
    if not should_raise:
        background_task = BackgroundTask(lambda: "")

        @get(
            path="/test",
            response_headers={"local-header": ResponseHeader(value="123")},
            response_cookies=[
                Cookie(key="redirect-cookie", value="aaa"),
                Cookie(key="general-cookie", value="xxx"),
            ],
        )
        def test_function() -> Stream:
            return Stream(
                iterator=iterator,
                headers={"response-header": "abc"},
                cookies=[Cookie(key="streaming-cookie", value="xyz")],
                background=background_task,
            )

        with create_client(test_function) as client:
            route = client.app.routes[0].handler  # type: ignore
            response = await route.to_response(data=route.fn(), app=None)  # type: ignore
            assert isinstance(response, StreamingResponse)
            assert response.headers["local-header"] == "123"
            assert response.headers["response-header"] == "abc"

            cookies = response.headers.getlist("set-cookie")
            assert len(cookies) == 3
            assert cookies[0] == "streaming-cookie=xyz; Path=/; SameSite=lax"
            assert cookies[1] == "general-cookie=xxx; Path=/; SameSite=lax"
            assert response.background == background_task
    else:
        with pytest.raises(ValidationError):
            Stream(iterator=iterator)


@pytest.mark.asyncio()
async def func_to_response_template_response() -> None:  # pragma: no cover
    background_task = BackgroundTask(lambda: "")

    @get(
        path="/test",
        response_headers={"local-header": ResponseHeader(value="123")},
        response_cookies=[
            Cookie(key="redirect-cookie", value="aaa"),
            Cookie(key="general-cookie", value="xxx"),
        ],
    )
    def test_function() -> Template:
        return Template(
            name="test.template",
            context={},
            headers={"response-header": "abc"},
            cookies=[Cookie(key="template-cookie", value="xyz")],
            background=background_task,
        )

    with create_client(test_function) as client:
        route = client.app.routes[0].handler  # type: ignore

        response = await route.to_response(data=route.fn(), app=None)  # type: ignore
        assert isinstance(response, TemplateResponse)
        assert response.headers["local-header"] == "123"
        assert response.headers["response-header"] == "abc"

        cookies = response.headers.getlist("set-cookie")
        assert len(cookies) == 2
        assert cookies[0] == "template-cookie=xyz; Path=/; SameSite=lax"
        assert cookies[1] == "general-cookie=xxx; Path=/; SameSite=lax"
        assert response.background == background_task
