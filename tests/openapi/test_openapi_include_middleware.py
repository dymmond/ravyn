from typing import Any, Dict, Union

from lilya.types import ASGIApp, Receive, Scope, Send
from pydantic import BaseModel

from ravyn import Gateway, Include, MiddlewareProtocol, get
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class Item(BaseModel):
    sku: Union[int, str]


class CustomMiddleware(MiddlewareProtocol):
    def __init__(self, app: ASGIApp, **kwargs: Any):
        super().__init__(app, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.app(scope, receive, send)


@get(middleware=[CustomMiddleware])
def read_people() -> Dict[str, str]:
    """ """


@get()
def read_mode() -> Dict[str, str]:
    """ """


@get("/item")
async def read_item() -> Dict[str, str]:
    """ """


def test_add_middleware_to_openapi(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=read_people),
            Gateway("/read-mode", handler=read_mode, middleware=[CustomMiddleware]),
            Include(
                "/child",
                routes=[Gateway(handler=read_item, middleware=[CustomMiddleware])],
            ),
        ],
        enable_openapi=True,
        settings_module=AppTestSettings,
    ) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200, response.text

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
                "/read-mode": {
                    "get": {
                        "summary": "Read Mode",
                        "description": "",
                        "operationId": "read_mode_read_mode_get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                },
                "/child/item": {
                    "get": {
                        "summary": "Read Item",
                        "description": "",
                        "operationId": "read_item_item_get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                },
                "/": {
                    "get": {
                        "summary": "Read People",
                        "description": "",
                        "operationId": "read_people__get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                },
            },
        }
