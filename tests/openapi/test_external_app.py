from typing import Dict, Union

from flask import Flask, request
from markupsafe import escape
from pydantic import BaseModel

from ravyn import Gateway, Include, get
from ravyn.middleware.wsgi import WSGIMiddleware
from ravyn.testclient import create_client
from tests.settings import AppTestSettings

flask_app = Flask(__name__)


@flask_app.route("/")
def flask_main():  # pragma: no cover
    name = request.args.get("name", "Ravyn")
    return f"Hello, {escape(name)} from Flask!"


class Item(BaseModel):
    sku: Union[int, str]


@get()
def read_people() -> Dict[str, str]: ...


def test_external_app_not_include_in_schema(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=read_people),
            Include("/child", app=WSGIMiddleware(flask_app)),
        ],
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
