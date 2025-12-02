from typing import Any

from pydantic import BaseModel

from ravyn import Gateway, Include, Inject, Injects, Security, get
from ravyn.security.api_key import APIKeyInQuery
from ravyn.testclient import create_client

api_key = APIKeyInQuery(name="key", description="API Key Query")


class User(BaseModel):
    username: str


def get_current_user(oauth_header: str = Security(api_key)):
    if oauth_header is None:
        return None
    user = User(username=oauth_header)
    return user


@get("/users/me", dependencies={"current_user": Inject(get_current_user)})
def read_current_user(current_user: User = Injects()) -> Any:
    if current_user is None:
        return {"msg": "Create an account first"}
    else:
        return current_user


def test_security_api_key():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
    ) as client:
        response = client.get("/users/me?key=secret")
        assert response.status_code == 200, response.text
        assert response.json() == {"username": "secret"}


def test_security_api_key_no_key():
    with create_client(
        routes=[
            Gateway(handler=read_current_user),
        ],
    ) as client:
        response = client.get("/users/me")
        assert response.status_code == 401, response.text
        assert response.json() == {"detail": "Not authenticated"}


def test_openapi_schema():
    with create_client(
        routes=[
            Include(routes=[Gateway(handler=read_current_user)], security=[api_key]),
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
                                "APIKeyInQuery": {
                                    "type": "apiKey",
                                    "description": "API Key Query",
                                    "name": "key",
                                    "in": "query",
                                    "scheme_name": "APIKeyInQuery",
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
                    "APIKeyInQuery": {
                        "type": "apiKey",
                        "description": "API Key Query",
                        "name": "key",
                        "in": "query",
                    }
                }
            },
        }
