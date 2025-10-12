from __future__ import annotations

from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    NoReturn,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
)

import orjson
from lilya import status
from lilya.responses import (
    RESPONSE_TRANSFORM_KWARGS,
    CSVResponse as CSVResponse,  # noqa
    Error as Error,  # noqa
    EventStreamResponse as EventStreamResponse,  # noqa
    FileResponse as FileResponse,  # noqa
    HTMLResponse as HTMLResponse,  # noqa
    ImageResponse as ImageResponse,  # noqa
    JSONResponse as JSONResponse,  # noqa
    NDJSONResponse as NDJSONResponse,  # noqa
    Ok as Ok,  # noqa
    PlainText as PlainText,  # noqa
    RedirectResponse as RedirectResponse,  # noqa
    Response as LilyaResponse,  # noqa
    StreamingResponse as StreamingResponse,  # noqa
    XMLResponse as XMLResponse,  # noqa
)
from typing_extensions import Annotated, Doc

from ravyn.encoders import Encoder
from ravyn.exceptions import ImproperlyConfigured
from ravyn.utils.enums import MediaType

from .mixins import ORJSONTransformMixin

PlainTextResponse = PlainText

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.background import BackgroundTask, BackgroundTasks
    from ravyn.types import ResponseCookies

T = TypeVar("T")


class Response(ORJSONTransformMixin, LilyaResponse, Generic[T]):
    """
    Default `Response` object from Ravyn where it can be as the
    return annotation of a [handler](https://ravyn.dev/routing/handlers/).

    Ravyn automatically will understand what time of response is going to be
    used and parse all the details automatically.

    **Example**

    ```python
    from pydantic import BaseModel

    from ravyn import Ravyn, Gateway, Response, get
    from ravyn.datastructures import Cookie


    @get(path="/me")
    async def home() -> Response:
        return Response(
            Item(id=1, sku="sku1238"),
            headers={"SKY-HEADER": "sku-xyz"},
            cookies=[Cookie(key="sku", value="a-value")],
        )


    Ravyn(routes=[Gateway(handler=home)])
    ```
    """

    def __init__(
        self,
        content: Annotated[
            Any,
            Doc(
                """
                Any content being sent to the response.
                """
            ),
        ],
        *,
        status_code: Annotated[
            int,
            Doc(
                """
                The response status code.
                """
            ),
        ] = status.HTTP_200_OK,
        media_type: Annotated[
            Optional[Union[MediaType, str]],
            Doc(
                """
                The media type used in the response.
                """
            ),
        ] = None,
        background: Annotated[
            Optional[Union[BackgroundTask, BackgroundTasks]],
            Doc(
                """
                Any instance of a [BackgroundTask or BackgroundTasks](https://ravyn.dev/background-tasks/).
                """
            ),
        ] = None,
        headers: Annotated[
            Optional[dict[str, Any]],
            Doc(
                """
                Any additional headers being passed to the response.
                """
            ),
        ] = None,
        cookies: Annotated[
            Optional[ResponseCookies],
            Doc(
                """
                A sequence of `ravyn.datastructures.Cookie` objects.

                Read more about the [Cookies](https://ravyn.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from ravyn import Response
                from ravyn.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                Response(cookies=response_cookies)
                ```
                """
            ),
        ] = None,
        encoders: Annotated[
            Union[Sequence[Encoder], None],
            Doc(
                """
                A sequence of `ravyn.encoders.Encoder` type of objects to be used
                by the response object directly.

                **Example**

                ```python
                from ravyn import Response
                from ravyn.encoders import PydanticEncoder, MsgSpecEncoder

                response_cookies=[
                    encoders=[PydanticEncoder, MsgSpecEncoder]
                ]

                Response(cookies=response_cookies)
                ```
                """
            ),
        ] = None,
        passthrough_body_types: Annotated[
            Union[tuple[type, ...], None],
            Doc(
                """
            A tuple with types, which should be passed through directly to the ASGI server.
            By default only "bytes" are passed through but some ASGI servers can also handle
            memoryviews or strings.
            If set, it should include the "bytes" type.
            As an alternative you can subclass and set a ClassVar named passthrough_body_types.

            Be warned: this is highly ASGI server specific and may requires you to set the content-length header yourself.
            """
            ),
        ] = None,
    ) -> None:
        self.cookies = cookies or []
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers or {},
            media_type=media_type,
            background=cast("BackgroundTask", background),
            encoders=encoders,
            passthrough_body_types=passthrough_body_types,
        )

    def make_response(self, content: Any) -> bytes:
        if (
            content is None
            or content is NoReturn
            and (
                self.status_code < 100
                or self.status_code in {status.HTTP_204_NO_CONTENT, status.HTTP_304_NOT_MODIFIED}
            )
        ):
            return b""
        transform_kwargs = RESPONSE_TRANSFORM_KWARGS.get()
        if transform_kwargs:
            transform_kwargs = transform_kwargs.copy()
        elif isinstance(content, str) and self.media_type != MediaType.JSON:
            # treat strings special when not using json and disable mangling when no context is active.
            transform_kwargs = None
        else:
            transform_kwargs = {}
        if transform_kwargs is not None:
            transform_kwargs.setdefault(
                "json_encode_fn",
                partial(
                    orjson.dumps,
                    option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_OMIT_MICROSECONDS,
                ),
            )
        try:
            # switch to a special mode for MediaType.JSON (default handlers)
            if self.media_type == MediaType.JSON:
                # keep it a serialized json object
                if transform_kwargs is not None:
                    transform_kwargs.setdefault("post_transform_fn", None)
            # otherwise use default logic of lilya striping '"'
            with self.with_transform_kwargs(transform_kwargs):
                # if content is bytes it won't be transformed and
                # if None or NoReturn, return b"", this differs from the dedicated JSONResponses.
                return super().make_response(content)
        except (AttributeError, ValueError, TypeError) as e:  # pragma: no cover
            raise ImproperlyConfigured("Unable to serialize response content") from e
