from __future__ import annotations

from ravyn import Gateway, JSONResponse, Ravyn, Request, post
from ravyn.contrib.cqrs import (
    CommandBus,
)
from ravyn.testclient import RavynTestClient


class Increment:
    def __init__(self, value: int) -> None:
        self.value = value


def test_endpoint_runs_cqrs_middleware_and_can_mutate_message(
    test_client_factory,
) -> None:
    seen: dict[str, int] = {"value": 0}

    async def bump_middleware(msg: Increment, nxt):
        msg.value += 1
        return await nxt(msg)

    bus = CommandBus(middleware=[bump_middleware])

    def handler(cmd: Increment) -> None:
        seen["value"] = cmd.value

    bus.register(Increment, handler)

    @post()
    async def endpoint(request: Request) -> JSONResponse:
        data = await request.json()
        await bus.dispatch(Increment(value=data["value"]))
        return JSONResponse({"seen": seen["value"]})

    app = Ravyn(routes=[Gateway("/inc", handler=endpoint)])
    client = RavynTestClient(app)

    r = client.post("/inc", json={"value": 1})

    assert r.status_code == 200

    # middleware should bump 1 -> 2 before handler
    assert r.json() == {"seen": 2}
