from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from lilya import status
from typing_extensions import Annotated, Doc

from ravyn.permissions.types import Permission
from ravyn.routing._decorator_factory import _create_handler_decorator, _create_route_decorator
from ravyn.routing.router import WebSocketHandler

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.types import (
        Dependencies,
        ExceptionHandlerMap,
        Middleware,
    )


SUCCESSFUL_RESPONSE = "Successful response"

F = TypeVar("F", bound=Callable[..., Any])


get = _create_handler_decorator("GET", status.HTTP_200_OK)
head = _create_handler_decorator("HEAD", status.HTTP_200_OK)
post = _create_handler_decorator("POST", status.HTTP_201_CREATED)
put = _create_handler_decorator("PUT", status.HTTP_200_OK)
patch = _create_handler_decorator("PATCH", status.HTTP_200_OK)
delete = _create_handler_decorator("DELETE", status.HTTP_204_NO_CONTENT)
options = _create_handler_decorator("OPTIONS", status.HTTP_200_OK)
trace = _create_handler_decorator("TRACE", status.HTTP_200_OK)
route = _create_route_decorator(is_webhook=False)


def websocket(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.

            **Example**

            ```python
            @websocket()
            ```

            **Example with parameters**

            ```python
            @websocket(path="/{age: int}")
            ```
            """
        ),
    ] = None,
    *,
    name: Annotated[
        Optional[str],
        Doc(
            """
            The name for the Gateway. The name can be reversed by `url_path_for()`.
            """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
            A dictionary of string and [Inject](https://ravyn.dev/dependencies/) instances enable application level dependency injection.
            """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
            A dictionary of [exception types](https://ravyn.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
            """
        ),
    ] = None,
    middleware: Annotated[
        Optional[list["Middleware"]],
        Doc(
            """
            A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
            """
        ),
    ] = None,
    permissions: Annotated[
        Optional[list["Permission"]],
        Doc(
            """
            A list of [permissions](https://ravyn.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
            """
        ),
    ] = None,
    before_request: Annotated[
        Union[Sequence[Callable[..., Any]], None],
        Doc(
            """
            A list of events that are triggered before the application processes the request.
            """
        ),
    ] = None,
    after_request: Annotated[
        Union[Sequence[Callable[..., Any]], None],
        Doc(
            """
            A list of events that are triggered after the application processes the request.
            """
        ),
    ] = None,
) -> Callable[[F], WebSocketHandler]:
    def wrapper(func: Any) -> WebSocketHandler:
        handler = WebSocketHandler(
            path=path,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            name=name,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = func
        handler.validate_websocket_handler_function()
        return handler

    return wrapper
