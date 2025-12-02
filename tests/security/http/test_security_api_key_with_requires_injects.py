from typing import Any

from lilya.middleware import DefineMiddleware
from lilya.middleware.request_context import RequestContextMiddleware
from pydantic import BaseModel

from ravyn import Gateway, Inject, Injects, Requires, Security, get
from ravyn.security.api_key import APIKeyInCookie
from ravyn.testclient import create_client

api_key = APIKeyInCookie(name="key")


class User(BaseModel):
    username: str


def get_current_user(oauth_header: str = Security(api_key)):
    user = User(username=oauth_header)
    return user


def get_user(user: User = Requires(get_current_user)) -> User:
    return user


@get("/users/me", security=[api_key], dependencies={"current_user": Inject(get_user)})
def read_current_user(current_user: User = Injects()) -> Any:
    return current_user


def test_security_api_key():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        middleware=[DefineMiddleware(RequestContextMiddleware)],
    ) as client:
        response = client.get("/users/me", cookies={"key": "secret"})
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "secret"}


def test_security_api_key_no_key():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
        middleware=[DefineMiddleware(RequestContextMiddleware)],
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
                                "APIKeyInCookie": {
                                    "type": "apiKey",
                                    "name": "key",
                                    "in": "cookie",
                                    "scheme_name": "APIKeyInCookie",
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
                    "APIKeyInCookie": {"type": "apiKey", "name": "key", "in": "cookie"}
                }
            },
        }
