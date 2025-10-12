from ravyn import Gateway, Ravyn, get
from ravyn.contrib.responses.shortcuts import abort
from ravyn.exceptions import HTTPException
from ravyn.responses import Response
from ravyn.testclient import TestClient


def test_abort_default_status(test_client_factory):
    @get()
    async def handler() -> None:
        abort(404)

    app = Ravyn(routes=[Gateway("/notfound", handler=handler)])
    client = TestClient(app)

    response = client.get("/notfound")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_abort_with_detail_string(test_client_factory):
    """
    Ensure abort() returns detail text in the body when provided.
    """

    @get()
    async def handler() -> None:
        abort(401, "Unauthorized access")

    app = Ravyn(routes=[Gateway("/unauthorized", handler=handler)])
    client = TestClient(app)

    response = client.get("/unauthorized")

    assert response.status_code == 401
    assert response.text == "Unauthorized access"


def test_abort_with_json_detail(test_client_factory):
    @get()
    async def handler() -> None:
        abort(400, {"error": "Bad Request", "code": 400})

    app = Ravyn(routes=[Gateway("/bad", handler=handler)])
    client = TestClient(app)

    response = client.get("/bad")

    assert response.status_code == 400
    assert response.json() == {"error": "Bad Request", "code": 400}


def test_abort_with_custom_headers(test_client_factory):
    """
    Ensure abort() sets custom headers properly.
    """

    @get()
    async def handler() -> None:
        abort(403, "Forbidden", headers={"X-Blocked": "true"})

    app = Ravyn(routes=[Gateway("/forbidden", handler=handler)])
    client = TestClient(app)

    response = client.get("/forbidden")

    assert response.status_code == 403
    assert response.headers["x-blocked"] == "true"
    assert "Forbidden" in response.text


def test_abort_does_not_continue_after_raise(test_client_factory):
    """
    Ensure that code after abort() is never executed.
    """

    @get()
    async def handler() -> None:
        abort(404, "Stop here")
        return {"message": "should never run"}  # pragma: no cover

    app = Ravyn(routes=[Gateway("/stop", handler=handler)])
    client = TestClient(app)

    response = client.get("/stop")

    assert response.status_code == 404
    assert "Stop here" in response.text


def test_abort_without_detail_uses_default_phrase(test_client_factory):
    @get()
    async def handler() -> None:
        abort(400)

    app = Ravyn(routes=[Gateway("/default-phrase", handler=handler)])
    client = TestClient(app)

    response = client.get("/default-phrase")

    assert response.status_code == 400
    assert response.json() == {"detail": "Bad Request"}  # default HTTP phrase


def test_abort_with_list_detail_returns_json(test_client_factory):
    @get()
    async def handler() -> None:
        abort(422, ["Invalid field", "Missing value"])

    app = Ravyn(routes=[Gateway("/list", handler=handler)])
    client = TestClient(app)

    response = client.get("/list")

    assert response.status_code == 422
    assert response.json() == ["Invalid field", "Missing value"]


def test_abort_allows_custom_response_passthrough(test_client_factory):
    @get()
    async def handler() -> None:
        response = Response("Custom body", status_code=418, headers={"X-Custom": "1"})
        raise HTTPException(status_code=418, response=response)

    app = Ravyn(routes=[Gateway("/passthrough", handler=handler)])
    client = TestClient(app)

    response = client.get("/passthrough")

    assert response.status_code == 418
    assert response.text == "Custom body"
    assert response.headers["x-custom"] == "1"


def test_abort_with_no_content_status_has_no_body(test_client_factory):
    @get()
    async def handler() -> None:
        abort(204)

    app = Ravyn(routes=[Gateway("/no-content", handler=handler)])
    client = TestClient(app)

    response = client.get("/no-content")

    assert response.status_code == 204
    assert not response.json()
