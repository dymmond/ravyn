from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/users/{id}")
async def read_user(id: int, role: list[int] | None = None) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
