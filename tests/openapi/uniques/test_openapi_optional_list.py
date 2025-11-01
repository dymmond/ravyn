from typing import List, Optional

from ravyn import Gateway, JSONResponse, get
from ravyn.testclient import create_client
from tests.openapi.utils import normalize_openapi


@get("/list")
async def check_list(a_value: Optional[List[str]]) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_open_api(test_app_client_factory):
    with create_client(routes=Gateway(handler=check_list)) as client:
        response = client.get("/openapi.json")

        assert response.status_code == 200, response.text

        got = normalize_openapi(response.json())

        assert got == {
            "openapi": "3.1.0",
            "info": {
                "title": "Ravyn",
                "summary": "Ravyn application",
                "description": "Highly scalable, performant, easy to learn and for every application.",
                "contact": {"name": "admin", "email": "admin@myapp.com"},
                "version": client.app.version,
            },
            "servers": [{"url": "/"}],
            "paths": {
                "/list": {
                    "get": {
                        "summary": "Check List",
                        "description": "",
                        "operationId": "check_list_list_get",
                        "parameters": [
                            {
                                "name": "a_value",
                                "in": "query",
                                "required": False,
                                "deprecated": False,
                                "allowEmptyValue": False,
                                "allowReserved": False,
                                "schema": {
                                    "items": {"type": "string"},
                                    "type": "array",
                                    "title": "A Value",
                                },
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            },
                            "422": {
                                "description": "Validation Error",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/HTTPValidationError"
                                        }
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
        }
