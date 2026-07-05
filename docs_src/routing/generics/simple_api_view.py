from ravyn import SimpleAPIController, delete, get, patch, post, put


class UserAPI(SimpleAPIController):
    @get()
    async def get(self) -> str: ...

    @post()
    async def post(self) -> str: ...

    @put()
    async def put(self) -> str: ...

    @patch()
    async def patch(self) -> str: ...

    @delete()
    async def delete(self) -> None: ...
