from fastapi import FastAPI
from lilya import status
from lilya.compat import reverse
from litestar import Litestar, get
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.testclient import TestClient

from ravyn import Gateway, Include, Ravyn, get as rget
from ravyn.testclient import create_client


async def route_one(request: Request):
    return JSONResponse({"test": 1}, status_code=202)


async def route_two(request: Request):
    return JSONResponse({"test": 2}, status_code=206)


async def route_three(request: Request):
    return JSONResponse({"test": 3}, status_code=200)


def test_add_asgi_starlette_app() -> None:
    """
    Adds a Starlette application to the main app.
    """

    asgi_app = Starlette(
        routes=[
            Route("/", route_one),
            Route(path="/second", endpoint=route_two),
            Route(path="/third", endpoint=route_three),
        ]
    )

    with create_client([]) as client:
        client.app.add_asgi_app("/", asgi_app)

        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK


def test_add_asgi_fastapi_app() -> None:
    """
    Adds a FastAPI application to the main app.
    """
    asgi_app = FastAPI()

    @asgi_app.get("/")
    async def route_one(request: Request):
        return JSONResponse({"test": 1}, status_code=202)

    @asgi_app.get("/second")
    async def route_two(request: Request):
        return JSONResponse({"test": 2}, status_code=206)

    @asgi_app.get("/third")
    async def route_three(request: Request):
        return JSONResponse({"test": 3}, status_code=200)

    with create_client([]) as client:
        client.app.add_asgi_app("/", asgi_app)

        response = client.get("/")
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED

        response = client.get("/second")

        assert response.json() == {"test": 2}
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT

        response = client.get("/third")

        assert response.json() == {"test": 3}
        assert response.status_code == status.HTTP_200_OK


def test_add_asgi_litestar_app() -> None:
    """
    Adds a Litestar application to the main app.
    """

    @get("/")
    async def hello_world() -> str:
        return "Hello, world!"

    asgi_app = Litestar([hello_world])

    with create_client([]) as client:
        client.app.add_asgi_app("/", asgi_app)

        response = client.get("/")

        assert response.text == "Hello, world!"
        assert response.status_code == 200


def test_test_asgi_path_mixed_from_ravyn_down() -> None:
    """
    Adds a Starlette application to the main app.
    """
    with create_client(
        routes=[
            Include(
                "/test",
                app=Starlette(
                    routes=[
                        Route("/starlette", route_one, name="star"),
                    ]
                ),
                name="test",
            )
        ]
    ) as client:
        url = reverse("test:star", app=client.app)

        response = client.get(url)
        assert response.json() == {"test": 1}
        assert response.status_code == status.HTTP_202_ACCEPTED


def test_test_asgi_path_mixed_from_starlette_down() -> None:
    """
    Adds a Starlette application to the main app.
    """

    @rget("/ravyn")
    async def route_four() -> dict:
        return {"test": 4}

    app = Starlette(
        routes=[
            Mount(
                "/test",
                app=Ravyn(
                    routes=[
                        Gateway(handler=route_four, name="ravyn"),
                    ]
                ),
                name="test",
            )
        ]
    )

    url = reverse("test:ravyn", app=app)
    client = TestClient(app)

    response = client.get(url)
    assert response.json() == {"test": 4}
    assert response.status_code == 200
