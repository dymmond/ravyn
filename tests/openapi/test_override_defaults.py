from typing import Dict

from pydantic import BaseModel

from ravyn import Gateway, Ravyn, get
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.testclient import RavynTestClient
from tests.settings import AppTestSettings


class PydanticError(BaseModel):
    detail: str
    code: int


@get(
    "/bar",
    tags=["bar"],
    responses={200: OpenAPIResponse(model=PydanticError, description="Pydantic response")},
)
async def bar() -> Dict[str, str]:
    return {"hello": "world"}


app = Ravyn(
    routes=[Gateway(handler=bar)],
    enable_openapi=True,
    tags=["test"],
    settings_module=AppTestSettings,
    contact={"name": "ravyn", "email": "ravyn@esmeral.dev"},
)


client = RavynTestClient(app)


def test_openapi_schema_tags_pydantic(test_client_factory):
    response = client.get("/openapi.json")

    assert response.status_code == 200, response.text

    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Ravyn",
            "summary": "Ravyn application",
            "description": "Highly scalable, performant, easy to learn and for every application.",
            "contact": {"name": "ravyn", "email": "ravyn@esmeral.dev"},
            "version": app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/bar": {
                "get": {
                    "tags": ["test", "bar"],
                    "summary": "Bar",
                    "description": "",
                    "operationId": "bar_bar_get",
                    "responses": {
                        "200": {
                            "description": "Pydantic response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PydanticError"}
                                }
                            },
                        }
                    },
                    "deprecated": False,
                }
            }
        },
        "components": {
            "schemas": {
                "PydanticError": {
                    "properties": {
                        "detail": {"type": "string", "title": "Detail"},
                        "code": {"type": "integer", "title": "Code"},
                    },
                    "type": "object",
                    "required": ["detail", "code"],
                    "title": "PydanticError",
                }
            }
        },
        "tags": ["test"],
    }
