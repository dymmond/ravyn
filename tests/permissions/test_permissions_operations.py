from typing import TYPE_CHECKING

from lilya.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from ravyn.permissions import BasePermission
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get
from ravyn.testclient import create_client

if TYPE_CHECKING:
    from ravyn.requests import Request
    from ravyn.types import APIGateHandler


class BaseTestPermission(BasePermission):
    custom_header: str = None

    def has_permission(self, request: "Request", controller: "APIGateHandler"):
        if not request.headers.get(self.custom_header):
            return False
        return True


class Op1Permission(BaseTestPermission):
    custom_header = "op1"


class Op2Permission(BaseTestPermission):
    custom_header = "op2"


class Op3Permission(BaseTestPermission):
    custom_header = "op3"


def test_permissions_with_single_op() -> None:
    @get(
        path="/permissions",
        permissions=[Op1Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test"})
        assert response.status_code == HTTP_200_OK


def test_permissions_with_and_ops() -> None:
    @get(
        path="/permissions",
        permissions=[Op1Permission & Op2Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test", "op2": "test"})
        assert response.status_code == HTTP_200_OK


def test_permissions_with_and_plus_extra_ops() -> None:
    @get(
        path="/permissions",
        permissions=[Op1Permission & Op2Permission, Op3Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op3": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test", "op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get(
            "/permissions", headers={"op1": "test", "op2": "test", "op3": "test"}
        )
        assert response.status_code == HTTP_200_OK


def test_permissions_with_inverted_and_ops() -> None:
    @get(
        path="/permissions",
        permissions=[~(Op1Permission & Op2Permission)],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op1": "test"})
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op2": "test"})
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op1": "test", "op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )


def test_permissions_with_or_ops() -> None:
    @get(
        path="/permissions",
        permissions=[Op1Permission | Op2Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test"})
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op2": "test"})
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op1": "test", "op2": "test"})
        assert response.status_code == HTTP_200_OK


def test_permissions_with_xor_ops() -> None:
    @get(
        path="/permissions",
        permissions=[Op1Permission ^ Op2Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        response = client.get("/permissions", headers={"op1": "test"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/permissions", headers={"op2": "test"})

        assert response.status_code == HTTP_200_OK

        response = client.get("/permissions", headers={"op1": "test", "op2": "test"})

        assert response.status_code == HTTP_403_FORBIDDEN


def test_permissions_with_nor_ops() -> None:
    @get(
        path="/nor-permissions",
        permissions=[Op1Permission - Op2Permission],  # Assuming P1 - P2 is mapped to NOR
    )
    def my_nor_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_nor_route_handler)],
    ) as client:
        # No headers present (Op1: False, Op2: False) -> NOR: True
        response = client.get("/nor-permissions")
        assert response.status_code == HTTP_200_OK

        # Header op1 present (Op1: True, Op2: False) -> NOR: False
        response = client.get("/nor-permissions", headers={"op1": "test"})

        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )

        # Header op2 present (Op1: False, Op2: True) -> NOR: False
        response = client.get("/nor-permissions", headers={"op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN

        # Both headers present (Op1: True, Op2: True) -> NOR: False
        response = client.get("/nor-permissions", headers={"op1": "test", "op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN


def test_permissions_with_or_plus_extra_ops() -> None:
    @get(
        path="/permissions",
        permissions=[Op1Permission | Op2Permission, Op3Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op3": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test", "op3": "test"})
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op2": "test", "op3": "test"})
        assert response.status_code == HTTP_200_OK
        response = client.get(
            "/permissions", headers={"op1": "test", "op2": "test", "op3": "test"}
        )
        assert response.status_code == HTTP_200_OK


def test_permissions_with_inverted_or_ops() -> None:
    @get(
        path="/permissions",
        permissions=[~(Op1Permission | Op2Permission)],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op1": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test", "op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )


def test_permissions_with_not_ops() -> None:
    @get(
        path="/permissions",
        permissions=[~Op1Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op1": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )


def test_permissions_with_not_plus_extra_ops() -> None:
    @get(
        path="/permissions",
        permissions=[~Op1Permission, Op2Permission],
    )
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/permissions")
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op1": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
        response = client.get("/permissions", headers={"op2": "test"})
        assert response.status_code == HTTP_200_OK
        response = client.get("/permissions", headers={"op1": "test", "op2": "test"})
        assert response.status_code == HTTP_403_FORBIDDEN
        assert (
            response.json().get("detail") == "You do not have permission to perform this action."
        )
