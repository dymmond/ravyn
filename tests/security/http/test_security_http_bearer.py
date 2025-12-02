from typing import Any

from ravyn import Inject, Injects, get
from ravyn.security.http import HTTPAuthorizationCredentials, HTTPBearer
from ravyn.testclient import create_client

security = HTTPBearer()


@get(
    "/users/me",
    security=[security],
    dependencies={"credentials": Inject(security)},
)
def read_current_user(credentials: HTTPAuthorizationCredentials = Injects()) -> Any:
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}


def test_security_http_bearer():
    with create_client(routes=[read_current_user]) as client:
        response = client.get("/users/me", headers={"Authorization": "Bearer foobar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"scheme": "Bearer", "credentials": "foobar"}


def test_security_http_bearer_no_credentials():
    with create_client(routes=[read_current_user]) as client:
        response = client.get("/users/me")
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_security_http_bearer_incorrect_scheme_credentials():
    with create_client(routes=[read_current_user]) as client:
        response = client.get("/users/me", headers={"Authorization": "Basic notreally"})
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Invalid authentication credentials"}


def test_openapi_schema():
    with create_client(routes=[read_current_user]) as client:
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
                                "HTTPBearer": {
                                    "type": "http",
                                    "scheme": "bearer",
                                    "scheme_name": "HTTPBearer",
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
            "components": {
                "securitySchemes": {"HTTPBearer": {"type": "http", "scheme": "bearer"}}
            },
        }
