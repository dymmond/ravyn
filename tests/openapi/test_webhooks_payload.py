from datetime import datetime

from pydantic import BaseModel

from ravyn import WebhookGateway, whpost
from ravyn.testclient import create_client
from tests.settings import AppTestSettings


class Payment(BaseModel):
    is_paid: bool
    amount: float
    paid_at: datetime


@whpost("new-payment", description="User receives a notification for every payment done.")
async def new_payment(payload: Payment) -> None:
    """"""


def test_openapi_schema():
    with create_client(
        routes=[],
        enable_openapi=True,
        webhooks=[WebhookGateway(handler=new_payment)],
        settings_module=AppTestSettings,
    ) as client:
        response = client.get("/openapi.json")

        assert response.status_code == 200, response.text
        assert response.json()["webhooks"] == {
            "new-payment": {
                "post": {
                    "summary": "New Payment",
                    "description": "User receives a notification for every payment done.",
                    "operationId": "new_paymentnew_payment_post",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Payment"}
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
                                    "schema": {"$ref": "#/components/schemas/HTTPValidationError"}
                                }
                            },
                        },
                    },
                    "deprecated": False,
                }
            }
        }

        assert response.json()["components"] == {
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
                "Payment": {
                    "properties": {
                        "is_paid": {"type": "boolean", "title": "Is Paid"},
                        "amount": {"type": "number", "title": "Amount"},
                        "paid_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Paid At",
                        },
                    },
                    "type": "object",
                    "required": ["is_paid", "amount", "paid_at"],
                    "title": "Payment",
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
        }
