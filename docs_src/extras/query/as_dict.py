from typing import Any
from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{id}")
async def read_user(id: int, roles: dict[str, Any] | None = None) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
