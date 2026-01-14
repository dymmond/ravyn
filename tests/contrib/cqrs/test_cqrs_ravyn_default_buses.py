from __future__ import annotations

from ravyn import Gateway, JSONResponse, Ravyn, Request, get, post
from ravyn.contrib.cqrs import (
    HandlerRegistry,
    command,
    default_command_bus,
    default_query_bus,
    query,
)
from ravyn.testclient import RavynTestClient


class SetValue:
    def __init__(self, key: str, value: str) -> None:
        self.key = key
        self.value = value


class GetValue:
    def __init__(self, key: str) -> None:
        self.key = key


def test_default_buses_work_inside_lilya_app(test_client_factory) -> None:
    # reset singletons to avoid leakage between tests
    default_command_bus._registry = HandlerRegistry()  # type: ignore[attr-defined]
    default_query_bus._registry = HandlerRegistry()  # type: ignore[attr-defined]

    store: dict[str, str] = {}

    @command(SetValue)
    def handle_set(cmd: SetValue) -> None:
        store[cmd.key] = cmd.value

    @query(GetValue)
    def handle_get(q: GetValue) -> str | None:
        return store.get(q.key)

    @post()
    async def set_endpoint(request: Request) -> JSONResponse:
        data = await request.json()
        await default_command_bus.dispatch(SetValue(key=data["key"], value=data["value"]))
        return JSONResponse({"ok": True})

    @get()
    async def get_endpoint(request: Request) -> JSONResponse:
        key = request.path_params["key"]
        val = await default_query_bus.ask(GetValue(key=key))
        if val is None:
            return JSONResponse({"detail": "not found"}, status_code=404)
        return JSONResponse({"value": val})

    app = Ravyn(
        routes=[
            Gateway("/kv", handler=set_endpoint),
            Gateway("/kv/{key}", handler=get_endpoint),
        ]
    )
    client = RavynTestClient(app)

    r = client.post("/kv", json={"key": "a", "value": "1"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    r = client.get("/kv/a")
    assert r.status_code == 200
    assert r.json() == {"value": "1"}

    r = client.get("/kv/missing")
    assert r.status_code == 404
    assert r.json() == {"detail": "not found"}
