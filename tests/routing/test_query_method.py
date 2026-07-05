from lilya import status
from lilya.middleware import DefineMiddleware
from pydantic import BaseModel

from ravyn import Gateway, Ravyn, Request, query, route


class SearchPayload(BaseModel):
    term: str
    limit: int


class CaptureMethodMiddleware:
    def __init__(self, app, seen: list[str]) -> None:
        self.app = app
        self.seen = seen

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            self.seen.append(scope["method"])
        await self.app(scope, receive, send)


def test_query_decorator_accepts_body_and_reaches_middleware(test_app_client_factory) -> None:
    seen: list[str] = []

    @query("/search")
    async def search(request: Request, payload: SearchPayload, page: int) -> dict:
        return {
            "method": request.method,
            "payload": payload.model_dump(),
            "page": page,
        }

    app = Ravyn(
        routes=[Gateway(handler=search)],
        middleware=[DefineMiddleware(CaptureMethodMiddleware, seen=seen)],
    )
    client = test_app_client_factory(app)

    response = client.query("/search?page=2", json={"term": "ravyn", "limit": 10})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "method": "QUERY",
        "payload": {"term": "ravyn", "limit": 10},
        "page": 2,
    }
    assert seen == ["QUERY"]


def test_generic_route_accepts_query_method(test_app_client_factory) -> None:
    @route("/search", methods=["QUERY"])
    async def search(payload: SearchPayload) -> dict:
        return payload.model_dump()

    app = Ravyn(routes=[Gateway(handler=search)])
    client = test_app_client_factory(app)

    response = client.request("QUERY", "/search", json={"term": "ravyn", "limit": 5})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"term": "ravyn", "limit": 5}
    assert client.get("/search").status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_app_query_decorator_registers_query_route(test_app_client_factory) -> None:
    app = Ravyn()

    @app.query("/search")
    async def search() -> dict:
        return {"method": "QUERY"}

    client = test_app_client_factory(app)
    response = client.query("/search")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"method": "QUERY"}
