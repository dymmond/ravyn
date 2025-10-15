from typing import Any, Annotated
from ravyn import Ravyn, Gateway, JSONResponse, Query, get
from ravyn.params import Query


@get("/users/{id}")
async def read_user(
    id: int, roles: Annotated[dict[str, Any] | None, Query()] = None
) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
