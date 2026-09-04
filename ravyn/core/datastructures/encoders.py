from typing import TYPE_CHECKING, Any, Optional, Type, Union

from typing_extensions import Annotated, Doc

from ravyn.core.datastructures.base import ResponseContainer
from ravyn.utils.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from ravyn.applications import Ravyn
    from ravyn.responses.encoders import ORJSONResponse, UJSONResponse
else:
    try:
        from ravyn.responses.encoders import ORJSONResponse
    except ImportError:  # pragma: no cover
        ORJSONResponse = None

    try:
        from ravyn.responses.encoders import UJSONResponse
    except ImportError:  # pragma: no cover
        UJSONResponse = None


class ORJSON(ResponseContainer[ORJSONResponse]):
    content: Annotated[
        Optional[dict[str, Any]],
        Doc(
            """
            The content being sent to the response.
            """
        ),
    ] = None
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            The status code of the response. It will default to the
            [handler](https://ravyn.dev/routing/handlers/) if none is provided.
            """
        ),
    ] = None
    media_type: Annotated[
        str,
        Doc(
            """
            The media type of the response.
            """
        ),
    ] = "application/json"

    def __init__(
        self,
        content: Optional[dict[str, Any]] = None,
        status_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.content = content
        self.status_code = status_code

    def to_response(
        self,
        headers: dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Ravyn"],
    ) -> ORJSONResponse:
        assert ORJSONResponse is not None, (
            "You must install the encoders or orjson to use ORJSONResponse"
        )
        status = self.status_code or status_code

        return ORJSONResponse(
            content=self.content,
            headers=headers,
            status_code=status,
            media_type=media_type,
            background=self.background,
        )


OrJSON = ORJSON


class UJSON(ResponseContainer[UJSONResponse]):
    content: Annotated[
        Optional[dict[str, Any]],
        Doc(
            """
            The content being sent to the response.
            """
        ),
    ] = None
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            The status code of the response. It will default to the
            [handler](https://ravyn.dev/routing/handlers/) if none is provided.
            """
        ),
    ] = None
    media_type: Annotated[
        str,
        Doc(
            """
            The media type of the response.
            """
        ),
    ] = "application/json"

    def __init__(
        self,
        content: Optional[dict[str, Any]] = None,
        status_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.content = content
        self.status_code = status_code

    def to_response(
        self,
        headers: dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Ravyn"],
    ) -> UJSONResponse:
        assert UJSONResponse is not None, (
            "You must install the encoders or ujson to use UJSONResponse"
        )
        status = self.status_code or status_code

        return UJSONResponse(
            content=self.content,
            headers=headers,
            status_code=status,
            media_type=media_type,
            background=self.background,
        )
