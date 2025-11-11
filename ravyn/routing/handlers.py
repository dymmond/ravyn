from functools import wraps
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

from ravyn.exceptions import ImproperlyConfigured
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.permissions.types import Permission
from ravyn.routing.router import HTTPHandler, WebSocketHandler
from ravyn.utils.constants import AVAILABLE_METHODS
from ravyn.utils.enums import HttpMethod, MediaType

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.openapi.schemas.v3_1_0 import SecurityScheme
    from ravyn.types import (
        BackgroundTaskType,
        Dependencies,
        ExceptionHandlerMap,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
    )


SUCCESSFUL_RESPONSE = "Successful response"

F = TypeVar("F", bound=Callable[..., Any])


def get(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.

            **Example**

            ```python
            @get()
            ```

            **Example with parameters**

            ```python
            @get(path="/{age: int}")
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import get


            @get(summary="Black Window joining Pretenders")
            async def get_joiners() -> None:
                ...
            ```
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import get


            @get(description=...)
            async def get_joiners() -> None:
                ...
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import get, JSONResponse

            @get(response_class=JSONResponse)
            ```
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import get
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            @get(response_cookies=response_cookies)
            ```
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from ravyn import get
            from ravyn.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            @get(response_headers=response_headers)
            ```
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.

            **Example**

            ```python
            from ravyn import get

            @get(tags=["application"])
            ```
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.

            **Example**

            ```python
            from ravyn import get

            @get(deprecated=True)
            ```
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.

            **Example**

            ```python
            from ravyn import get
            from ravyn.openapi.security.http import Bearer

            @get(security=[Bearer()])
            ```
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.


            **Example**

            ```python
            from ravyn import get
            from ravyn.openapi.datastructures import OpenAPIResponse
            from pydantic import BaseModel

            class Power(BaseModel):
                name: str
                description: str


            class Error(BaseModel):
                detail: str


            @get(path='/read', responses={
                    200: OpenAPIResponse(model=Power, description=...)
                    400: OpenAPIResponse(model=Error, description=...)
                }
            )
            async def create() -> Union[None, ItemOut]:
                ...
            ```
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `get` and
    all of its operatations.

    **Example**

    ```python
    from ravyn import get


    @get()
    async def get() -> str:
        return "Hello, World!"
    ```
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=[HttpMethod.GET],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.GET.value
        handler.__original_status_code__ = status.HTTP_200_OK

        if status_code != handler.__original_status_code__:
            handler.__is_status_overridden__ = True

        handler.validate_handler()
        return handler

    return wrapper


def head(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `head` and
    all of its operatations.
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=[HttpMethod.HEAD],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.HEAD.value
        handler.__original_status_code__ = status.HTTP_200_OK

        if status_code != handler.__original_status_code__:
            handler.__is_status_overridden__ = True

        handler.validate_handler()
        return handler

    return wrapper


def post(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.

            **Example**

            ```python
            @post()
            ```

            **Example with parameters**

            ```python
            @post(path="/{age: int}")
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import post
            from pydantic import BaseModel


            class Pretender(BaseModel):
                name: str


            @post(summary="Black Window joining Pretenders")
            async def create_joiners(data: Pretender) -> None:
                ...
            ```
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import post


            @post(description=...)
            async def create_joiners() -> None:
                ...
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_201_CREATED,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import post, JSONResponse

            @post(response_class=JSONResponse)
            ```
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import post
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            @post(response_cookies=response_cookies)
            ```
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from ravyn import post
            from ravyn.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            @post(response_headers=response_headers)
            ```
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.

            **Example**

            ```python
            from ravyn import post

            @post(tags=["application"])
            ```
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.

            **Example**

            ```python
            from ravyn import post

            @post(deprecated=True)
            ```
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.

            **Example**

            ```python
            from ravyn import post
            from ravyn.openapi.security.http import Bearer

            @post(security=[Bearer()])
            ```
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.


            **Example**

            ```python
            from ravyn import post
            from ravyn.openapi.datastructures import OpenAPIResponse
            from pydantic import BaseModel

            class Power(BaseModel):
                name: str
                description: str


            class Error(BaseModel):
                detail: str


            @post(path='/read', responses={
                    200: OpenAPIResponse(model=Power, description=...)
                    400: OpenAPIResponse(model=Error, description=...)
                }
            )
            async def create() -> Union[None, ItemOut]:
                ...
            ```
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `post` and
    all of its operatations.

    **Example**

    ```python
    from ravyn import post


    @post()
    async def create() -> None:
        ...
    ```
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            summary=summary,
            description=description,
            methods=[HttpMethod.POST],
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.POST.value
        handler.__original_status_code__ = status.HTTP_201_CREATED
        handler.validate_handler()
        return handler

    return wrapper


def put(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.

            **Example**

            ```python
            @put()
            ```

            **Example with parameters**

            ```python
            @put(path="/{age: int}")
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import put


            @put(summary="Black Window joining Pretenders")
            async def update_joiners() -> None:
                ...
            ```
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import put


            @put(description=...)
            async def update_joiners() -> None:
                ...
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import put, JSONResponse

            @put(response_class=JSONResponse)
            ```
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import put
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            @put(response_cookies=response_cookies)
            ```
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from ravyn import put
            from ravyn.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            @put(response_headers=response_headers)
            ```
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.

            **Example**

            ```python
            from ravyn import put

            @put(tags=["application"])
            ```
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.

            **Example**

            ```python
            from ravyn import put

            @put(deprecated=True)
            ```
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.

            **Example**

            ```python
            from ravyn import put
            from ravyn.openapi.security.http import Bearer

            @put(security=[Bearer()])
            ```
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.


            **Example**

            ```python
            from ravyn import put
            from ravyn.openapi.datastructures import OpenAPIResponse
            from pydantic import BaseModel

            class Power(BaseModel):
                name: str
                description: str


            class Error(BaseModel):
                detail: str


            @put(path='/read', responses={
                    200: OpenAPIResponse(model=Power, description=...)
                    400: OpenAPIResponse(model=Error, description=...)
                }
            )
            async def create() -> Union[None, ItemOut]:
                ...
            ```
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `put` and
    all of its operatations.

    **Example**

    ```python
    from ravyn import put


    @put()
    async def update() -> str:
        return "updated!"
    ```
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=[HttpMethod.PUT],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.PUT.value
        handler.__original_status_code__ = status.HTTP_200_OK

        if status_code != handler.__original_status_code__:
            handler.__is_status_overridden__ = True

        handler.validate_handler()
        return handler

    return wrapper


def patch(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.

            **Example**

            ```python
            @patch()
            ```

            **Example with parameters**

            ```python
            @patch(path="/{age: int}")
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import patch


            @patch(summary="Black Window joining Pretenders")
            async def update_partial_joiners() -> None:
                ...
            ```
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import patch


            @patch(description=...)
            async def update_partial_joiners() -> None:
                ...
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import patch, JSONResponse

            @patch(response_class=JSONResponse)
            ```
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import patch
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            @patch(response_cookies=response_cookies)
            ```
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from ravyn import patch
            from ravyn.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            @patch(response_headers=response_headers)
            ```
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.

            **Example**

            ```python
            from ravyn import patch

            @patch(tags=["application"])
            ```
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.

            **Example**

            ```python
            from ravyn import patch

            @patch(deprecated=True)
            ```
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.

            **Example**

            ```python
            from ravyn import patch
            from ravyn.openapi.security.http import Bearer

            @patch(security=[Bearer()])
            ```
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.


            **Example**

            ```python
            from ravyn import patch
            from ravyn.openapi.datastructures import OpenAPIResponse
            from pydantic import BaseModel

            class Power(BaseModel):
                name: str
                description: str


            class Error(BaseModel):
                detail: str


            @patch(path='/read', responses={
                    200: OpenAPIResponse(model=Power, description=...)
                    400: OpenAPIResponse(model=Error, description=...)
                }
            )
            async def update() -> Union[None, ItemOut]:
                ...
            ```
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `path` and
    all of its operatations.

    **Example**

    ```python
    from ravyn import patch


    @patch()
    async def update_partial() -> str:
        return "done!"
    ```
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=[HttpMethod.PATCH],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.PATCH.value
        handler.__original_status_code__ = status.HTTP_200_OK

        if status_code != handler.__original_status_code__:
            handler.__is_status_overridden__ = True

        handler.validate_handler()
        return handler

    return wrapper


def delete(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.

            **Example**

            ```python
            @delete()
            ```

            **Example with parameters**

            ```python
            @delete(path="/{age: int}")
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import delete


            @delete(summary="Black Window joining Pretenders")
            async def delete_joiners() -> None:
                ...
            ```
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import delete


            @delete(description=...)
            async def delete_joiners() -> None:
                ...
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_204_NO_CONTENT,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import delete, JSONResponse

            @delete(response_class=JSONResponse)
            ```
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import delete
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            @delete(response_cookies=response_cookies)
            ```
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from ravyn import delete
            from ravyn.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            @delete(response_headers=response_headers)
            ```
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.

            **Example**

            ```python
            from ravyn import delete

            @delete(tags=["application"])
            ```
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.

            **Example**

            ```python
            from ravyn import delete

            @delete(deprecated=True)
            ```
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.

            **Example**

            ```python
            from ravyn import delete
            from ravyn.openapi.security.http import Bearer

            @delete(security=[Bearer()])
            ```
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.


            **Example**

            ```python
            from ravyn import delete
            from ravyn.openapi.datastructures import OpenAPIResponse
            from pydantic import BaseModel

            class Power(BaseModel):
                name: str
                description: str


            class Error(BaseModel):
                detail: str


            @delete(path='/read', responses={
                    400: OpenAPIResponse(model=Error, description=...)
                    401: OpenAPIResponse(model=Power, description=...)
                }
            )
            async def remove() -> Union[None, ItemOut]:
                ...
            ```
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `delete` and
    all of its operatations.

    **Example**

    ```python
    from ravyn import delete


    @delete()
    async def remove() -> None:
        ...
    ```
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=[HttpMethod.DELETE],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.DELETE.value
        handler.__original_status_code__ = status.HTTP_204_NO_CONTENT
        handler.validate_handler()
        return handler

    return wrapper


def options(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `options` and
    all of its operatations.
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=[HttpMethod.OPTIONS],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.OPTIONS.value
        handler.__original_status_code__ = status.HTTP_200_OK

        if status_code != handler.__original_status_code__:
            handler.__is_status_overridden__ = True

        handler.validate_handler()
        return handler

    return wrapper


def trace(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.
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
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for the HTTP method `trace` and
    all of its operatations.
    """

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=[HttpMethod.TRACE],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )
        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.TRACE.value
        handler.__original_status_code__ = status.HTTP_200_OK

        if status_code != handler.__original_status_code__:
            handler.__is_status_overridden__ = True

        handler.validate_handler()
        return handler

    return wrapper


def route(
    path: Annotated[
        Optional[str],
        Doc(
            """
            Relative path of the `handler`.
            The path can contain parameters in a dictionary like format
            and if the path is not provided, it will default to `/`.

            **Example**

            ```python
            @route()
            ```

            **Example with parameters**

            ```python
            @route(path="/{age: int}")
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
    methods: Annotated[
        list[str],
        Doc(
            """
            list of strings of methods allowed by the handler.

            **Example**

            ```python
            from ravyn import route


            @route(methods=["GET", "POST", "PUT", "DELETE"])
            async def handle_stuff() -> None:
                ...
            ```
            """
        ),
    ] = None,
    summary: Annotated[
        Optional[str],
        Doc(
            """
            The summary of the handler. This short summary is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import route


            @route(summary="Black Window joining Pretenders")
            async def operate() -> None:
                ...
            ```
            """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
            The description of the Ravyn application/API. This description is displayed when the [OpenAPI](https://ravyn.dev/openapi/) documentation is used.

            **Example**

            ```python
            from ravyn import route


            @route(description=...)
            async def operate_joiners() -> None:
                ...
            """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            An integer indicating the status code of the handler.

            This can be achieved by passing directly the value or
            by using the `ravyn.status` or even the `lilya.status`.
            """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content encoding of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
            The string indicating the content media type of the handler.

            This is used for the generation of the [OpenAPI](https://ravyn.dev/openapi/)
            documentation.
            """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
            An instance of an `ravyn.background.BackgroundTask` or `ravyn.background.BackgroundTasks` to be passed onto the handler.

            Read more about [Background tasks](https://ravyn.dev/background-tasks/) to
            understand what can be done.
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
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
            The default `media-type` used by the handler.
            """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Response class to be used within the
            handler application.

            Read more about the [Responses](https://ravyn.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from ravyn import route, JSONResponse

            @route(response_class=JSONResponse)
            ```
            """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `ravyn.datastructures.Cookie` objects.

            Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from ravyn import route
            from ravyn.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            @route(response_cookies=response_cookies)
            ```
            """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `ravyn.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://ravyn.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from ravyn import route
            from ravyn.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            @route(response_headers=response_headers)
            ```
            """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Ravyn can be done in [levels](https://ravyn.dev/application/levels/), which means
            these tags on a Ravyn instance, means it will be added to every route even
            if those routes also contain tags.

            **Example**

            ```python
            from ravyn import route

            @route(tags=["application"])
            ```
            """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if the handler
            should be deprecated in the OpenAPI documentation.

            **Example**

            ```python
            from ravyn import route

            @route(deprecated=True)
            ```
            """
        ),
    ] = None,
    security: Annotated[
        Optional[list["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Ravyn offers some out of the box solutions where this is implemented.

            The [Ravyn security](https://ravyn.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://ravyn.dev/application/levels/).

            For custom security objects, you **must** subclass
            `ravyn.openapi.security.base.HTTPBase` object.

            **Example**

            ```python
            from ravyn import route
            from ravyn.openapi.security.http import Bearer

            @route(security=[Bearer()])
            ```
            """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
            The unique identifier of the `handler`. This acts as a unique ID
            for the OpenAPI documentation.

            !!! Tip
                Usually you don't need this as Ravyn handles it automatically
                but it is here if you want to add your own.
            """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
            A description of the response. This is used for OpenAPI documentation
            purposes only and accepts all the docstrings including `markdown` format.
            """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[dict[int, OpenAPIResponse]],
        Doc(
            """
            Additional responses that are handled by the handler and need to be described
            in the OpenAPI documentation.

            The `responses` is a dictionary like object where the first parameter is an
            `integer` and the second is an instance of an [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object.


            Read more about [OpenAPIResponse](https://ravyn.dev/responses/#openapi-responses) object and how to use it.


            **Example**

            ```python
            from ravyn import route
            from ravyn.openapi.datastructures import OpenAPIResponse
            from pydantic import BaseModel

            class Power(BaseModel):
                name: str
                description: str


            class Error(BaseModel):
                detail: str


            @route(path='/read', responses={
                    200: OpenAPIResponse(model=Power, description=...)
                    400: OpenAPIResponse(model=Error, description=...)
                }
            )
            async def operate() -> Union[None, ItemOut]:
                ...
            ```
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
) -> Callable[[F], HTTPHandler]:
    """
    Handler responsible for allowing multiple HTTP verbs in one go
    all of its operatations.

    **Example**

    ```python
    from ravyn import route


    @route(methods=["GET", "POST", "DELETE"])
    async def operate() -> str:
        return "Hello, World!"
    ```
    """
    if not methods or not isinstance(methods, list):
        raise ImproperlyConfigured(
            "http handler demands `methods` to be declared. An example would be: @route(methods=['GET', 'PUT'])."
        )

    for method in methods:
        if method.upper() not in AVAILABLE_METHODS:
            raise ImproperlyConfigured(
                f"Invalid method {method}. An example would be: @route(methods=['GET', 'PUT'])."
            )

    methods = [method.upper() for method in methods]
    if not status_code:  # pragma: no cover
        status_code = status.HTTP_200_OK

    def wrapper(func: Callable[..., Any]) -> HTTPHandler:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        handler = HTTPHandler(
            path=path,
            name=name,
            methods=methods,
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
            before_request=before_request,
            after_request=after_request,
        )

        handler.fn = func
        handler.handler = wrapped
        handler.__type__ = HttpMethod.GET.value
        handler.__original_status_code__ = status.HTTP_200_OK

        if status_code != handler.__original_status_code__:
            handler.__is_status_overridden__ = True

        handler.validate_handler()
        return handler

    return wrapper


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
