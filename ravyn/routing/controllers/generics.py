from typing import ClassVar

from typing_extensions import Annotated, Doc

from ravyn.routing.controllers.views import (
    ListController,
    SimpleAPIController,
)


class GenericMixin:
    __is_generic__: ClassVar[bool] = True


class CreateAPIController(GenericMixin, SimpleAPIController):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIController`.

    ```python
    from ravyn.routing.controllers.generics import CreateAPIController
    ```

    **Example**

    ```python
    from ravyn import patch, post, put
    from ravyn.routing.controllers.generics import CreateAPIController


    class UserAPI(CreateAPIController):
        '''
        CreateAPIController only allows the `post`, `put` and `patch`
        to be used by default.
        '''

        @post()
        async def post(self) -> str:
            ...

        @put()
        async def put(self) -> str:
            ...

        @patch()
        async def patch(self) -> str:
        ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["post", "put", "patch"]


class DeleteAPIController(GenericMixin, SimpleAPIController):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIController`.

    ```python
    from ravyn.routing.controllers.generics import DeleteAPIController
    ```

    **Example**

    ```python
    from ravyn import delete
    from ravyn.routing.controllers.generics import DeleteAPIController


    class UserAPI(DeleteAPIController):
        '''
        DeleteAPIController only allows the `delete` to be used by default.
        '''

        @delete()
        async def delete(self) -> None:
            ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["delete"]


class ReadAPIController(GenericMixin, SimpleAPIController):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIController`.

    ```python
    from ravyn.routing.controllers.generics import ReadAPIController
    ```

    **Example**

    ```python
    from ravyn import get
    from ravyn.routing.controllers.generics import ReadAPIController


    class UserAPI(ReadAPIController):
        '''
        ReadAPIController only allows the `get` to be used by default..
        '''

        @get()
        async def get(self) -> None:
            ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["get"]


class ListAPIController(GenericMixin, ListController):
    """
    Only allows the return to be lists.
    """

    ...
