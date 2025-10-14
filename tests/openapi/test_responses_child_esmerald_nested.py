from typing import Dict, Union

import pytest
from pydantic import BaseModel

from ravyn import JSON, ChildRavyn, Gateway, Include, get
from ravyn.conf import monkay as monkay_for_settings
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class Item(BaseModel):
    sku: Union[int, str]


@get()
def read_people() -> Dict[str, str]:
    """ """


@get(
    "/item",
    description="Read an item",
    responses={200: OpenAPIResponse(model=Item, description="The SKU information of an item")},
)
async def read_item() -> JSON:
    """ """


@pytest.fixture(scope="function", autouse=True)
def isolate_global_settings():
    with monkay_for_settings.with_settings(AppTestSettings()):
        yield


def test_child_nested_ravyn_disabled_openapi():
    with create_client(
        routes=[
            Gateway(handler=read_people),
            Include(
                "/child",
                app=ChildRavyn(
                    routes=[
                        Gateway(handler=read_item),
                        Include(
                            "/another-child",
                            app=ChildRavyn(
                                routes=[Gateway(handler=read_item)],
                                enable_openapi=False,
                                include_in_schema=True,
                            ),
                        ),
                    ],
                    enable_openapi=False,
                    include_in_schema=True,
                    root_path_in_servers=False,
                ),
            ),
        ],
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
                }
            },
            "components": {
                "schemas": {
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
                    }
                }
            },
        }


def test_child_nested_ravyn_not_included_in_schema(test_client_factory):
    with create_client(
        routes=[
            Include(
                "/child",
                app=ChildRavyn(
                    routes=[
                        Gateway(handler=read_item),
                        Include(
                            "/another-child",
                            app=ChildRavyn(
                                routes=[Gateway(handler=read_item)],
                                enable_openapi=True,
                                include_in_schema=False,
                            ),
                        ),
                    ],
                    enable_openapi=True,
                    include_in_schema=False,
                ),
            ),
            Gateway(handler=read_people),
        ],
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
                }
            },
            "components": {
                "schemas": {
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
                    }
                }
            },
        }


def test_access_nested_child_ravyn_openapi_only(test_client_factory):
    with create_client(
        routes=[
            Gateway(handler=read_people),
            Include(
                "/child",
                app=ChildRavyn(
                    routes=[
                        Gateway(handler=read_item),
                        Include(
                            "/another-child",
                            app=ChildRavyn(
                                routes=[Gateway(handler=read_item)],
                                enable_openapi=True,
                                include_in_schema=True,
                            ),
                        ),
                    ],
                    enable_openapi=True,
                    include_in_schema=True,
                ),
            ),
        ],
    ) as client:
        response = client.get("/child/another-child/openapi.json")
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
            "servers": [{"url": "/child/another-child"}, {"url": "/"}],
            "paths": {
                "/item": {
                    "get": {
                        "summary": "Read Item",
                        "description": "Read an item",
                        "operationId": "read_item_item_get",
                        "responses": {
                            "200": {
                                "description": "The SKU information of an item",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Item"}
                                    }
                                },
                            }
                        },
                        "deprecated": False,
                    }
                }
            },
            "components": {
                "schemas": {
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
                    }
                }
            },
        }


def test_access_nested_child_ravyn_openapi_only_with_disable_openapi_on_parent(
    test_client_factory,
):
    with create_client(
        routes=[
            Gateway(handler=read_people),
            Include(
                "/child",
                app=ChildRavyn(
                    routes=[
                        Gateway(handler=read_item),
                        Include(
                            "/another-child",
                            app=ChildRavyn(
                                routes=[Gateway(handler=read_item)],
                                enable_openapi=True,
                                include_in_schema=True,
                                description="Test description",
                                summary="A summary",
                            ),
                        ),
                    ],
                    enable_openapi=False,
                    include_in_schema=False,
                ),
            ),
        ],
    ) as client:
        response = client.get("/child/another-child/openapi.json")
        assert response.status_code == 200, response.text

        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Ravyn",
                "summary": "A summary",
                "description": "Test description",
                "contact": {"name": "admin", "email": "admin@myapp.com"},
                "version": client.app.version,
            },
            "servers": [{"url": "/child/another-child"}, {"url": "/"}],
            "paths": {
                "/item": {
                    "get": {
                        "summary": "Read Item",
                        "description": "Read an item",
                        "operationId": "read_item_item_get",
                        "responses": {
                            "200": {
                                "description": "The SKU information of an item",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Item"}
                                    }
                                },
                            }
                        },
                        "deprecated": False,
                    }
                }
            },
            "components": {
                "schemas": {
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
                    }
                }
            },
        }


def test_access_nested_child_ravyn_openapi_only_with_disable_include_openapi_openapi_on_parent(
    test_client_factory,
):
    with create_client(
        routes=[
            Gateway(handler=read_people),
            Include(
                "/child",
                app=ChildRavyn(
                    routes=[
                        Gateway(handler=read_item),
                        Include(
                            "/another-child",
                            app=ChildRavyn(
                                routes=[Gateway(handler=read_item)],
                                enable_openapi=True,
                                include_in_schema=True,
                            ),
                        ),
                    ],
                    enable_openapi=True,
                    include_in_schema=False,
                ),
            ),
        ],
    ) as client:
        response = client.get("/child/another-child/openapi.json")
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
            "servers": [{"url": "/child/another-child"}, {"url": "/"}],
            "paths": {
                "/item": {
                    "get": {
                        "summary": "Read Item",
                        "description": "Read an item",
                        "operationId": "read_item_item_get",
                        "responses": {
                            "200": {
                                "description": "The SKU information of an item",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Item"}
                                    }
                                },
                            }
                        },
                        "deprecated": False,
                    }
                }
            },
            "components": {
                "schemas": {
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
                    }
                }
            },
        }
