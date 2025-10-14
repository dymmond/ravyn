import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Sequence, Set

from lilya._internal._connection import Connection  # noqa
from lilya.authentication import (
    AuthCredentials,  # noqa
    AuthenticationBackend,
)
from lilya.middleware.authentication import (
    AuthenticationMiddleware as LilyaAuthenticationMiddleware,
)
from lilya.types import ASGIApp, Receive, Scope, Send
from typing_extensions import Annotated, Doc

from ravyn.core.protocols.middleware import MiddlewareProtocol
from ravyn.exceptions import AuthenticationError
from ravyn.parsers import ArbitraryBaseModel
from ravyn.responses.base import Response
from ravyn.utils.enums import ScopeType


class AuthResult(ArbitraryBaseModel):
    user: Annotated[
        Any,
        Doc(
            """
            Arbitrary user coming from the `authenticate` of the `BaseAuthMiddleware`
            and can be assigned to the `request.user`.
            """
        ),
    ]


class BaseAuthMiddleware(ABC, MiddlewareProtocol):  # pragma: no cover
    """
    `BaseAuthMiddleware` is the object that you can implement if you
    want to implement any `authentication` middleware with Ravyn.

    It is not mandatory to use it and you are free to implement your.

    Ravyn being based on Lilya, also offers a simple but powerful
    interface for handling `authentication` and [permissions](https://ravyn.dev/permissions/).

    Once you have installed the `AuthenticationMiddleware` and implemented the
    `authenticate`, the `request.user` will be available in any of your
    endpoints.

    Read more about how [Ravyn implements](https://ravyn.dev/middleware/middleware#baseauthmiddleware) the `BaseAuthMiddleware`.

    When implementing the `authenticate`, you must assign the result into the
    `AuthResult` object in order for the middleware to assign the `request.user`
    properly.

    !!! Warning "Deprecation Warning"
        `BaseAuthMiddleware` is deprecated and will be removed in a future release.
        Please use `AuthenticationMiddleware` from `ravyn.middleware.authentication`
        which provides the same functionality with a more robust implementation.

    The `AuthResult` is of type `ravyn.middleware.authentication.AuthResult`.
    """

    def __init__(
        self,
        app: Annotated[
            ASGIApp,
            Doc(
                """
                An ASGI type callable.
                """
            ),
        ],
    ):
        super().__init__(app)
        self.app = app
        self.scopes: Set[str] = {ScopeType.HTTP, ScopeType.WEBSOCKET}

        warning_msg = (
            "`BaseAuthMiddleware` is deprecated and will be removed in a future release (0.4.0). "
            "Please use `AuthenticationMiddleware`from `ravyn.middleware.authentication` which "
            "provides the same functionality with a more robust implementation."
        )
        warnings.warn(
            warning_msg,
            DeprecationWarning,
            stacklevel=2,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Function callable that automatically will call the `authenticate` function
        from any middleware subclassing the `BaseAuthMiddleware` and assign the `AuthUser` user
        to the `request.user`.
        """
        if scope["type"] not in self.scopes:
            await self.app(scope, receive, send)
            return

        auth_result = await self.authenticate(Connection(scope))
        scope["user"] = auth_result.user
        await self.app(scope, receive, send)

    @abstractmethod
    async def authenticate(self, request: Connection) -> AuthResult:
        """
        The abstract method that needs to be implemented for any authentication middleware.
        """
        raise NotImplementedError("authenticate must be implemented.")


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
