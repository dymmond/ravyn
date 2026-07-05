from ravyn import JSONResponse, Request, get


@get(tags=["home"])
async def home(request: Request) -> JSONResponse:
    """
    Ravyn request has a `user` property that also
    comes from its origins (Lilya).

    When building an authentication middleware, it
    is recommended to use `AuthenticationMiddleware`.

    See more info here: https://ravyn.dymmond.com/middleware/authentication/
    """
    return JSONResponse({"message": f"hello {request.user.email}"})
