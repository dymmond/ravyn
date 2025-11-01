import pytest
from lilya import status
from lilya.protocols.permissions import PermissionProtocol
from lilya.types import Receive, Scope, Send

from ravyn import Include
from ravyn.exceptions import NotAuthorized, PermissionDenied
from ravyn.permissions import BasePermission
from ravyn.requests import Request
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get
from ravyn.testclient import create_client


class RavynPermission(BasePermission):
    def has_permission(self, request, controller):
        if not request.headers.get("allow_all"):
            return False
        return True


# Testing for lilya permissions
class LilyaDeny(PermissionProtocol):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotAuthorized()


class LilyaPermDeny(PermissionProtocol):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive)
        if request.headers.get("allow_all"):
            await self.app(scope, receive, send)
            return
        raise PermissionDenied()


def test_mix_permissions_with_native_ravyn() -> None:
    @get(path="/secret", permissions=[LilyaDeny])
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler, permissions=[RavynPermission])],
    ) as client:
        response = client.get("/secret")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json().get("detail") == "Not Authorized."
        response = client.get("/secret", headers={"Authorization": "yes"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json().get("detail") == "Not Authorized."
        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_two_permissions_mixed_same_level_raises_error() -> None:
    with pytest.raises(AssertionError):

        @get(path="/secret", permissions=[RavynPermission, LilyaDeny])
        def my_http_route_handler() -> None: ...


@pytest.mark.parametrize("path", ["/secret", "", "/"])
def test_include_routes(path) -> None:
    was_reached = False

    @get(path=path)
    def my_http_route_handler() -> None:
        nonlocal was_reached
        was_reached = True
        raise Exception("Should not be reached")

    with create_client(
        routes=[
            Include(routes=[Gateway(handler=my_http_route_handler)], permissions=[LilyaDeny]),
        ],
        permissions=[RavynPermission],
    ) as client:
        response = client.get(path or "/", headers={"Authorization": "yes", "allow_all": "false"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not was_reached
        response = client.get(path or "/", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not was_reached
