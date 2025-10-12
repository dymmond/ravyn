from typing import cast

from lilya import status
from lilya.exceptions import HTTPException as LilyaHTTPException
from lilya.requests import Request
from lilya.responses import Response as LilyaResponse
from orjson import loads
from pydantic import ValidationError

from ravyn.exceptions import (
    ExceptionErrorMap,
    HTTPException,
    ImproperlyConfigured,
)
from ravyn.responses import JSONResponse, Response
from ravyn.utils.enums import MediaType


async def http_exception_handler(
    request: Request, exc: HTTPException | LilyaHTTPException
) -> JSONResponse | Response:  # pragma: no cover
    """
    Default exception handler for LilyaHTTPException and Ravyn HTTPException.
    """

    extra = getattr(exc, "extra", None)
    headers = getattr(exc, "headers", None)
    response = getattr(exc, "response", None)

    if exc.response is not None:
        return cast(Response, response)

    if exc.status_code in {204, 304}:
        return JSONResponse(None, status_code=exc.status_code, headers=headers)

    if headers and not extra:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=headers)
    elif headers and extra:
        return JSONResponse(
            {"detail": exc.detail, "extra": extra},
            status_code=exc.status_code,
            headers=headers,
        )
    elif not headers and extra:
        return JSONResponse({"detail": exc.detail, "extra": extra}, status_code=exc.status_code)
    else:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


async def validation_error_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:  # pragma: no cover
    extra = getattr(exc, "extra", None)
    status_code = status.HTTP_400_BAD_REQUEST

    if extra:
        errors_extra = exc.extra.get("extra", {})
        return JSONResponse(
            {"detail": exc.detail, "errors": errors_extra},
            status_code=status_code,
        )
    else:
        return JSONResponse(
            {"detail": exc.detail},
            status_code=status_code,
        )


async def http_error_handler(
    _: Request, exc: ExceptionErrorMap
) -> JSONResponse:  # pragma: no cover
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


async def improperly_configured_exception_handler(
    request: Request, exc: ImproperlyConfigured
) -> LilyaResponse:  # pragma: no cover
    """
    When an ImproperlyConfiguredException is raised.
    """
    status_code = (
        exc.status_code
        if isinstance(exc, LilyaHTTPException)
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    if not status_code:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    content = {"detail": exc.detail}
    if exc.extra:
        content.update({"extra": exc.extra})  # type: ignore[dict-item]
    headers = exc.headers if isinstance(exc, (HTTPException, LilyaHTTPException)) else None

    return Response(
        media_type=MediaType.JSON,
        content=content,
        status_code=status_code,
        headers=headers,
    )


async def pydantic_validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:  # pragma: no cover
    """
    This handler is to be used when a pydantic validation error is triggered during the logic
    of a code block and not the definition of a handler.

    This is different from validation_error_exception_handler
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return JSONResponse({"detail": loads(exc.json())}, status_code=status_code)


async def value_error_handler(
    request: Request, exc: ValueError
) -> JSONResponse:  # pragma: no cover
    """
    Simple handler that manages all the ValueError exceptions thrown to the user properly
    formatted.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    details = loads(exc.json()) if hasattr(exc, "json") else exc.args[0]
    return JSONResponse({"detail": details}, status_code=status_code)
