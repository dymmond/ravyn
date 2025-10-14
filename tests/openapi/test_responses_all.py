from typing import Dict

from ravyn import Gateway, Ravyn, Router, get
from ravyn.testclient import RavynTestClient
from tests.settings import AppTestSettings


@get()
def read_people() -> Dict[str, str]:
    return {"id": "foo"}


router = Router(routes=[Gateway(path="/people", handler=read_people)])


app = Ravyn(
    enable_openapi=True,
    version="2.0.0",
    title="Custom title",
    summary="Summary",
    description="Description",
    settings_module=AppTestSettings,
)
app.add_router(router=router)

client = RavynTestClient(app)


def test_path_operation():
    response = client.get("/people")
    assert response.status_code == 200, response.text
    assert response.json() == {"id": "foo"}


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Custom title",
            "summary": "Summary",
            "description": "Description",
            "contact": {"name": "admin", "email": "admin@myapp.com"},
            "version": app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/people": {
                "get": {
                    "summary": "Read People",
                    "description": "",
                    "operationId": "read_people_people_get",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {"application/json": {"schema": {"type": "string"}}},
                        }
                    },
                    "deprecated": False,
                }
            }
        },
    }


another_app = Ravyn(title="Ravyn", enable_openapi=True, settings_module=AppTestSettings)
another_router = Router(routes=[Gateway(path="/people", handler=read_people)])
another_app.add_router(router=another_router)

another_client = RavynTestClient(another_app)


def test_openapi_schema_default():
    response = another_client.get("/openapi.json")
    assert response.status_code == 200, response.text

    assert response.json() == {
        "openapi": "3.1.0",
        "info": {
            "title": "Ravyn",
            "summary": "Ravyn application",
            "description": "Highly scalable, performant, easy to learn and for every application.",
            "contact": {"name": "admin", "email": "admin@myapp.com"},
            "version": another_app.version,
        },
        "servers": [{"url": "/"}],
        "paths": {
            "/people": {
                "get": {
                    "summary": "Read People",
                    "description": "",
                    "operationId": "read_people_people_get",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {"application/json": {"schema": {"type": "string"}}},
                        }
                    },
                    "deprecated": False,
                }
            }
        },
    }
