from typing import Dict

from pydantic import BaseModel

from ravyn import Gateway, Ravyn, post
from ravyn.core.datastructures.msgspec import Struct
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.testclient import RavynTestClient
from tests.settings import AppTestSettings


class PydanticError(BaseModel):
    detail: str
    code: int


class MsgSpecError(Struct):
    detail: str
    code: int


@post(
    "/foo",
    tags=["foo"],
    responses={
        200: OpenAPIResponse(model=MsgSpecError),
        201: OpenAPIResponse(model=PydanticError),
    },
)
async def foo() -> Dict[str, str]:
    return {"hello": "world"}


app = Ravyn(
    routes=[Gateway(handler=foo)],
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
            "/foo": {
                "post": {
                    "tags": ["test", "foo"],
                    "summary": "Foo",
                    "description": "",
                    "operationId": "foo_foo_post",
                    "responses": {
                        "201": {
                            "description": "Additional response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PydanticError"}
                                }
                            },
                        },
                        "200": {
                            "description": "Additional response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MsgSpecError"}
                                }
                            },
                        },
                    },
                    "deprecated": False,
                }
            }
        },
        "components": {
            "schemas": {
                "MsgSpecError": {
                    "properties": {
                        "detail": {"type": "string", "title": "Detail"},
                        "code": {"type": "integer", "title": "Code"},
                    },
                    "type": "object",
                    "required": ["detail", "code"],
                    "title": "MsgSpecError",
                },
                "PydanticError": {
                    "properties": {
                        "detail": {"type": "string", "title": "Detail"},
                        "code": {"type": "integer", "title": "Code"},
                    },
                    "type": "object",
                    "required": ["detail", "code"],
                    "title": "PydanticError",
                },
            }
        },
        "tags": ["test"],
    }
