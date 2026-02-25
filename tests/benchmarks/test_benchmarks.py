"""Performance benchmarks for the Ravyn framework."""

import pytest
from lilya import status
from pydantic import BaseModel

from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get, post
from ravyn.testclient import create_client

# ---------------------------------------------------------------------------
# Handlers used across benchmarks
# ---------------------------------------------------------------------------


@get("/")
def homepage() -> dict:
    return {"message": "welcome"}


@get("/hello/{name}")
def greet(name: str) -> dict:
    return {"message": f"Hello, {name}!"}


class Item(BaseModel):
    name: str
    price: float
    quantity: int = 1


@post("/items")
def create_item(data: Item) -> dict:
    return {"name": data.name, "total": data.price * data.quantity}


@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "test-user"}


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------


@pytest.mark.benchmark
def test_bench_app_creation():
    """Measure the cost of creating a Ravyn application with routes."""
    client = create_client(
        routes=[
            Gateway(handler=homepage),
            Gateway(handler=greet),
            Gateway(handler=create_item),
            Gateway(handler=get_user),
        ],
        enable_openapi=False,
    )
    # Ensure the app is valid
    assert client.app is not None


@pytest.mark.benchmark
def test_bench_simple_get_request():
    """Measure a plain GET request through the full stack."""
    with create_client(
        routes=[Gateway(handler=homepage)],
        enable_openapi=False,
    ) as client:
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.benchmark
def test_bench_parametrized_get_request():
    """Measure a GET request with a path parameter."""
    with create_client(
        routes=[Gateway(handler=greet)],
        enable_openapi=False,
    ) as client:
        response = client.get("/hello/world")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.benchmark
def test_bench_post_request_with_validation():
    """Measure a POST request with Pydantic model validation."""
    with create_client(
        routes=[Gateway(handler=create_item)],
        enable_openapi=False,
    ) as client:
        response = client.post(
            "/items",
            json={"name": "widget", "price": 9.99, "quantity": 3},
        )
        assert response.status_code == 201


@pytest.mark.benchmark
def test_bench_multiple_routes():
    """Measure routing resolution across several registered routes."""
    with create_client(
        routes=[
            Gateway(handler=homepage),
            Gateway(handler=greet),
            Gateway(handler=create_item),
            Gateway(handler=get_user),
        ],
        enable_openapi=False,
    ) as client:
        response = client.get("/users/42")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 42, "name": "test-user"}
