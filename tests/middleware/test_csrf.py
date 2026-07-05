from typing import Optional

import pytest
from lilya import status
from lilya.status import HTTP_200_OK, HTTP_201_CREATED

from ravyn.core.config import CSRFConfig
from ravyn.routing.gateways import Gateway, WebSocketGateway
from ravyn.routing.handlers import delete, get, patch, post, put, query, websocket
from ravyn.testclient import create_client
from ravyn.utils.crypto import get_random_secret_key
from ravyn.websockets import WebSocket


@get(path="/")
def get_handler() -> None: ...


@post(path="/")
def post_handler() -> None: ...


@query(path="/")
def query_handler() -> dict:
    return {"method": "QUERY"}


@put(path="/")
def put_handler() -> None:
    """ """


@delete(path="/")
def delete_handler() -> None:
    """ """


@patch(path="/")
def patch_handler() -> None:
    """ """


def test_csrf_successful_flow() -> None:
    with create_client(
        routes=[
            Gateway(path="/", handler=get_handler),
            Gateway(path="/", handler=post_handler),
        ],
        csrf_config=CSRFConfig(secret=get_random_secret_key()),
    ) as client:
        response = client.get("/")
        assert response.status_code == HTTP_200_OK

        csrf_token: Optional[str] = response.cookies.get("csrftoken")  # type: ignore[no-untyped-call]
        assert csrf_token is not None

        set_cookie_header = response.headers.get("set-cookie")
        assert set_cookie_header is not None
        assert set_cookie_header.split("; ") == [
            f"csrftoken={csrf_token}",
            "Path=/",
            "SameSite=lax",
        ]

        response = client.post("/", headers={"x-csrftoken": csrf_token})
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "method",
    ["POST", "PUT", "DELETE", "PATCH"],
)
def test_unsafe_method_fails_without_csrf_header(method: str) -> None:
    with create_client(
        routes=[
            Gateway(path="/", handler=get_handler),
            Gateway(path="/", handler=post_handler),
            Gateway(path="/", handler=put_handler),
            Gateway(path="/", handler=delete_handler),
            Gateway(path="/", handler=patch_handler),
        ],
        csrf_config=CSRFConfig(secret=get_random_secret_key()),
    ) as client:
        response = client.get("/")
        assert response.status_code == HTTP_200_OK

        csrf_token: Optional[str] = response.cookies.get("csrftoken")  # type: ignore[no-untyped-call]
        assert csrf_token is not None

        response = client.request(method, "/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        data = response.json()
        assert data["detail"] == "CSRF token verification failed."
        assert data["status_code"] == 403


def test_query_method_is_csrf_safe_without_header() -> None:
    with create_client(
        routes=[Gateway(path="/", handler=query_handler)],
        csrf_config=CSRFConfig(secret=get_random_secret_key()),
    ) as client:
        response = client.query("/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"method": "QUERY"}


def test_invalid_csrf_token() -> None:
    with create_client(
        routes=[
            Gateway(path="/", handler=get_handler),
            Gateway(path="/", handler=post_handler),
        ],
        csrf_config=CSRFConfig(secret=get_random_secret_key()),
    ) as client:
        response = client.get("/")
        assert response.status_code == HTTP_200_OK

        csrf_token: Optional[str] = response.cookies.get("csrftoken")  # type: ignore[no-untyped-call]
        assert csrf_token is not None

        response = client.post("/", headers={"x-csrftoken": csrf_token + "invalid"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        data = response.json()
        assert data["detail"] == "CSRF token verification failed."
        assert data["status_code"] == 403


def test_csrf_token_too_short() -> None:
    with create_client(
        routes=[
            Gateway(path="/", handler=get_handler),
            Gateway(path="/", handler=post_handler),
        ],
        csrf_config=CSRFConfig(secret=get_random_secret_key()),
    ) as client:
        response = client.get("/")
        assert response.status_code == HTTP_200_OK

        assert "csrftoken" in response.cookies

        response = client.post("/", headers={"x-csrftoken": "too-short"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        data = response.json()
        assert data["detail"] == "CSRF token verification failed."
        assert data["status_code"] == 403


def test_websocket_ignored() -> None:
    @websocket(path="/")
    async def websocket_handler(socket: WebSocket) -> None:
        await socket.accept()
        await socket.send_json({"data": "123"})
        await socket.close()

    with (
        create_client(
            routes=[WebSocketGateway(path="/", handler=websocket_handler)],
            csrf_config=CSRFConfig(secret=get_random_secret_key()),
        ) as client,
        client.websocket_connect("/") as ws,
    ):
        response = ws.receive_json()
        assert response is not None


def test_custom_csrf_config() -> None:
    with create_client(
        base_url="http://test.com",
        routes=[
            Gateway(path="/", handler=get_handler),
            Gateway(path="/", handler=post_handler),
        ],
        csrf_config=CSRFConfig(
            secret=get_random_secret_key(),
            cookie_name="custom-csrftoken",
            header_name="x-custom-csrftoken",
        ),
    ) as client:
        response = client.get("/")
        assert response.status_code == HTTP_200_OK

        csrf_token: Optional[str] = response.cookies.get("custom-csrftoken")  # type: ignore[no-untyped-call]
        assert csrf_token is not None

        set_cookie_header = response.headers.get("set-cookie")
        assert set_cookie_header is not None
        assert set_cookie_header.split("; ") == [
            f"custom-csrftoken={csrf_token}",
            "Path=/",
            "SameSite=lax",
        ]

        response = client.post("/", headers={"x-custom-csrftoken": csrf_token})
        assert response.status_code == HTTP_201_CREATED
