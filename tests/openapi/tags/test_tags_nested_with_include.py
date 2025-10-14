from typing import Dict

from ravyn import Gateway, Include, Ravyn, get
from ravyn.testclient import RavynTestClient
from tests.settings import AppTestSettings


@get("/bar")
async def bar() -> Dict[str, str]:
    return {"hello": "world"}


app = Ravyn(
    routes=[Include("/api/v2", routes=[Include(routes=[Gateway(handler=bar)])], tags=["Include"])],
    enable_openapi=True,
    settings_module=AppTestSettings,
)


def test_openapi_schema_tags_include(test_client_factory):
    client = RavynTestClient(app)

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
            "/api/v2/bar": {
                "get": {
                    "tags": ["Include"],
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
    }
