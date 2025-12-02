from typing import Any

from ravyn import Gateway, Inject, Injects, get
from ravyn.security.http import HTTPAuthorizationCredentials, HTTPBase
from ravyn.testclient import create_client

security = HTTPBase(scheme="Other")


@get(
    "/users/me",
    dependencies={"credentials": Inject(security)},
    security=[security],
)
def read_current_user(
    credentials: HTTPAuthorizationCredentials = Injects(),
) -> Any:
    if credentials is None:
        return {"msg": "Create an account first"}
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}


def test_security_http_base():
    with create_client(routes=[Gateway(handler=read_current_user)]) as client:
        response = client.get("/users/me", headers={"Authorization": "Other foobar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"scheme": "Other", "credentials": "foobar"}


def test_security_http_base_no_credentials():
    with create_client(routes=[Gateway(handler=read_current_user)]) as client:
        response = client.get("/users/me")
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_openapi_schema():
    with create_client(routes=[Gateway(handler=read_current_user)], enable_openapi=True) as client:
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
                "/users/me": {
                    "get": {
                        "summary": "Read Current User",
                        "description": "",
                        "operationId": "read_current_user_users_me_get",
                        "deprecated": False,
                        "security": [
                            {
                                "HTTPBase": {
                                    "type": "http",
                                    "scheme": "Other",
                                    "scheme_name": "HTTPBase",
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                    }
                }
            },
            "components": {"securitySchemes": {"HTTPBase": {"type": "http", "scheme": "Other"}}},
        }
