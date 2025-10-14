from typing import Union

from pydantic import BaseModel

from ravyn import Gateway, get
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class Item(BaseModel):
    sku: Union[int, str]


class ResponseOut(BaseModel):
    status: str
    message: str


class Another(BaseModel):
    status: str
    message: str


@get(
    responses={
        200: OpenAPIResponse(model=Item, description="Override default response of 200"),
        201: OpenAPIResponse(model=Another),
    }
)
def read_item() -> ResponseOut:
    """ """


def test_open_api_schema(test_client_factory):
    with create_client(
        routes=[Gateway(handler=read_item)],
        enable_openapi=True,
        include_in_schema=True,
        settings_module=AppTestSettings,
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
                    "get": {
                        "summary": "Read Item",
                        "description": "",
                        "operationId": "read_item__get",
                        "responses": {
                            "200": {
                                "description": "Override default response of 200",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Item"}
                                    }
                                },
                            },
                            "201": {
                                "description": "Additional response",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Another"}
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
                    "Another": {
                        "properties": {
                            "status": {"type": "string", "title": "Status"},
                            "message": {"type": "string", "title": "Message"},
                        },
                        "type": "object",
                        "required": ["status", "message"],
                        "title": "Another",
                    },
                    "Item": {
                        "properties": {
                            "sku": {
                                "anyOf": [{"type": "integer"}, {"type": "string"}],
                                "title": "Sku",
                            }
                        },
                        "type": "object",
                        "required": ["sku"],
                        "title": "Item",
                    },
                }
            },
        }
