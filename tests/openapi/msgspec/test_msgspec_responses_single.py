from typing import Union

from ravyn.core.datastructures.msgspec import Struct
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import post
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class User(Struct):
    name: str
    email: Union[str, None] = None


@post(responses={203: OpenAPIResponse(model=User)})
def user(payload: User) -> None: ...


def test_user_msgspec_with_pydantic_openapi(test_client_factory):
    with create_client(routes=[Gateway(handler=user)], settings_module=AppTestSettings) as client:
        response = client.get("/openapi.json")

        assert response.json() == {
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
                "/": {
                    "post": {
                        "summary": "User",
                        "description": "",
                        "operationId": "user__post",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            },
                            "required": True,
                        },
                        "responses": {
                            "201": {"description": "Successful response"},
                            "203": {
                                "description": "Additional response",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
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
                    "User": {
                        "properties": {
                            "name": {"type": "string", "title": "Name"},
                            "email": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "title": "Email",
                            },
                        },
                        "type": "object",
                        "required": ["name", "email"],
                        "title": "User",
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
