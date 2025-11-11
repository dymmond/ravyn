from json import JSONDecodeError
from unittest.mock import patch

import pytest

from ravyn.requests import Request
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get
from ravyn.testclient import create_client


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_request_empty_body_to_json() -> None:
    with patch.object(Request, "body", return_value=b""):
        request_empty_payload: Request = Request(scope={"type": "http"})
        request_json = await request_empty_payload.json()
        assert request_json is None


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_request_invalid_body_to_json() -> None:
    with patch.object(Request, "body", return_value=b"invalid"), pytest.raises(JSONDecodeError):
        request_empty_payload: Request = Request(scope={"type": "http"})
        await request_empty_payload.json()


@pytest.mark.asyncio()  # type: ignore[misc]
async def test_request_valid_body_to_json() -> None:
    with patch.object(Request, "body", return_value=b'{"test": "valid"}'):
        request_empty_payload: Request = Request(scope={"type": "http"})
        request_json = await request_empty_payload.json()
        assert request_json == {"test": "valid"}


def test_request_resolve_url() -> None:
    @get(path="/proxy")
    def proxy() -> None:
        """ """

    @get(path="/test")
    def root(request: Request) -> dict:
        return {"url": request.url_for("proxy")}

    with create_client(
        routes=[
            Gateway(path="/", handler=proxy, name="proxy"),
            Gateway(path="/", handler=root),
        ]
    ) as client:
        response = client.get("/test")
        assert response.json() == {"url": "http://testserver/proxy"}
