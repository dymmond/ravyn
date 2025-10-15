from typing import Annotated

from ravyn import Ravyn, Gateway, JSONResponse, Query, get


@get("/users/{id}")
async def read_user(
    id: int,
    role: Annotated[list[int] | None, Query()] = None,
) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
