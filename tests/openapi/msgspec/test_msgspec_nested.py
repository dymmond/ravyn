from ravyn.core.datastructures.msgspec import Struct
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import post
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class Address(Struct):
    name: str


class AddressBook(Struct):
    address: Address


@post()
def user_with_pydantic(payload: AddressBook) -> None: ...


def test_user_msgspec_openapi(test_client_factory):
    with create_client(
        routes=[Gateway(handler=user_with_pydantic)], settings_module=AppTestSettings
    ) as client:
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
                        "summary": "User With Pydantic",
                        "description": "",
                        "operationId": "user_with_pydantic__post",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AddressBook"}
                                }
                            },
                            "required": True,
                        },
                        "responses": {
                            "201": {"description": "Successful response"},
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
                    "AddressBook": {
                        "properties": {
                            "address": {
                                "properties": {"name": {"type": "string"}},
                                "type": "object",
                                "required": ["name"],
                                "title": "Address",
                            }
                        },
                        "type": "object",
                        "required": ["address"],
                        "title": "AddressBook",
                    },
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
