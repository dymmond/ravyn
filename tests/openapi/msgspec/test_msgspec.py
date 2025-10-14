from typing import Union

import msgspec
from pydantic import BaseModel
from typing_extensions import Annotated

from ravyn.core.datastructures.msgspec import Struct
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import post
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class User(Struct):
    name: str
    email: Union[str, None] = None


class BaseUser(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    user: User


class Address(msgspec.Struct):
    name: str


class AddressBook(msgspec.Struct):
    address: Address


Id = Annotated[int, msgspec.Meta(gt=0)]
Email = Annotated[str, msgspec.Meta(min_length=5, max_length=100, pattern="[^@]+@[^@]+\\.[^@]+")]


class Comment(msgspec.Struct):
    id: Id
    email: Email


@post()
def user(payload: User) -> User:
    return payload


def test_user_msgspec_openapi(test_client_factory):
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
                            "201": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "properties": {
                                                "name": {"type": "string", "title": "Name"},
                                                "email": {
                                                    "anyOf": [
                                                        {"type": "string"},
                                                        {"type": "null"},
                                                    ],
                                                    "title": "Email",
                                                },
                                            },
                                            "type": "object",
                                            "required": ["name", "email"],
                                            "title": "User",
                                        }
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
