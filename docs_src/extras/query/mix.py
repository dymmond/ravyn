from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{id}")
async def read_user(
    id: int,
    roles: list[str] | None = None,
    positions: list[str] | None = None,
    indexes: list[int] | None = None,
    others: dict[str, str] | None = None,
    q: str | None = None,
) -> JSONResponse:
    """
    A lot of query parameters passed here
    """
    return JSONResponse(
        {
            "id": id,
            "roles": roles,
            "positions": positions,
            "indexes": indexes,
            "others": others,
            "q": q,
        }
    )


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
