from typing import Any, Optional

from ravyn import Inject, Injects, get
from ravyn.security.http import HTTPAuthorizationCredentials, HTTPDigest
from ravyn.testclient import create_client

security = HTTPDigest(auto_error=False)


@get("/users/me", security=[security], dependencies={"credentials": Inject(security)})
def read_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Injects(),
) -> Any:
    if credentials is None:
        return {"msg": "Create an account first"}
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}


def xtest_security_http_digest():
    with create_client(routes=[read_current_user]) as client:
        response = client.get("/users/me", headers={"Authorization": "Digest foobar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"scheme": "Digest", "credentials": "foobar"}


def test_security_http_digest_no_credentials():
    with create_client(routes=[read_current_user]) as client:
        response = client.get("/users/me")
        assert response.status_code == 200, response.text
        assert response.json() == {"msg": "Create an account first"}


def test_security_http_digest_incorrect_scheme_credentials():
    with create_client(routes=[read_current_user]) as client:
        response = client.get("/users/me", headers={"Authorization": "Other invalidauthorization"})
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
                                "HTTPDigest": {
                                    "type": "http",
                                    "scheme": "digest",
                                    "scheme_name": "HTTPDigest",
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
                "securitySchemes": {"HTTPDigest": {"type": "http", "scheme": "digest"}}
            },
        }
