from http import HTTPStatus
from typing import Any, Optional, Tuple, Union, cast

from lilya import status
from lilya.exceptions import (
    EnvironmentError as EnvironmentError,
    HTTPException as LilyaHTTPException,
    ImproperlyConfigured as ImproperlyConfigured,
    LilyaException as LilyaException,
    MethodNotAllowed as MethodNotAllowed,
    NotAuthorized as NotAuthorized,
    NotFound as NotFound,
    PermissionDenied as PermissionDenied,
    TemplateNotFound as TemplateNotFound,
    WebSocketException as WebSocketException,
)
from typing_extensions import Annotated, Doc

from ravyn.contrib.encoding import force_str


def _get_error_details(data: Any) -> Any:
    if isinstance(data, (list, tuple)):
        return [_get_error_details(item) for item in data]

    elif isinstance(data, dict):
        return {key: _get_error_details(value) for key, value in data.items()}

    text = force_str(data)
    return ErrorDetail(text)


class ErrorDetail(str):
    def __new__(cls, string: str) -> "ErrorDetail":
        self = super().__new__(cls, string)
        return self

    def __repr__(self) -> str:
        return "ErrorDetail(string=%r)" % (str(self))

    def __hash__(self) -> int:
        return hash(str(self))


class RavynAPIException(LilyaException): ...


class HTTPException(LilyaHTTPException, RavynAPIException):
    """
    Base of all `Ravyn` execeptions.

    !!! Tip
        For an implementation of a custom exception that you need
        to be thrown by Ravyn, it is advised to subclass `HTTPException`.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *args: Annotated[
            Any,
            Doc(
                """
                The args passed to the exception.
                """
            ),
        ],
        detail: Annotated[
            Optional[str],
            Doc(
                """
                A string text with the details of the error being thrown.
                """
            ),
        ] = None,
        status_code: Annotated[
            Optional[int],
            Doc(
                """
                An integer with the status code to be raised.
                """
            ),
        ] = None,
        headers: Annotated[
            Optional[dict[str, Any]],
            Doc(
                """
                Any python dictionary containing headers.
                """
            ),
        ] = None,
        response: Any | None = None,
        **extra: Annotated[
            Any,
            Doc(
                """
                Any extra information used by the exception.
                """
            ),
        ],
    ) -> None:
        detail = detail or getattr(self, "detail", None)
        status_code = status_code or getattr(self, "status_code", None)
        if not detail:
            detail = args[0] if args else HTTPStatus(status_code or self.status_code).phrase
            args = args[1:]
        super().__init__(
            status_code=status_code, detail=detail, headers=headers, response=response
        )
        self.detail = detail
        self.headers = headers
        self.args = (f"{self.status_code}: {self.detail}", *args)
        self.extra = extra

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.status_code}: {self.__class__.__name__} />"


class ImproperlyMiddlewareConfigured(ImproperlyConfigured): ...


class NotAuthenticated(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication credentials were not provided."


class ValidationErrorException(HTTPException, ValueError):
    status_code = status.HTTP_400_BAD_REQUEST


class InternalServerError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ServiceUnavailable(HTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class MissingDependency(RavynAPIException, ImportError): ...


class OpenAPIException(ImproperlyConfigured): ...


class AuthenticationError(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED


class ValidationError(HTTPException):
    """
    Provides a more detailed error message for validation errors
    when thrown by the application.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Validation error."

    def __init__(
        self,
        detail: Union[str, list[str], dict[str, Any], Tuple[str]] = None,
        status_code: Annotated[
            Optional[int],
            Doc(
                """
                An integer with the status code to be raised.
                """
            ),
        ] = None,
        headers: Annotated[
            Optional[dict[str, Any]],
            Doc(
                """
                Any python dictionary containing headers.
                """
            ),
        ] = None,
        **extra: Annotated[
            Any,
            Doc(
                """
                Any extra information used by the exception.
                """
            ),
        ],
    ) -> None:
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        detail = _get_error_details(detail)
        super().__init__(
            status_code=status_code, detail=cast(str, detail), headers=headers, **extra
        )


ExceptionErrorMap = Union[
    HTTPException,
    NotAuthenticated,
    PermissionDenied,
    NotAuthorized,
    NotFound,
    MethodNotAllowed,
    InternalServerError,
    ServiceUnavailable,
]
