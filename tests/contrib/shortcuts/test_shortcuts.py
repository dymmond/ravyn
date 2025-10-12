import asyncio
import json
from typing import Any

import pytest
from lilya.responses import JSONResponse, Response, StreamingResponse

from ravyn import Gateway, Ravyn, get
from ravyn.contrib.responses.shortcuts import (
    empty,
    forbidden,
    json_error,
    not_found,
    send_json,
    stream,
    unauthorized,
)
from ravyn.responses import JSONResponse as RavynJSONResponse
from ravyn.testclient import TestClient

pytestmark = pytest.mark.anyio


def test_send_json_returns_json_response():
    data = {"key": "value"}
    response = send_json(data)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert json.loads(response.body.decode()) == data
    assert response.headers["content-type"].startswith("application/json")


def test_send_json_with_custom_status_and_headers():
    data = {"ok": True}
    response = send_json(data, status_code=201, headers={"X-Test": "true"})

    assert response.status_code == 201
    assert response.headers["x-test"] == "true"
    assert json.loads(response.body.decode()) == {"ok": True}


def test_send_json_works_with_list_payload():
    response = send_json([1, 2, 3])
    assert json.loads(response.body.decode()) == [1, 2, 3]


def test_json_error_from_string_message():
    response = json_error("Invalid input")

    assert isinstance(response, JSONResponse)
    data = json.loads(response.body.decode())

    assert data == {"error": "Invalid input"}
    assert response.status_code == 400


def test_json_error_from_dict_message():
    payload = {"error": "Bad", "code": 400}
    response = json_error(payload, status_code=422)

    assert json.loads(response.body.decode()) == payload
    assert response.status_code == 422


def test_json_error_with_headers():
    response = json_error("Oops", headers={"X-Failed": "1"})
    assert response.headers["x-failed"] == "1"


@pytest.mark.parametrize("backend", ["asyncio", "trio"])
def test_stream_with_sync_generator(backend):
    def gen():
        for i in range(3):
            yield f"Line {i}\n"

    @get()
    async def endpoint() -> Any:
        return stream(gen(), mimetype="text/plain")

    app = Ravyn(routes=[Gateway("/stream", handler=endpoint)])
    client = TestClient(app, backend=backend)

    response = client.get("/stream")
    assert response.status_code == 200
    assert "Line 0" in response.text
    assert response.headers["content-type"].startswith("text/plain")


@pytest.mark.parametrize("backend", ["asyncio"])
def test_stream_with_async_generator(backend):
    async def gen():
        for i in range(2):
            yield f"Chunk {i}\n"
            await asyncio.sleep(0.01)

    @get()
    async def endpoint() -> Any:
        return stream(gen(), mimetype="text/event-stream")

    app = Ravyn(routes=[Gateway("/astream", handler=endpoint)])
    client = TestClient(app, backend=backend)

    response = client.get("/astream")

    assert response.status_code == 200
    assert "Chunk 0" in response.text
    assert "Chunk 1" in response.text
    assert response.headers["content-type"].startswith("text/event-stream")


def test_stream_with_custom_headers():
    def gen():
        yield "data\n"

    response = stream(gen(), headers={"X-Stream": "true"})
    assert isinstance(response, StreamingResponse)
    assert response.headers["x-stream"] == "true"


def test_empty_returns_204_by_default():
    response = empty()
    assert isinstance(response, Response)
    assert response.status_code == 204
    assert response.body == b""


def test_empty_with_custom_status_and_headers():
    response = empty(status_code=304, headers={"X-NoContent": "yes"})

    assert response.status_code == 304
    assert response.headers["x-nocontent"] == "yes"


def test_unauthorized_returns_json_response():
    response = unauthorized("Login required")

    assert isinstance(response, JSONResponse)
    assert response.status_code == 401

    data = json.loads(response.body.decode())

    assert data == {"error": "Login required"}
    assert response.headers["content-type"].startswith("application/json")


def test_forbidden_returns_json_response():
    response = forbidden("Access denied")

    assert isinstance(response, JSONResponse)
    assert response.status_code == 403

    data = json.loads(response.body.decode())

    assert data == {"error": "Access denied"}
    assert response.headers["content-type"].startswith("application/json")


def test_not_found_returns_json_response():
    response = not_found("Item not found")

    assert isinstance(response, JSONResponse)
    assert response.status_code == 404

    data = json.loads(response.body.decode())

    assert data == {"error": "Item not found"}
    assert response.headers["content-type"].startswith("application/json")


@pytest.mark.parametrize("backend", ["asyncio", "trio"])
def test_unauthorized_in_route(backend):
    @get()
    async def endpoint() -> RavynJSONResponse:
        return unauthorized()

    app = Ravyn(routes=[Gateway("/unauthorized", handler=endpoint)])
    client = TestClient(app, backend=backend)

    response = client.get("/unauthorized")

    assert response.status_code == 401
    assert "Unauthorized" in response.text
    assert response.headers["content-type"].startswith("application/json")


@pytest.mark.parametrize("backend", ["asyncio", "trio"])
def test_forbidden_in_route(backend):
    @get()
    async def endpoint() -> RavynJSONResponse:
        return forbidden("Stop right there")

    app = Ravyn(routes=[Gateway("/forbidden", handler=endpoint)])
    client = TestClient(app, backend=backend)

    response = client.get("/forbidden")

    assert response.status_code == 403
    assert "Stop right there" in response.text
    assert response.headers["content-type"].startswith("application/json")


@pytest.mark.parametrize("backend", ["asyncio", "trio"])
def test_not_found_in_route(backend):
    @get()
    async def endpoint() -> RavynJSONResponse:
        return not_found("User not found")

    app = Ravyn(routes=[Gateway("/notfound", handler=endpoint)])
    client = TestClient(app, backend=backend)

    response = client.get("/notfound")

    assert response.status_code == 404
    assert "User not found" in response.text
    assert response.headers["content-type"].startswith("application/json")


def test_shortcuts_accept_custom_headers():
    response = unauthorized("No token", headers={"X-Failed": "true"})
    assert response.headers["x-failed"] == "true"

    response = forbidden("Forbidden", headers={"X-Reason": "policy"})
    assert response.headers["x-reason"] == "policy"

    response = not_found("Lost", headers={"X-Missing": "object"})
    assert response.headers["x-missing"] == "object"
