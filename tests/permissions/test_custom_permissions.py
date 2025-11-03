from typing import TYPE_CHECKING

from lilya.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from ravyn import Controller
from ravyn.permissions import BasePermission
from ravyn.requests import Request
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get
from ravyn.testclient import create_client

if TYPE_CHECKING:
    from ravyn.types import APIGateHandler  # pragma: no cover


class IsAdmin(BasePermission):
    def has_permission(self, request: "Request", controller: "APIGateHandler"):
        if not request.headers.get("is_admin", "false") == "true":
            return False
        return True


class IsSupport(BasePermission):
    def has_permission(self, request: "Request", controller: "APIGateHandler"):
        if not request.headers.get("is_support", "false") == "true":
            return False
        return True


class MyController(Controller):
    @get(permissions=[IsAdmin | IsSupport])
    async def get_info(self) -> None: ...


def test_custom_or_permissions():
    with create_client(
        routes=[
            Gateway("/", handler=MyController),
        ]
    ) as client:
        response = client.get("/")

        assert response.status_code == HTTP_403_FORBIDDEN

        response = client.get("/", headers={"is_admin": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_support": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "false", "is_support": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "true", "is_support": "false"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "false", "is_support": "false"})

        assert response.status_code == HTTP_403_FORBIDDEN


class AsyncIsAdmin(BasePermission):
    async def has_permission(self, request: "Request", controller: "APIGateHandler"):
        if not request.headers.get("is_admin", "false") == "true":
            return False
        return True


class AsyncIsSupport(BasePermission):
    async def has_permission(self, request: "Request", controller: "APIGateHandler"):
        if not request.headers.get("is_support", "false") == "true":
            return False
        return True


class MyControllerAsync(Controller):
    @get(permissions=[AsyncIsAdmin | AsyncIsSupport])
    async def get_info(self) -> None: ...


def test_custom_or_permissions_async():
    with create_client(
        routes=[
            Gateway("/", handler=MyControllerAsync),
        ]
    ) as client:
        response = client.get("/")

        assert response.status_code == HTTP_403_FORBIDDEN

        response = client.get("/", headers={"is_admin": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_support": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "false", "is_support": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "true", "is_support": "false"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "false", "is_support": "false"})

        assert response.status_code == HTTP_403_FORBIDDEN


class MyControllerMixed(Controller):
    @get(permissions=[IsAdmin | AsyncIsSupport])
    async def get_info(self) -> None: ...


def test_custom_or_permissions_mixed():
    with create_client(
        routes=[
            Gateway("/", handler=MyControllerMixed),
        ]
    ) as client:
        response = client.get("/")

        assert response.status_code == HTTP_403_FORBIDDEN

        response = client.get("/", headers={"is_admin": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_support": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "false", "is_support": "true"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "true", "is_support": "false"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/", headers={"is_admin": "false", "is_support": "false"})

        assert response.status_code == HTTP_403_FORBIDDEN
