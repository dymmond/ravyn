from ravyn import Ravyn, Gateway, JSONResponse, Query, get


@get("/users")
async def read_user(q: str = Query(max_length=10)) -> JSONResponse: ...


app = Ravyn(
    routes=[
        Gateway(read_user),
    ]
)
