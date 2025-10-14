from typing import Dict, Optional

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
async def bar(name: Optional[str]) -> Dict[str, str]:
    return {"hello": "world"}


app = Ravyn(
    routes=[Gateway(handler=bar)],
    enable_openapi=True,
    tags=["test"],
    settings_module=AppTestSettings,
    contact={"name": "ravyn", "email": "ravyn@esmeral.dev"},
)


client = RavynTestClient(app)


def test_openapi_query_params_optional(test_client_factory):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Ravyn",
            "summary": "Ravyn application",
            "description": "Highly scalable, performant, easy to learn and for every application.",
            "contact": {"name": "ravyn", "email": "ravyn@esmeral.dev"},
            "version": client.app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/bar": {
                "get": {
                    "tags": ["test", "bar"],
                    "summary": "Bar",
                    "description": "",
                    "operationId": "bar_bar_get",
                    "parameters": [
                        {
                            "name": "name",
                            "in": "query",
                            "required": False,
                            "deprecated": False,
                            "allowEmptyValue": False,
                            "allowReserved": False,
                            "schema": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "title": "Name",
                            },
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Pydantic response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PydanticError"}
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HTTPValidationError"}
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
                "HTTPValidationError": {
                    "properties": {
                        "detail": {
                            "items": {"$ref": "#/components/schemas/ValidationError"},
                            "type": "array",
                            "title": "Detail",
                        }
                    },
                    "type": "object",
                    "title": "HTTPValidationError",
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
                "ValidationError": {
                    "properties": {
                        "loc": {
                            "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                            "type": "array",
                            "title": "Location",
                        },
                        "msg": {"type": "string", "title": "Message"},
                        "type": {"type": "string", "title": "Error Type"},
                    },
                    "type": "object",
                    "required": ["loc", "msg", "type"],
                    "title": "ValidationError",
                },
            }
        },
        "tags": ["test"],
    }
