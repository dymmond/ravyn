from typing import Union

from pydantic import BaseModel

from ravyn import Gateway, get
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class Item(BaseModel):
    sku: Union[int, str]


@get()
def read_item() -> Item:
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
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "properties": {
                                                "sku": {
                                                    "anyOf": [
                                                        {"type": "integer"},
                                                        {"type": "string"},
                                                    ],
                                                    "title": "Sku",
                                                }
                                            },
                                            "type": "object",
                                            "required": ["sku"],
                                            "title": "Item",
                                        }
                                    }
                                },
                            }
                        },
                        "deprecated": False,
                    }
                }
            },
        }
