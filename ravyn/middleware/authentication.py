from collections.abc import Callable
from typing import Any, Sequence

from lilya._internal._connection import Connection  # noqa
from lilya.authentication import (
    AuthCredentials,  # noqa
    AuthenticationBackend,
)
from lilya.middleware.authentication import (
    AuthenticationMiddleware as LilyaAuthenticationMiddleware,
)
from lilya.types import ASGIApp
from typing_extensions import Annotated, Doc

from ravyn.exceptions import AuthenticationError
from ravyn.parsers import ArbitraryBaseModel
from ravyn.responses.base import Response


class AuthResult(ArbitraryBaseModel):
    user: Annotated[
        Any,
        Doc(
            """
            Arbitrary user coming from authentication and assignable to `request.user`.
            """
        ),
    ]


class AuthenticationMiddleware(LilyaAuthenticationMiddleware):
    def __init__(
        self,
        app: Annotated[
            ASGIApp,
            Doc(
                """
                The ASGI application callable wrapped by this middleware.
                """
            ),
        ],
        backend: Annotated[
            AuthenticationBackend | Sequence[AuthenticationBackend] | None,
            Doc(
                """
                One or more authentication backends used to authenticate the connection.
                If multiple backends are provided, they are tried in order.
                """
            ),
        ] = None,
        on_error: Annotated[
            Callable[[Connection, AuthenticationError], Response] | None,
            Doc(
                """
                An optional error handler function called when authentication fails.
                It receives the Connection and AuthenticationError and must return an
                ASGI-compatible Response object.
                """
            ),
        ] = None,
    ) -> None:
        super().__init__(app=app, backend=backend, on_error=on_error)  # type: ignore[arg-type]
