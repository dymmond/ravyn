from __future__ import annotations

from ravyn import Gateway, JSONResponse, Ravyn, Request, get, post
from ravyn.contrib.cqrs import CommandBus, QueryBus
from ravyn.testclient import RavynTestClient


class CreateUser:
    def __init__(self, user_id: str, email: str) -> None:
        self.user_id = user_id
        self.email = email


class GetUserEmail:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


def build_app():
    store: dict[str, str] = {}

    cmd_bus = CommandBus()
    qry_bus: QueryBus[str | None] = QueryBus()

    def handle_create(cmd: CreateUser) -> None:
        store[cmd.user_id] = cmd.email

    def handle_get(q: GetUserEmail) -> str | None:
        return store.get(q.user_id)

    cmd_bus.register(CreateUser, handle_create)
    qry_bus.register(GetUserEmail, handle_get)

    @post()
    async def create_user(request: Request) -> JSONResponse:
        data = await request.json()
        await cmd_bus.dispatch(CreateUser(user_id=data["user_id"], email=data["email"]))
        return JSONResponse({"status": "created"}, status_code=201)

    @get()
    async def get_user_email(request: Request) -> JSONResponse:
        user_id = request.path_params["user_id"]
        email = await qry_bus.ask(GetUserEmail(user_id=user_id))

        if email is None:
            return JSONResponse({"detail": "not found"}, status_code=404)
        return JSONResponse({"user_id": user_id, "email": email})

    routes = [
        Gateway("/users", handler=create_user),
        Gateway("/users/{user_id}", handler=get_user_email),
    ]

    return Ravyn(routes=routes)


def test_post_then_get_roundtrip(test_client_factory) -> None:
    app = build_app()
    client = RavynTestClient(app)

    r = client.post("/users", json={"user_id": "u1", "email": "u1@example.com"})
    assert r.status_code == 201
    assert r.json() == {"status": "created"}

    r = client.get("/users/u1")
    assert r.status_code == 200
    assert r.json() == {"user_id": "u1", "email": "u1@example.com"}


def test_get_missing_returns_404(test_client_factory) -> None:
    app = build_app()
    client = RavynTestClient(app)

    r = client.get("/users/nope")
    assert r.status_code == 404
    assert r.json() == {"detail": "not found"}


def test_post_invalid_json_is_error(test_client_factory) -> None:
    """
    We don't pin the exact error body because frameworks vary,
    but we prove Lilya is parsing request.json() and failing properly.
    """
    app = build_app()
    client = RavynTestClient(app, raise_server_exceptions=False)

    r = client.post("/users", data=b'{"user_id": "u2", "email": ')  # invalid JSON
    assert r.status_code >= 400
