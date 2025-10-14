from typing import Dict

from ravyn import Gateway, Include, Ravyn, get
from ravyn.testclient import RavynTestClient, create_client
from tests.settings import AppTestSettings


@get("/bar", tags=["bar"])
async def bar() -> Dict[str, str]:
    return {"hello": "world"}


app = Ravyn(
    routes=[Gateway(handler=bar)],
    enable_openapi=True,
    tags=["test"],
    settings_module=AppTestSettings,
)


client = RavynTestClient(app)


def test_tags_nested(test_client_factory):
    with create_client(
        routes=[
            Include(
                routes=[Gateway(handler=bar, tags=["gateway"])],
                tags=["include"],
            )
        ],
        enable_openapi=True,
        tags=["test"],
    ) as client:
        response = client.get("/openapi.json")

        assert response.status_code == 200, response.text
        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Ravyn",
                "summary": "Ravyn application",
                "description": "Highly scalable, performant, easy to learn and for every application.",
                "contact": {"name": "admin", "email": "admin@myapp.com"},
                "version": app.version,
            },
            "servers": [{"url": "/"}],
            "paths": {
                "/bar": {
                    "get": {
                        "tags": ["test", "include", "gateway", "bar"],
                        "summary": "Bar",
                        "description": "",
                        "operationId": "bar_bar_get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                }
            },
            "tags": ["test"],
        }
