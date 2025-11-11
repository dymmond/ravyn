import os
from contextlib import asynccontextmanager

import anyio
import pytest
from lilya import status
from lilya.middleware import DefineMiddleware
from lilya.routing import Host

from ravyn import Request
from ravyn.applications import Ravyn
from ravyn.exceptions import HTTPException, ImproperlyConfigured, WebSocketException
from ravyn.middleware import TrustedHostMiddleware
from ravyn.responses import JSONResponse, PlainText
from ravyn.routing.gateways import Gateway, WebSocketGateway
from ravyn.routing.handlers import get, head, options, route, websocket
from ravyn.routing.router import Include, Router
from ravyn.staticfiles import StaticFiles
from ravyn.websockets import WebSocket


async def error_500(request, exc):  # pragma: no cover
    return JSONResponse({"detail": "Server Error"}, status_code=500)


async def method_not_allowed(request, exc):
    return JSONResponse({"detail": "Custom message"}, status_code=405)


async def http_exception(request, exc):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@route(methods=["GET", "HEAD", "TRACE"])
def func_homepage(request: Request) -> PlainText:
    return PlainText("Hello, world!")


@get()
async def async_homepage(request: Request) -> PlainText:
    return PlainText("Hello, world!")


@get()
def all_users_page(request: Request) -> PlainText:
    return PlainText("Hello, everyone!")


@get()
def user_page(request: Request) -> PlainText:
    username = request.path_params["username"]
    return PlainText(f"Hello, {username}!")


@get()
def custom_subdomain(request: Request) -> PlainText:
    return PlainText("Subdomain: " + request.path_params["subdomain"])


@get()
def runtime_error(request: Request) -> None:
    raise RuntimeError()  # pragma: no cover


@head()
def head_func(request: Request) -> PlainText:
    return PlainText("Hello, world!")


@options()
def head_options(request: Request) -> PlainText:
    return PlainText("Hello, world!")


@websocket()
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, world!")
    await socket.close()


@websocket()
async def websocket_raise_websocket(socket: WebSocket) -> None:
    await socket.accept()
    raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA)


class CustomWSException(Exception):
    pass


@websocket()
async def websocket_raise_custom(socket: WebSocket) -> None:
    await socket.accept()
    raise CustomWSException()


def custom_ws_exception_handler(websocket: WebSocket, exc: CustomWSException):
    anyio.from_thread.run(websocket.close, status.WS_1013_TRY_AGAIN_LATER)


users = Router(
    routes=[
        Gateway("/", handler=all_users_page),
        Gateway("/{username}", handler=user_page),
    ]
)

subdomain = Router(
    routes=[
        Gateway("/", handler=custom_subdomain),
    ]
)

exception_handlers = {
    500: error_500,
    405: method_not_allowed,
    HTTPException: http_exception,
    CustomWSException: custom_ws_exception_handler,
}

middleware = [
    DefineMiddleware(TrustedHostMiddleware, allowed_hosts=["testserver", "*.example.org"])
]

app = Ravyn(
    routes=[
        Gateway("/head", handler=head_func),
        Gateway("/options", handler=head_options),
        Gateway("/func", handler=func_homepage),
        Gateway("/async", handler=async_homepage),
        Gateway("/500", handler=runtime_error),
        WebSocketGateway("/ws", handler=websocket_endpoint),
        WebSocketGateway("/ws-raise-websocket", handler=websocket_raise_websocket),
        WebSocketGateway("/ws-raise-custom", handler=websocket_raise_custom),
        Include("/users", app=users),
        Host("{subdomain}.example.org", app=subdomain),
    ],
    exception_handlers=exception_handlers,
    middleware=middleware,
)


@pytest.fixture
def client(test_client_factory):
    with test_client_factory(app) as client:
        yield client


def test_url_for():
    assert app.url_for("func_homepage") == "/func"


def test_func_route(client):
    response = client.get("/func")
    assert response.status_code == 200

    response = client.head("/func")
    assert response.status_code == 200
    assert response.text == ""


def test_head_route(client):
    response = client.head("/head")
    assert response.status_code == 200

    response = client.get("/head")
    assert response.status_code == 405


def test_options_route(client):
    response = client.options("/options")
    assert response.status_code == 200
    assert response.text == "Hello, world!"

    response = client.get("/options")
    assert response.status_code == 405


def test_async_route(client):
    response = client.get("/async")
    assert response.status_code == 200
    assert response.text == "Hello, world!"


def test_mounted_route(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.text == "Hello, everyone!"


def test_mounted_route_path_params(client):
    response = client.get("/users/tomchristie")
    assert response.status_code == 200
    assert response.text == "Hello, tomchristie!"


def test_subdomain_route(test_client_factory):
    client = test_client_factory(app, base_url="https://foo.example.org/")

    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Subdomain: foo"


def test_websocket_route(client):
    with client.websocket_connect("/ws") as session:
        text = session.receive_text()
        assert text == "Hello, world!"


def test_400(client):
    response = client.get("/404")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_405(client):
    response = client.post("/func")
    assert response.status_code == 405
    assert response.json() == {"detail": "Custom message"}


def test_websocket_raise_websocket_exception(client):
    with client.websocket_connect("/ws-raise-websocket") as session:
        response = session.receive()
        assert response == {
            "type": "websocket.close",
            "code": status.WS_1003_UNSUPPORTED_DATA,
            "reason": "",
        }


def test_websocket_raise_custom_exception(client):
    with client.websocket_connect("/ws-raise-custom") as session:
        response = session.receive()
        assert response == {
            "type": "websocket.close",
            "code": status.WS_1013_TRY_AGAIN_LATER,
            "reason": "",
        }


def test_middleware(test_client_factory):
    client = test_client_factory(app, base_url="http://incorrecthost")
    response = client.get("/func")
    assert response.status_code == 400
    assert response.text == "Invalid host header"


def test_app_mount(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "example.txt")
    with open(path, "w") as file:
        file.write("<file content>")

    app = Ravyn(
        routes=[
            Include("/static", StaticFiles(directory=tmpdir)),
        ]
    )

    client = test_client_factory(app)

    response = client.get("/static/example.txt")
    assert response.status_code == 200
    assert response.text == "<file content>"

    response = client.post("/static/example.txt")
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


def test_app_debug(test_client_factory):
    @get()
    async def homepage(request: Request) -> None:
        raise RuntimeError()

    app = Ravyn(
        routes=[
            Gateway("/", handler=homepage),
        ]
    )
    app.debug = True

    client = test_client_factory(app, raise_server_exceptions=False)
    response = client.get("/")
    assert response.status_code == 500
    assert "RuntimeError" in response.text
    assert app.debug


def test_app_add_route(test_client_factory):
    @get()
    async def homepage(request: Request) -> PlainText:
        return PlainText("Hello, World!")

    app = Ravyn(
        routes=[
            Gateway("/", handler=homepage),
        ]
    )

    client = test_client_factory(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, World!"


@pytest.mark.parametrize("path", ["/stuff", "/test", "/a-root-path", "/new-root-path"])
def test_app_add_route_with_root_path(test_client_factory, path):
    @get()
    async def homepage(request: Request) -> PlainText:
        return PlainText("Hello, World!")

    app = Ravyn(
        routes=[
            Gateway("/", handler=homepage),
        ],
        root_path=f"/{path}",
    )

    client = test_client_factory(app)
    response = client.get(f"/{path}")

    assert response.status_code == 200
    assert response.text == "Hello, World!"


def test_app_add_websocket_route(test_client_factory):
    @websocket()
    async def websocket_endpoint(socket: WebSocket) -> None:
        await socket.accept()
        await socket.send_text("Hello, world!")
        await socket.close()

    app = Ravyn(
        routes=[
            WebSocketGateway("/ws", handler=websocket_endpoint),
        ]
    )
    client = test_client_factory(app)

    with client.websocket_connect("/ws") as session:
        text = session.receive_text()
        assert text == "Hello, world!"


def test_app_add_event_handler(test_client_factory):
    startup_complete = False
    cleanup_complete = False

    def run_startup():
        nonlocal startup_complete
        startup_complete = True

    def run_cleanup():
        nonlocal cleanup_complete
        cleanup_complete = True

    app = Ravyn(
        on_startup=[run_startup],
        on_shutdown=[run_cleanup],
    )

    assert not startup_complete
    assert not cleanup_complete
    with test_client_factory(app):
        assert startup_complete
        assert not cleanup_complete
    assert startup_complete
    assert cleanup_complete


def test_app_async_cm_lifespan(test_client_factory):
    startup_complete = False
    cleanup_complete = False

    @asynccontextmanager
    async def lifespan(app):
        nonlocal startup_complete, cleanup_complete
        startup_complete = True
        yield
        cleanup_complete = True

    app = Ravyn(lifespan=lifespan)

    assert not startup_complete
    assert not cleanup_complete
    with test_client_factory(app):
        assert startup_complete
        assert not cleanup_complete
    assert startup_complete
    assert cleanup_complete


def test_app_async_gen_lifespan(test_client_factory):
    startup_complete = False
    cleanup_complete = False

    @asynccontextmanager
    async def lifespan(app):
        nonlocal startup_complete, cleanup_complete
        startup_complete = True
        yield
        cleanup_complete = True

    app = Ravyn(lifespan=lifespan)

    assert not startup_complete
    assert not cleanup_complete
    with test_client_factory(app):
        assert startup_complete
        assert not cleanup_complete
    assert startup_complete
    assert cleanup_complete


def test_raise_improperly_configured_on_websocket_route_function(test_client_factory):
    with pytest.raises(ImproperlyConfigured):
        app = Ravyn(routes=[])
        app.websocket_route(path="/")
