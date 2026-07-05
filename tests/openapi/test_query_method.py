from pydantic import BaseModel

from ravyn import Gateway, Query, WebhookGateway, query, whquery
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class SearchPayload(BaseModel):
    term: str
    limit: int


@query("/search", tags=["search"])
async def search(payload: SearchPayload, page: int = Query()) -> dict:
    return {"term": payload.term, "limit": payload.limit, "page": page}


@whquery("search-webhook")
async def search_webhook(payload: SearchPayload) -> None: ...


def test_query_route_openapi_schema() -> None:
    with create_client(
        routes=[Gateway(handler=search)],
        enable_openapi=True,
        settings_module=AppTestSettings,
    ) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200, response.text

    schema = response.json()
    operation = schema["paths"]["/search"]["query"]

    assert schema["openapi"] == "3.2.0"
    assert operation["operationId"] == "search_search_query"
    assert operation["parameters"] == [
        {
            "name": "page",
            "in": "query",
            "required": True,
            "deprecated": False,
            "allowEmptyValue": False,
            "allowReserved": False,
            "schema": {"type": "integer", "title": "Page"},
        }
    ]
    assert operation["requestBody"] == {
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/SearchPayload"}}
        },
        "required": True,
    }
    assert "SearchPayload" in schema["components"]["schemas"]


def test_query_webhook_openapi_schema() -> None:
    with create_client(
        routes=[],
        enable_openapi=True,
        webhooks=[WebhookGateway(handler=search_webhook)],
        settings_module=AppTestSettings,
    ) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200, response.text

    schema = response.json()
    operation = schema["webhooks"]["search-webhook"]["query"]

    assert schema["openapi"] == "3.2.0"
    assert operation["operationId"] == "search_webhooksearch_webhook_query"
    assert operation["requestBody"] == {
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/SearchPayload"}}
        },
        "required": True,
    }
