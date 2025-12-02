from typing import Any

from pydantic import BaseModel

from ravyn import Gateway, Inject, Injects, Security, get
from ravyn.security.open_id import OpenIdConnect
from ravyn.testclient import create_client

oid = OpenIdConnect(openIdConnectUrl="/openid", description="OpenIdConnect security scheme")


class User(BaseModel):
    username: str


def get_current_user(oauth_header: str = Security(oid)):
    user = User(username=oauth_header)
    return user


@get("/users/me", security=[oid], dependencies={"current_user": Inject(get_current_user)})
def read_current_user(current_user: User = Injects()) -> Any:
    return current_user


def test_security_oauth2():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/users/me", headers={"Authorization": "Bearer footokenbar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "Bearer footokenbar"}


def test_security_oauth2_password_other_header():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/users/me", headers={"Authorization": "Other footokenbar"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "Other footokenbar"}


def test_security_oauth2_password_bearer_no_header():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
    ) as client:
        response = client.get("/users/me")
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_openapi_schema():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        enable_openapi=True,
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
                "/users/me": {
                    "get": {
                        "summary": "Read Current User",
                        "description": "",
                        "operationId": "read_current_user_users_me_get",
                        "deprecated": False,
                        "security": [
                            {
                                "OpenIdConnect": {
                                    "type": "openIdConnect",
                                    "description": "OpenIdConnect security scheme",
                                    "openIdConnectUrl": "/openid",
                                    "scheme_name": "OpenIdConnect",
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
                "securitySchemes": {
                    "OpenIdConnect": {
                        "type": "openIdConnect",
                        "description": "OpenIdConnect security scheme",
                        "openIdConnectUrl": "/openid",
                    }
                }
            },
        }
