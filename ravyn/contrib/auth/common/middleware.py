from typing import Any, TypeVar

from jwt.exceptions import PyJWTError
from lilya._internal._connection import Connection
from lilya.authentication import AuthCredentials
from lilya.types import ASGIApp

from ravyn.core.config.jwt import JWTConfig
from ravyn.exceptions import AuthenticationError, NotAuthorized
from ravyn.middleware.authentication import AuthenticationBackend, AuthenticationMiddleware
from ravyn.security.jwt.token import Token

T = TypeVar("T")


class CommonJWTAuthBackend(AuthenticationBackend):  # pragma: no cover
    """
    The simple JWT authentication Middleware.
    """

    def __init__(
        self,
        config: "JWTConfig",
        user_model: T,
    ):
        """
        The user is simply the class type to be queried from the Tortoise ORM.

        Example how to use:

            1. User table

                from ravyn.contrib.auth.edgy.base_user import User as BaseUser

                class User(BaseUser):
                    ...

            2. Middleware

                from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware
                from ravyn.config import JWTConfig

                jwt_config = JWTConfig(...)

                class CustomJWTMidleware(JWTAuthMiddleware):
                    def __init__(self, app: "ASGIApp"):
                        super().__init__(app, config=jwt_config, user=User)

            3. The application
                from ravyn import Ravyn
                from myapp.middleware import CustomJWTMidleware

                app = Ravyn(routes=[...], middleware=[CustomJWTMidleware])

        """
        self.config = config
        self.user_model = user_model

    async def authenticate(
        self, request: Connection, **kwargs: Any
    ) -> tuple[AuthCredentials, Any]:
        """
        Retrieves the header default of the config and validates against the decoding.

        Raises Authentication error if invalid.
        """
        token = request.headers.get(self.config.authorization_header, None)

        if not token or token is None:
            raise NotAuthorized(detail="Token not found in the request header")

        token_partition = token.partition(" ")
        token_type = token_partition[0]
        auth_token = token_partition[-1]

        if token_type not in self.config.auth_header_types:
            raise NotAuthorized(detail=f"'{token_type}' is not an authorized header.")

        try:
            token = Token.decode(
                token=auth_token,
                key=self.config.signing_key,
                algorithms=[self.config.algorithm],
            )
        except PyJWTError as e:
            raise AuthenticationError(str(e)) from e

        user = await self.retrieve_user(token.sub)
        if not user:
            raise AuthenticationError("User not found.")
        return AuthCredentials(), user


class CommonJWTAuthMiddleware(AuthenticationMiddleware):
    """
    The simple JWT authentication Middleware.
    """

    def __init__(
        self,
        app: ASGIApp,
        backend: AuthenticationBackend | list[AuthenticationBackend] | None = None,
    ):
        super().__init__(app, backend=backend)
