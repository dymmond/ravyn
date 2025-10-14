from __future__ import annotations

import base64
import binascii
from collections.abc import Awaitable, Callable

import pytest
from lilya.authentication import AuthCredentials, AuthenticationBackend, BasicUser
from lilya.middleware import DefineMiddleware
from lilya.middleware.authentication import BaseAuthMiddleware

from ravyn import Gateway, get
from ravyn.exceptions import AuthenticationError
from ravyn.middleware.authentication import AuthenticationMiddleware
from ravyn.requests import Connection, Request
from ravyn.responses import JSONResponse, Response
from ravyn.testclient import create_client

AsyncEndpoint = Callable[..., Awaitable[Response]]
SyncEndpoint = Callable[..., Response]


class BasicAuth(AuthenticationBackend):
    async def authenticate(
        self,
        request: Connection,
    ) -> tuple[AuthCredentials, BasicUser] | None:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials") from None

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), BasicUser(username)


def on_auth_error(request: Connection, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse({"error": str(exc)}, status_code=401)


@get()
def control_panel(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.display_name,
        }
    )


def test_raise_error_on_incomplete(test_client_factory) -> None:
    with pytest.raises(TypeError):
        with create_client(
            routes=[Gateway("/control-panel", handler=control_panel)],
            middleware=[DefineMiddleware(BaseAuthMiddleware, backend=BasicAuth())],
        ):
            ...


class CustomWorkingMiddleware(AuthenticationMiddleware):
    async def authenticate(self, request: Connection) -> tuple[AuthCredentials, BasicUser] | None:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials") from None

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), BasicUser(username)


class CustomWorkingMiddleware2(BaseAuthMiddleware):
    async def authenticate(self, request: Connection) -> tuple[AuthCredentials, BasicUser] | None:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials") from None

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), BasicUser(username)


class CustomBackendRequiringMiddleware(AuthenticationMiddleware):
    async def authenticate(self, request: Connection) -> tuple[AuthCredentials, BasicUser] | None:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials") from None

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), BasicUser(username)

    authenticate.requires_backend = True


@pytest.mark.parametrize("middleware", [CustomWorkingMiddleware, CustomWorkingMiddleware2])
def test_custom_on_error_with_authenticate(test_client_factory, middleware) -> None:
    with create_client(
        routes=[Gateway("/control-panel", handler=control_panel)],
        middleware=[DefineMiddleware(middleware, on_error=on_auth_error)],
    ) as client:
        response = client.get("/control-panel", auth=("lilya", "example"))
        assert response.status_code == 200
        assert response.json() == {"authenticated": True, "user": "lilya"}

        response = client.get("/control-panel", headers={"Authorization": "basic foobar"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid basic auth credentials", "status_code": 401}


@pytest.mark.parametrize(
    "middleware", [AuthenticationMiddleware, CustomBackendRequiringMiddleware]
)
def test_raise_assertation_error_no_backend(test_client_factory, middleware) -> None:
    with pytest.raises(AssertionError):
        with create_client(
            routes=[Gateway("/control-panel", handler=control_panel)],
            middleware=[DefineMiddleware(middleware)],
        ):
            ...
