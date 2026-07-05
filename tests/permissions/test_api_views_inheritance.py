from ravyn import Controller, get
from ravyn.permissions import AllowAny, DenyAll, IsAuthenticated
from ravyn.testclient import create_client


class MyController(Controller):
    permissions = [DenyAll]

    @get("/home")
    async def home(self) -> str:
        return "home"


class MySimpleController(MyController):
    permissions = [AllowAny]

    @get(
        "/new-home",
    )
    async def get(self) -> str:
        return "home simple"


class AnotherAPI(MyController):
    permissions = [AllowAny]

    @get("/another", permissions=[IsAuthenticated])
    async def get(self) -> str: ...


def test_cannot_access_controller(test_client_factory):
    with create_client(routes=[MyController]) as client:
        response = client.get("/home")

        assert response.status_code == 403
        assert MyController.permissions == [DenyAll]


def test_cannot_access_simple_controller():
    with create_client(routes=[MySimpleController]) as client:
        response = client.get("/new-home")

        assert response.status_code == 403
        assert MySimpleController.permissions == [DenyAll, AllowAny]


def test_inheritance_total(test_client_factory):
    with create_client(routes=[AnotherAPI], enable_openapi=False) as client:
        response = client.get("/another")

        assert response.status_code == 403
        assert AnotherAPI.permissions == [DenyAll, AllowAny]
