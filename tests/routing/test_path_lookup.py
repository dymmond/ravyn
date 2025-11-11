from lilya.compat import reverse

from ravyn import Controller, Gateway, Include, get, post
from ravyn.testclient import create_client


@get("/hello")
async def get_hello() -> str:
    return "Hello World"


@post("/new")
async def post_new() -> str:
    return "New World"


@get("/home", name="home")
async def home() -> str:
    return "Hello World"


@post("/new-home", name="new-home")
async def post_new_home() -> str:
    return "New World"


class TestController(Controller):
    @get("/int", name="int")
    async def get_int(self, id: int) -> int:
        return id


class Test2Controller(Controller):
    path = "/test"

    @get("/int", name="int")
    async def get_int(self, id: int) -> int:
        return id


routes = [
    Include(
        "/api",
        routes=[
            Include(
                routes=[
                    Gateway(handler=get_hello, name="hello"),
                    Gateway(handler=post_new, name="new"),
                    Gateway(handler=home, name="home"),
                    Gateway(handler=post_new_home, name="new-home"),
                    Gateway(handler=TestController, name="test"),
                    Gateway(handler=Test2Controller),
                ],
                name="v1",
            ),
        ],
        name="api",
    ),
    Include(
        "/ravyn",
        routes=[
            Include(
                "/api",
                routes=[
                    Include(
                        routes=[
                            Gateway(handler=get_hello, name="hello"),
                            Gateway(handler=post_new, name="new"),
                            Gateway(handler=home, name="home"),
                            Gateway(handler=post_new_home, name="new-home"),
                            Gateway(handler=TestController, name="test"),
                            Gateway(handler=Test2Controller),
                        ],
                        name="v1",
                    ),
                ],
                name="api",
            ),
        ],
        name="ravyn",
    ),
]


def test_can_reverse_simple(test_client_factory):
    with create_client(routes=routes, enable_openapi=False) as client:
        app = client.app

        assert app.url_path_for("api:v1:hello") == "/api/hello"
        assert app.url_path_for("api:v1:new") == "/api/new"

        assert reverse("api:v1:hello") == "/api/hello"
        assert reverse("api:v1:new") == "/api/new"


def test_can_reverse_with_gateway_and_handler_name(test_client_factory):
    with create_client(routes=routes, enable_openapi=False) as client:
        app = client.app

        assert app.url_path_for("api:v1:home:home") == "/api/home"
        assert reverse("api:v1:home:home") == "/api/home"

        assert app.url_path_for("api:v1:new-home:new-home") == "/api/new-home"
        assert reverse("api:v1:new-home:new-home") == "/api/new-home"


def test_can_reverse_with_controller_and_handler_name(test_client_factory):
    with create_client(routes=routes, enable_openapi=False) as client:
        app = client.app

        assert app.url_path_for("api:v1:test:int") == "/api/int"
        assert reverse("api:v1:test:int") == "/api/int"


def test_can_reverse_with_no_controller_name_and_handler_name(test_client_factory):
    with create_client(routes=routes, enable_openapi=False) as client:
        app = client.app

        assert app.url_path_for("api:v1:test2controller:int") == "/api/test/int"
        assert reverse("api:v1:test2controller:int") == "/api/test/int"


def test_can_reverse_lookup_all(test_client_factory):
    with create_client(routes=routes, enable_openapi=False) as client:
        app = client.app

        assert app.url_path_for("api:v1:hello") == "/api/hello"
        assert app.url_path_for("api:v1:new") == "/api/new"

        assert reverse("api:v1:hello") == "/api/hello"
        assert reverse("api:v1:new") == "/api/new"

        assert app.url_path_for("api:v1:home:home") == "/api/home"
        assert reverse("api:v1:home:home") == "/api/home"

        assert app.url_path_for("api:v1:new-home:new-home") == "/api/new-home"
        assert reverse("api:v1:new-home:new-home") == "/api/new-home"

        assert app.url_path_for("api:v1:test:int") == "/api/int"
        assert reverse("api:v1:test:int") == "/api/int"

        assert app.url_path_for("api:v1:test2controller:int") == "/api/test/int"
        assert reverse("api:v1:test2controller:int") == "/api/test/int"


def test_can_reverse_lookup_all_nested(test_client_factory):
    with create_client(routes=routes, enable_openapi=False) as client:
        app = client.app

        assert app.url_path_for("ravyn:api:v1:hello") == "/ravyn/api/hello"
        assert app.url_path_for("ravyn:api:v1:new") == "/ravyn/api/new"

        assert reverse("ravyn:api:v1:hello") == "/ravyn/api/hello"
        assert reverse("ravyn:api:v1:new") == "/ravyn/api/new"

        assert app.url_path_for("ravyn:api:v1:home:home") == "/ravyn/api/home"
        assert reverse("ravyn:api:v1:home:home") == "/ravyn/api/home"

        assert app.url_path_for("ravyn:api:v1:new-home:new-home") == "/ravyn/api/new-home"
        assert reverse("ravyn:api:v1:new-home:new-home") == "/ravyn/api/new-home"

        assert app.url_path_for("ravyn:api:v1:test:int") == "/ravyn/api/int"
        assert reverse("ravyn:api:v1:test:int") == "/ravyn/api/int"

        assert app.url_path_for("ravyn:api:v1:test2controller:int") == "/ravyn/api/test/int"
        assert reverse("ravyn:api:v1:test2controller:int") == "/ravyn/api/test/int"
